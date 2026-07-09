from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.models.device import Device


class WorkspaceManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_workspace(
        self,
        name: str,
        description: str,
        owner_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> Workspace:
        workspace = Workspace(
            id=uuid.uuid4(),
            name=name,
            description=description,
            owner_id=owner_id,
            meta_data=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(workspace)
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def get_workspace(self, id: uuid.UUID) -> Workspace | None:
        result = await self.session.execute(select(Workspace).where(Workspace.id == id))
        return result.scalar_one_or_none()

    async def list_workspaces(self) -> list[Workspace]:
        result = await self.session.execute(select(Workspace))
        return list(result.scalars().all())

    async def update_workspace(self, id: uuid.UUID, updates: dict[str, Any]) -> Workspace | None:
        workspace = await self.get_workspace(id)
        if workspace is None:
            return None
        for key, value in updates.items():
            if key == "metadata":
                workspace.meta_data = value
            elif hasattr(workspace, key):
                setattr(workspace, key, value)
        workspace.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def delete_workspace(self, id: uuid.UUID) -> bool:
        workspace = await self.get_workspace(id)
        if workspace is None:
            return False
        await self.session.delete(workspace)
        await self.session.commit()
        return True

    async def register_device(
        self,
        workspace_id: uuid.UUID,
        name: str,
        type: str,
        os: str,
        capabilities: dict[str, Any] | None = None,
    ) -> Device | None:
        workspace = await self.get_workspace(workspace_id)
        if workspace is None:
            return None
        device = Device(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            name=name,
            type=type,
            os=os,
            status="online",
            last_seen=datetime.utcnow(),
            capabilities=capabilities or {},
            created_at=datetime.utcnow(),
        )
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        return device

    async def list_devices(self, workspace_id: uuid.UUID) -> list[Device]:
        result = await self.session.execute(
            select(Device).where(Device.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def remove_device(self, workspace_id: uuid.UUID, device_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(Device).where(
                Device.id == device_id,
                Device.workspace_id == workspace_id,
            )
        )
        device = result.scalar_one_or_none()
        if device is None:
            return False
        await self.session.delete(device)
        await self.session.commit()
        return True
