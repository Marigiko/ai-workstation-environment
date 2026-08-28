#!/usr/bin/env python3
"""Task Decomposer - Breaks complex tasks into subtasks using LLM."""

import json
import logging
from dataclasses import dataclass
from typing import Dict, List

from .task_classifier import classify_task

logger = logging.getLogger(__name__)


@dataclass
class DecomposedTask:
    id: str
    title: str
    description: str
    agent_type: str
    difficulty: str
    estimated_tokens: int
    estimated_duration: int
    dependencies: List[str]
    priority: int


class TaskDecomposer:
    """Decomposes complex tasks into manageable subtasks."""

    DECOMPOSITION_PROMPT = """You are a task decomposer for an AI Engineering platform.
Break down the following task into specific subtasks. For each subtask, provide:
- id: unique identifier
- title: short title
- description: detailed description
- agent_type: one of architect, coder, reviewer, documenter, tester, debugger
- dependencies: list of subtask ids this depends on
- priority: 1 (highest) to 5 (lowest)

Return as JSON array.

Task: {task}

Context: {context}
"""

    def __init__(self, gateway_client=None):
        self.gateway = gateway_client

    async def decompose(
        self, task: str, context: str = "", max_subtasks: int = 10
    ) -> List[DecomposedTask]:
        """Decompose a task into subtasks."""
        prompt = self.DECOMPOSITION_PROMPT.format(task=task, context=context)

        try:
            if self.gateway:
                result = await self.gateway.chat_completions(
                    messages=[{"role": "user", "content": prompt}],
                    model="qwen2.5-coder:7b",
                )
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "[]")

                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                subtasks_data = json.loads(content)
                subtasks = []
                for i, s in enumerate(subtasks_data[:max_subtasks]):
                    desc = s.get("description", "")
                    classification = classify_task(desc)
                    subtasks.append(
                        DecomposedTask(
                            id=s.get("id", f"task-{i}"),
                            title=s.get("title", f"Subtask {i}"),
                            description=desc,
                            agent_type=s.get("agent_type", "coder"),
                            difficulty=classification.difficulty.value,
                            estimated_tokens=classification.estimated_tokens,
                            estimated_duration=classification.estimated_duration_seconds,
                            dependencies=s.get("dependencies", []),
                            priority=s.get("priority", 3),
                        )
                    )
                return subtasks
            else:
                return self._default_decomposition(task)
        except Exception as e:
            logger.error(f"Decomposition failed: {e}")
            return self._default_decomposition(task)

    def _default_decomposition(self, task: str) -> List[DecomposedTask]:
        """Default decomposition when LLM is unavailable."""
        classification = classify_task(task)
        difficulty = classification.difficulty.value
        tokens = classification.estimated_tokens
        duration = classification.estimated_duration_seconds

        return [
            DecomposedTask(
                id="plan-1",
                title="Architecture Planning",
                description=f"Plan architecture for: {task}",
                agent_type="architect",
                difficulty=difficulty,
                estimated_tokens=tokens,
                estimated_duration=duration,
                dependencies=[],
                priority=1,
            ),
            DecomposedTask(
                id="impl-1",
                title="Implementation",
                description=f"Implement: {task}",
                agent_type="coder",
                difficulty=difficulty,
                estimated_tokens=tokens,
                estimated_duration=duration,
                dependencies=["plan-1"],
                priority=2,
            ),
            DecomposedTask(
                id="review-1",
                title="Code Review",
                description="Review implementation",
                agent_type="reviewer",
                difficulty=difficulty,
                estimated_tokens=tokens,
                estimated_duration=duration,
                dependencies=["impl-1"],
                priority=3,
            ),
            DecomposedTask(
                id="doc-1",
                title="Documentation",
                description="Document implementation",
                agent_type="documenter",
                difficulty=difficulty,
                estimated_tokens=tokens,
                estimated_duration=duration,
                dependencies=["impl-1"],
                priority=4,
            ),
        ]

    async def estimate_effort(self, subtasks: List[DecomposedTask]) -> Dict:
        """Estimate effort for subtasks."""
        total = len(subtasks)
        by_agent = {}
        for st in subtasks:
            by_agent[st.agent_type] = by_agent.get(st.agent_type, 0) + 1

        return {
            "total_subtasks": total,
            "by_agent": by_agent,
            "estimated_time_minutes": total * 2,  # Rough estimate
        }
