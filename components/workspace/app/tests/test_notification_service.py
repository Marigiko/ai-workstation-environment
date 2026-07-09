import pytest
from uuid import uuid4
from app.core.workspace_manager import WorkspaceManager
from app.core.notification_service import NotificationService


@pytest.fixture
async def workspace(db):
    mgr = WorkspaceManager(db)
    return await mgr.create_workspace("Notif WS", "", "owner-1")


@pytest.mark.asyncio
async def test_create_notification(db, workspace):
    svc = NotificationService(db)
    notif = await svc.create_notification(workspace.id, "user-1", "task.completed", "Title", "Message", "info")
    assert notif.title == "Title"
    assert notif.read is False


@pytest.mark.asyncio
async def test_list_notifications(db, workspace):
    svc = NotificationService(db)
    await svc.create_notification(workspace.id, "user-1", "info", "N1", "", "info")
    await svc.create_notification(workspace.id, "user-1", "info", "N2", "", "warning")
    notifs = await svc.list_notifications(workspace.id)
    assert len(notifs) >= 2


@pytest.mark.asyncio
async def test_mark_read(db, workspace):
    svc = NotificationService(db)
    notif = await svc.create_notification(workspace.id, "user-1", "info", "Read", "", "info")
    marked = await svc.mark_read(notif.id)
    assert marked.read is True


@pytest.mark.asyncio
async def test_create_rule(db, workspace):
    svc = NotificationService(db)
    rule = await svc.create_rule(workspace.id, "Task Failures", {"event": "task.failed"}, [{"type": "push"}])
    assert rule.name == "Task Failures"
    assert rule.enabled is True
