from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.storage.redis import RedisClient
from app.events.bus import event_bus


async def get_database() -> AsyncSession:
    async for session in get_db():
        yield session


async def get_redis() -> RedisClient:
    from app.storage.redis import redis_client
    yield redis_client


async def get_event_bus():
    yield event_bus
