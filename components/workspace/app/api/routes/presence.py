from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.presence_service import PresenceService

router = APIRouter()


@router.post("/heartbeat")
async def heartbeat(device_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PresenceService(db)
    await svc.heartbeat(device_id)
    return {"status": "ok"}


@router.get("/devices")
async def list_devices(workspace_id: UUID = Query(...), db: AsyncSession = Depends(get_db)):
    svc = PresenceService(db)
    return await svc.get_devices(workspace_id)


@router.get("/users")
async def list_users(workspace_id: UUID = Query(...), db: AsyncSession = Depends(get_db)):
    svc = PresenceService(db)
    return await svc.get_users(workspace_id)


@router.get("/activity")
async def get_activity(workspace_id: UUID = Query(...), db: AsyncSession = Depends(get_db)):
    svc = PresenceService(db)
    return await svc.get_activity(workspace_id)
