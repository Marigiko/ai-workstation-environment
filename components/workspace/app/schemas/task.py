from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class TaskCreate(BaseModel):
    workspace_id: UUID
    session_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    title: str
    description: str = ""
    priority: int = 0
    agent_id: str = ""
    model: str = ""
    input: dict = {}


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    agent_id: Optional[str] = None
    model: Optional[str] = None


class TaskResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    session_id: Optional[UUID]
    parent_task_id: Optional[UUID]
    title: str
    description: str
    status: str
    priority: int
    agent_id: str
    model: str
    progress: float
    input: dict
    output: dict
    error: dict
    logs: List[str]
    duration_ms: Optional[int]
    cost_usd: Optional[float]
    tokens_used: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
