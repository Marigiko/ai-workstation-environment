import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), default="")
    owner_id = Column(String(255), nullable=False)
    meta_data = Column("meta_data", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    devices = relationship("Device", back_populates="workspace", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="workspace", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="workspace", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="workspace", cascade="all, delete-orphan")
