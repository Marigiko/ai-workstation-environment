import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=True)
    parent_task_id = Column(UUID(as_uuid=True), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(String, default="")
    status = Column(String(20), default="pending")  # pending, running, paused, completed, failed, cancelled
    priority = Column(Integer, default=0)
    agent_id = Column(String(255), default="")
    model = Column(String(255), default="")
    progress = Column(Float, default=0.0)
    input = Column(JSON, default=dict)
    output = Column(JSON, default=dict)
    error = Column(JSON, default=dict)
    logs = Column(JSON, default=list)
    duration_ms = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="tasks")
