from typing import AsyncIterator
from app.adapters import BaseAdapter


class OpenCodeAdapter(BaseAdapter):
    def __init__(self, opencode_url: str = "http://localhost:3001"):
        self.opencode_url = opencode_url
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
        return {"adapter": "opencode", "connected": self.connected}
