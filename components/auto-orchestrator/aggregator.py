#!/usr/bin/env python3
"""Result Aggregator - Combines results from multiple agents."""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AggregatedResult:
    summary: str
    details: Dict[str, str]
    success: bool
    errors: List[str]


class ResultAggregator:
    """Aggregates results from multiple agent executions."""

    async def aggregate(
        self, results: Dict[str, any], task_context: str = ""
    ) -> AggregatedResult:
        """Aggregate results from multiple agents."""
        success_count = 0
        error_count = 0
        errors = []
        details = {}

        for agent_type, result in results.items():
            if isinstance(result, dict):
                if "error" in result:
                    error_count += 1
                    errors.append(f"{agent_type}: {result['error']}")
                    details[agent_type] = f"ERROR: {result['error']}"
                else:
                    success_count += 1
                    details[agent_type] = str(result.get("output", result))
            else:
                success_count += 1
                details[agent_type] = str(result)

        summary = self._build_summary(success_count, error_count, errors, task_context)

        return AggregatedResult(
            summary=summary,
            details=details,
            success=error_count == 0,
            errors=errors,
        )

    def _build_summary(
        self, success: int, errors: int, error_list: List[str], context: str
    ) -> str:
        """Build a human-readable summary."""
        parts = []

        if errors == 0:
            parts.append(f"✅ All {success} agents completed successfully.")
        else:
            parts.append(f"⚠️ {success} succeeded, {errors} failed.")
            for err in error_list[:3]:
                parts.append(f"  ❌ {err}")

        if context:
            parts.append(f"\nContext: {context[:200]}")

        return "\n".join(parts)

    def format_for_telegram(self, result: AggregatedResult) -> str:
        """Format result for Telegram notification."""
        emoji = "✅" if result.success else "⚠️"
        lines = [f"{emoji} *Task Complete*\n"]
        lines.append(result.summary)

        if result.errors:
            lines.append("\n*Errors:*")
            for err in result.errors[:5]:
                lines.append(f"• {err}")

        return "\n".join(lines)

    def format_for_workspace(self, result: AggregatedResult) -> Dict:
        """Format result for workspace API."""
        return {
            "status": "completed" if result.success else "completed_with_errors",
            "summary": result.summary,
            "details": result.details,
            "errors": result.errors,
        }
