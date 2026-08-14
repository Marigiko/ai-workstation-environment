"""Tests for core.mcp module."""

import json
from pathlib import Path

import yaml

from core.mcp import MCPManager


def _setup_mcp(tmp_path: Path) -> Path:
    mcp_dir = tmp_path / "mcp"
    mcp_dir.mkdir()
    servers_dir = mcp_dir / "servers"
    servers_dir.mkdir()

    registry = {
        "servers": [
            {
                "name": "test-server", "enabled": True,
                "priority": "immediate", "description": "Test",
            },
            {
                "name": "disabled-server", "enabled": False,
                "priority": "nice-to-have", "description": "Disabled",
            },
        ]
    }
    (mcp_dir / "registry.yaml").write_text(yaml.dump(registry))

    server_def = {
        "name": "test-server",
        "config": {"command": "npx", "args": ["-y", "test"]},
    }
    (servers_dir / "test-server.yaml").write_text(yaml.dump(server_def))

    return tmp_path


def test_get_enabled_servers(tmp_path):
    root = _setup_mcp(tmp_path)
    mcp = MCPManager(root)
    enabled = mcp.get_enabled_servers()
    assert "test-server" in enabled
    assert "disabled-server" not in enabled


def test_enable_disable(tmp_path):
    root = _setup_mcp(tmp_path)
    mcp = MCPManager(root)

    assert mcp.disable("test-server")
    assert "test-server" not in mcp.get_enabled_servers()

    assert mcp.enable("test-server")
    assert "test-server" in mcp.get_enabled_servers()


def test_list_servers(tmp_path):
    root = _setup_mcp(tmp_path)
    mcp = MCPManager(root)
    servers = mcp.list_servers()
    assert len(servers) == 2
    names = [s["name"] for s in servers]
    assert "test-server" in names
    assert "disabled-server" in names


def test_generate_config_opencode(tmp_path):
    root = _setup_mcp(tmp_path)
    mcp = MCPManager(root)
    mcp.config_dir = tmp_path / ".config"
    assert mcp.generate_config("opencode")
    config_file = tmp_path / ".config" / "opencode" / "config.json"
    assert config_file.exists()
    with open(config_file) as f:
        data = json.load(f)
    assert "mcp" in data
    server = data["mcp"]["test-server"]
    assert server["enabled"] is True
    assert server["type"] == "local"
    assert server["command"] == ["npx", "-y", "test"]

    compact_cmd = tmp_path / ".config" / "opencode" / "commands" / "compact.md"
    assert compact_cmd.exists()
    content = compact_cmd.read_text()
    assert "description:" in content
    assert "headroom" in content


def test_generate_config_claude(tmp_path, monkeypatch):
    """Claude Code reads ~/.claude.json, so the generator must merge into that file.

    Previously it wrote ~/.config/claude/config.json in OpenCode's shape
    ({enabled, type, ...}), which Claude Code never reads - the config had no effect.
    AWE_CLAUDE_CONFIG keeps this test off the real home directory.
    """
    import json as _json

    root = _setup_mcp(tmp_path)
    target = tmp_path / "claude.json"
    target.write_text(_json.dumps({"keepMe": True, "mcpServers": {"old": {"command": "x"}}}))
    monkeypatch.setenv("AWE_CLAUDE_CONFIG", str(target))

    mgr = MCPManager(root)
    assert mgr.generate_config("claude-code")

    data = _json.loads(target.read_text())
    # unrelated keys and pre-existing servers must survive the merge
    assert data["keepMe"] is True
    assert "old" in data["mcpServers"]
    # and the generated entries use Claude Code's schema, not OpenCode's
    for entry in data["mcpServers"].values():
        assert "enabled" not in entry
        assert "type" not in entry

def test_generate_config_zed(tmp_path):
    root = _setup_mcp(tmp_path)
    mcp = MCPManager(root)
    mcp.config_dir = tmp_path / ".config"
    assert mcp.generate_config("zed")
    config_file = tmp_path / ".config" / "zed" / "settings.json"
    assert config_file.exists()


def test_generate_config_mimo(tmp_path, monkeypatch):
    """mimo/mimo-new use McpLocalConfig: a single command ARRAY plus `environment`.

    Emitting OpenCode's entry shape (command string + separate args, `env`) made
    mimo-new reject every server with "Configuration is invalid ... Invalid input
    mcp.<name>". The SDK type is:
        McpLocalConfig = { type: "local"; command: Array<string>; environment?: {...} }
    """
    import json as _json

    root = _setup_mcp(tmp_path)
    target = tmp_path / "mimocode.json"
    target.write_text(_json.dumps({"model": "keep-me", "mcp": {"old": {"enabled": True}}}))
    monkeypatch.setenv("AWE_MIMO_CONFIG", str(target))

    mgr = MCPManager(root)
    assert mgr.generate_config("mimo")

    data = _json.loads(target.read_text())
    assert data["model"] == "keep-me"          # unrelated keys survive the merge
    assert "old" in data["mcp"]                # pre-existing entries survive
    for name, entry in data["mcp"].items():
        if name == "old":
            continue
        assert entry["type"] == "local"
        assert isinstance(entry["command"], list)   # never a bare string
        assert "args" not in entry
        assert "env" not in entry


def test_generate_config_mimo_with_template(tmp_path, monkeypatch):
    """Placeholders like {{ HOME }} must be expanded inside the command array too."""

    root = _setup_mcp(tmp_path)
    target = tmp_path / "mimocode2.json"
    monkeypatch.setenv("AWE_MIMO_CONFIG", str(target))
    monkeypatch.setenv("HOME", str(tmp_path))

    mgr = MCPManager(root)
    assert mgr.generate_config("mimo")
    blob = target.read_text()
    assert "{{ HOME }}" not in blob
    assert "{{" not in blob
