#!/usr/bin/env python3
"""Model Assigner - Assigns optimal models based on task difficulty and capabilities."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from .evaluator import ModelEvaluator
from .task_classifier import DifficultyLevel, classify_task

logger = logging.getLogger(__name__)


@dataclass
class ModelAssignment:
    agent_type: str
    model: str
    difficulty: str
    reason: str
    estimated_tokens: int
    estimated_duration: int


class ModelAssigner:
    """Assigns optimal models based on task difficulty and capabilities."""

    MODEL_TIERS = {
        "local_fast": ["qwen2.5-coder:1.5b", "phi3:mini", "gemma2:2b"],
        "local_balanced": ["qwen2.5-coder:7b", "gemma4:12b"],
        "cloud_free": ["gemini-2.5-flash", "gemini-2.5-pro"],
        "cloud_paid": ["claude-sonnet-4-20250514", "gpt-4o"],
    }

    def __init__(self, evaluator: Optional[ModelEvaluator] = None):
        self.evaluator = evaluator or ModelEvaluator()
        self.custom_assignments: Dict[str, str] = {}

    def assign(
        self,
        task_description: str,
        agent_type: str = "coder",
        preferred_model: Optional[str] = None,
    ) -> ModelAssignment:
        """Assign a model based on task difficulty and capabilities."""
        for pattern, model in self.custom_assignments.items():
            if pattern in task_description:
                classification = classify_task(task_description)
                return ModelAssignment(
                    agent_type=agent_type,
                    model=model,
                    difficulty=classification.difficulty.value,
                    reason=f"Custom assignment for pattern: {pattern}",
                    estimated_tokens=classification.estimated_tokens,
                    estimated_duration=classification.estimated_duration_seconds,
                )

        classification = classify_task(task_description)
        difficulty = classification.difficulty
        task_type = classification.task_type

        if preferred_model:
            return ModelAssignment(
                agent_type=agent_type,
                model=preferred_model,
                difficulty=difficulty.value,
                reason=f"Preferred model selected for {task_type}",
                estimated_tokens=classification.estimated_tokens,
                estimated_duration=classification.estimated_duration_seconds,
            )

        best_model = self._find_best_model(difficulty, task_type)
        return ModelAssignment(
            agent_type=agent_type,
            model=best_model,
            difficulty=difficulty.value,
            reason=f"Best fit for {task_type} at {difficulty.value}",
            estimated_tokens=classification.estimated_tokens,
            estimated_duration=classification.estimated_duration_seconds,
        )

    def _find_best_model(self, difficulty: DifficultyLevel, task_type: str) -> str:
        """Find the best model for the given difficulty and task type."""
        if difficulty == DifficultyLevel.EASY:
            return self.MODEL_TIERS["local_fast"][0]
        elif difficulty == DifficultyLevel.MEDIUM:
            return self.MODEL_TIERS["local_balanced"][0]
        elif difficulty == DifficultyLevel.HARD:
            return self.MODEL_TIERS["local_balanced"][-1]
        else:
            return self.MODEL_TIERS["cloud_free"][0]

    def assign_batch(
        self, tasks: List[str], agent_types: Optional[List[str]] = None
    ) -> List[ModelAssignment]:
        """Assign models to multiple tasks."""
        if agent_types is None:
            agent_types = ["coder"] * len(tasks)

        return [
            self.assign(task, agent_type)
            for task, agent_type in zip(tasks, agent_types)
        ]

    def set_custom_assignment(self, model: str, task_description: str):
        """Set a custom model assignment for a task pattern."""
        self.custom_assignments[task_description] = model
        logger.info(f"Custom assignment: {task_description[:30]}... -> {model}")

    def clear_custom_assignments(self):
        """Clear all custom assignments."""
        self.custom_assignments.clear()
