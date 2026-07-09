from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class WorkflowCreate(BaseModel):
    workspace_id: UUID
    name: str
    description: str = ""
    steps: list = []
    input: dict = {}


class WorkflowResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    description: str
    status: str
    steps: list
    current_step: int
    input: dict
    output: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
