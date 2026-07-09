import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(String(255), default="")
    type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    message = Column(String, default="")
    severity = Column(String(20), default="info")  # info, warning, error, critical
    read = Column(Boolean, default=False)
    actions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationRule(Base):
    __tablename__ = "notification_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    condition = Column(JSON, nullable=False)
    actions = Column(JSON, default=list)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
