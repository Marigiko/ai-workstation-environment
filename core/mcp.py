"""MCP server management: install, enable, disable, generate configs."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml

from core.logger import log


def _expand_placeholders(value):
    """Expand {{ VAR }} placeholders used in mcp/servers/*.yaml.

    Generated configs previously contained the literal string '{{ HOME }}',
    which every MCP client treats as a path and fails on.
    """
    import os
    import re as _re

    if isinstance(value, str):
        return _re.sub(
            r'\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}',
            lambda m: os.environ.get(m.group(1).strip(), m.group(0)),
            value,
        )
    if isinstance(value, list):
        return [_expand_placeholders(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_placeholders(v) for k, v in value.items()}
    return value


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
                    "command": _expand_placeholders(config.get("command", "")),
                    "args": _expand_placeholders(config.get("args", [])),
                }
                env = config.get("env", {})
                if env:
                    server_entry["env"] = _expand_placeholders(env)
                mcp_servers[name] = server_entry

        generators = {
            "opencode": self._gen_opencode,
            "claude-code": self._gen_claude,
            "zed": self._gen_zed,
            "mimo": self._gen_mimo,
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
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.info("Generated: %s", config_file)

        commands_dir = self.config_dir / "opencode" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)

        compact_cmd = commands_dir / "compact.md"
        compact_cmd.write_text(
            "---\n"
            "description: Comprimir el contexto de la conversacion usando headroom\n"
            "---\n\n"
            "Comprime el contexto de esta conversacion usando el MCP de headroom.\n\n"
            "Identifica la informacion mas importante y descarta detalles "
            "redundantes o irrelevantes. Manten el contexto esencial para continuar "
            "trabajando efectivamente.\n",
            encoding="utf-8",
        )
        log.info("Generated: %s", compact_cmd)
        return True

    def _gen_claude(self, servers: dict) -> bool:
        """Merge MCP servers into ~/.claude.json, which is what Claude Code reads.

        This used to write ~/.config/claude/config.json in OpenCode's shape
        ({enabled, type, command, args}). Claude Code reads neither that path nor
        those keys, so the generated config had no effect. We now write the schema
        Claude Code expects (command/args/env) into ~/.claude.json, merging rather
        than replacing so the rest of that file (it holds a lot of state) survives,
        and taking a timestamped backup first.
        """
        import datetime
        import shutil
        from pathlib import Path

        # Injectable so tests never write to a real home directory.
        target = Path(os.environ.get("AWE_CLAUDE_CONFIG", Path.home() / ".claude.json"))
        claude_servers = {
            name: {
                k: v
                for k, v in (
                    ("command", entry.get("command")),
                    ("args", entry.get("args")),
                    ("env", entry.get("env")),
                )
                if v
            }
            for name, entry in servers.items()
        }

        data: dict[str, Any] = {}
        if target.exists():
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = target.with_suffix(f".json.bak.{stamp}")
            shutil.copy2(target, backup)
            log.info("Backed up %s -> %s", target, backup)
            try:
                with open(target) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                log.error("Refusing to overwrite unreadable %s: %s", target, exc)
                return False

        existing = data.get("mcpServers", {})
        existing.update(claude_servers)
        data["mcpServers"] = existing
        with open(target, "w") as f:
            json.dump(data, f, indent=2)
        log.info("Merged %d MCP servers into %s", len(claude_servers), target)
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

    def _gen_mimo(self, servers: dict) -> bool:
        config_file = self.config_dir / "mimocode" / "mimocode.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        template_path = self.project_root / "configs" / "mimo-template.json"
        if template_path.exists():
            with open(template_path) as f:
                config = json.load(f)
        else:
            config = {"$schema": "https://mimo.xiaomi.com/mimocode/config.json"}

        mimo_servers: dict[str, Any] = {}
        for name, srv in servers.items():
            cmd = srv.get("command", "")
            args = srv.get("args", [])
            if isinstance(cmd, str) and cmd:
                full_cmd = [cmd] + args
            elif isinstance(cmd, list):
                full_cmd = cmd + args
            else:
                full_cmd = args
            entry: dict[str, Any] = {
                "type": "local",
                "command": full_cmd,
                "enabled": True,
            }
            env = srv.get("env", {})
            if env:
                entry["environment"] = env
            mimo_servers[name] = entry

        config["mcp"] = mimo_servers
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
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
