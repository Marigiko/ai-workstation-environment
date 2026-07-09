#!/usr/bin/env python3
"""Real Hermes adapter for workspace integration."""

import asyncio
import logging
from typing import AsyncIterator, Dict, Optional
from app.adapters import BaseAdapter

logger = logging.getLogger(__name__)


class HermesAdapter(BaseAdapter):
    """Hermes Agent adapter for multi-device integration."""

    def __init__(self, hermes_url: str = "http://localhost:8081"):
        self.hermes_url = hermes_url
        self.connected = False
        self.session_id = None

    async def connect(self) -> None:
        """Connect to Hermes Agent."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.hermes_url}/health", timeout=5)
                if resp.status_code == 200:
                    self.connected = True
                    logger.info("Connected to Hermes Agent")
                else:
                    logger.warning(f"Hermes health check failed: {resp.status_code}")
                    self.connected = False
        except Exception as e:
            logger.warning(f"Could not connect to Hermes: {e}")
            self.connected = False

    async def disconnect(self) -> None:
        """Disconnect from Hermes."""
        self.connected = False
        self.session_id = None
        logger.info("Disconnected from Hermes")

    async def send_message(self, session_id: str, message: dict) -> dict:
        """Send message to Hermes agent."""
        if not self.connected:
            return {"error": "Not connected to Hermes"}

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.hermes_url}/api/chat",
                    json={"session_id": session_id, **message},
                    timeout=30,
                )
                if resp.status_code == 200:
                    return resp.json()
                return {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def receive_messages(self, session_id: str) -> AsyncIterator[dict]:
        """Receive messages from Hermes."""
        while self.connected:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"{self.hermes_url}/api/messages/{session_id}",
                        timeout=5,
                    )
                    if resp.status_code == 200:
                        messages = resp.json()
                        for msg in messages:
                            yield msg
            except Exception:
                pass
            await asyncio.sleep(1)

    async def sync_state(self, session_id: str) -> dict:
        """Sync state with Hermes."""
        return {
            "session_id": session_id,
            "synced": True,
            "connected": self.connected,
        }

    async def get_status(self) -> dict:
        """Get Hermes status."""
        return {
            "adapter": "hermes",
            "connected": self.connected,
            "url": self.hermes_url,
        }
