import pytest
from uuid import uuid4
from app.core.workspace_manager import WorkspaceManager
from app.core.task_manager import TaskManager


@pytest.fixture
async def workspace(db):
    mgr = WorkspaceManager(db)
    return await mgr.create_workspace("Task WS", "", "owner-1")


@pytest.mark.asyncio
async def test_create_task(db, workspace):
    mgr = TaskManager(db)
    task = await mgr.create_task(workspace.id, "Test Task", "Description")
    assert task.title == "Test Task"
    assert task.status == "pending"


@pytest.mark.asyncio
async def test_start_task(db, workspace):
    mgr = TaskManager(db)
    task = await mgr.create_task(workspace.id, "Start Task")
    started = await mgr.start_task(task.id, "agent-1")
    assert started.status == "running"
    assert started.agent_id == "agent-1"


@pytest.mark.asyncio
async def test_complete_task(db, workspace):
    mgr = TaskManager(db)
    task = await mgr.create_task(workspace.id, "Complete Task")
    await mgr.start_task(task.id, "agent-1")
    completed = await mgr.complete_task(task.id, {"result": "done"}, 1000, 0.01, 150)
    assert completed.status == "completed"
    assert completed.duration_ms == 1000


@pytest.mark.asyncio
async def test_pause_resume_task(db, workspace):
    mgr = TaskManager(db)
    task = await mgr.create_task(workspace.id, "Pause Task")
    await mgr.start_task(task.id, "agent-1")
    paused = await mgr.pause_task(task.id)
    assert paused.status == "paused"
    resumed = await mgr.resume_task(task.id)
    assert resumed.status == "running"


@pytest.mark.asyncio
async def test_cancel_task(db, workspace):
    mgr = TaskManager(db)
    task = await mgr.create_task(workspace.id, "Cancel Task")
    await mgr.start_task(task.id, "agent-1")
    cancelled = await mgr.cancel_task(task.id)
    assert cancelled.status == "cancelled"


@pytest.mark.asyncio
async def test_fail_task(db, workspace):
    mgr = TaskManager(db)
    task = await mgr.create_task(workspace.id, "Fail Task")
    await mgr.start_task(task.id, "agent-1")
    failed = await mgr.fail_task(task.id, {"error": "timeout"})
    assert failed.status == "failed"
    assert failed.error == {"error": "timeout"}
