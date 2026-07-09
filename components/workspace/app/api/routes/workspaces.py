from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from app.schemas.device import DeviceCreate, DeviceResponse
from app.core.workspace_manager import WorkspaceManager

router = APIRouter()


@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(data: WorkspaceCreate, db: AsyncSession = Depends(get_db)):
    mgr = WorkspaceManager(db)
    ws = await mgr.create_workspace(data.name, data.description, data.owner_id, data.metadata)
    return WorkspaceResponse.from_orm_model(ws)


@router.get("/", response_model=list[WorkspaceResponse])
async def list_workspaces(db: AsyncSession = Depends(get_db)):
    mgr = WorkspaceManager(db)
    wss = await mgr.list_workspaces()
    return [WorkspaceResponse.from_orm_model(w) for w in wss]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = WorkspaceManager(db)
    ws = await mgr.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return WorkspaceResponse.from_orm_model(ws)


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(workspace_id: UUID, data: WorkspaceUpdate, db: AsyncSession = Depends(get_db)):
    mgr = WorkspaceManager(db)
    updates = data.model_dump(exclude_unset=True)
    if "metadata" in updates:
        updates["meta_data"] = updates.pop("metadata")
    ws = await mgr.update_workspace(workspace_id, **updates)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return WorkspaceResponse.from_orm_model(ws)


@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = WorkspaceManager(db)
    deleted = await mgr.delete_workspace(workspace_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"status": "deleted"}


@router.post("/{workspace_id}/devices", response_model=DeviceResponse)
async def register_device(workspace_id: UUID, data: DeviceCreate, db: AsyncSession = Depends(get_db)):
    mgr = WorkspaceManager(db)
    device = await mgr.register_device(workspace_id, data.name, data.type, data.os, data.capabilities)
    return device


@router.get("/{workspace_id}/devices", response_model=list[DeviceResponse])
async def list_devices(workspace_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = WorkspaceManager(db)
    return await mgr.list_devices(workspace_id)


@router.delete("/{workspace_id}/devices/{device_id}")
async def remove_device(workspace_id: UUID, device_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = WorkspaceManager(db)
    removed = await mgr.remove_device(workspace_id, device_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"status": "removed"}
