# AI Workstation Environment

[![CI](https://github.com/YOUR_USERNAME/ai-workstation-environment/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/ai-workstation-environment/actions/workflows/ci.yml)

Infrastructure as Code for AI Engineering workstations. Transform any computer into a fully-configured professional AI development environment.

## Features

- **Idempotent bootstrap**: Run `./bootstrap` on any machine — it only installs what's missing
- **Profile-based**: Different setups for notebook, desktop, host, or minimal
- **Modular components**: Each tool (git, docker, zed, opencode, etc.) is independently installable
- **Declarative configuration**: YAML-based config with layered overrides
- **Dotfiles management**: Manifest-driven symlinks for shell, git, editor configs
- **MCP management**: Install, enable, disable MCP servers for AI tools
- **Prompts library**: Organized collection of reusable prompts
- **Workflows**: Composable workflow definitions for common tasks
- **Self-update**: Update the environment and tools with one command
- **Dependency resolution**: Automatic topological sort of component dependencies

## Quick Start

```bash
git clone <this-repo> ~/ai-workstation-environment
cd ~/ai-workstation-environment
./bootstrap --profile notebook
```

## Commands

```bash
./bootstrap detect                    # Show detected environment
./bootstrap bootstrap --profile X     # Install profile (notebook|desktop|host|minimal)
./bootstrap list                      # List available components
./bootstrap status                    # Show installed components
./bootstrap bootstrap --only git      # Install single component
./bootstrap update                    # Update environment (git pull + re-bootstrap)
./bootstrap update-tools              # Check for component updates
./bootstrap mcp-list                  # List MCP servers
./bootstrap mcp-enable <name>         # Enable an MCP server
./bootstrap mcp-disable <name>        # Disable an MCP server
./bootstrap mcp-generate <tool>       # Generate MCP config (opencode|claude-code|zed)
```

## Profiles

| Profile | Use Case | Components |
|---------|----------|------------|
| `notebook` | Laptop AI dev | git, ssh, node, python, zed, opencode, claude-code, terax, tailscale, docker |
| `desktop` | Workstation AI dev | notebook + rust, vscode |
| `host` | Infrastructure server | git, ssh, docker, tailscale, node, python, ollama, omniroute, qdrant, postgresql, n8n |
| `minimal` | Bare minimum | git, ssh |

## Components

| Component | Description | Platforms |
|-----------|-------------|-----------|
| `git` | Version control | linux, darwin |
| `ssh` | OpenSSH client/server | linux, darwin |
| `node` | Node.js via nvm | linux, darwin |
| `python` | Python 3.x | linux, darwin |
| `rust` | Rust via rustup | linux, darwin |
| `docker` | Docker Engine + Compose | linux |
| `tailscale` | VPN client | linux, darwin |
| `zed` | Zed editor | linux, darwin |
| `vscode` | Visual Studio Code (optional) | linux, darwin |
| `opencode` | OpenCode AI assistant | linux, darwin |
| `claude-code` | Claude Code AI assistant | linux, darwin |
| `terax` | Terax AI-native terminal (optional) | linux, darwin |
| `ollama` | Local LLM runner (Docker) | linux |
| `omniroute` | Unified OpenAI-compatible LLM gateway (Docker Compose) | linux |
| `qdrant` | Vector database (Docker) | linux |
| `postgresql` | PostgreSQL database (Docker) | linux |
| `n8n` | Workflow automation (Docker) | linux |

## MCP Management

```bash
./bootstrap mcp-list                    # List all MCP servers
./bootstrap mcp-enable docker           # Enable an MCP server
./bootstrap mcp-disable docker          # Disable an MCP server
./bootstrap mcp-generate opencode       # Generate MCP config for AI tool
./bootstrap bootstrap --generate-mcp    # Generate configs during bootstrap
```

## Prompts Library

Organized collection of reusable prompts in `prompts/`:

| Category | Prompts |
|----------|---------|
| `architecture/` | system-design, tradeoff-analysis, component-design |
| `coding/` | clean-implementation, refactoring, pattern-implementation |
| `review/` | code-review, pr-review, security-audit |
| `planning/` | project-planning, task-estimation, sprint-planning |
| `debug/` | systematic-debugging, log-analysis, performance-debugging |
| `documentation/` | readme-generation, api-documentation, inline-documentation |
| `security/` | threat-modeling, secure-coding-review |

## Workflows

Composable workflows in `workflows/`:

| Workflow | Description |
|----------|-------------|
| `create-fastapi-project` | Scaffold a production-ready FastAPI project |
| `create-scraper` | Build a robust web scraper |
| `review-pr` | Comprehensive pull request review |
| `generate-tests` | Generate test suite for existing code |
| `create-rag` | Set up a RAG pipeline |
| `debug-python` | Systematic Python debugging |

## Scripts

Utility scripts in `scripts/`:

| Script | Description |
|--------|-------------|
| `health-check.sh` | Verify all components are working |
| `setup-ssh-keys.sh` | Generate and configure SSH keys |
| `backup.sh` | Backup configs and state |

## OpenCode Commands

Custom slash commands for OpenCode (auto-generated during bootstrap):

| Command | Description |
|---------|-------------|
| `/compact` | Compress conversation context using headroom MCP |

These commands are defined as markdown files in `~/.config/opencode/commands/` and generated automatically when running:

```bash
./bootstrap mcp-generate opencode
```

## Architecture

```
ai-workstation-environment/
├── bootstrap              # Bash shim → Python venv → core
├── TERAX.md               # Terax workspace memory (project-level)
├── core/                  # Python engine
│   ├── detect.py          # System detection (OS, WSL, GPU, Docker, etc.)
│   ├── config.py          # Layered YAML config merge
│   ├── graph.py           # Dependency resolution (topological sort)
│   ├── component.py       # Component lifecycle (check/install/uninstall)
│   ├── state.py           # Installation state tracking
│   ├── dotfiles.py        # Manifest-driven symlink engine
│   ├── mcp.py             # MCP server management
│   └── main.py            # CLI entry point
├── components/            # Each tool = isolated directory
│   └── <name>/
│       ├── component.yaml # Metadata, deps, platforms
│       ├── check.sh       # Is it installed?
│       ├── install.sh     # Idempotent install
│       └── uninstall.sh   # Cleanup
├── profiles/              # notebook.yaml, desktop.yaml, host.yaml, minimal.yaml
├── dotfiles/              # zsh, git, ssh, starship configs + manifest.yaml
├── mcp/                   # MCP server definitions + registry
├── prompts/               # Organized prompt library
├── workflows/             # Composable workflow definitions
├── scripts/               # Utility scripts
├── templates/             # Project templates
├── configs/               # default.yaml (base config)
└── tests/                 # pytest suite
```

## Adding a Component

Create `components/<name>/` with:

```yaml
# component.yaml
name: my-tool
version: "1.0"
description: "My awesome tool"
platforms: [linux, darwin]
profiles: [notebook, desktop]
depends_on: [git]
optional: false
```

```bash
#!/usr/bin/env bash
# check.sh
command -v my-tool &>/dev/null
```

```bash
#!/usr/bin/env bash
# install.sh
set -euo pipefail
# ... idempotent installation logic
```

## Configuration

Three-layer config merge:

1. `configs/default.yaml` — base (versioned)
2. `profiles/<profile>.yaml` — profile overrides
3. `configs/local.yaml` — local machine overrides (gitignored)

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check core/ tests/
```

## CI/CD

The project includes GitHub Actions workflows for automated testing and validation:

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `ci.yml` | Push/PR to main | Run tests on Python 3.10, 3.11, 3.12 + linting |
| `shellcheck.yml` | Push/PR (shell scripts) | Validate bash scripts with shellcheck |
| `yaml-validation.yml` | Push/PR (YAML files) | Validate all YAML files are well-formed |
| `release.yml` | Tag push (v*) | Build and publish release artifacts |

All workflows run automatically on push and pull requests to ensure code quality.

## Requirements

- Python >= 3.10
- Linux, macOS, or WSL
- Bash

## License

MIT