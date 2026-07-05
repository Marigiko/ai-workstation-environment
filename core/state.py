"""State tracking: what's installed, when, which version."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.logger import log


class State:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_file = state_dir / "installed.json"
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self.state_file.exists():
            with open(self.state_file) as f:
                self._data = json.load(f)
        else:
            self._data = {}

    def save(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self._data, f, indent=2)

    def is_installed(self, name: str) -> bool:
        return name in self._data

    def get(self, name: str) -> dict[str, Any] | None:
        return self._data.get(name)

    def record(
        self,
        name: str,
        version: str = "unknown",
        method: str = "unknown",
    ) -> None:
        self._data[name] = {
            "version": version,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "method": method,
        }
        self.save()
        log.info("Recorded install: %s (v%s)", name, version)

    def remove(self, name: str) -> None:
        if name in self._data:
            del self._data[name]
            self.save()
            log.info("Removed state: %s", name)

    def list_installed(self) -> dict[str, Any]:
        return self._data.copy()
