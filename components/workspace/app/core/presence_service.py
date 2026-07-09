from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device


class PresenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def heartbeat(self, device_id: uuid.UUID) -> None:
        result = await self.session.execute(
            select(Device).where(Device.id == device_id)
        )
        device = result.scalar_one_or_none()
        if device is None:
            return
        device.last_seen = datetime.utcnow()
        device.status = "online"
        await self.session.commit()

    async def get_devices(self, workspace_id: uuid.UUID) -> list[Device]:
        result = await self.session.execute(
            select(Device).where(Device.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def get_users(self, workspace_id: uuid.UUID) -> list[dict[str, Any]]:
        result = await self.session.execute(
            select(Device).where(
                Device.workspace_id == workspace_id,
                Device.status == "online",
            )
        )
        devices = result.scalars().all()
        seen: set[str] = set()
        users: list[dict[str, Any]] = []
        for device in devices:
            owner = device.capabilities.get("owner_id", "")
            if owner and owner not in seen:
                seen.add(owner)
                users.append({
                    "user_id": owner,
                    "device_id": str(device.id),
                    "device_name": device.name,
                    "last_seen": device.last_seen.isoformat(),
                })
        return users

    async def get_activity(self, workspace_id: uuid.UUID) -> list[dict[str, Any]]:
        result = await self.session.execute(
            select(Device)
            .where(Device.workspace_id == workspace_id)
            .order_by(Device.last_seen.desc())
        )
        devices = result.scalars().all()
        return [
            {
                "device_id": str(d.id),
                "device_name": d.name,
                "device_type": d.type,
                "status": d.status,
                "last_seen": d.last_seen.isoformat(),
            }
            for d in devices
        ]

    async def check_idle(self, timeout_seconds: int = 300) -> list[Device]:
        cutoff = datetime.utcnow() - timedelta(seconds=timeout_seconds)
        result = await self.session.execute(
            select(Device).where(
                Device.status == "online",
                Device.last_seen < cutoff,
            )
        )
        idle_devices = list(result.scalars().all())
        for device in idle_devices:
            device.status = "idle"
        if idle_devices:
            await self.session.commit()
        return idle_devices
