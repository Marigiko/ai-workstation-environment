# AI Engineering Platform - Architecture

## Overview

The AI Engineering Platform is a distributed system that combines:
- **ai-workstation**: Core platform with routing, context, memory, and evaluation
- **ai-workstation-environment**: Infrastructure components and tools
- **Telegram Bot**: Mobile interface for task management
- **Auto Orchestrator**: Multi-agent task planning and execution
- **Hermes Agent**: Mobile client for notifications and commands

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Terax   │  │ Telegram │  │  Hermes  │  │   Web    │  │
│  │ (Desktop)│  │ (Mobile) │  │ (Mobile) │  │  (UI)    │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼──────────────┼──────────────┼──────────────┼────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    GATEWAY LAYER                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ai-workstation Gateway (FastAPI :8000)              │   │
│  │  PipelineService → Context → Memory → Routing → LLM │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Workspace API (FastAPI :8080)                       │   │
│  │  Sessions · Tasks · Workflows · Notifications        │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  n8n (Port 5678)                                    │   │
│  │  Telegram Bot · Workflow Automation                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Auto Orchestrator                                   │   │
│  │  Plan → Decompose → Distribute → Aggregate          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  MiMo    │  │ Claude   │  │  Agent   │                 │
│  │  Code    │  │  Code    │  │ Registry │                 │
│  └────┬─────┘  └────┬─────┘  └──────────┘                 │
└───────┼──────────────┼─────────────────────────────────────┘
        │              │
        ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ OmniRoute│  │ Ollama   │  │   RAG    │  │   MCP    │  │
│  │ Gateway  │  │ Local    │  │  Engine  │  │  Tools   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Telegram Command Flow
```
1. User sends /prompt "Create a hello world app" via Telegram
2. Telegram Bot receives message
3. Bot sends to n8n webhook
4. n8n creates task in Workspace API
5. Auto Orchestrator picks up task
6. Architect agent plans (qwen2.5-coder:7b)
7. Task decomposed into subtasks
8. Subtasks distributed to agents:
   - Coder → qwen2.5-coder:7b
   - Reviewer → gemini-2.5-flash
   - Documenter → qwen2.5-coder:1.5b
9. Agents execute via MiMo/ai-workstation
10. Results aggregated
11. Notification sent back via Telegram
```

### Worktree Isolation
```
Worktree 1: /mnt/d/Projects/project-a
├── Git repo A
├── Session A
├── Model: qwen2.5-coder:7b
└── Agent: coder

Worktree 2: /mnt/d/Projects/project-b
├── Git repo B
├── Session B
├── Model: gemini-2.5-flash
└── Agent: reviewer
```

## Configuration Files

| File | Purpose |
|------|---------|
| `configs/auto-mode.yaml` | Auto orchestrator settings |
| `configs/serena.yaml` | Optimal efficiency settings |
| `configs/worktrees.yaml` | Worktree defaults |
| `components/telegram-bot/config/bot.yaml` | Telegram bot config |
| `components/hermes/config/config.yaml` | Hermes connection |
| `components/omniroute/` | OmniRoute gateway (Docker Compose) |
| `components/workspace/docker-compose.yaml` | Workspace services |

## API Endpoints

### Gateway (:8000)
- `POST /chat` - Pipeline chat
- `POST /v1/chat/completions` - OpenAI-compatible
- `GET /v1/models` - List models
- `POST /sessions` - Create session
- `POST /skills/{name}/execute` - Execute skill

### Workspace (:8080)
- `POST /workspaces` - Create workspace
- `POST /sessions` - Create session
- `POST /tasks` - Create task
- `POST /tasks/{id}/approve` - Approve task
- `GET /notifications` - List notifications
- `WS /ws` - Real-time events

### Telegram Bot
- `/prompt <text>` - Send task
- `/status` - System status
- `/approve <id>` - Approve task
- `/commit <msg>` - Git commit
- `/worktrees` - List worktrees
- `/model <name>` - Switch model
- `/agent <name>` - Switch agent
- `/auto` - Toggle auto mode
