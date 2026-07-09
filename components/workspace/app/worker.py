import asyncio
import logging

from app.config import settings
from app.events.bus import event_bus
from app.events.handlers import register_handlers
from app.core.presence_service import PresenceService
from app.database import async_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("workspace.worker")


async def idle_checker():
    while True:
        try:
            async with async_session() as db:
                svc = PresenceService(db)
                await svc.check_idle(timeout_seconds=300)
        except Exception as e:
            logger.error("Idle check failed: %s", e)
        await asyncio.sleep(60)


async def main():
    logger.info("Starting workspace worker...")
    await event_bus.connect()
    register_handlers()
    logger.info("Event handlers registered")

    await asyncio.gather(idle_checker())


if __name__ == "__main__":
    asyncio.run(main())
