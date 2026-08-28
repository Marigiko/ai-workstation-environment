"""Tests for auto_orchestrator.task_classifier module."""

import pytest

from components.auto_orchestrator.task_classifier import (
    DifficultyLevel,
    TaskClassification,
    TaskClassifier,
    classify_task,
    get_task_type,
)


class TestGetTaskType:
    def test_greeting(self):
        assert get_task_type("Hello, how are you?") == "greeting"

    def test_code_generation(self):
        assert get_task_type("Write a Python function to sort a list") == "code_generation"

    def test_explanation(self):
        assert get_task_type("Explain how TCP works") == "explanation"

    def test_classification(self):
        assert get_task_type("Classify this as positive or negative") == "classification"

    def test_summarization(self):
        assert get_task_type("Summarize the key points") == "summarization"

    def test_debugging(self):
        assert get_task_type("Debug this error in my code") == "debugging"

    def test_refactoring(self):
        assert get_task_type("Refactor this class to be cleaner") == "refactoring"

    def test_default_fallback(self):
        assert get_task_type("Tell me something random") == "explanation"


class TestClassifyTask:
    def test_greeting_easy(self):
        result = classify_task("Hello!")
        assert result.task_type == "greeting"
        assert result.difficulty == DifficultyLevel.EASY
        assert result.estimated_tokens <= 100

    def test_simple_code(self):
        result = classify_task("Write a simple function to add two numbers")
        assert result.task_type == "code_generation"
        assert result.difficulty in (DifficultyLevel.EASY, DifficultyLevel.MEDIUM)

    def test_complex_code(self):
        result = classify_task(
            "Implement a distributed microservice architecture with multi-file system design"
        )
        assert result.task_type == "code_generation"
        assert result.difficulty == DifficultyLevel.HARD

    def test_extreme_code(self):
        result = classify_task(
            "Build a complete framework for a full stack compiler system"
        )
        assert result.difficulty == DifficultyLevel.EXTREME

    def test_debugging_hard(self):
        result = classify_task("Debug this race condition in my concurrent code")
        assert result.task_type == "debugging"
        assert result.difficulty == DifficultyLevel.HARD

    def test_refactoring_easy(self):
        result = classify_task("Rename this variable to be more descriptive")
        assert result.task_type == "refactoring"
        assert result.difficulty == DifficultyLevel.EASY

    def test_explanation_medium(self):
        result = classify_task("Explain how DNS resolution works in detail")
        assert result.task_type == "explanation"
        assert result.difficulty in (DifficultyLevel.EASY, DifficultyLevel.MEDIUM)


class TestTokenEstimation:
    def test_greeting_tokens(self):
        result = classify_task("Hi")
        assert result.estimated_tokens >= 50
        assert result.estimated_tokens <= 200

    def test_code_tokens(self):
        result = classify_task("Write a function")
        assert result.estimated_tokens >= 100
        assert result.estimated_tokens <= 1500

    def test_long_text_more_tokens(self):
        short = classify_task("Hi")
        long = classify_task(" ".join(["word"] * 60))
        assert long.estimated_tokens >= short.estimated_tokens


class TestDurationEstimation:
    def test_easy_short_duration(self):
        result = classify_task("Hello!")
        assert result.estimated_duration_seconds <= 30

    def test_hard_longer_duration(self):
        result = classify_task(
            "Implement a distributed system with microservice architecture"
        )
        assert result.estimated_duration_seconds >= 10


class TestTaskClassifier:
    def test_classify_returns_all_fields(self):
        result = classify_task("Write a script")
        assert isinstance(result, TaskClassification)
        assert result.task_type
        assert isinstance(result.difficulty, DifficultyLevel)
        assert result.estimated_tokens > 0
        assert result.estimated_duration_seconds > 0
        assert result.reasoning

    def test_classifier_direct_init(self):
        classifier = TaskClassifier("Build a complete compiler framework")
        result = classifier.classify()
        assert result.difficulty == DifficultyLevel.EXTREME
