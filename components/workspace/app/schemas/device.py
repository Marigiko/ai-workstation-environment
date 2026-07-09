from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class DeviceCreate(BaseModel):
    name: str
    type: str  # notebook, desktop, android, web
    os: str = ""
    capabilities: dict = {}


class DeviceResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    type: str
    os: str
    status: str
    last_seen: datetime
    capabilities: dict
    created_at: datetime

    class Config:
        from_attributes = True
