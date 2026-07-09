import pytest
from uuid import uuid4
from app.core.workspace_manager import WorkspaceManager
from app.core.session_manager import SessionManager
from app.core.task_manager import TaskManager


@pytest.mark.asyncio
async def test_full_workflow(db):
    ws_mgr = WorkspaceManager(db)
    ws = await ws_mgr.create_workspace("Integration WS", "Full workflow test", "owner-1")

    device = await ws_mgr.register_device(ws.id, "Notebook", "notebook", "linux")
    assert device.status == "offline"

    sess_mgr = SessionManager(db)
    session = await sess_mgr.create_session(ws.id, "Integration Session")
    assert session.status == "created"

    msg1 = await sess_mgr.add_message(session.id, "user", "Hello workspace")
    msg2 = await sess_mgr.add_message(session.id, "assistant", "Hello! How can I help?")
    assert msg1.sequence == 1
    assert msg2.sequence == 2

    task_mgr = TaskManager(db)
    task = await task_mgr.create_task(ws.id, "Run analysis", "Analyze the codebase", priority=5)
    started = await task_mgr.start_task(task.id, "agent-1")
    assert started.status == "running"

    progress = await task_mgr.update_progress(task.id, 0.5)
    assert progress.progress == 0.5

    completed = await task_mgr.complete_task(task.id, {"report": "All clear"}, 5000, 0.05, 300)
    assert completed.status == "completed"
    assert completed.duration_ms == 5000

    sessions = await sess_mgr.list_sessions(ws.id)
    assert len(sessions) >= 1

    tasks = await task_mgr.list_tasks(ws.id)
    assert len(tasks) >= 1

    deleted = await ws_mgr.delete_workspace(ws.id)
    assert deleted is True
