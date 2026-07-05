"""MCP server management: install, enable, disable, generate configs."""

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from core.logger import log


class MCPManager:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.registry_path = project_root / "mcp" / "registry.yaml"
        self.servers_dir = project_root / "mcp" / "servers"
        self.config_dir = Path.home() / ".config"

    def load_registry(self) -> dict[str, Any]:
        if not self.registry_path.exists():
            return {"servers": []}
        with open(self.registry_path) as f:
            return yaml.safe_load(f) or {"servers": []}

    def save_registry(self, data: dict[str, Any]) -> None:
        with open(self.registry_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    def get_enabled_servers(self) -> list[str]:
        registry = self.load_registry()
        return [
            s["name"]
            for s in registry.get("servers", [])
            if s.get("enabled", False)
        ]

    def get_server_def(self, name: str) -> dict[str, Any] | None:
        server_file = self.servers_dir / f"{name}.yaml"
        if not server_file.exists():
            return None
        with open(server_file) as f:
            return yaml.safe_load(f)

    def enable(self, name: str) -> bool:
        registry = self.load_registry()
        for server in registry.get("servers", []):
            if server["name"] == name:
                server["enabled"] = True
                self.save_registry(registry)
                log.info("Enabled MCP: %s", name)
                return True
        log.error("MCP not found in registry: %s", name)
        return False

    def disable(self, name: str) -> bool:
        registry = self.load_registry()
        for server in registry.get("servers", []):
            if server["name"] == name:
                server["enabled"] = False
                self.save_registry(registry)
                log.info("Disabled MCP: %s", name)
                return True
        log.error("MCP not found in registry: %s", name)
        return False

    def install_server(self, name: str) -> bool:
        server_def = self.get_server_def(name)
        if not server_def:
            log.error("MCP definition not found: %s", name)
            return False

        install_cmd = server_def.get("install", "")
        if not install_cmd:
            log.info("No install command for %s", name)
            return True

        log.info("Installing MCP: %s", name)
        r = subprocess.run(
            ["bash", "-c", install_cmd],
            capture_output=True, text=True, timeout=300,
        )
        if r.returncode != 0:
            log.error("Install failed for %s: %s", name, r.stderr)
            return False
        return True

    def generate_config(self, tool: str) -> bool:
        enabled = self.get_enabled_servers()
        if not enabled:
            log.warning("No MCP servers enabled")
            return False

        mcp_servers: dict[str, Any] = {}
        for name in enabled:
            server_def = self.get_server_def(name)
            if not server_def:
                continue
            config = server_def.get("config", {})
            if config:
                server_entry: dict[str, Any] = {
                    "enabled": True,
                    "type": "local",
                    "command": config.get("command", ""),
                    "args": config.get("args", []),
                }
                env = config.get("env", {})
                if env:
                    server_entry["env"] = env
                mcp_servers[name] = server_entry

        generators = {
            "opencode": self._gen_opencode,
            "claude-code": self._gen_claude,
            "zed": self._gen_zed,
        }

        gen = generators.get(tool)
        if not gen:
            log.error("Unknown tool: %s", tool)
            return False

        return gen(mcp_servers)

    def _gen_opencode(self, servers: dict) -> bool:
        config_file = self.config_dir / "opencode" / "config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"mcp": servers}
        with open(config_file, "w") as f:
            json.dump(data, f, indent=2)
        log.info("Generated: %s", config_file)
        return True

    def _gen_claude(self, servers: dict) -> bool:
        config_file = self.config_dir / "claude" / "config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"mcpServers": servers}
        with open(config_file, "w") as f:
            json.dump(data, f, indent=2)
        log.info("Generated: %s", config_file)
        return True

    def _gen_zed(self, servers: dict) -> bool:
        config_file = self.config_dir / "zed" / "settings.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        existing: dict = {}
        if config_file.exists():
            with open(config_file) as f:
                existing = json.load(f)

        existing["context_servers"] = servers
        with open(config_file, "w") as f:
            json.dump(existing, f, indent=2)
        log.info("Generated: %s", config_file)
        return True

    def list_servers(self) -> list[dict[str, Any]]:
        registry = self.load_registry()
        result = []
        for server in registry.get("servers", []):
            name = server["name"]
            server_def = self.get_server_def(name)
            result.append({
                "name": name,
                "enabled": server.get("enabled", False),
                "priority": server.get("priority", "unknown"),
                "description": server.get("description", ""),
                "version": server_def.get("version", "unknown") if server_def else "unknown",
            })
        return result
