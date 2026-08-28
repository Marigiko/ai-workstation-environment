#!/usr/bin/env python3
"""Auto Orchestrator - Plans, decomposes, distributes, and aggregates tasks."""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import httpx

from .assigner import ModelAssigner
from .task_classifier import classify_task

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(Enum):
    ARCHITECT = "architect"
    CODER = "coder"
    REVIEWER = "reviewer"
    DOCUMENTER = "documenter"
    TESTER = "tester"
    DEBUGGER = "debugger"


@dataclass
class SubTask:
    id: str
    title: str
    description: str
    agent_type: AgentType
    model: str
    difficulty: str = "medium"
    estimated_tokens: int = 0
    estimated_duration: int = 0
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    error: str = ""
    dependencies: List[str] = field(default_factory=list)


@dataclass
class OrchestrationPlan:
    task_id: str
    original_prompt: str
    subtasks: List[SubTask]
    status: TaskStatus = TaskStatus.PENDING


class AutoOrchestrator:
    """Orchestrates multi-agent task execution with auto mode.

    All model calls go through AI Proxy (port 8090) which applies
    Headroom compression before forwarding to MiMo/Claude backends.
    """

    def __init__(
        self,
        gateway_client=None,
        headroom_client=None,
        proxy_url: str = "http://localhost:8090",
    ):
        self.gateway = gateway_client
        self.headroom = headroom_client
        self.proxy_url = proxy_url
        self.plans: Dict[str, OrchestrationPlan] = {}
        self.assigner = ModelAssigner()

    def get_model_for_task(self, task_description: str, agent_type: AgentType) -> str:
        """Select model based on task difficulty and agent type."""
        assignment = self.assigner.assign(
            task_description=task_description,
            agent_type=agent_type.value,
        )
        return assignment.model

    async def plan_task(self, task_id: str, prompt: str) -> OrchestrationPlan:
        """Create an orchestration plan from a prompt."""
        logger.info(f"Planning task {task_id}: {prompt[:50]}...")

        plan = OrchestrationPlan(
            task_id=task_id,
            original_prompt=prompt,
            subtasks=[],
            status=TaskStatus.PLANNING,
        )

        classification = classify_task(prompt)

        architecture_subtask = SubTask(
            id=f"{task_id}-arch",
            title="Architecture Planning",
            description=f"Plan the implementation for: {prompt}",
            agent_type=AgentType.ARCHITECT,
            model=self.get_model_for_task(prompt, AgentType.ARCHITECT),
            difficulty=classification.difficulty.value,
            estimated_tokens=classification.estimated_tokens,
            estimated_duration=classification.estimated_duration_seconds,
        )

        subtask_configs = [
            (AgentType.CODER, "Implementation", f"Implement the solution for: {prompt}"),
            (AgentType.REVIEWER, "Code Review", "Review the implementation for quality"),
            (AgentType.DOCUMENTER, "Documentation", "Document the implementation"),
        ]

        plan.subtasks = [architecture_subtask]
        for agent_type, title, description in subtask_configs:
            subtask = SubTask(
                id=f"{task_id}-{agent_type.value}",
                title=title,
                description=description,
                agent_type=agent_type,
                model=self.get_model_for_task(description, agent_type),
                difficulty=classification.difficulty.value,
                estimated_tokens=classification.estimated_tokens,
                estimated_duration=classification.estimated_duration_seconds,
            )
            plan.subtasks.append(subtask)

        self.plans[task_id] = plan
        return plan

    async def execute_plan(self, task_id: str) -> Dict:
        """Execute an orchestration plan."""
        plan = self.plans.get(task_id)
        if not plan:
            return {"error": f"Plan {task_id} not found"}

        plan.status = TaskStatus.EXECUTING
        results = {}

        # Execute architect first
        arch_task = plan.subtasks[0]
        try:
            arch_task.status = TaskStatus.EXECUTING
            result = await self._execute_subtask(arch_task)
            arch_task.result = result
            arch_task.status = TaskStatus.COMPLETED
            results["architect"] = result
        except Exception as e:
            arch_task.error = str(e)
            arch_task.status = TaskStatus.FAILED
            results["architect"] = {"error": str(e)}

        # Execute remaining subtasks (can be parallel)
        remaining_tasks = plan.subtasks[1:]
        remaining_results = await asyncio.gather(
            *[self._execute_subtask(t) for t in remaining_tasks],
            return_exceptions=True,
        )

        for task, result in zip(remaining_tasks, remaining_results):
            if isinstance(result, Exception):
                task.error = str(result)
                task.status = TaskStatus.FAILED
                results[task.agent_type.value] = {"error": str(result)}
            else:
                task.result = result
                task.status = TaskStatus.COMPLETED
                results[task.agent_type.value] = result

        # Aggregate results
        aggregated = await self._aggregate_results(results)
        plan.status = TaskStatus.COMPLETED

        return {
            "task_id": task_id,
            "status": "completed",
            "results": results,
            "aggregated": aggregated,
            "subtasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "agent": t.agent_type.value,
                    "model": t.model,
                    "status": t.status.value,
                }
                for t in plan.subtasks
            ],
        }

    async def _execute_subtask(self, subtask: SubTask) -> str:
        """Execute a single subtask via AI Proxy (with Headroom compression).

        All model calls go through the proxy, which compresses prompts
        via Headroom before forwarding to MiMo/Claude backends.
        """
        # Build messages
        messages = [{"role": "user", "content": subtask.description}]

        # Wrap with Headroom compression
        if self.headroom:
            messages = await self.headroom.wrap_context(
                f"You are a {subtask.agent_type.value} agent.",
                subtask.description,
            )

        # Try proxy first (MiMo/Claude with Headroom compression)
        if self.proxy_url:
            try:
                result = await self._execute_via_proxy(messages, subtask.model)
                return result
            except Exception as e:
                logger.warning(f"Proxy failed, trying gateway: {e}")

        # Fallback to gateway (LiteLLM)
        if self.gateway:
            result = await self.gateway.chat_completions(
                messages=messages,
                model=subtask.model,
            )
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"[Simulated] {subtask.agent_type.value} completed: {subtask.title}"

    async def _execute_via_proxy(self, messages: List[Dict], model: str) -> str:
        """Execute via AI Proxy Server (which handles Headroom compression)."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.proxy_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 1024,
                    "headroom": True,
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _aggregate_results(self, results: Dict) -> str:
        """Aggregate results from all subtasks."""
        aggregated = []
        for agent_type, result in results.items():
            if isinstance(result, dict) and "error" in result:
                aggregated.append(f"❌ {agent_type}: {result['error']}")
            else:
                aggregated.append(f"✅ {agent_type}: {str(result)[:200]}")
        return "\n".join(aggregated)

    def get_plan(self, task_id: str) -> Optional[OrchestrationPlan]:
        return self.plans.get(task_id)

    def list_plans(self) -> List[Dict]:
        return [
            {
                "task_id": p.task_id,
                "status": p.status.value,
                "subtasks": len(p.subtasks),
            }
            for p in self.plans.values()
        ]
