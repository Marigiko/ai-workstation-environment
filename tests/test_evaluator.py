"""Tests for auto_orchestrator.evaluator module."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from components.auto_orchestrator.evaluator import (
    CapabilityProfile,
    HardwareInfo,
    PerformanceMetrics,
    TaskCapability,
    ModelEvaluator,
    load_profile,
    save_profile,
)


@pytest.fixture
def sample_profile():
    return CapabilityProfile(
        model="gemma4:12b",
        benchmark_date="2026-08-28T12:00:00+00:00",
        hardware=HardwareInfo(gpu="RTX 2060", vram="6GB", ram="35GB"),
        performance=PerformanceMetrics(
            generation_speed=5.0,
            prompt_speed=20.0,
            vram_usage="~4GB",
            ram_usage="~4GB",
        ),
        task_capabilities={
            "greeting": TaskCapability(max_tokens=512, timeout=30, quality="good"),
            "code_generation": TaskCapability(max_tokens=1024, timeout=120, quality="acceptable"),
        },
        routing_rules={
            "max_difficulty": "medium",
            "fallback_model": "cloud",
            "timeout_multiplier": 2.0,
        },
    )


@pytest.fixture
def config_file(tmp_path):
    return tmp_path / "config.yaml"


class TestCapabilityProfile:
    def test_to_dict_roundtrip(self, sample_profile):
        data = sample_profile.to_dict()
        restored = CapabilityProfile.from_dict(data)
        assert restored.model == sample_profile.model
        assert restored.hardware.gpu == sample_profile.hardware.gpu
        assert restored.performance.generation_speed == sample_profile.performance.generation_speed
        assert len(restored.task_capabilities) == len(sample_profile.task_capabilities)

    def test_from_dict_minimal(self):
        data = {
            "model": "test",
            "benchmark_date": "2026-01-01T00:00:00+00:00",
            "hardware": {"gpu": "none", "vram": "0GB", "ram": "8GB"},
            "performance": {"generation_speed": 0, "prompt_speed": 0, "vram_usage": "0", "ram_usage": "0"},
            "task_capabilities": {},
            "routing_rules": {},
        }
        profile = CapabilityProfile.from_dict(data)
        assert profile.model == "test"
        assert profile.task_capabilities == {}


class TestModelEvaluator:
    @pytest.mark.asyncio
    async def test_run_benchmark_calls_ollama(self, tmp_path):
        evaluator = ModelEvaluator(ollama_url="http://fake:11434")
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Hello world"}
        mock_response.raise_for_status = MagicMock()

        with patch("components.auto_orchestrator.evaluator.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=MagicMock(post=AsyncMock(return_value=mock_response))
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            results = await evaluator.run_benchmark("test-model")

        assert "greeting" in results
        assert results["greeting"]["success"] is True
        assert results["greeting"]["tokens_generated"] == 2

    @pytest.mark.asyncio
    async def test_run_benchmark_handles_failure(self):
        evaluator = ModelEvaluator(ollama_url="http://fake:11434")

        with patch("components.auto_orchestrator.evaluator.httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.post = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            results = await evaluator.run_benchmark("test-model")

        assert results["greeting"]["success"] is False
        assert "error" in results["greeting"]

    def test_compute_performance_empty(self):
        evaluator = ModelEvaluator()
        perf = evaluator._compute_performance({})
        assert perf.generation_speed == 0.0

    def test_compute_performance_with_results(self):
        evaluator = ModelEvaluator()
        results = {
            "greeting": {"success": True, "tokens_per_second": 5.0, "elapsed_seconds": 1.0},
            "code_generation": {"success": True, "tokens_per_second": 3.0, "elapsed_seconds": 2.0},
        }
        perf = evaluator._compute_performance(results)
        assert perf.generation_speed == 4.0  # avg of 5.0 and 3.0

    def test_compute_task_capabilities_success(self):
        evaluator = ModelEvaluator()
        results = {
            "greeting": {"success": True, "tokens_per_second": 5.0, "elapsed_seconds": 1.0},
            "code_generation": {"success": False},
        }
        caps = evaluator._compute_task_capabilities(results)
        assert caps["greeting"].quality == "good"
        assert caps["code_generation"].quality == "poor"

    def test_default_max_tokens(self):
        evaluator = ModelEvaluator()
        assert evaluator._default_max_tokens("greeting") == 512
        assert evaluator._default_max_tokens("code_generation") == 1024
        assert evaluator._default_max_tokens("unknown") == 512


class TestProfilePersistence:
    def test_save_and_load_profile(self, sample_profile, config_file):
        save_profile(sample_profile, config_file)
        loaded = load_profile(config_file)
        assert loaded is not None
        assert loaded.model == "gemma4:12b"
        assert loaded.hardware.gpu == "RTX 2060"

    def test_load_profile_missing_file(self, tmp_path):
        result = load_profile(tmp_path / "nonexistent.yaml")
        assert result is None

    def test_load_profile_no_profile_section(self, config_file):
        config_file.write_text("local_model:\n  enabled: true\n")
        result = load_profile(config_file)
        assert result is None

    def test_save_profile_creates_section(self, sample_profile, config_file):
        config_file.write_text("existing_key: value\n")
        save_profile(sample_profile, config_file)
        with open(config_file) as f:
            config = yaml.safe_load(f)
        assert "local_model" in config
        assert config["local_model"]["capability_profile"]["model"] == "gemma4:12b"
        assert config["existing_key"] == "value"
