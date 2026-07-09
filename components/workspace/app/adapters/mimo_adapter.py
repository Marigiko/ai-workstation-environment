from typing import AsyncIterator
from app.adapters import BaseAdapter


class MimoAdapter(BaseAdapter):
    def __init__(self, mimo_url: str = "http://localhost:3000"):
        self.mimo_url = mimo_url
        self.connected = False

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.connected = False

    async def send_message(self, session_id: str, message: dict) -> dict:
        return {"status": "sent", "session_id": session_id}

    async def receive_messages(self, session_id: str) -> AsyncIterator[dict]:
        yield {"type": "connected", "session_id": session_id}

    async def sync_state(self, session_id: str) -> dict:
        return {"session_id": session_id, "synced": True}

    async def get_status(self) -> dict:
        return {"adapter": "mimo", "connected": self.connected}
