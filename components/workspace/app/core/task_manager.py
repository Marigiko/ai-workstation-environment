from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


class TaskManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_task(
        self,
        workspace_id: uuid.UUID,
        title: str,
        description: str = "",
        priority: int = 0,
        agent_id: str = "",
        model: str = "",
        session_id: uuid.UUID | None = None,
        input: dict[str, Any] | None = None,
    ) -> Task:
        task = Task(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            session_id=session_id,
            title=title,
            description=description,
            status="pending",
            priority=priority,
            agent_id=agent_id,
            model=model,
            input=input or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_task(self, id: uuid.UUID) -> Task | None:
        result = await self.session.execute(select(Task).where(Task.id == id))
        return result.scalar_one_or_none()

    async def list_tasks(
        self, workspace_id: uuid.UUID, status: str | None = None
    ) -> list[Task]:
        stmt = select(Task).where(Task.workspace_id == workspace_id)
        if status:
            stmt = stmt.where(Task.status == status)
        stmt = stmt.order_by(Task.priority.desc(), Task.created_at)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_task(self, id: uuid.UUID, updates: dict[str, Any]) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete_task(self, id: uuid.UUID) -> bool:
        task = await self.get_task(id)
        if task is None:
            return False
        await self.session.delete(task)
        await self.session.commit()
        return True

    async def start_task(self, id: uuid.UUID, agent_id: str) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.status = "running"
        task.agent_id = agent_id
        task.started_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def pause_task(self, id: uuid.UUID) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.status = "paused"
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def resume_task(self, id: uuid.UUID) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.status = "running"
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def cancel_task(self, id: uuid.UUID) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.status = "cancelled"
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def restart_task(self, id: uuid.UUID) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.status = "pending"
        task.progress = 0.0
        task.output = {}
        task.error = {}
        task.started_at = None
        task.completed_at = None
        task.duration_ms = None
        task.cost_usd = None
        task.tokens_used = None
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def complete_task(
        self,
        id: uuid.UUID,
        output: dict[str, Any] | None = None,
        duration_ms: int | None = None,
        cost_usd: float | None = None,
        tokens_used: int | None = None,
    ) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.status = "completed"
        task.progress = 1.0
        task.output = output or {}
        task.duration_ms = duration_ms
        task.cost_usd = cost_usd
        task.tokens_used = tokens_used
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def fail_task(self, id: uuid.UUID, error: dict[str, Any]) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.status = "failed"
        task.error = error
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update_progress(self, id: uuid.UUID, progress: float) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.progress = min(max(progress, 0.0), 1.0)
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def approve_task(self, id: uuid.UUID) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def reject_task(self, id: uuid.UUID) -> Task | None:
        task = await self.get_task(id)
        if task is None:
            return None
        task.status = "cancelled"
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task
