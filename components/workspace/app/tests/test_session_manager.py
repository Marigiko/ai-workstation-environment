import pytest
from uuid import uuid4
from app.core.workspace_manager import WorkspaceManager
from app.core.session_manager import SessionManager


@pytest.fixture
async def workspace(db):
    mgr = WorkspaceManager(db)
    return await mgr.create_workspace("Test WS", "", "owner-1")


@pytest.mark.asyncio
async def test_create_session(db, workspace):
    mgr = SessionManager(db)
    session = await mgr.create_session(workspace.id, "Test Session")
    assert session.title == "Test Session"
    assert session.status == "created"


@pytest.mark.asyncio
async def test_add_message(db, workspace):
    mgr = SessionManager(db)
    session = await mgr.create_session(workspace.id, "Msg Session")
    msg = await mgr.add_message(session.id, "user", "Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.sequence == 1


@pytest.mark.asyncio
async def test_pause_resume_session(db, workspace):
    mgr = SessionManager(db)
    session = await mgr.create_session(workspace.id, "Pause Session")
    await mgr.add_message(session.id, "user", "Start")
    paused = await mgr.pause_session(session.id)
    assert paused.status == "paused"
    resumed = await mgr.resume_session(session.id)
    assert resumed.status == "active"


@pytest.mark.asyncio
async def test_archive_session(db, workspace):
    mgr = SessionManager(db)
    session = await mgr.create_session(workspace.id, "Archive Session")
    archived = await mgr.archive_session(session.id)
    assert archived.status == "archived"


@pytest.mark.asyncio
async def test_list_sessions(db, workspace):
    mgr = SessionManager(db)
    await mgr.create_session(workspace.id, "S1")
    await mgr.create_session(workspace.id, "S2")
    sessions = await mgr.list_sessions(workspace.id)
    assert len(sessions) >= 2
