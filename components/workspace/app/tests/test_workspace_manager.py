import pytest
from uuid import uuid4
from app.core.workspace_manager import WorkspaceManager


@pytest.mark.asyncio
async def test_create_workspace(db):
    mgr = WorkspaceManager(db)
    ws = await mgr.create_workspace("Test WS", "Description", "owner-1")
    assert ws.name == "Test WS"
    assert ws.owner_id == "owner-1"


@pytest.mark.asyncio
async def test_get_workspace(db):
    mgr = WorkspaceManager(db)
    ws = await mgr.create_workspace("Get WS", "Desc", "owner-1")
    found = await mgr.get_workspace(ws.id)
    assert found is not None
    assert found.name == "Get WS"


@pytest.mark.asyncio
async def test_list_workspaces(db):
    mgr = WorkspaceManager(db)
    await mgr.create_workspace("WS 1", "", "owner-1")
    await mgr.create_workspace("WS 2", "", "owner-1")
    wss = await mgr.list_workspaces()
    assert len(wss) >= 2


@pytest.mark.asyncio
async def test_update_workspace(db):
    mgr = WorkspaceManager(db)
    ws = await mgr.create_workspace("Update WS", "", "owner-1")
    updated = await mgr.update_workspace(ws.id, name="Updated")
    assert updated.name == "Updated"


@pytest.mark.asyncio
async def test_delete_workspace(db):
    mgr = WorkspaceManager(db)
    ws = await mgr.create_workspace("Delete WS", "", "owner-1")
    deleted = await mgr.delete_workspace(ws.id)
    assert deleted is True
    found = await mgr.get_workspace(ws.id)
    assert found is None


@pytest.mark.asyncio
async def test_register_device(db):
    mgr = WorkspaceManager(db)
    ws = await mgr.create_workspace("Device WS", "", "owner-1")
    device = await mgr.register_device(ws.id, "My Notebook", "notebook", "linux")
    assert device.name == "My Notebook"
    assert device.type == "notebook"


@pytest.mark.asyncio
async def test_list_devices(db):
    mgr = WorkspaceManager(db)
    ws = await mgr.create_workspace("List Devices WS", "", "owner-1")
    await mgr.register_device(ws.id, "D1", "notebook", "linux")
    await mgr.register_device(ws.id, "D2", "desktop", "linux")
    devices = await mgr.list_devices(ws.id)
    assert len(devices) >= 2
