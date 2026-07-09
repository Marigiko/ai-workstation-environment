import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # notebook, desktop, android, web
    os = Column(String(50), default="")
    status = Column(String(20), default="offline")  # online, offline
    last_seen = Column(DateTime, default=datetime.utcnow)
    capabilities = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="devices")
