from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow


class WorkflowEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_workflow(
        self,
        workspace_id: uuid.UUID,
        name: str,
        description: str = "",
        steps: list[dict[str, Any]] | None = None,
        input: dict[str, Any] | None = None,
    ) -> Workflow:
        workflow = Workflow(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            name=name,
            description=description,
            status="created",
            steps=steps or [],
            current_step=0,
            input=input or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(workflow)
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow

    async def get_workflow(self, id: uuid.UUID) -> Workflow | None:
        result = await self.session.execute(select(Workflow).where(Workflow.id == id))
        return result.scalar_one_or_none()

    async def list_workflows(self, workspace_id: uuid.UUID) -> list[Workflow]:
        result = await self.session.execute(
            select(Workflow).where(Workflow.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def execute_workflow(self, id: uuid.UUID) -> Workflow | None:
        workflow = await self.get_workflow(id)
        if workflow is None:
            return None
        workflow.status = "running"
        workflow.current_step = 0
        workflow.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow

    async def pause_workflow(self, id: uuid.UUID) -> Workflow | None:
        workflow = await self.get_workflow(id)
        if workflow is None:
            return None
        workflow.status = "paused"
        workflow.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow

    async def resume_workflow(self, id: uuid.UUID) -> Workflow | None:
        workflow = await self.get_workflow(id)
        if workflow is None:
            return None
        workflow.status = "running"
        workflow.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow

    async def cancel_workflow(self, id: uuid.UUID) -> Workflow | None:
        workflow = await self.get_workflow(id)
        if workflow is None:
            return None
        workflow.status = "failed"
        workflow.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow

    async def get_step(self, workflow_id: uuid.UUID, step_id: str) -> dict[str, Any] | None:
        workflow = await self.get_workflow(workflow_id)
        if workflow is None:
            return None
        for step in workflow.steps:
            if step.get("id") == step_id:
                return step
        return None
