#!/usr/bin/env python3
"""Model Assigner - Assigns optimal models to agents based on task type."""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelAssignment:
    agent_type: str
    model: str
    reason: str


# Model tiers based on hardware: RTX 2060 (6GB VRAM) + 48GB RAM
MODEL_TIERS = {
    "local_fast": {
        "models": ["qwen2.5-coder:1.5b", "phi3:mini", "gemma2:2b"],
        "vram": "~2GB",
        "use_case": "Fast responses, simple tasks",
    },
    "local_balanced": {
        "models": ["qwen2.5-coder:7b"],
        "vram": "~5GB",
        "use_case": "Balanced quality/speed",
    },
    "cloud_free": {
        "models": ["gemini-2.5-flash", "gemini-2.5-pro", "opencode-auto"],
        "vram": "N/A",
        "use_case": "Free tier cloud models",
    },
    "cloud_paid": {
        "models": ["claude-sonnet-4-20250514", "gpt-4o", "gpt-4o-mini"],
        "vram": "N/A",
        "use_case": "Paid cloud models",
    },
}

# Default model assignments per agent type
DEFAULT_ASSIGNMENTS = {
    "architect": {"model": "qwen2.5-coder:7b", "tier": "local_balanced", "reason": "Complex planning needs balanced model"},
    "coder": {"model": "qwen2.5-coder:7b", "tier": "local_balanced", "reason": "Code generation needs quality model"},
    "reviewer": {"model": "gemini-2.5-flash", "tier": "cloud_free", "reason": "Review benefits from larger context window"},
    "documenter": {"model": "qwen2.5-coder:1.5b", "tier": "local_fast", "reason": "Documentation is straightforward, fast model sufficient"},
    "tester": {"model": "phi3:mini", "tier": "local_fast", "reason": "Test generation is pattern-based, fast model works"},
    "debugger": {"model": "qwen2.5-coder:7b", "tier": "local_balanced", "reason": "Debugging needs reasoning capability"},
}


class ModelAssigner:
    """Assigns optimal models to agents based on task requirements."""

    def __init__(self, available_models: List[str] = None):
        self.available_models = available_models or list(DEFAULT_ASSIGNMENTS.keys())
        self.custom_assignments: Dict[str, str] = {}

    def assign(self, agent_type: str, task_complexity: str = "medium") -> ModelAssignment:
        """Assign a model to an agent based on type and complexity."""
        # Check custom assignments first
        if agent_type in self.custom_assignments:
            model = self.custom_assignments[agent_type]
            return ModelAssignment(
                agent_type=agent_type,
                model=model,
                reason="Custom assignment",
            )

        # Get default assignment
        default = DEFAULT_ASSIGNMENTS.get(agent_type, DEFAULT_ASSIGNMENTS["coder"])

        # Adjust based on complexity
        if task_complexity == "simple":
            model = "qwen2.5-coder:1.5b"
            reason = "Simple task, using fast model"
        elif task_complexity == "complex":
            model = "qwen2.5-coder:7b"
            reason = "Complex task, using quality model"
        else:
            model = default["model"]
            reason = default["reason"]

        return ModelAssignment(
            agent_type=agent_type,
            model=model,
            reason=reason,
        )

    def assign_batch(self, agent_types: List[str], task_complexity: str = "medium") -> List[ModelAssignment]:
        """Assign models to multiple agents."""
        return [self.assign(at, task_complexity) for at in agent_types]

    def set_custom_assignment(self, agent_type: str, model: str):
        """Set a custom model assignment for an agent type."""
        self.custom_assignments[agent_type] = model
        logger.info(f"Custom assignment: {agent_type} -> {model}")

    def clear_custom_assignments(self):
        """Clear all custom assignments."""
        self.custom_assignments.clear()

    def get_model_tiers(self) -> Dict:
        """Get available model tiers."""
        return MODEL_TIERS

    def suggest_assignment(self, task_description: str) -> Dict[str, ModelAssignment]:
        """Suggest model assignments based on task description."""
        task_lower = task_description.lower()

        assignments = {}

        # Detect task complexity
        if any(word in task_lower for word in ["simple", "basic", "quick", "format"]):
            complexity = "simple"
        elif any(word in task_lower for word in ["complex", "architect", "design", "system"]):
            complexity = "complex"
        else:
            complexity = "medium"

        # Assign based on detected patterns
        agent_types = ["architect", "coder", "reviewer", "documenter"]
        for agent_type in agent_types:
            assignments[agent_type] = self.assign(agent_type, complexity)

        return assignments
