from app.events.types import EventType
from app.events.bus import Event, event_bus
from app.core.notification_service import NotificationService
from app.core.presence_service import PresenceService


async def handle_task_completed(event: Event):
    payload = event.payload
    task_id = payload.get("task_id")
    workspace_id = event.workspace_id

    from app.database import async_session
    async with async_session() as db:
        svc = NotificationService(db)
        await svc.create_notification(
            workspace_id=workspace_id,
            user_id=payload.get("user_id", ""),
            type="task.completed",
            title=f"Task completed: {payload.get('title', 'Unknown')}",
            message=f"Task {task_id} has completed successfully.",
            severity="info",
        )


async def handle_task_failed(event: Event):
    payload = event.payload
    task_id = payload.get("task_id")
    workspace_id = event.workspace_id

    from app.database import async_session
    async with async_session() as db:
        svc = NotificationService(db)
        await svc.create_notification(
            workspace_id=workspace_id,
            user_id=payload.get("user_id", ""),
            type="task.failed",
            title=f"Task failed: {payload.get('title', 'Unknown')}",
            message=f"Task {task_id} has failed: {payload.get('error', 'Unknown error')}",
            severity="error",
        )


async def handle_device_online(event: Event):
    pass


async def handle_device_offline(event: Event):
    pass


def register_handlers():
    event_bus.on(EventType.TASK_COMPLETED, handle_task_completed)
    event_bus.on(EventType.TASK_FAILED, handle_task_failed)
    event_bus.on(EventType.DEVICE_ONLINE, handle_device_online)
    event_bus.on(EventType.DEVICE_OFFLINE, handle_device_offline)
