# Diseno: Mimo + AI Engineering Platform

> Historical document (written before 2026-09-25). LiteLLM was later replaced by OmniRoute (http://localhost:20128/v1); see docs/INTEGRATION-ARCHITECTURE.md for the current setup.

## Arquitectura

```
+---------------------------------------------------------+
|                    MIMO (Frontend)                       |
|  +----------+  +----------+  +----------+  +---------+  |
|  |  Build    |  |  Plan    |  | Compose  |  | Custom  |  |
|  |  Agent    |  |  Agent   |  |  Mode    |  | Agents  |  |
|  +----+-----+  +----+-----+  +----+-----+  +----+----+  |
|       |              |             |              |       |
|  +----+--------------+-------------+--------------+----+ |
|  |              MCP Client Layer                       | |
|  |  filesystem | git | github | headroom | memory | ...| |
|  +-----------------------+-----------------------------+ |
|                          |                               |
|  +-----------------------+-----------------------------+ |
|  |           Skills | Custom Tools | Rules             | |
|  +-----------------------+-----------------------------+ |
+--------------------------+--------------------------------+
                           | OpenAI-compatible API
                           v
+----------------------------------------------------------+
|              LITELLM (Model Router)                       |
|              http://localhost:4000/v1                     |
|                                                          |
|  +---------+ +----------+ +-----------+ +------------+   |
|  |  Ollama  | | Anthropic| |  OpenAI   | | OpenRouter |   |
|  | (local)  | | (Claude) | |  (GPT)    | |  (fallback)|   |
|  +---------+ +----------+ +-----------+ +------------+   |
|                                                          |
|  +---------+ +----------+                               |
|  | Gemini  | |  Custom  |                               |
|  |         | | Provider |                               |
|  +---------+ +----------+                               |
+----------------------------------------------------------+
                           |
+--------------------------+--------------------------------+
|           AI WORKSTATION PLATFORM (Backend)              |
|                                                          |
|  +----------+  +----------+  +----------+  +---------+   |
|  | Qdrant   |  |   n8n    |  |PostgreSQL|  | Docker  |   |
|  | (vector) |  | (workflow)|  |  (data)  |  | (infra) |   |
|  +----------+  +----------+  +----------+  +---------+   |
|                                                          |
|  +--------------------------------------------------+   |
|  |  MCP Servers (filesystem, git, github, headroom,  |   |
|  |  codebase-memory, ponytail, docker, postgres,     |   |
|  |  playwright, sequential-thinking, browser)         |   |
|  +--------------------------------------------------+   |
|                                                          |
|  +--------------------------------------------------+   |
|  |  Prompts | Workflows | Templates | Dotfiles       |   |
|  +--------------------------------------------------+   |
+----------------------------------------------------------+
```

## Flujo de Datos

```
Usuario -> Mimo TUI
  -> Agente (Build/Plan/Compose/Custom)
    -> Skill cargada si aplica
    -> MCP tools disponibles
    -> Custom tools si needed
      |
  LiteLLM (localhost:4000)
    -> Model routing por nombre
      -> Claude Sonnet (tareas complejas)
      -> GPT-4 (reasoning)
      -> Ollama/local (privacidad, velocidad)
      -> OpenRouter (fallback, modelos exoticos)
      -> Gemini (multimodal)
    |
  Respuesta -> Mimo renderiza
    -> Checkpoint guardado
    -> Memory actualizada
    -> Task progress logged
```

## Configuracion Ideal de Mimo

### Global: `~/.config/mimocode/mimocode.json`

```jsonc
{
  "$schema": "https://mimo.xiaomi.com/mimocode/config.json",
  "model": "litellm/claude-sonnet-4-20250514",
  "small_model": "litellm/ollama",
  "provider": {
    "litellm": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LiteLLM Gateway",
      "options": {
        "baseURL": "http://localhost:4000/v1",
        "apiKey": "${LITELLM_API_KEY}"
      },
      "models": {
        "claude-sonnet-4-20250514": { "name": "Claude Sonnet 4" },
        "gpt-4": { "name": "GPT-4" },
        "ollama": { "name": "Ollama Local" }
      }
    }
  },
  "disabled_providers": ["openai", "google", "openrouter"],
  "default_agent": "build",
  "mcp": {
    "filesystem": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "{env:HOME}"],
      "enabled": true
    },
    "git": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-git"],
      "enabled": true
    },
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "enabled": true,
      "environment": { "GITHUB_TOKEN": "{env:GITHUB_TOKEN}" }
    },
    "headroom": {
      "type": "local",
      "command": ["npx", "-y", "@headroom/mcp-server"],
      "enabled": true
    },
    "codebase-memory": {
      "type": "local",
      "command": ["npx", "-y", "@codebase-memory/mcp-server"],
      "enabled": true
    },
    "ponytail": {
      "type": "local",
      "command": ["npx", "-y", "@ponytail/mcp-server"],
      "enabled": true
    },
    "docker": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-docker"],
      "enabled": true
    },
    "sequential-thinking": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sequential-thinking"],
      "enabled": true
    }
  },
  "skills": {
    "paths": ["~/.config/mimocode/skills/", "{env:HOME}/.opencode/skills/"]
  },
  "instructions": ["AGENTS.md"],
  "compaction": { "auto": true, "prune": true, "tail_turns": 3 },
  "permission": { "bash": "allow", "edit": "allow" },
  "command": {
    "review": {
      "template": "Review this PR comprehensively.",
      "description": "Full PR review",
      "agent": "build"
    },
    "debug": {
      "template": "Systematically debug this issue.",
      "description": "Systematic debugging",
      "agent": "build"
    },
    "test": {
      "template": "Generate comprehensive tests.",
      "description": "Generate tests",
      "agent": "build"
    },
    "doc": {
      "template": "Generate documentation.",
      "description": "Generate docs",
      "agent": "build"
    },
    "architect": {
      "template": "Analyze architecture. Do NOT make changes.",
      "description": "Architecture analysis",
      "agent": "plan"
    },
    "benchmark": {
      "template": "Benchmark models.",
      "description": "Model benchmark",
      "agent": "build"
    }
  },
  "autoupdate": "notify",
  "share": "manual"
}
```

## LiteLLM Model Router Enhanced

```yaml
model_list:
  - model_name: local
    litellm_params:
      model: ollama/llama3
      api_base: http://host.docker.internal:11434
  - model_name: claude-sonnet
    litellm_params:
      model: claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: claude-opus
    litellm_params:
      model: claude-opus-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: os.environ/OPENAI_API_KEY
  - model_name: openrouter/auto
    litellm_params:
      model: openrouter/auto
      api_key: os.environ/OPENROUTER_API_KEY
  - model_name: gemini
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: os.environ/GEMINI_API_KEY
  - model_name: fast
    litellm_params:
      model: ollama/llama3
      api_base: http://host.docker.internal:11434
  - model_name: smart
    litellm_params:
      model: claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: reasoning
    litellm_params:
      model: gpt-4
      api_key: os.environ/OPENAI_API_KEY

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
```

## Agentes Custom

| Agent | Tipo | Modelo | Proposito |
|---|---|---|---|
| `security-auditor.md` | subagent | claude-sonnet | Auditoria de seguridad |
| `docs-writer.md` | subagent | ollama | Documentacion (modelo local) |
| `perf-analyzer.md` | subagent | claude-sonnet | Analisis de rendimiento |
| `tdd-driver.md` | subagent | gpt-4 | TDD estricto |
| `refactor.md` | subagent | claude-sonnet | Refactoring seguro |
| `infra.md` | subagent | gpt-4 | Infraestructura y Docker |

## Skills (migrados de prompts)

```
~/.config/mimocode/skills/
  architecture/
    system-design/SKILL.md
    component-design/SKILL.md
    tradeoff-analysis/SKILL.md
  coding/
    clean-implementation/SKILL.md
    refactoring/SKILL.md
    pattern-implementation/SKILL.md
  review/
    code-review/SKILL.md
    pr-review/SKILL.md
    security-audit/SKILL.md
  planning/
    project-planning/SKILL.md
    sprint-planning/SKILL.md
    task-estimation/SKILL.md
  debug/
    systematic-debugging/SKILL.md
    performance-debugging/SKILL.md
    log-analysis/SKILL.md
  documentation/
    readme-generation/SKILL.md
    api-documentation/SKILL.md
    inline-documentation/SKILL.md
  security/
    threat-modeling/SKILL.md
    secure-coding-review/SKILL.md
  platform/
    litellm-routing/SKILL.md
    mcp-debugging/SKILL.md
    component-creation/SKILL.md
    workflow-execution/SKILL.md
```

## Custom Tools

| Tool | Funcion |
|---|---|
| `model-router.ts` | Switch modelo en-session via LiteLLM API |
| `health-check.ts` | Verificar estado de todos los servicios |
| `workflow-runner.ts` | Ejecutar workflows de la plataforma |
| `benchmark.ts` | Benchmark entre modelos |
| `context-injector.ts` | Inyectar contexto RAG desde Qdrant |

## Workflows -> Compose Mode

| Workflow | Mimo Compose Skill |
|---|---|
| `create-fastapi-project` | `/compose fastapi` |
| `create-scraper` | `/compose scraper` |
| `review-pr` | `/compose pr-review` |
| `generate-tests` | `/compose tests` |
| `create-rag` | `/compose rag-pipeline` |
| `debug-python` | `/compose debug` |
