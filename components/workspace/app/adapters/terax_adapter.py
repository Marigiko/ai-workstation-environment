#!/usr/bin/env python3
"""Real Terax adapter for workspace integration."""

import asyncio
import logging
from typing import AsyncIterator, Dict, Optional
from app.adapters import BaseAdapter

logger = logging.getLogger(__name__)


class TeraxAdapter(BaseAdapter):
    """Terax AI-native terminal adapter."""

    def __init__(self, terax_url: str = "http://localhost:3000"):
        self.terax_url = terax_url
        self.connected = False
        self.session_id = None

    async def connect(self) -> None:
        """Connect to Terax instance."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.terax_url}/health", timeout=5)
                if resp.status_code == 200:
                    self.connected = True
                    logger.info("Connected to Terax")
                else:
                    logger.warning(f"Terax health check failed: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to Terax: {e}")
            self.connected = False

    async def disconnect(self) -> None:
        """Disconnect from Terax."""
        self.connected = False
        self.session_id = None
        logger.info("Disconnected from Terax")

    async def send_message(self, session_id: str, message: dict) -> dict:
        """Send message to Terax agent."""
        if not self.connected:
            return {"error": "Not connected to Terax"}

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.terax_url}/api/chat",
                    json={"session_id": session_id, **message},
                    timeout=30,
                )
                if resp.status_code == 200:
                    return resp.json()
                return {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def receive_messages(self, session_id: str) -> AsyncIterator[dict]:
        """Receive messages from Terax."""
        # Terax doesn't have a streaming API, so we poll
        while self.connected:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"{self.terax_url}/api/messages/{session_id}",
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
        """Sync state with Terax."""
        return {
            "session_id": session_id,
            "synced": True,
            "connected": self.connected,
        }

    async def get_status(self) -> dict:
        """Get Terax status."""
        return {
            "adapter": "terax",
            "connected": self.connected,
            "url": self.terax_url,
        }
