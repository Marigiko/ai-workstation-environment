import pytest
from uuid import uuid4
from app.core.workspace_manager import WorkspaceManager
from app.core.presence_service import PresenceService


@pytest.fixture
async def workspace(db):
    mgr = WorkspaceManager(db)
    return await mgr.create_workspace("Presence WS", "", "owner-1")


@pytest.fixture
async def device(db, workspace):
    mgr = WorkspaceManager(db)
    return await mgr.register_device(workspace.id, "Test Device", "notebook", "linux")


@pytest.mark.asyncio
async def test_heartbeat(db, device):
    svc = PresenceService(db)
    await svc.heartbeat(device.id)


@pytest.mark.asyncio
async def test_list_devices(db, workspace):
    svc = PresenceService(db)
    devices = await svc.get_devices(workspace.id)
    assert isinstance(devices, list)
