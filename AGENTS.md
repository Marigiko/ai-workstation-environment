# AGENTS.md

## Project Overview

AI Workstation Environment — Infrastructure as Code that transforms any computer into a fully-configured AI Engineering workstation. One command (`./bootstrap`) installs all tools, configs, dotfiles, and MCP servers.

## Tech Stack

- **Language**: Python 3.10+ (core engine), Bash (component scripts, bootstrap shim)
- **Config format**: YAML (PyYAML)
- **Testing**: pytest
- **Linting**: ruff
- **CI**: GitHub Actions (ci.yml, shellcheck.yml, yaml-validation.yml)

## Project Structure

```
core/              # Python engine (detect, config, graph, component, state, dotfiles, mcp)
components/        # Each tool = isolated directory (component.yaml + check/install/uninstall.sh)
profiles/          # notebook.yaml, desktop.yaml, host.yaml, minimal.yaml
dotfiles/          # zsh, git, ssh, starship configs + manifest.yaml
mcp/               # MCP server definitions + registry
prompts/           # Organized prompt library (architecture, coding, review, etc.)
workflows/         # Composable workflow definitions (YAML)
scripts/           # Utility scripts (health-check, backup, setup-ssh-keys)
templates/         # Project templates (fastapi, scraper, rag)
configs/           # default.yaml (base config)
tests/             # pytest suite
.github/workflows/ # CI/CD
```

## Commands

```bash
# Development
pip install -e ".[dev]"
pytest tests/ -v
ruff check core/ tests/
ruff check --fix core/ tests/

# Usage
./bootstrap detect                    # Detect system environment
./bootstrap bootstrap --profile X     # Install profile (notebook|desktop|host|minimal)
./bootstrap list                      # List available components
./bootstrap status                    # Show installed components
./bootstrap update                    # Git pull + re-bootstrap
./bootstrap update-tools              # Check for component updates
./bootstrap mcp-list                  # List MCP servers
./bootstrap mcp-enable <name>         # Enable an MCP server
./bootstrap mcp-disable <name>        # Disable an MCP server
./bootstrap mcp-generate <tool>       # Generate MCP config (opencode|claude-code|zed)
```

## Conventions

### Adding a Component

Create `components/<name>/` with 4 files:

1. **`component.yaml`** — Metadata:
   ```yaml
   name: my-tool
   version: "1.0"
   description: "Description"
   platforms: [linux, darwin]
   profiles: [notebook, desktop]
   depends_on: []
   optional: false
   packages:
     apt: [my-tool]
     pacman: [my-tool]
   ```

2. **`check.sh`** — Exit 0 if installed, 1 if not
3. **`install.sh`** — Idempotent installation (check before installing)
4. **`uninstall.sh`** — Cleanup

All scripts must use `#!/usr/bin/env bash` and `set -euo pipefail`.

### Component Rules

- `install.sh` MUST be idempotent (safe to run multiple times)
- `check.sh` MUST be fast with no side effects
- Each component is self-contained — no shared state between components
- State is tracked in `.state/installed.json`

### Configuration

Three-layer merge: `configs/default.yaml` → `profiles/<profile>.yaml` → `configs/local.yaml`

### MCP Servers

Definitions in `mcp/servers/<name>.yaml`. Each has:
- `config.command`, `config.args`, optional `config.env`
- `install` and `update` shell commands

Generated configs use OpenCode format: `{ "mcp": { "<name>": { "enabled": true, "type": "local", "command": "...", "args": [...] } } }`

## Code Style

- Python: ruff (line-length 100, target py310, select E/F/I/W)
- Bash: shellcheck compliant, `set -euo pipefail`
- No comments unless explaining non-obvious intent
- Functions < 20 lines preferred
- Type hints on all Python functions

## Testing

- Tests in `tests/test_<module>.py`
- Run: `pytest tests/ -v`
- Lint: `ruff check core/ tests/`
- CI runs on Python 3.10, 3.11, 3.12

## Key Design Decisions

- **Python core + Bash shim**: Bootstrap works on bare machines (only needs Python 3.10+)
- **Symlinks for dotfiles**: Changes in repo reflect instantly
- **YAML config**: Readable, layered merge
- **One component = one directory**: Independent, testable, deletable
- **State file (`.state/installed.json`)**: Enables idempotency
- **apt/pacman**: Package managers supported (Linux), brew for macOS
