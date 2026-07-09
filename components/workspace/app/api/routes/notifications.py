from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.notification import (
    NotificationResponse, NotificationRuleCreate, NotificationRuleResponse,
)
from app.core.notification_service import NotificationService

router = APIRouter()
rules_router = APIRouter()


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    workspace_id: UUID = Query(...),
    user_id: str = Query(None),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    svc = NotificationService(db)
    return await svc.list_notifications(workspace_id, user_id, unread_only)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    notif = await svc.get_notification(notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(notification_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    notif = await svc.mark_read(notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


@router.post("/{notification_id}/dismiss")
async def dismiss(notification_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    dismissed = await svc.dismiss(notification_id)
    if not dismissed:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "dismissed"}


@rules_router.post("/", response_model=NotificationRuleResponse)
async def create_rule(data: NotificationRuleCreate, db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    rule = await svc.create_rule(data.workspace_id, data.name, data.condition, data.actions)
    return rule


@rules_router.get("/", response_model=list[NotificationRuleResponse])
async def list_rules(workspace_id: UUID = Query(...), db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    return await svc.list_rules(workspace_id)


@rules_router.put("/{rule_id}", response_model=NotificationRuleResponse)
async def update_rule(rule_id: UUID, data: dict, db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    rule = await svc.update_rule(rule_id, **data)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@rules_router.delete("/{rule_id}")
async def delete_rule(rule_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    deleted = await svc.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"status": "deleted"}
