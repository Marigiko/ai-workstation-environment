import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    title = Column(String(500), default="")
    status = Column(String(20), default="created")  # created, active, paused, archived, migrating
    current_device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    checkpoint_id = Column(UUID(as_uuid=True), nullable=True)
    meta_data = Column("meta_data", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.sequence")
    checkpoints = relationship("Checkpoint", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(String, default="")
    tool_calls = Column(JSON, default=list)
    tool_results = Column(JSON, default=list)
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    state = Column(JSON, nullable=False)
    auto = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="checkpoints")
