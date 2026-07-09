from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class WorkspaceCreate(BaseModel):
    name: str
    description: str = ""
    owner_id: str
    metadata: dict = {}


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    description: str
    owner_id: str
    metadata: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            owner_id=obj.owner_id,
            metadata=obj.meta_data or {},
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
