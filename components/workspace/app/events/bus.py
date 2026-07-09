import json
import asyncio
from typing import Callable, Dict, List, Any
from datetime import datetime
import uuid

import redis.asyncio as aioredis

from app.config import settings
from app.events.types import EventType


class Event:
    def __init__(self, event_type: EventType, workspace_id: str, payload: dict, metadata: dict = None):
        self.id = str(uuid.uuid4())
        self.type = event_type
        self.workspace_id = workspace_id
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.payload = payload
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "workspace_id": self.workspace_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class EventBus:
    def __init__(self):
        self.redis: aioredis.Redis = None
        self.handlers: Dict[str, List[Callable]] = {}
        self._pubsub = None

    async def connect(self):
        self.redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        self._pubsub = self.redis.pubsub()

    async def disconnect(self):
        if self._pubsub:
            await self._pubsub.unsubscribe()
        if self.redis:
            await self.redis.close()

    async def publish(self, event: Event):
        channel = f"workspace:{event.workspace_id}:events"
        await self.redis.publish(channel, event.to_json())

    async def subscribe(self, workspace_id: str, handler: Callable):
        channel = f"workspace:{workspace_id}:events"
        await self._pubsub.subscribe(channel)
        asyncio.create_task(self._listen(channel, handler))

    async def _listen(self, channel: str, handler: Callable):
        async for message in self._pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    await handler(data)
                except Exception:
                    pass

    def on(self, event_type: EventType, handler: Callable):
        key = event_type.value
        if key not in self.handlers:
            self.handlers[key] = []
        self.handlers[key].append(handler)

    async def emit(self, event_type: EventType, workspace_id: str, payload: dict, metadata: dict = None):
        event = Event(event_type, workspace_id, payload, metadata)
        await self.publish(event)

        handlers = self.handlers.get(event_type.value, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                pass


event_bus = EventBus()
