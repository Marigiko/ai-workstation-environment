from typing import List
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session, Message, Checkpoint
from app.sync.vector_clock import VectorClock
from app.sync.conflict_resolution import resolve_conflict


class SyncEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_messages(self, session_id: UUID, messages: list[dict], last_sequence: int) -> dict:
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .where(Message.sequence > last_sequence)
            .order_by(Message.sequence)
        )
        existing = list(result.scalars().all())

        existing_dicts = [
            {
                "id": str(m.id),
                "sequence": m.sequence,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in existing
        ]

        merged = resolve_conflict(existing_dicts, messages)

        applied = 0
        new_sequence = last_sequence
        for msg_data in messages:
            if msg_data.get("sequence", 0) > last_sequence:
                msg = Message(
                    session_id=session_id,
                    role=msg_data["role"],
                    content=msg_data.get("content", ""),
                    tool_calls=msg_data.get("tool_calls", []),
                    tool_results=msg_data.get("tool_results", []),
                    sequence=msg_data["sequence"],
                )
                self.db.add(msg)
                applied += 1
                new_sequence = max(new_sequence, msg_data["sequence"])

        await self.db.commit()

        return {
            "applied": applied,
            "new_sequence": new_sequence,
            "conflicts": [],
        }

    async def create_checkpoint(self, session_id: UUID, state: dict, auto: bool = False) -> Checkpoint:
        checkpoint = Checkpoint(session_id=session_id, state=state, auto=auto)
        self.db.add(checkpoint)
        await self.db.commit()
        await self.db.refresh(checkpoint)
        return checkpoint

    async def restore_checkpoint(self, session_id: UUID, checkpoint_id: UUID) -> dict | None:
        result = await self.db.execute(
            select(Checkpoint).where(
                Checkpoint.id == checkpoint_id,
                Checkpoint.session_id == session_id,
            )
        )
        checkpoint = result.scalar_one_or_none()
        if checkpoint:
            return checkpoint.state
        return None
