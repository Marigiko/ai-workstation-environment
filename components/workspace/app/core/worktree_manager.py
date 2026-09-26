#!/usr/bin/env python3
"""Worktree Manager - Manages multiple isolated worktrees."""

import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Worktree:
    id: str
    name: str
    path: str
    model: str = "qwen2.5-coder:7b"
    agent: str = "coder"
    session_id: Optional[str] = None
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict = field(default_factory=dict)


class WorktreeManager:
    """Manages multiple isolated worktrees with independent state."""

    def __init__(self, base_path: str = "/mnt/e/Projects"):
        self.base_path = Path(base_path)
        self.worktrees: Dict[str, Worktree] = {}
        self.config_path = Path.home() / ".config" / "workspace" / "worktrees.json"
        self._load_worktrees()

    def _load_worktrees(self):
        """Load worktrees from config file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                for wt_data in data.get("worktrees", []):
                    wt = Worktree(**wt_data)
                    self.worktrees[wt.id] = wt
            except Exception as e:
                logger.error(f"Failed to load worktrees: {e}")

    def _save_worktrees(self):
        """Save worktrees to config file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "worktrees": [
                {
                    "id": wt.id,
                    "name": wt.name,
                    "path": wt.path,
                    "model": wt.model,
                    "agent": wt.agent,
                    "session_id": wt.session_id,
                    "status": wt.status,
                    "created_at": wt.created_at,
                    "metadata": wt.metadata,
                }
                for wt in self.worktrees.values()
            ]
        }
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def create_worktree(
        self,
        name: str,
        project_path: str,
        model: str = "qwen2.5-coder:7b",
        agent: str = "coder",
    ) -> Worktree:
        """Create a new worktree."""
        import uuid
        wt_id = str(uuid.uuid4())[:8]
        wt_path = str(self.base_path / name)

        wt = Worktree(
            id=wt_id,
            name=name,
            path=wt_path,
            model=model,
            agent=agent,
        )

        self.worktrees[wt_id] = wt
        self._save_worktrees()

        logger.info(f"Created worktree {wt_id}: {name}")
        return wt

    def get_worktree(self, wt_id: str) -> Optional[Worktree]:
        return self.worktrees.get(wt_id)

    def list_worktrees(self) -> List[Worktree]:
        return list(self.worktrees.values())

    def update_worktree(self, wt_id: str, **kwargs) -> Optional[Worktree]:
        wt = self.worktrees.get(wt_id)
        if wt:
            for key, value in kwargs.items():
                if hasattr(wt, key):
                    setattr(wt, key, value)
            self._save_worktrees()
        return wt

    def delete_worktree(self, wt_id: str) -> bool:
        if wt_id in self.worktrees:
            del self.worktrees[wt_id]
            self._save_worktrees()
            return True
        return False

    def get_active_worktree(self) -> Optional[Worktree]:
        for wt in self.worktrees.values():
            if wt.status == "active":
                return wt
        return None
