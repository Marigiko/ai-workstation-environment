"""Initial workspace schema

Revision ID: 001
Revises:
Create Date: 2026-07-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), default=""),
        sa.Column("owner_id", sa.String(255), nullable=False),
        sa.Column("metadata", postgresql.JSON, default={}),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now()),
    )

    op.create_table(
        "devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("os", sa.String(50), default=""),
        sa.Column("status", sa.String(20), default="offline"),
        sa.Column("last_seen", sa.DateTime, default=sa.func.now()),
        sa.Column("capabilities", postgresql.JSON, default={}),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("title", sa.String(500), default=""),
        sa.Column("status", sa.String(20), default="created"),
        sa.Column("current_device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id"), nullable=True),
        sa.Column("checkpoint_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSON, default={}),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now()),
    )

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, default=""),
        sa.Column("tool_calls", postgresql.JSON, default=[]),
        sa.Column("tool_results", postgresql.JSON, default=[]),
        sa.Column("sequence", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )

    op.create_table(
        "checkpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("state", postgresql.JSON, nullable=False),
        sa.Column("auto", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=True),
        sa.Column("parent_task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, default=""),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("priority", sa.Integer, default=0),
        sa.Column("agent_id", sa.String(255), default=""),
        sa.Column("model", sa.String(255), default=""),
        sa.Column("progress", sa.Float, default=0.0),
        sa.Column("input", postgresql.JSON, default={}),
        sa.Column("output", postgresql.JSON, default={}),
        sa.Column("error", postgresql.JSON, default={}),
        sa.Column("logs", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("cost_usd", sa.Float, nullable=True),
        sa.Column("tokens_used", sa.Integer, nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now()),
    )

    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), default=""),
        sa.Column("status", sa.String(20), default="created"),
        sa.Column("steps", postgresql.JSON, default=[]),
        sa.Column("current_step", sa.Integer, default=0),
        sa.Column("input", postgresql.JSON, default={}),
        sa.Column("output", postgresql.JSON, default={}),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now()),
    )

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.String(255), default=""),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("message", sa.Text, default=""),
        sa.Column("severity", sa.String(20), default="info"),
        sa.Column("read", sa.Boolean, default=False),
        sa.Column("actions", postgresql.JSON, default=[]),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )

    op.create_table(
        "notification_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("condition", postgresql.JSON, nullable=False),
        sa.Column("actions", postgresql.JSON, default=[]),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )


def downgrade():
    op.drop_table("notification_rules")
    op.drop_table("notifications")
    op.drop_table("workflows")
    op.drop_table("tasks")
    op.drop_table("checkpoints")
    op.drop_table("messages")
    op.drop_table("sessions")
    op.drop_table("devices")
    op.drop_table("workspaces")
