"""Component lifecycle: check, install, uninstall."""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from core.logger import log
from core.state import State


@dataclass
class Component:
    name: str
    path: Path
    metadata: dict[str, Any]

    @classmethod
    def load(cls, component_dir: Path) -> "Component":
        meta_path = component_dir / "component.yaml"
        if not meta_path.exists():
            raise FileNotFoundError(f"No component.yaml in {component_dir}")
        with open(meta_path) as f:
            meta = yaml.safe_load(f)
        return cls(
            name=meta.get("name", component_dir.name),
            path=component_dir,
            metadata=meta,
        )

    @property
    def description(self) -> str:
        return self.metadata.get("description", "")

    @property
    def platforms(self) -> list[str]:
        return self.metadata.get("platforms", [])

    @property
    def profiles(self) -> list[str]:
        return self.metadata.get("profiles", [])

    @property
    def depends_on(self) -> list[str]:
        return self.metadata.get("depends_on", [])

    @property
    def optional(self) -> bool:
        return self.metadata.get("optional", False)

    def check(self) -> bool:
        check_script = self.path / "check.sh"
        if not check_script.exists():
            return False
        import os
        env = dict(os.environ)
        # Ensure PATH is set for subprocess
        if "PATH" not in env or not env["PATH"]:
            env["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        env["NVM_DIR"] = env.get("NVM_DIR", str(Path.home() / ".nvm"))
        r = subprocess.run(
            ["bash", str(check_script)],
            capture_output=True, text=True, timeout=30,
            env=env,
        )
        return r.returncode == 0

    def install(self) -> bool:
        install_script = self.path / "install.sh"
        if not install_script.exists():
            log.error("No install.sh for %s", self.name)
            return False
        log.info("Installing %s...", self.name)
        r = subprocess.run(
            ["bash", str(install_script)],
            capture_output=True, text=True, timeout=600,
        )
        if r.returncode != 0:
            log.error("Install failed for %s: %s", self.name, r.stderr)
            return False
        return True

    def uninstall(self) -> bool:
        uninstall_script = self.path / "uninstall.sh"
        if not uninstall_script.exists():
            log.warning("No uninstall.sh for %s", self.name)
            return True
        log.info("Uninstalling %s...", self.name)
        r = subprocess.run(
            ["bash", str(uninstall_script)],
            capture_output=True, text=True, timeout=300,
        )
        return r.returncode == 0


def discover_components(components_dir: Path) -> dict[str, Component]:
    if not components_dir.exists():
        return {}
    found: dict[str, Component] = {}
    for entry in sorted(components_dir.iterdir()):
        if entry.is_dir() and (entry / "component.yaml").exists():
            try:
                comp = Component.load(entry)
                found[comp.name] = comp
            except Exception as e:
                log.warning("Skipping %s: %s", entry.name, e)
    return found


def install_component(comp: Component, state: State, current_os: str) -> bool:
    if comp.platforms and current_os not in comp.platforms:
        log.info("Skipping %s (not for %s)", comp.name, current_os)
        return True

    if comp.check():
        log.info("Already installed: %s", comp.name)
        # Record it anyway: previously this returned early without touching state, so
        # pre-existing tools (git, ssh, node, python) never appeared in .state and
        # `status` under-reported reality.
        state.record(comp.name, version=comp.metadata.get("version", "unknown"), method="detected")
        return True

    if not comp.install():
        if comp.optional:
            log.info("Skipped optional component: %s", comp.name)
            return True
        return False

    # Verify installation actually succeeded
    if not comp.check():
        if comp.optional:
            log.info("Skipped optional component (not available): %s", comp.name)
            return True
        log.error("Install reported success but check failed for %s", comp.name)
        return False

    log.info("Installed %s", comp.name)
    version = comp.metadata.get("version", "unknown")
    state.record(comp.name, version=version, method="script")
    return True
