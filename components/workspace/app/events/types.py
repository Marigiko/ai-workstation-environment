from enum import Enum


class EventType(str, Enum):
    # Session events
    SESSION_CREATED = "session.created"
    SESSION_MESSAGE_NEW = "session.message.new"
    SESSION_PAUSED = "session.paused"
    SESSION_RESUMED = "session.resumed"
    SESSION_MIGRATED = "session.migrated"
    SESSION_CHECKPOINT_CREATED = "session.checkpoint.created"
    SESSION_ARCHIVED = "session.archived"

    # Task events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_PAUSED = "task.paused"
    TASK_RESUMED = "task.resumed"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"

    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    # Presence events
    DEVICE_ONLINE = "device.online"
    DEVICE_OFFLINE = "device.offline"
    USER_ACTIVE = "user.active"
    USER_IDLE = "user.idle"

    # Notification events
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_DELIVERED = "notification.delivered"
    NOTIFICATION_READ = "notification.read"
