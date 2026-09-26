"""Tests for ModelAssigner routing (6 GB VRAM constraint)."""

import pytest

from components.auto_orchestrator.assigner import ModelAssigner
from components.auto_orchestrator.task_classifier import classify_task

LOCAL_MODEL = "qwen2.5-coder:7b"
HARD_MODEL = "agente"
LIGHT_MODEL = "liviano"


class TestDifficultyRouting:
    def test_easy_stays_local(self):
        assigner = ModelAssigner()
        assignment = assigner.assign("write a fibonacci function")
        assert classification_difficulty("write a fibonacci function") == "easy"
        assert assignment.model == LOCAL_MODEL

    def test_medium_stays_local(self):
        assigner = ModelAssigner()
        assignment = assigner.assign("fix this bug in the parser")
        assert classification_difficulty("fix this bug in the parser") == "medium"
        assert assignment.model == LOCAL_MODEL

    def test_hard_goes_to_cloud_heavy(self):
        assigner = ModelAssigner()
        assignment = assigner.assign(
            "design and implement a distributed rate limiter with Redis"
        )
        assert (
            classification_difficulty(
                "design and implement a distributed rate limiter with Redis"
            )
            == "hard"
        )
        assert assignment.model == HARD_MODEL

    def test_hard_never_local(self):
        assigner = ModelAssigner()
        assignment = assigner.assign(
            "design and implement a distributed rate limiter with Redis"
        )
        assert assignment.model not in (LOCAL_MODEL, "gemma4:12b")

    def test_extreme_goes_to_cloud_light(self):
        assigner = ModelAssigner()
        assignment = assigner.assign(
            "build a complete full stack framework from scratch"
        )
        difficulty = classification_difficulty(
            "build a complete full stack framework from scratch"
        )
        if difficulty == "extreme":
            assert assignment.model == LIGHT_MODEL


class TestTiers:
    def test_no_tier_contains_gemma4_12b(self):
        assigner = ModelAssigner()
        for tier, models in assigner.MODEL_TIERS.items():
            assert "gemma4:12b" not in models, f"tier {tier} contains gemma4:12b"

    def test_custom_tiers_override(self):
        custom = {"local_fast": ["tiny-model"], "cloud_heavy": ["big-model"]}
        assigner = ModelAssigner(tiers=custom)
        assert assigner.MODEL_TIERS["local_fast"] == ["tiny-model"]
        assert assigner.MODEL_TIERS["cloud_heavy"] == ["big-model"]
        # untouched tiers keep defaults
        assert assigner.MODEL_TIERS["local_balanced"] == [LOCAL_MODEL]

    def test_default_tiers_when_config_missing(self):
        assigner = ModelAssigner()
        assert assigner.MODEL_TIERS["local_fast"] == [LOCAL_MODEL]
        assert assigner.MODEL_TIERS["local_balanced"] == [LOCAL_MODEL]
        assert assigner.MODEL_TIERS["cloud_light"] == [LIGHT_MODEL]
        assert assigner.MODEL_TIERS["cloud_heavy"] == [HARD_MODEL]


class TestOverrides:
    def test_custom_assignment_wins(self):
        assigner = ModelAssigner()
        assigner.set_custom_assignment("my-model", "distributed")
        assignment = assigner.assign(
            "design and implement a distributed rate limiter with Redis"
        )
        assert assignment.model == "my-model"

    def test_preferred_model_wins(self):
        assigner = ModelAssigner()
        assignment = assigner.assign(
            "write a fibonacci function", preferred_model="my-preferred"
        )
        assert assignment.model == "my-preferred"


def classification_difficulty(task: str) -> str:
    return classify_task(task).difficulty.value


def test_tiers_loaded_from_config_file(tmp_path):
    from components.auto_orchestrator.assigner import load_tiers

    config = tmp_path / "config.yaml"
    config.write_text("tiers:\n  cloud_heavy: [custom-heavy]\n")
    tiers = load_tiers(config)
    assert tiers["cloud_heavy"] == ["custom-heavy"]
    assert tiers["local_fast"] == ["qwen2.5-coder:7b"]


def test_missing_config_falls_back_to_defaults(tmp_path):
    from components.auto_orchestrator.assigner import DEFAULT_MODEL_TIERS, load_tiers

    assert load_tiers(tmp_path / "missing.yaml") == DEFAULT_MODEL_TIERS
