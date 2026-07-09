from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session, Message, Checkpoint


class SessionManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(
        self,
        workspace_id: uuid.UUID,
        title: str,
        metadata: dict[str, Any] | None = None,
    ) -> Session:
        sess = Session(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            title=title,
            status="created",
            meta_data=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(sess)
        await self.session.commit()
        await self.session.refresh(sess)
        return sess

    async def get_session(self, id: uuid.UUID) -> Session | None:
        result = await self.session.execute(select(Session).where(Session.id == id))
        return result.scalar_one_or_none()

    async def list_sessions(self, workspace_id: uuid.UUID) -> list[Session]:
        result = await self.session.execute(
            select(Session).where(Session.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def add_message(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
        tool_results: list[dict[str, Any]] | None = None,
    ) -> Message:
        result = await self.session.execute(
            select(func.coalesce(func.max(Message.sequence), 0)).where(
                Message.session_id == session_id
            )
        )
        next_seq = result.scalar() + 1

        message = Message(
            id=uuid.uuid4(),
            session_id=session_id,
            role=role,
            content=content,
            tool_calls=tool_calls or [],
            tool_results=tool_results or [],
            sequence=next_seq,
            created_at=datetime.utcnow(),
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_messages(
        self, session_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> list[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.sequence)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def pause_session(self, id: uuid.UUID) -> Session | None:
        sess = await self.get_session(id)
        if sess is None:
            return None
        sess.status = "paused"
        sess.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(sess)
        return sess

    async def resume_session(self, id: uuid.UUID) -> Session | None:
        sess = await self.get_session(id)
        if sess is None:
            return None
        sess.status = "active"
        sess.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(sess)
        return sess

    async def archive_session(self, id: uuid.UUID) -> Session | None:
        sess = await self.get_session(id)
        if sess is None:
            return None
        sess.status = "archived"
        sess.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(sess)
        return sess

    async def create_checkpoint(
        self, session_id: uuid.UUID, state: dict[str, Any], auto: bool = False
    ) -> Checkpoint:
        checkpoint = Checkpoint(
            id=uuid.uuid4(),
            session_id=session_id,
            state=state,
            auto=auto,
            created_at=datetime.utcnow(),
        )
        self.session.add(checkpoint)

        result = await self.session.execute(
            select(Session).where(Session.id == session_id)
        )
        sess = result.scalar_one_or_none()
        if sess:
            sess.checkpoint_id = checkpoint.id
            sess.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(checkpoint)
        return checkpoint

    async def restore_checkpoint(
        self, session_id: uuid.UUID, checkpoint_id: uuid.UUID
    ) -> Session | None:
        result = await self.session.execute(
            select(Checkpoint).where(
                Checkpoint.id == checkpoint_id,
                Checkpoint.session_id == session_id,
            )
        )
        checkpoint = result.scalar_one_or_none()
        if checkpoint is None:
            return None

        sess_result = await self.session.execute(
            select(Session).where(Session.id == session_id)
        )
        sess = sess_result.scalar_one_or_none()
        if sess is None:
            return None

        sess.checkpoint_id = checkpoint_id
        sess.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(sess)
        return sess

    async def migrate_session(
        self, session_id: uuid.UUID, target_device_id: uuid.UUID
    ) -> Session | None:
        sess = await self.get_session(session_id)
        if sess is None:
            return None
        sess.status = "migrating"
        sess.current_device_id = target_device_id
        sess.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(sess)
        return sess
