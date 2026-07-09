import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), default="")
    status = Column(String(20), default="created")  # created, running, paused, completed, failed
    steps = Column(JSON, default=list)
    current_step = Column(Integer, default=0)
    input = Column(JSON, default=dict)
    output = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="workflows")
