from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class NotificationResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    user_id: str
    type: str
    title: str
    message: str
    severity: str
    read: bool
    actions: list
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationRuleCreate(BaseModel):
    workspace_id: UUID
    name: str
    condition: dict
    actions: list = []
    enabled: bool = True


class NotificationRuleResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    condition: dict
    actions: list
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True
