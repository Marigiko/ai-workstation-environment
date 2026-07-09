#!/usr/bin/env python3
"""Integration tests for the AI Engineering platform."""

import pytest


class TestTelegramBot:
    """Test Telegram bot commands."""

    def test_bot_initialization(self):
        from components.telegram_bot.bot import TelegramBot
        bot = TelegramBot()
        assert bot.config is not None

    def test_config_loading(self):
        from components.telegram_bot.bot import TelegramBot
        bot = TelegramBot()
        assert "bot" in bot.config
        assert "n8n" in bot.config
        assert "proxy" in bot.config


class TestAutoOrchestrator:
    """Test auto orchestrator functionality."""

    def test_orchestrator_initialization(self):
        from components.auto_orchestrator.orchestrator import AutoOrchestrator
        orch = AutoOrchestrator()
        assert orch.plans == {}

    def test_model_selection(self):
        from components.auto_orchestrator.orchestrator import AgentType, AutoOrchestrator
        orch = AutoOrchestrator()
        model = orch.get_model_for_agent(AgentType.CODER)
        assert model == "mimo-auto"

    @pytest.mark.asyncio
    async def test_plan_creation(self):
        from components.auto_orchestrator.orchestrator import AutoOrchestrator
        orch = AutoOrchestrator()
        plan = await orch.plan_task("test-1", "Create a hello world app")
        assert plan.task_id == "test-1"
        assert len(plan.subtasks) > 0


class TestTaskDecomposer:
    """Test task decomposition."""

    def test_decomposer_initialization(self):
        from components.auto_orchestrator.decomposer import TaskDecomposer
        dec = TaskDecomposer()
        assert dec.gateway is None

    def test_default_decomposition(self):
        from components.auto_orchestrator.decomposer import TaskDecomposer
        dec = TaskDecomposer()
        subtasks = dec._default_decomposition("Test task")
        assert len(subtasks) == 4
        assert subtasks[0].agent_type == "architect"


class TestResultAggregator:
    """Test result aggregation."""

    def test_aggregator_initialization(self):
        from components.auto_orchestrator.aggregator import ResultAggregator
        agg = ResultAggregator()
        assert agg is not None

    @pytest.mark.asyncio
    async def test_aggregation(self):
        from components.auto_orchestrator.aggregator import ResultAggregator
        agg = ResultAggregator()
        results = {
            "architect": "Plan created",
            "coder": "Code implemented",
            "reviewer": {"error": "Review failed"},
        }
        result = await agg.aggregate(results)
        assert result.success is False
        assert len(result.errors) == 1


class TestModelAssigner:
    """Test model assignment."""

    def test_assigner_initialization(self):
        from components.auto_orchestrator.assigner import ModelAssigner
        assigner = ModelAssigner()
        assert assigner.custom_assignments == {}

    def test_model_assignment(self):
        from components.auto_orchestrator.assigner import ModelAssigner
        assigner = ModelAssigner()
        assignment = assigner.assign("coder", "medium")
        assert assignment.model == "qwen2.5-coder:7b"

    def test_custom_assignment(self):
        from components.auto_orchestrator.assigner import ModelAssigner
        assigner = ModelAssigner()
        assigner.set_custom_assignment("coder", "phi3:mini")
        assignment = assigner.assign("coder")
        assert assignment.model == "phi3:mini"


class TestHeadroomWrapper:
    """Test headroom context compression."""

    def test_wrapper_initialization(self):
        from components.auto_orchestrator.headroom_wrapper import HeadroomWrapper
        wrapper = HeadroomWrapper()
        assert wrapper.config.enabled is True

    @pytest.mark.asyncio
    async def test_wrap_messages(self):
        from components.auto_orchestrator.headroom_wrapper import HeadroomWrapper
        wrapper = HeadroomWrapper()
        messages = [{"role": "user", "content": "Hello"}]
        result = await wrapper.wrap_messages(messages)
        assert len(result) == 1


class TestWorktreeManager:
    """Test worktree management."""

    def test_manager_initialization(self):
        from components.workspace.app.core.worktree_manager import WorktreeManager
        manager = WorktreeManager()
        assert isinstance(manager.worktrees, dict)

    def test_create_worktree(self):
        from components.workspace.app.core.worktree_manager import WorktreeManager
        manager = WorktreeManager()
        wt = manager.create_worktree("test-project", "/tmp/test")
        assert wt.name == "test-project"
        assert wt.id in manager.worktrees

    def test_list_worktrees(self):
        from components.workspace.app.core.worktree_manager import WorktreeManager
        manager = WorktreeManager()
        initial_count = len(manager.list_worktrees())
        manager.create_worktree("project1", "/tmp/p1")
        manager.create_worktree("project2", "/tmp/p2")
        assert len(manager.list_worktrees()) == initial_count + 2


class TestHermesSync:
    """Test Hermes synchronization."""

    def test_sync_initialization(self):
        from components.workspace.app.core.hermes_sync import HermesSync
        sync = HermesSync()
        assert sync.states == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
