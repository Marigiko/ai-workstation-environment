#!/usr/bin/env python3
"""Task Classifier - Rule-based difficulty estimation and task categorization."""

import re
from dataclasses import dataclass
from enum import Enum


def _word_match(text: str, keyword: str) -> bool:
    """Check if keyword appears as a whole word/phrase in text."""
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"


@dataclass
class TaskClassification:
    task_type: str
    difficulty: DifficultyLevel
    estimated_tokens: int
    estimated_duration_seconds: int
    reasoning: str


# Keywords mapped to task types (ordered by priority - first match wins)
TASK_TYPE_KEYWORDS = {
    "greeting": ["hello", "hi", "hey", "greetings", "good morning"],
    "refactoring": [
        "refactor", "restructure", "reorganize", "clean up",
        "optimize", "simplify", "improve", "rename", "extract",
    ],
    "debugging": [
        "debug", "fix the", "fix this", "error", "bug", "issue",
        "not working", "broken", "fails", "crash",
    ],
    "code_generation": [
        "write", "create", "implement", "build", "function", "script",
        "code", "program", "module", "api", "endpoint", "handler",
    ],
    "explanation": [
        "explain", "describe", "what is", "how does", "why does",
        "tell me about", "define", "clarify",
    ],
    "classification": [
        "classify", "categorize", "label", "sentiment",
        "positive or negative",
    ],
    "summarization": [
        "summarize", "summary", "tldr", "brief", "key points",
        "main ideas", "condense",
    ],
}

# Complexity indicators per task type
COMPLEXITY_SIGNALS = {
    "code_generation": {
        "easy": ["function", "script", "simple", "basic", "small"],
        "medium": ["class", "module", "api", "endpoint", "integration"],
        "hard": ["system", "architecture", "multi-file", "microservice", "distributed"],
        "extreme": ["full stack", "complete system", "framework", "compiler"],
    },
    "debugging": {
        "easy": ["typo", "syntax", "missing import"],
        "medium": ["logic", "memory", "null pointer"],
        "hard": ["race condition", "concurrency", "concurrent", "distributed", "performance"],
        "extreme": ["production outage", "data corruption"],
    },
    "refactoring": {
        "easy": ["rename", "extract", "format"],
        "medium": ["pattern", "structure", "decouple"],
        "hard": ["architecture", "rewrite", "migration"],
        "extreme": ["complete rewrite", "paradigm shift"],
    },
}


@dataclass
class TokenEstimate:
    min_tokens: int
    max_tokens: int
    avg_tokens: int


TOKEN_ESTIMATES = {
    "greeting": TokenEstimate(50, 100, 75),
    "code_generation": TokenEstimate(200, 1000, 600),
    "explanation": TokenEstimate(100, 500, 300),
    "classification": TokenEstimate(50, 200, 125),
    "summarization": TokenEstimate(100, 400, 250),
    "debugging": TokenEstimate(200, 800, 500),
    "refactoring": TokenEstimate(300, 1200, 750),
}


class TaskClassifier:
    """Estimates task difficulty and categorizes tasks."""

    def __init__(self, text: str):
        self.text = text
        self.text_lower = text.lower()

    def classify(self) -> TaskClassification:
        """Classify task and return full classification."""
        task_type = self.get_task_type()
        difficulty = self._estimate_difficulty(task_type)
        tokens = self._estimate_tokens(task_type)
        duration = self._estimate_duration(task_type, difficulty)
        reasoning = self._build_reasoning(task_type, difficulty)

        return TaskClassification(
            task_type=task_type,
            difficulty=difficulty,
            estimated_tokens=tokens,
            estimated_duration_seconds=duration,
            reasoning=reasoning,
        )

    def get_task_type(self) -> str:
        """Categorize task by type based on keyword matching."""
        scores = {}
        for task_type, keywords in TASK_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if _word_match(self.text, kw))
            if score > 0:
                scores[task_type] = score

        if not scores:
            return "explanation"  # default fallback

        return max(scores, key=scores.get)

    def _estimate_difficulty(self, task_type: str) -> DifficultyLevel:
        """Estimate difficulty based on task type and complexity signals."""
        signals = COMPLEXITY_SIGNALS.get(task_type, {})
        if not signals:
            return self._generic_difficulty()

        for level in ["extreme", "hard", "medium", "easy"]:
            keywords = signals.get(level, [])
            if any(_word_match(self.text, kw) for kw in keywords):
                return DifficultyLevel(level)

        return DifficultyLevel.MEDIUM

    def _generic_difficulty(self) -> DifficultyLevel:
        """Fallback difficulty estimation based on text length and complexity."""
        word_count = len(self.text.split())
        has_code = "```" in self.text or "def " in self.text or "class " in self.text

        if word_count > 100 or has_code:
            return DifficultyLevel.HARD
        if word_count > 30:
            return DifficultyLevel.MEDIUM
        return DifficultyLevel.EASY

    def _estimate_tokens(self, task_type: str) -> int:
        """Estimate token count based on task type."""
        estimate = TOKEN_ESTIMATES.get(task_type, TokenEstimate(100, 500, 300))
        word_count = len(self.text.split())
        if word_count > 50:
            return estimate.max_tokens
        if word_count < 10:
            return estimate.min_tokens
        return estimate.avg_tokens

    def _estimate_duration(self, task_type: str, difficulty: DifficultyLevel) -> int:
        """Estimate execution duration in seconds."""
        base = TOKEN_ESTIMATES.get(task_type, TokenEstimate(100, 500, 300))
        multiplier = {
            DifficultyLevel.EASY: 0.5,
            DifficultyLevel.MEDIUM: 1.0,
            DifficultyLevel.HARD: 2.0,
            DifficultyLevel.EXTREME: 4.0,
        }
        return max(10, int(base.avg_tokens / 5 * multiplier[difficulty]))

    def _build_reasoning(self, task_type: str, difficulty: DifficultyLevel) -> str:
        """Build human-readable reasoning for classification."""
        return f"Task type: {task_type}, difficulty: {difficulty.value}"


def classify_task(text: str) -> TaskClassification:
    """Classify a task and return difficulty + estimated tokens."""
    classifier = TaskClassifier(text)
    return classifier.classify()


def get_task_type(text: str) -> str:
    """Categorize task type (greeting, code, explanation, etc.)."""
    classifier = TaskClassifier(text)
    return classifier.get_task_type()
