from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationRule


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_notification(
        self,
        workspace_id: uuid.UUID,
        user_id: str,
        type: str,
        title: str,
        message: str = "",
        severity: str = "info",
        actions: list[dict[str, Any]] | None = None,
    ) -> Notification:
        notification = Notification(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            severity=severity,
            read=False,
            actions=actions or [],
            created_at=datetime.utcnow(),
        )
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def get_notification(self, id: uuid.UUID) -> Notification | None:
        result = await self.session.execute(
            select(Notification).where(Notification.id == id)
        )
        return result.scalar_one_or_none()

    async def list_notifications(
        self,
        workspace_id: uuid.UUID,
        user_id: str = "",
        unread_only: bool = False,
    ) -> list[Notification]:
        stmt = select(Notification).where(Notification.workspace_id == workspace_id)
        if user_id:
            stmt = stmt.where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.read == False)
        stmt = stmt.order_by(Notification.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_read(self, id: uuid.UUID) -> Notification | None:
        notification = await self.get_notification(id)
        if notification is None:
            return None
        notification.read = True
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def dismiss(self, id: uuid.UUID) -> bool:
        notification = await self.get_notification(id)
        if notification is None:
            return False
        await self.session.delete(notification)
        await self.session.commit()
        return True

    async def create_rule(
        self,
        workspace_id: uuid.UUID,
        name: str,
        condition: dict[str, Any],
        actions: list[dict[str, Any]] | None = None,
    ) -> NotificationRule:
        rule = NotificationRule(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            name=name,
            condition=condition,
            actions=actions or [],
            enabled=True,
            created_at=datetime.utcnow(),
        )
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def list_rules(self, workspace_id: uuid.UUID) -> list[NotificationRule]:
        result = await self.session.execute(
            select(NotificationRule).where(NotificationRule.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def update_rule(
        self, id: uuid.UUID, updates: dict[str, Any]
    ) -> NotificationRule | None:
        result = await self.session.execute(
            select(NotificationRule).where(NotificationRule.id == id)
        )
        rule = result.scalar_one_or_none()
        if rule is None:
            return None
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def delete_rule(self, id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(NotificationRule).where(NotificationRule.id == id)
        )
        rule = result.scalar_one_or_none()
        if rule is None:
            return False
        await self.session.delete(rule)
        await self.session.commit()
        return True

    async def evaluate_rules(
        self, event_type: str, event_data: dict[str, Any]
    ) -> list[Notification]:
        created: list[Notification] = []
        result = await self.session.execute(
            select(NotificationRule).where(NotificationRule.enabled == True)
        )
        rules = result.scalars().all()

        for rule in rules:
            if self._match_condition(rule.condition, event_type, event_data):
                for action in rule.actions:
                    notification = Notification(
                        id=uuid.uuid4(),
                        workspace_id=rule.workspace_id,
                        user_id=action.get("user_id", ""),
                        type=action.get("type", event_type),
                        title=action.get("title", f"Event: {event_type}"),
                        message=action.get("message", str(event_data)),
                        severity=action.get("severity", "info"),
                        read=False,
                        actions=[],
                        created_at=datetime.utcnow(),
                    )
                    self.session.add(notification)
                    created.append(notification)

        if created:
            await self.session.commit()
            for n in created:
                await self.session.refresh(n)

        return created

    def _match_condition(
        self,
        condition: dict[str, Any],
        event_type: str,
        event_data: dict[str, Any],
    ) -> bool:
        if "event_type" in condition and condition["event_type"] != event_type:
            return False
        for key, expected in condition.items():
            if key == "event_type":
                continue
            if event_data.get(key) != expected:
                return False
        return True
