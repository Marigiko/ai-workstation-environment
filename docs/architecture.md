# Architecture

## Bounded Contexts

| Context | Responsibility |
|---------|---------------|
| **Core** | Engine: detection, dependency graph, idempotency, logging |
| **Components** | Atomic installable units (each tool, each config) |
| **Profiles** | Declarative component selection per machine type |
| **Dotfiles** | Personal config file management (shell, git, SSH) |
| **MCP** | MCP server lifecycle (install/update/enable/disable) |
| **Prompts** | Categorized library of reusable prompts |
| **Workflows** | Composable workflows (prompt + tools + MCPs + context) |
| **Configs** | Global declarative configuration layer (YAML) |
| **Templates** | Project templates (fastapi, scraper, etc.) |
| **Self-Update** | Environment and tool updates |

## Component Model

Every installable unit follows the same interface:

```
components/<name>/
├── component.yaml    # Metadata: deps, platforms, version
├── install.sh        # Idempotent installation
├── check.sh          # Exit 0 = installed, 1 = missing
└── uninstall.sh      # Cleanup
```

## Configuration Layers

1. `configs/default.yaml` — Base (versioned in git)
2. `profiles/<profile>.yaml` — Profile overrides
3. `configs/local.yaml` — Local machine overrides (gitignored)

Merge order: default → profile → local (later overrides earlier)

## Dependency Resolution

Components declare dependencies in `component.yaml`:

```yaml
depends_on: [git, node]
```

The engine performs topological sort to ensure correct installation order.

## State Tracking

Installation state is stored in `.state/installed.json`:

```json
{
  "git": {
    "version": "2.40",
    "installed_at": "2026-07-04T10:00:00Z",
    "method": "apt"
  }
}
```

This enables idempotency: `check.sh` is called before `install.sh`.
