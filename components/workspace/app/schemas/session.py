from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class SessionCreate(BaseModel):
    workspace_id: UUID
    title: str = ""
    metadata: dict = {}


class SessionResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    status: str
    current_device_id: Optional[UUID] = None
    metadata: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, obj):
        return cls(
            id=obj.id,
            workspace_id=obj.workspace_id,
            title=obj.title,
            status=obj.status,
            current_device_id=obj.current_device_id,
            metadata=obj.meta_data or {},
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


class MessageCreate(BaseModel):
    role: str
    content: str = ""
    tool_calls: list = []
    tool_results: list = []


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    tool_calls: list
    tool_results: list
    sequence: int
    created_at: datetime

    class Config:
        from_attributes = True


class CheckpointResponse(BaseModel):
    id: UUID
    session_id: UUID
    state: dict
    auto: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SyncRequest(BaseModel):
    messages: List[MessageCreate] = []
    last_sequence: int = 0


class SyncResponse(BaseModel):
    applied: int
    new_sequence: int
    conflicts: list = []
