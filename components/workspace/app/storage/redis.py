import redis.asyncio as aioredis

from app.config import settings


class RedisClient:
    def __init__(self):
        self.redis: aioredis.Redis = None

    async def connect(self):
        self.redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expires: int = None):
        await self.redis.set(key, value, ex=expires)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def publish(self, channel: str, message: str):
        await self.redis.publish(channel, message)

    async def subscribe(self, channel: str):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub


redis_client = RedisClient()
