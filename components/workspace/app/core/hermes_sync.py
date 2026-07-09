#!/usr/bin/env python3
"""Hermes sync engine for workspace state synchronization."""

import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SyncState:
    session_id: str
    last_sync: datetime
    pending_changes: List[Dict]
    synced: bool = True


class HermesSync:
    """Synchronizes state between Hermes and workspace."""

    def __init__(self, workspace_url: str = "http://localhost:8080"):
        self.workspace_url = workspace_url
        self.states: Dict[str, SyncState] = {}

    async def sync_session(self, session_id: str) -> Dict:
        """Sync a session with the workspace."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.workspace_url}/sessions/{session_id}",
                    timeout=10,
                )
                if resp.status_code == 200:
                    session = resp.json()
                    state = SyncState(
                        session_id=session_id,
                        last_sync=datetime.utcnow(),
                        pending_changes=[],
                        synced=True,
                    )
                    self.states[session_id] = state
                    return {"status": "synced", "session": session}
                return {"status": "error", "code": resp.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def sync_task(self, task_id: str) -> Dict:
        """Sync a task with the workspace."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.workspace_url}/tasks/{task_id}",
                    timeout=10,
                )
                if resp.status_code == 200:
                    return {"status": "synced", "task": resp.json()}
                return {"status": "error", "code": resp.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_pending_changes(self, session_id: str) -> List[Dict]:
        """Get pending changes for a session."""
        state = self.states.get(session_id)
        if state:
            return state.pending_changes
        return []

    def mark_synced(self, session_id: str):
        """Mark a session as synced."""
        if session_id in self.states:
            self.states[session_id].synced = True
            self.states[session_id].pending_changes = []
