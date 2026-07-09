from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.models.device import Device


class PostgresRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workspace(self, name: str, description: str, owner_id: str, metadata: dict = None) -> Workspace:
        ws = Workspace(name=name, description=description, owner_id=owner_id, meta_data=metadata or {})
        self.db.add(ws)
        await self.db.commit()
        await self.db.refresh(ws)
        return ws

    async def get_workspace(self, id: UUID) -> Optional[Workspace]:
        result = await self.db.execute(select(Workspace).where(Workspace.id == id))
        return result.scalar_one_or_none()

    async def list_workspaces(self) -> list[Workspace]:
        result = await self.db.execute(select(Workspace))
        return list(result.scalars().all())

    async def update_workspace(self, id: UUID, **kwargs) -> Optional[Workspace]:
        ws = await self.get_workspace(id)
        if ws:
            for key, value in kwargs.items():
                if hasattr(ws, key):
                    setattr(ws, key, value)
            ws.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(ws)
        return ws

    async def delete_workspace(self, id: UUID) -> bool:
        result = await self.db.execute(delete(Workspace).where(Workspace.id == id))
        await self.db.commit()
        return result.rowcount > 0

    async def create_device(self, workspace_id: UUID, name: str, type: str, os: str = "", capabilities: dict = None) -> Device:
        device = Device(workspace_id=workspace_id, name=name, type=type, os=os, capabilities=capabilities or {})
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def get_device(self, id: UUID) -> Optional[Device]:
        result = await self.db.execute(select(Device).where(Device.id == id))
        return result.scalar_one_or_none()

    async def list_devices(self, workspace_id: UUID) -> list[Device]:
        result = await self.db.execute(select(Device).where(Device.workspace_id == workspace_id))
        return list(result.scalars().all())

    async def delete_device(self, id: UUID) -> bool:
        result = await self.db.execute(delete(Device).where(Device.id == id))
        await self.db.commit()
        return result.rowcount > 0
