#!/usr/bin/env python3
"""Model Evaluator - Benchmarks local models and creates capability profiles."""

import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import httpx
import yaml

logger = logging.getLogger(__name__)


@dataclass
class TaskCapability:
    max_tokens: int
    timeout: int
    quality: str


@dataclass
class HardwareInfo:
    gpu: str
    vram: str
    ram: str


@dataclass
class PerformanceMetrics:
    generation_speed: float  # tokens/second
    prompt_speed: float  # tokens/second
    vram_usage: str
    ram_usage: str


@dataclass
class CapabilityProfile:
    model: str
    benchmark_date: str
    hardware: HardwareInfo
    performance: PerformanceMetrics
    task_capabilities: Dict[str, TaskCapability]
    routing_rules: Dict[str, object]

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "CapabilityProfile":
        hw = HardwareInfo(**data["hardware"])
        perf = PerformanceMetrics(**data["performance"])
        tasks = {k: TaskCapability(**v) for k, v in data["task_capabilities"].items()}
        return cls(
            model=data["model"],
            benchmark_date=data["benchmark_date"],
            hardware=hw,
            performance=perf,
            task_capabilities=tasks,
            routing_rules=data["routing_rules"],
        )


# Default benchmark prompts per task type
BENCHMARK_PROMPTS = {
    "greeting": "Hello! How are you today?",
    "code_generation": (
        "Write a Python function that finds the longest "
        "common subsequence of two strings."
    ),
    "explanation": "Explain the difference between TCP and UDP.",
    "classification": (
        "Classify as positive, negative, or neutral: "
        "'The product works fine but shipping was slow.'"
    ),
    "summarization": (
        "Summarize the key principles of object-oriented "
        "programming in 3 bullet points."
    ),
}


class ModelEvaluator:
    """Benchmarks Ollama models and creates capability profiles."""

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        config_path: Optional[Path] = None,
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.config_path = config_path or Path(__file__).parent / "config.yaml"

    async def run_benchmark(self, model: str) -> Dict[str, Dict]:
        """Execute benchmark suite against Ollama API."""
        results = {}
        for task_type, prompt in BENCHMARK_PROMPTS.items():
            result = await self._benchmark_single(model, task_type, prompt)
            results[task_type] = result
        return results

    async def _benchmark_single(
        self, model: str, task_type: str, prompt: str
    ) -> Dict:
        """Run a single benchmark and measure performance."""
        start_time = time.monotonic()
        try:
            result = await self._call_ollama(model, prompt)
            elapsed = time.monotonic() - start_time
            tokens = len(result.split())
            return {
                "success": True,
                "elapsed_seconds": round(elapsed, 2),
                "tokens_generated": tokens,
                "tokens_per_second": round(tokens / max(elapsed, 0.01), 2),
                "output_preview": result[:200],
            }
        except Exception as e:
            elapsed = time.monotonic() - start_time
            logger.warning(f"Benchmark failed for {task_type}: {e}")
            return {
                "success": False,
                "elapsed_seconds": round(elapsed, 2),
                "error": str(e),
            }

    async def _call_ollama(self, model: str, prompt: str) -> str:
        """Call Ollama generate endpoint."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 512},
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")

    async def create_profile(
        self,
        model: str,
        hardware: HardwareInfo,
        benchmark_results: Optional[Dict] = None,
    ) -> CapabilityProfile:
        """Create a capability profile from benchmark results."""
        if benchmark_results is None:
            benchmark_results = await self.run_benchmark(model)

        perf = self._compute_performance(benchmark_results)
        tasks = self._compute_task_capabilities(benchmark_results)
        routing = self._default_routing_rules()

        return CapabilityProfile(
            model=model,
            benchmark_date=datetime.now(timezone.utc).isoformat(),
            hardware=hardware,
            performance=perf,
            task_capabilities=tasks,
            routing_rules=routing,
        )

    def _compute_performance(self, results: Dict) -> PerformanceMetrics:
        """Compute aggregate performance metrics from benchmark results."""
        success = [v for v in results.values() if v.get("success")]
        if not success:
            return PerformanceMetrics(
                generation_speed=0.0,
                prompt_speed=0.0,
                vram_usage="unknown",
                ram_usage="unknown",
            )

        avg_tps = sum(r["tokens_per_second"] for r in success) / len(success)
        return PerformanceMetrics(
            generation_speed=round(avg_tps, 1),
            prompt_speed=round(avg_tps * 4, 1),  # prompt processing ~4x gen
            vram_usage="~4GB",
            ram_usage="~4GB",
        )

    def _compute_task_capabilities(self, results: Dict) -> Dict[str, TaskCapability]:
        """Derive per-task capabilities from benchmark results."""
        capabilities = {}
        for task_type, result in results.items():
            if result.get("success"):
                elapsed = result["elapsed_seconds"]
                timeout = max(30, int(elapsed * 2.5))
                quality = "good" if result["tokens_per_second"] > 3 else "acceptable"
            else:
                timeout = 60
                quality = "poor"

            max_tokens = self._default_max_tokens(task_type)
            capabilities[task_type] = TaskCapability(
                max_tokens=max_tokens, timeout=timeout, quality=quality
            )
        return capabilities

    def _default_max_tokens(self, task_type: str) -> int:
        defaults = {
            "greeting": 512,
            "code_generation": 1024,
            "explanation": 512,
            "classification": 256,
            "summarization": 512,
        }
        return defaults.get(task_type, 512)

    def _default_routing_rules(self) -> Dict[str, object]:
        return {
            "max_difficulty": "medium",
            "fallback_model": "cloud",
            "timeout_multiplier": 2.0,
        }


def load_profile(config_path: Optional[Path] = None) -> Optional[CapabilityProfile]:
    """Load capability profile from config.yaml."""
    path = config_path or Path(__file__).parent / "config.yaml"
    if not path.exists():
        return None

    with open(path) as f:
        config = yaml.safe_load(f) or {}

    profile_data = config.get("local_model", {}).get("capability_profile")
    if not profile_data:
        return None

    return CapabilityProfile.from_dict(profile_data)


def save_profile(profile: CapabilityProfile, config_path: Optional[Path] = None) -> None:
    """Save capability profile to config.yaml."""
    path = config_path or Path(__file__).parent / "config.yaml"
    if path.exists():
        with open(path) as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}

    config.setdefault("local_model", {})["capability_profile"] = profile.to_dict()

    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Saved capability profile for {profile.model}")
