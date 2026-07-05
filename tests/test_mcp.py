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
    assert server["command"] == "npx"


def test_generate_config_claude(tmp_path):
    root = _setup_mcp(tmp_path)
    mcp = MCPManager(root)
    mcp.config_dir = tmp_path / ".config"
    assert mcp.generate_config("claude-code")
    config_file = tmp_path / ".config" / "claude" / "config.json"
    assert config_file.exists()


def test_generate_config_zed(tmp_path):
    root = _setup_mcp(tmp_path)
    mcp = MCPManager(root)
    mcp.config_dir = tmp_path / ".config"
    assert mcp.generate_config("zed")
    config_file = tmp_path / ".config" / "zed" / "settings.json"
    assert config_file.exists()
