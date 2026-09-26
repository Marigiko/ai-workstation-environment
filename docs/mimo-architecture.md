# Mimo como Frontend de AI Engineering Platform

> Historical document (written before 2026-09-25). LiteLLM was later replaced by OmniRoute (http://localhost:20128/v1); see docs/INTEGRATION-ARCHITECTURE.md for the current setup.

## Analisis de Capacidades de Mimo

| Capacidad | Soporte | Notas |
|---|---|---|
| **MCP** | Completo | Local + Remote, OAuth, per-agent |
| **OpenAI Compatible** | Nativo | Via `@ai-sdk/openai-compatible` |
| **LiteLLM** | Directo | LiteLLM expone OpenAI-compatible API |
| **Modelos locales (Ollama)** | Via proxy | A traves de LiteLLM o directo |
| **Skills** | SKILL.md | Frontmatter YAML, descubrimiento recursivo |
| **Agentes custom** | JSON + Markdown | Prompts, modelos, tools, permisos |
| **Custom Tools** | TypeScript | `.mimocode/tools/`, puede invocar cualquier lenguaje |
| **Persistent Memory** | SQLite FTS5 | MEMORY.md, checkpoints, dream/distill |
| **Compose Mode** | Specs-driven | Orquestacion de workflows |
| **Subagentes** | Paralelos | Task tracking, cancelacion |
| **Dream/Distill** | Self-improvement | Extrae conocimiento y skills de uso |
| **Plugins** | npm/local | Extensible |
| **Rules** | AGENTS.md + instructions | Multi-source |
| **Custom Commands** | Templates | Para tareas repetitivas |
| **75+ providers** | AI SDK | Todos los principales |
| **Voice** | TenVAD + ASR | Streaming |
| **LSP** | Integrado | Language servers |
| **RAG nativo** | No | Pero MCP puede cubrirlo |

## Que es Mimo

- **Nombre**: Xiaomi MiMo Code (MiMoCode)
- **Tipo**: CLI tool (terminal-native AI coding assistant)
- **Base**: Fork de OpenCode
- **GitHub**: https://github.com/XiaomiMiMo/MiMo-Code
- **npm**: `@mimo-ai/cli`
- **Docs**: https://mimo.xiaomi.com/mimocode/start
- **Licencia**: MIT

## Diferencias con OpenCode

Mimo anade sobre OpenCode:
- Persistent memory (SQLite FTS5)
- Intelligent context management (checkpoints automaticos)
- Subagent orchestration
- Goal-driven autonomous loops
- Compose workflows (specs-driven development)
- Self-improvement via dream/distill
- Voice input (TenVAD + MiMo ASR)
- Task tracking (tree-shaped: T1, T1.1, T1.2)
- Session checkpoints

## Configuracion

### Archivos

| Archivo | Project-level | Global |
|---|---|---|
| Main config | `.mimocode/mimocode.jsonc` | `~/.config/mimocode/mimocode.json` |
| TUI config | `.mimocode/tui.json` | `~/.config/mimocode/tui.json` |
| Auth | - | `~/.local/share/mimocode/auth.json` |

### Schema

```jsonc
{ "$schema": "https://mimo.xiaomi.com/mimocode/config.json" }
```

### Variables

- `{env:VAR}` - reemplazado con env var (vacio si no existe)
- `{file:path}` - contenido de archivo (relativo al config o absoluto)

## MCP en Mimo

### Formato Local

```jsonc
{
  "mcp": {
    "server-name": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-command"],
      "enabled": true,
      "environment": { "MY_VAR": "value" }
    }
  }
}
```

### Formato Remote

```jsonc
{
  "mcp": {
    "server-name": {
      "type": "remote",
      "url": "https://my-mcp-server.com",
      "enabled": true,
      "headers": { "Authorization": "Bearer TOKEN" }
    }
  }
}
```

### OAuth

- Deteccion automatica de 401
- Dynamic Client Registration (RFC 7591)
- `mimo mcp auth <server>` para autenticar manualmente
- `mimo mcp logout <server>` para limpiar credenciales

## Agentes

### Built-in

| Agente | Tipo | Descripcion |
|---|---|---|
| build | primary | Default. Full tool permissions |
| plan | primary | Read-only analysis |
| general | subagent | Multi-step tasks, parallel work |
| explore | subagent | Fast read-only codebase exploration |

### Custom (JSON)

```jsonc
{
  "agent": {
    "reviewer": {
      "description": "Code review specialist",
      "mode": "subagent",
      "model": "litellm/claude-sonnet",
      "prompt": "You are a code reviewer...",
      "permission": { "edit": "deny", "bash": "deny" }
    }
  }
}
```

### Custom (Markdown)

```markdown
---
description: Code review specialist
mode: subagent
model: litellm/claude-sonnet
permission:
  edit: deny
  bash: deny
---

You are a code reviewer...
```

## Skills

- Ubicacion: `.mimocode/skills/**/SKILL.md` o `~/.config/mimocode/skills/**/SKILL.md`
- Compatibilidad: `.claude/`, `.agents/`, `.codex/`, `.opencode/`
- Frontmatter YAML: `name` (required), `description` (required), `hidden` (optional)
- Carga on-demand via tool `skill`

## Custom Tools

- Ubicacion: `.mimocode/tools/` o `~/.config/mimocode/tools/`
- Lenguaje: TypeScript/JavaScript (definicion), cualquier lenguaje (implementacion)
- Helper: `import { tool } from "@mimocode/cli/plugin"`
- El filename se convierte en tool name

## Compose Mode

Workflow estructurado para specs-driven development:
- Built-in skills: planning, execution, code review, TDD, debugging, verification, merging
- Orquesta el ciclo completo desde spec hasta shipped code

## Dream & Distill

- `/dream` - Extrae conocimiento persistente de sesiones recientes a project memory
- `/distill` - Detecta workflows repetitivos y los empaqueta en skills/subagents/commands
