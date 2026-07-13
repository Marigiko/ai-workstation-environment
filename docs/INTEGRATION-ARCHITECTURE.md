# AI Engineering Platform — Complete Integration Architecture

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Complete Architecture Diagram](#2-complete-architecture-diagram)
3. [Data Flow — Telegram Message](#3-data-flow--telegram-message)
4. [Component Breakdown](#4-component-breakdown)
5. [API Contracts](#5-api-contracts)
6. [Implementation Phases](#6-implementation-phases)
7. [File Structure](#7-file-structure)
8. [Configuration](#8-configuration)
9. [Error Handling](#9-error-handling)
10. [Security](#10-security)
11. [Testing Strategy](#11-testing-strategy)

---

## 1. Architecture Overview

### System Identity

Two distinct projects cooperate:

| Project | Role | Port | Runtime |
|---------|------|------|---------|
| **ai-workstation** (`/mnt/d/Projects/ai-workstation`) | Platform core — PipelineService, context engine, memory, routing, evaluation | 8000 | Python (uv, FastAPI) |
| **ai-workstation-environment** (`/mnt/d/Projects/ai-workstation-environment`) | Infrastructure — components, MCP, Terax, MiMo, Workspace API, n8n, Telegram | 8080 | Python + Docker |

### Design Principles

1. **No monolith rewrite** — every integration plugs into existing interfaces
2. **OpenAI-compatible protocol** — all frontends (Terax, Hermes, Telegram) speak the same language
3. **Workspace API as hub** — single source of truth for sessions, tasks, notifications, presence
4. **Event-driven** — Redis Pub/Sub connects Workspace API ↔ n8n ↔ Telegram ↔ MiMo
5. **Tiered model routing** — free → paid cascade with per-agent model selection
6. **Headroom wraps everything** — all model inputs compressed before LLM call

### Service Map

| Service | Endpoint | Purpose |
|---------|----------|---------|
| ai-workstation Gateway | `http://localhost:8000` | PipelineService, context, memory, routing |
| LiteLLM Proxy | `http://localhost:4000` | OpenAI-compatible LLM gateway |
| Workspace API | `http://localhost:8080` | Sessions, tasks, notifications, WebSocket |
| Ollama | `http://localhost:11434` | Local model inference |
| PostgreSQL | `localhost:5432` | Workspace + ai-workstation storage |
| Redis | `localhost:6379` | Event bus, cache (workspace uses 6380) |
| Qdrant | `http://localhost:6333` | Vector DB for memory + RAG |
| n8n | `http://localhost:5678` | Workflow automation |
| Headroom MCP | via MCP protocol | Context compression |

---

## 2. Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                   │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  Terax   │  │  Hermes  │  │ Telegram │  │  OpenCode │               │
│  │ (Tauri)  │  │ (Mobile) │  │   Bot    │  │  (CLI)    │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │              │              │              │                     │
│       │ OSC 777      │ WS/REST      │ Webhook      │ OpenAI API         │
│       ▼              ▼              ▼              ▼                     │
├───────┼──────────────┼──────────────┼──────────────┼─────────────────────┤
│       │         GATEWAY LAYER     │              │                     │
│       │              │              │              │                     │
│       ▼              ▼              ▼              ▼                     │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │              LiteLLM Proxy (port 4000)                      │       │
│  │   OpenAI-compatible API · Model routing · Load balancing    │       │
│  └──────────┬──────────────────────────────┬───────────────────┘       │
│             │                              │                           │
│             ▼                              ▼                           │
│  ┌──────────────────┐          ┌──────────────────────┐               │
│  │  ai-workstation  │          │   Workspace API      │               │
│  │   Gateway:8000   │◄────────►│     Port:8080        │               │
│  │                  │          │                      │               │
│  │ • PipelineService│          │ • Sessions           │               │
│  │ • Context Engine │          │ • Tasks              │               │
│  │ • Memory (Qdrant)│          │ • Notifications      │               │
│  │ • Agent Router   │          │ • Presence           │               │
│  │ • Tiered Routing │          │ • WebSocket          │               │
│  │ • Evaluation     │          │ • Event Bus          │               │
│  └──────┬───────────┘          └──────────┬───────────┘               │
│         │                                 │                           │
│         │              ORCHESTRATION       │                           │
│         ▼                                 ▼                           │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │                     n8n (port 5678)                         │       │
│  │  Telegram ←→ Webhook ←→ Workspace API ←→ MiMo ←→ LiteLLM  │       │
│  └──────┬──────────────────────────────┬───────────────────────┘       │
│         │                              │                               │
│         │           MODEL LAYER        │                               │
│         ▼                              ▼                               │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │                    Ollama (port 11434)                      │       │
│  │  qwen2.5-coder:1.5b · phi3:mini · gemma2:2b · coder:7b    │       │
│  │  nomic-embed-text                                          │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐         │
│  │   Qdrant:6333    │  │  PostgreSQL  │  │  Headroom MCP    │         │
│  │   (Vector DB)    │  │  :5432       │  │  (Compression)   │         │
│  └──────────────────┘  └──────────────┘  └──────────────────┘         │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │              MiMo Code (Orchestrator)                       │       │
│  │  6 Agents · 28 Skills · 7 Tools · 4 n8n Workflows          │       │
│  │  OSC 777 markers · External agent launch                    │       │
│  └─────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Connection Matrix

```
┌─────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ From \ To   │ LiteLLM  │ Worksp.  │ ai-ws    │ n8n      │ Ollama   │
│             │ :4000    │ API:8080 │ GW:8000  │ :5678    │ :11434   │
├─────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Terax       │ HTTP*    │ WS       │ —        │ —        │ —        │
│ Hermes      │ —        │ WS/REST  │ —        │ —        │ —        │
│ Telegram    │ —        │ —        │ —        │ Webhook  │ —        │
│ OpenCode    │ HTTP*    │ —        │ HTTP     │ —        │ —        │
│ Workspace   │ —        │ —        │ HTTP     │ Redis PS │ —        │
│ ai-ws GW    │ HTTP     │ —        │ —        │ —        │ —        │
│ n8n         │ HTTP     │ HTTP/WS  │ —        │ —        │ —        │
│ MiMo        │ HTTP     │ HTTP     │ —        │ Webhook  │ —        │
│ LiteLLM     │ —        │ —        │ —        │ —        │ HTTP     │
└─────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

* = through OpenAI-compatible endpoint
Redis PS = Redis Pub/Sub
```

---

## 3. Data Flow — Telegram Message

### End-to-End Flow

```
User (Phone)                    System
    │
    │ 1. Send /prompt "add auth to /api/users"
    ▼
┌─────────────┐
│  Telegram   │
│    Bot      │
└──────┬──────┘
       │ 2. HTTP POST to n8n webhook
       ▼
┌─────────────┐
│    n8n      │
│  Workflow   │
└──────┬──────┘
       │ 3. Parse message, extract command + args
       │ 4. Register task via Workspace API
       ▼
┌─────────────────────────────────────────────┐
│           Workspace API (:8080)              │
│  POST /tasks {title, agent_type: "code",    │
│               model: "auto", source:        │
│               "telegram"}                   │
│  → Returns task_id                          │
│  → Event: TASK_CREATED → Redis Pub/Sub      │
└──────┬──────────────────────────────────────┘
       │ 5. Notify MiMo via n8n
       ▼
┌─────────────────────────────────────────────┐
│              MiMo Code                       │
│  Receive task via n8n webhook                │
│  6. Determine agent type from task           │
│  7. If auto mode:                            │
│     a. Architect agent plans (qwen2.5-coder:7b) │
│     b. Break into sub-tasks                  │
│     c. Distribute to specialists             │
│  8. If manual: route to specified agent      │
└──────┬──────────────────────────────────────┘
       │ 9. Agent needs LLM → call LiteLLM
       ▼
┌─────────────────────────────────────────────┐
│          LiteLLM Proxy (:4000)               │
│  POST /v1/chat/completions                  │
│  model: "ollama/qwen2.5-coder:7b"           │
│  → Routes to Ollama                          │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│           Ollama (:11434)                    │
│  qwen2.5-coder:7b processes task            │
│  → Returns completion                        │
└──────┬──────────────────────────────────────┘
       │ 10. Result back to MiMo
       ▼
┌─────────────────────────────────────────────┐
│              MiMo Code                       │
│  11. Update task progress via Workspace API │
│  12. Complete task with result               │
└──────┬──────────────────────────────────────┘
       │ 13. Event: TASK_COMPLETED → Redis
       ▼
┌─────────────────────────────────────────────┐
│           Workspace API (:8080)              │
│  Task status → completed                     │
│  Notification created → n8n picks up        │
└──────┬──────────────────────────────────────┘
       │ 14. n8n receives notification event
       ▼
┌─────────────┐
│    n8n      │
│  Workflow   │
└──────┬──────┘
       │ 15. Format message, send to Telegram
       ▼
┌─────────────┐
│  Telegram   │
│    Bot      │
└──────┬──────┘
       │ 16. Reply to user
       ▼
User (Phone)
    │
    │ "Task completed. Auth middleware added
    │  to /api/users. 3 files modified."
    ▼
```

### Auto Mode Orchestration Detail

```
User Prompt: "add auth to /api/users"
    │
    ▼
┌─────────────────────────────────────────┐
│ ARCHITECT AGENT (qwen2.5-coder:7b)      │
│ Input: user prompt + project context     │
│ Output: {                               │
│   "plan": [                             │
│     {                                   │
│       "id": "sub-1",                    │
│       "type": "code",                   │
│       "description": "Create auth        │
│         middleware",                     │
│       "files": ["middleware/auth.ts"]   │
│     },                                  │
│     {                                   │
│       "id": "sub-2",                    │
│       "type": "code",                   │
│       "description": "Add route guards", │
│       "files": ["routes/users.ts"]      │
│     },                                  │
│     {                                   │
│       "id": "sub-3",                    │
│       "type": "review",                 │
│       "description": "Review changes",   │
│       "depends_on": ["sub-1", "sub-2"]  │
│     },                                  │
│     {                                   │
│       "id": "sub-4",                    │
│       "type": "docs",                   │
│       "description": "Update API docs",  │
│       "depends_on": ["sub-3"]           │
│     }                                   │
│   ]                                     │
│ }                                       │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ DISTRIBUTOR                              │
│ Creates Workspace API tasks:             │
│ • sub-1 → coder task (qwen2.5-coder:7b) │
│ • sub-2 → coder task (qwen2.5-coder:7b) │
│ sub-1, sub-2 run IN PARALLEL            │
│                                         │
│ After sub-1 + sub-2 complete:           │
│ • sub-3 → reviewer task (gemini-flash)   │
│ • sub-3 completes                        │
│ • sub-4 → doc task (qwen2.5-coder:1.5b) │
│ sub-4 runs SEQUENTIALLY after sub-3     │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ AGGREGATOR                               │
│ Collects all sub-task results            │
│ Sends combined result to user            │
└─────────────────────────────────────────┘
```

---

## 4. Component Breakdown

### 4.1 Terax ↔ MiMo Communication

**What exists**: Terax is an independent AI terminal. MiMo is a separate CLI tool. Both connect to LiteLLM independently.

**What needs to be built**:

| Component | Type | Purpose |
|-----------|------|---------|
| `components/terax/scripts/mimo-bridge.sh` | New script | Launches MiMo as external agent, captures OSC 777 markers |
| `components/terax/config/TERAX.md` | Update | Add MiMo launch instructions and agent detection config |
| `components/mimo/tools/terax-bridge.ts` | New tool | MiMo tool to send results back to Terax terminal |

**Architecture**:

```
Terax (Tauri terminal)
  │
  │ 1. User types /mimo "do something"
  │ 2. Terax detects OSC 777 marker pattern
  │
  ├──────────────────────────────────────────┐
  │                                          │
  ▼                                          ▼
MiMo CLI (launched as subprocess)     Terax waits for output
  │                                    (OSC 777 marker signals
  │ 3. MiMo processes task               completion)
  │ 4. MiMo outputs result
  │ 5. Result wrapped in OSC 777:
  │    \033]777;ai-result;{json}\007
  │ 6. Terax captures and displays
  └──────────────────────────────────────────┘
```

**OSC 777 Marker Protocol**:

```
Start marker:  \033]777;ai-start;{"agent":"mimo","task_id":"..."}\007
Progress:      \033]777;ai-progress;{"percent":50,"status":"..."}\007
Complete:      \033]777;ai-complete;{"result":"...","task_id":"..."}\007
Error:         \033]777;ai-error;{"error":"...","task_id":"..."}\007
```

### 4.2 Multi-Worktree Sessions

**What exists**: Workspace API has session/task management but no worktree concept.

**What needs to be built**:

| Component | Type | Purpose |
|-----------|------|---------|
| `components/workspace/app/models/worktree.py` | New model | Worktree state: git path, session, model, agent |
| `components/workspace/app/core/worktree_manager.py` | New manager | Create/switch/list worktrees |
| `components/workspace/app/api/routes/worktrees.py` | New router | REST API for worktree operations |
| `components/workspace/app/schemas/worktree.py` | New schema | Pydantic models for worktree DTOs |

**Worktree Model**:

```python
class Worktree(Base):
    __tablename__ = "worktrees"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"))
    name: Mapped[str] = mapped_column(String(255))
    git_path: Mapped[str] = mapped_column(String(1024))  # Absolute path
    session_id: Mapped[UUID | None] = mapped_column(ForeignKey("sessions.id"))
    current_model: Mapped[str] = mapped_column(String(100), default="auto")
    current_agent: Mapped[str] = mapped_column(String(50), default="general")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

**Switching Flow**:

```
User: /worktree switch frontend
  │
  ▼
Workspace API: GET /worktrees?name=frontend
  │ Returns worktree config
  │
  ▼
Workspace API: Creates session for worktree
  │ POST /sessions {workspace_id, worktree_id: "..."}
  │
  ▼
Returns: {session_id, git_path, current_model, current_agent}
  │
  ▼
Client (Terax/Hermes/Telegram) switches context
  cd /path/to/frontend-worktree
  Model/agent updated for this session
```

### 4.3 Dynamic Agent Selection

**What exists**: `AgentRegistry` in ai-workstation with 7 agent types. `classify_task()` uses regex.

**What needs to be modified**:

| Component | Change | Purpose |
|-----------|--------|---------|
| `packages/routing/src/routing/agent_registry.py` | Add `architect` agent type | Plan → distribute orchestrator |
| `components/mimo/agents/architect.md` | New agent | Planning + task decomposition |
| `components/workspace/app/api/routes/tasks.py` | Add `agent_type` parameter | Manual agent override |
| `configs/default.yaml` | Add agent model mappings | Per-agent model selection |

**New Agent Types**:

```python
# In agent_registry.py — add to DEFAULT_AGENTS:
"architect": AgentModelConfig(
    agent_type="architect",
    tiers=[
        Tier(name="local", models=["ollama/qwen2.5-coder:7b"], token_budget=-1),
        Tier(name="free", models=["gemini/gemini-2.5-pro"], token_budget=200_000),
        Tier(name="paid", models=["claude-sonnet-4-20250514"], token_budget=-1),
    ],
),
```

**Selection Modes**:

| Mode | Behavior | When to use |
|------|----------|-------------|
| `auto` | Architect plans → distribute to specialists | Complex multi-step tasks |
| `manual` | User specifies agent type + optional model | Simple, known tasks |
| `cascade` | Try free → fall back to paid | Default for budget control |

### 4.4 Auto Mode Orchestration

**What exists**: MiMo has compose workflows, n8n has 4 basic workflows.

**What needs to be built**:

| Component | Type | Purpose |
|-----------|------|---------|
| `components/mimo/agents/architect.md` | New agent | Plans tasks, creates sub-task graph |
| `components/mimo/skills/auto-orchestrate/SKILL.md` | New skill | Orchestrates plan → distribute → aggregate |
| `components/mimo/tools/workspace-bridge.ts` | New tool | Creates/manages tasks via Workspace API |
| `workflows/auto-orchestrate.yaml` | New workflow | n8n workflow for auto mode |
| `components/workspace/app/api/routes/tasks.py` | Add `subtasks` support | Parent/child task relationships |

**Orchestration Flow**:

```python
# Pseudocode for auto-orchestrate skill
async def auto_orchestrate(prompt: str, workspace_id: str):
    # 1. Architect plans
    plan = await llm.complete(
        model="ollama/qwen2.5-coder:7b",
        messages=[architect_system_prompt, prompt],
        response_format={"type": "json_object"}
    )
    subtasks = plan["subtasks"]  # List of {type, description, depends_on, files}
    
    # 2. Create tasks in Workspace API
    task_ids = []
    for st in subtasks:
        resp = await workspace_api.post("/tasks", json={
            "workspace_id": workspace_id,
            "title": st["description"],
            "agent_type": st["type"],
            "model": "auto",
            "parent_id": plan["id"],
        })
        task_ids.append(resp["id"])
    
    # 3. Execute sub-tasks (respecting dependencies)
    completed = set()
    for st in sorted(subtasks, key=lambda x: len(x.get("depends_on", []))):
        # Wait for dependencies
        for dep in st.get("depends_on", []):
            await wait_for_task(dep)
        
        # Execute
        result = await execute_subtask(st, task_ids[st["id"]])
        completed.add(st["id"])
    
    # 4. Aggregate results
    all_results = [get_task_result(tid) for tid in task_ids]
    return aggregate(all_results)
```

### 4.5 Headroom Context Wrapping

**What exists**: Headroom MCP server defined in `mcp/servers/headroom.yaml` but disabled.

**What needs to be done**:

| Step | Action | Purpose |
|------|--------|---------|
| 1 | Enable Headroom MCP in `mcp/registry.yaml` | Activate the server |
| 2 | Add Headroom wrapper to PipelineService | Wrap all model inputs |
| 3 | Add `--headroom` flag to MiMo tools | Per-tool compression option |
| 4 | Configure compression ratios | 60-90% target |

**Integration Point in PipelineService**:

```python
# In pipeline/service.py — add before _augment_messages:
async def _compress_context(self, messages: list[Message]) -> list[Message]:
    if not self.headroom_client:
        return messages
    
    # Compress system context and long tool results
    compressed = []
    for msg in messages:
        if msg.role == Role.SYSTEM and len(msg.content) > 2000:
            compressed_content = await self.headroom_client.compress(
                msg.content,
                target_ratio=0.3  # 70% compression
            )
            compressed.append(Message(role=msg.role, content=compressed_content))
        else:
            compressed.append(msg)
    return compressed
```

**Headroom Client**:

```python
# New file: packages/context/src/context/headroom.py
class HeadroomClient:
    """Wraps Headroom MCP server for context compression."""
    
    def __init__(self, mcp_url: str = "http://localhost:3001"):
        self.mcp_url = mcp_url
    
    async def compress(self, text: str, target_ratio: float = 0.3) -> str:
        """Compress text to target_ratio of original size."""
        # Call Headroom MCP compress tool
        ...
    
    async def expand(self, compressed: str, context: str) -> str:
        """Expand compressed text back."""
        ...
```

### 4.6 Serena Configuration

**What exists**: `.serena/` directory exists but contents not examined.

**Optimal Config**:

```yaml
# .serena/config.yaml
serena:
  # Model selection
  models:
    fast: "ollama/qwen2.5-coder:1.5b"      # Quick edits, autocomplete
    balanced: "ollama/phi3:mini"             # General tasks
    smart: "ollama/qwen2.5-coder:7b"        # Complex code
    free: "gemini/gemini-2.5-flash"          # Cloud fallback
  
  # Resource limits
  resources:
    max_concurrent: 2
    max_context_tokens: 8192
    timeout_seconds: 300
  
  # Startup optimization
  startup:
    lazy_load: true
    preload_models: ["ollama/qwen2.5-coder:1.5b"]
    cache_enabled: true
  
  # Integration
  integration:
    workspace_api: "http://localhost:8080"
    litellm_url: "http://localhost:4000"
    headroom_enabled: true
```

### 4.7 Hermes Agent Integration

**What exists**: `HermesAdapter` stub in workspace API. No real implementation.

**What needs to be built**:

| Component | Type | Purpose |
|-----------|------|---------|
| `components/workspace/app/adapters/hermes_adapter.py` | Rewrite | Real WebSocket client to Hermes |
| `components/hermes/` | New component | Hermes installation + config |
| `components/hermes/component.yaml` | New | Component metadata |
| `components/hermes/install.sh` | New | Install Hermes |
| `components/hermes/config/hermes-config.yaml` | New | Connection config |

**Hermes Adapter (Real)**:

```python
class HermesAdapter(BaseAdapter):
    def __init__(self, hermes_url: str = "ws://localhost:8081/ws"):
        self.hermes_url = hermes_url
        self.ws: WebSocket | None = None
        self.connected = False
    
    async def connect(self) -> None:
        self.ws = await websockets.connect(self.hermes_url)
        self.connected = True
    
    async def send_message(self, session_id: str, message: dict) -> dict:
        if not self.connected:
            raise ConnectionError("Hermes not connected")
        
        payload = {
            "type": "message",
            "session_id": session_id,
            "content": message["content"],
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.ws.send(json.dumps(payload))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def receive_messages(self, session_id: str) -> AsyncIterator[dict]:
        async for raw in self.ws:
            data = json.loads(raw)
            if data.get("session_id") == session_id:
                yield data
    
    async def get_status(self) -> dict:
        return {
            "adapter": "hermes",
            "connected": self.connected,
            "url": self.hermes_url,
        }
```

### 4.8 Telegram Integration

**What exists**: n8n can receive webhooks. MiMo has `n8n-trigger` tool.

**What needs to be built**:

| Component | Type | Purpose |
|-----------|------|---------|
| `components/telegram/` | New component | Telegram bot + n8n workflows |
| `components/telegram/component.yaml` | New | Component metadata |
| `components/telegram/install.sh` | New | Create bot via BotFather, configure n8n |
| `components/telegram/n8n-workflows/telegram-receiver.json` | New | Receive Telegram messages |
| `components/telegram/n8n-workflows/telegram-notify.json` | New | Send notifications to Telegram |
| `components/telegram/bot/config.yaml` | New | Bot token, chat IDs, commands |
| `components/telegram/bot/handler.py` | New | Python bot handler |

**n8n Workflow: Telegram → System**:

```
Telegram Bot Webhook
  │
  ▼
n8n: Telegram Receiver Workflow
  │
  ├─ Parse message (command detection)
  │   /prompt <text>  → Create task
  │   /approve <id>   → Approve task
  │   /commit <msg>   → Git commit
  │   /status         → Check status
  │   /worktree <cmd> → Manage worktrees
  │
  ├─ Route by command:
  │   /prompt → POST http://localhost:8080/tasks
  │   /status → GET http://localhost:8080/tasks?status=in_progress
  │   /commit → POST http://localhost:5678/webhook/git-notify
  │
  └─ Reply via Telegram Bot API
```

**n8n Workflow: System → Telegram**:

```
Workspace API Event (Redis Pub/Sub)
  │
  ▼
n8n: Notification Workflow
  │
  ├─ Filter: task.completed, task.failed, notification.new
  │
  ├─ Format message:
  │   "✅ Task completed: {title}"
  │   "❌ Task failed: {error}"
  │   "📊 Status: {in_progress}/{total} tasks running"
  │
  └─ Send via Telegram Bot API
```

### 4.9 n8n Automation

**What exists**: 4 basic workflows (git-notifier, health-monitor, session-summary, post-commit-tests).

**What needs to be added**:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `telegram-receiver.json` | Telegram webhook | Receive commands from phone |
| `telegram-notify.json` | Redis event | Send notifications to phone |
| `auto-orchestrate.json` | Workspace API webhook | Trigger auto mode for tasks |
| `task-distributor.json` | TASK_CREATED event | Route tasks to appropriate agents |
| `result-aggregator.json` | TASK_COMPLETED event | Collect results and notify |

**n8n Workflow Import Path**:
```
components/mimo/n8n-workflows/
├── git-notifier.json          (existing)
├── health-monitor.json        (existing)
├── session-summary.json       (existing)
├── post-commit-tests.json     (existing)
├── telegram-receiver.json     (new)
├── telegram-notify.json       (new)
├── auto-orchestrate.json      (new)
├── task-distributor.json      (new)
└── result-aggregator.json     (new)
```

### 4.10 ai-workstation Integration

**What exists**: PipelineService at port 8000 with full routing, context, memory.

**Integration points**:

```
All model requests → ai-workstation Gateway (port 8000)
  │
  ├─ PipelineService.execute()
  │   ├─ Context Engine (tree-sitter + embeddings + PixelRAG)
  │   ├─ Memory Service (Qdrant)
  │   ├─ Agent Router (classify → tiered routing)
  │   ├─ Provider (LiteLLM → Ollama/Cloud)
  │   ├─ Evaluation (quality scoring)
  │   └─ Observability (tracing)
  │
  └─ Workspace API delegates to Gateway for:
      ├─ Model completions
      ├─ Context gathering
      └─ Memory recall
```

**Workspace API → ai-workstation Gateway Client**:

```python
# New file: components/workspace/app/clients/gateway.py
class GatewayClient:
    """Client for ai-workstation PipelineService."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.http = httpx.AsyncClient(base_url=base_url, timeout=300)
    
    async def complete(
        self,
        messages: list[dict],
        agent_type: str = "general",
        model: str | None = None,
        project_id: str | None = None,
    ) -> dict:
        payload = {
            "messages": messages,
            "agent_type": agent_type,
            "model": model,
            "project_id": project_id,
        }
        resp = await self.http.post("/v1/chat/completions", json=payload)
        return resp.json()
    
    async def gather_context(self, query: str, project_id: str) -> list[dict]:
        resp = await self.http.get("/v1/context", params={"query": query, "project_id": project_id})
        return resp.json().get("chunks", [])
    
    async def recall_memory(self, query: str, scope: str = "project") -> list[dict]:
        resp = await self.http.get("/v1/memory/recall", params={"query": query, "scope": scope})
        return resp.json().get("memories", [])
```

---

## 5. API Contracts

### 5.1 Workspace API — New Endpoints

#### Worktrees

```
POST   /workspaces/{id}/worktrees          Create worktree
GET    /workspaces/{id}/worktrees          List worktrees
GET    /workspaces/{id}/worktrees/{wid}    Get worktree
PUT    /workspaces/{id}/worktrees/{wid}    Update worktree
DELETE /workspaces/{id}/worktrees/{wid}    Delete worktree
POST   /workspaces/{id}/worktrees/{wid}/switch  Switch to worktree
```

**Request/Response Schema**:

```json
// POST /workspaces/{id}/worktrees
{
  "name": "frontend",
  "git_path": "/mnt/d/Projects/frontend",
  "current_model": "auto",
  "current_agent": "general"
}

// Response 201
{
  "id": "uuid",
  "workspace_id": "uuid",
  "name": "frontend",
  "git_path": "/mnt/d/Projects/frontend",
  "session_id": null,
  "current_model": "auto",
  "current_agent": "general",
  "status": "active",
  "created_at": "2026-07-07T12:00:00Z"
}

// POST /workspaces/{id}/worktrees/{wid}/switch
// Response 200
{
  "worktree_id": "uuid",
  "session_id": "uuid-new-session",
  "git_path": "/mnt/d/Projects/frontend",
  "current_model": "ollama/qwen2.5-coder:7b",
  "current_agent": "code"
}
```

#### Tasks — Enhanced

```
POST   /tasks                          Create task (enhanced with subtasks)
GET    /tasks?parent_id={id}           Get subtasks
POST   /tasks/{id}/delegate            Delegate to specific agent
```

**Request Schema**:

```json
// POST /tasks — Enhanced
{
  "workspace_id": "uuid",
  "session_id": "uuid",
  "title": "Add auth middleware",
  "agent_type": "code",          // "auto" | "code" | "review" | "docs" | etc.
  "model": "auto",               // "auto" | model name
  "parent_id": null,             // For subtasks
  "depends_on": [],              // Task IDs this depends on
  "priority": "normal",          // "low" | "normal" | "high" | "critical"
  "source": "telegram",          // "terax" | "telegram" | "hermes" | "api"
  "input": {
    "prompt": "add auth to /api/users",
    "worktree_id": "uuid",
    "files_context": ["src/routes/users.ts"]
  }
}

// Response 201
{
  "id": "uuid",
  "status": "pending",
  "agent_type": "code",
  "model": "ollama/qwen2.5-coder:7b",
  "routing_info": {
    "tier": "local",
    "provider": "ollama",
    "model": "qwen2.5-coder:7b"
  }
}
```

#### Notifications — Telegram Bridge

```
POST   /notifications/telegram/send     Send message to Telegram
GET    /notifications?channel=telegram  Get Telegram notifications
```

### 5.2 n8n — Webhook Contracts

#### Telegram Receiver

```
POST http://localhost:5678/webhook/telegram-receive

Request:
{
  "message_id": 12345,
  "chat": {"id": 123456789},
  "text": "/prompt add auth to /api/users",
  "from": {"id": 123456789, "username": "keyz"}
}

Response:
{
  "ok": true,
  "task_id": "uuid",
  "message": "Task created. ID: uuid"
}
```

#### Task Webhook (for MiMo)

```
POST http://localhost:5678/webhook/task-update

Request:
{
  "task_id": "uuid",
  "status": "completed",          // "in_progress" | "completed" | "failed"
  "progress": 100,
  "result": {
    "files_modified": ["src/middleware/auth.ts"],
    "summary": "Added JWT auth middleware"
  }
}
```

### 5.3 MiMo — Workspace Bridge

```
// MiMo tool: workspace-bridge.ts
// Creates tasks via Workspace API

interface WorkspaceBridgeArgs {
  action: "create_task" | "update_task" | "list_tasks" | "get_task";
  workspace_id?: string;
  task_id?: string;
  title?: string;
  agent_type?: string;
  model?: string;
  status?: string;
  result?: object;
}
```

### 5.4 Terax — MiMo Bridge Protocol

```
# Terax launches MiMo
mimo run --prompt "add auth" --format osc777

# MiMo outputs with OSC 777 markers
\033]777;ai-start;{"agent":"mimo","task_id":"..."}\007
\033]777;ai-progress;{"percent":50,"status":"Planning..."}\007
\033]777;ai-complete;{"result":"...","task_id":"..."}\007

# Terax captures markers and displays in terminal
```

---

## 6. Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Core infrastructure works end-to-end

| # | Task | Files | Dependencies |
|---|------|-------|-------------|
| 1.1 | Enable Headroom MCP | `mcp/registry.yaml` | None |
| 1.2 | Update agent registry with architect type | `packages/routing/src/routing/agent_registry.py` | None |
| 1.3 | Add worktree model + manager | `components/workspace/app/models/worktree.py`, `core/worktree_manager.py`, `api/routes/worktrees.py`, `schemas/worktree.py` | None |
| 1.4 | Enhanced task schema (parent/child, depends_on) | `components/workspace/app/models/task.py`, `schemas/task.py` | None |
| 1.5 | Gateway client for Workspace API | `components/workspace/app/clients/gateway.py` | None |

### Phase 2: Agent Integration (Week 2)
**Goal**: MiMo can create/manage tasks via Workspace API

| # | Task | Files | Dependencies |
|---|------|-------|-------------|
| 2.1 | MiMo workspace-bridge tool | `components/mimo/tools/workspace-bridge.ts` | 1.3, 1.4 |
| 2.2 | Architect agent definition | `components/mimo/agents/architect.md` | 1.2 |
| 2.3 | Auto-orchestrate skill | `components/mimo/skills/auto-orchestrate/SKILL.md` | 2.1, 2.2 |
| 2.4 | Headroom integration in PipelineService | `packages/pipeline/src/pipeline/service.py` | 1.1 |
| 2.5 | Task delegation endpoint | `components/workspace/app/api/routes/tasks.py` | 1.4 |

### Phase 3: Terax ↔ MiMo Bridge (Week 3)
**Goal**: Terax can launch MiMo as external agent

| # | Task | Files | Dependencies |
|---|------|-------|-------------|
| 3.1 | OSC 777 protocol implementation | `components/terax/scripts/mimo-bridge.sh` | None |
| 3.2 | Terax MiMo tool | `components/mimo/tools/terax-bridge.ts` | 3.1 |
| 3.3 | TERAX.md update with MiMo instructions | `components/terax/config/TERAX.md` | 3.1 |
| 3.4 | Agent detection in Terax | `components/terax/config/terax-config.yaml` | 3.3 |

### Phase 4: Telegram Integration (Week 4)
**Goal**: User can control platform from phone

| # | Task | Files | Dependencies |
|---|------|-------|-------------|
| 4.1 | Telegram bot component | `components/telegram/` (new) | None |
| 4.2 | n8n Telegram receiver workflow | `components/mimo/n8n-workflows/telegram-receiver.json` | 4.1 |
| 4.3 | n8n Telegram notification workflow | `components/mimo/n8n-workflows/telegram-notify.json` | 4.1 |
| 4.4 | Task notification → Telegram | `components/workspace/app/events/handlers.py` | 1.4 |
| 4.5 | Command routing (prompt/approve/commit/status) | `components/telegram/bot/handler.py` | 4.2 |

### Phase 5: Hermes Integration (Week 5)
**Goal**: Hermes mobile client connects to Workspace API

| # | Task | Files | Dependencies |
|---|------|-------|-------------|
| 5.1 | Real Hermes adapter | `components/workspace/app/adapters/hermes_adapter.py` | 1.3 |
| 5.2 | Hermes component | `components/hermes/` (new) | None |
| 5.3 | Hermes notification subscription | `components/workspace/app/events/handlers.py` | 5.1 |
| 5.4 | Mobile-optimized endpoints | `components/workspace/app/api/routes/` | 5.1 |

### Phase 6: Auto Mode + n8n (Week 6)
**Goal**: Full auto orchestration works

| # | Task | Files | Dependencies |
|---|------|-------|-------------|
| 6.1 | Auto-orchestrate n8n workflow | `components/mimo/n8n-workflows/auto-orchestrate.json` | 2.3 |
| 6.2 | Task distributor n8n workflow | `components/mimo/n8n-workflows/task-distributor.json` | 1.4, 2.5 |
| 6.3 | Result aggregator n8n workflow | `components/mimo/n8n-workflows/result-aggregator.json` | 6.2 |
| 6.4 | Multi-worktree support in auto mode | `components/mimo/skills/auto-orchestrate/SKILL.md` | 1.3, 2.3 |
| 6.5 | Serena optimal config | `.serena/config.yaml` | None |

### Phase 7: Testing + Hardening (Week 7)
**Goal**: All integrations tested and production-ready

| # | Task | Files | Dependencies |
|---|------|-------|-------------|
| 7.1 | Integration tests for Workspace API | `components/workspace/app/tests/test_*.py` | All |
| 7.2 | n8n workflow tests | `tests/test_n8n_workflows.py` | 4.2, 4.3, 6.1-6.3 |
| 7.3 | End-to-end Telegram test | `tests/test_telegram_e2e.py` | 4.5 |
| 7.4 | Terax-MiMo bridge test | `tests/test_terax_mimo_bridge.py` | 3.1, 3.2 |
| 7.5 | Error handling + retry logic | Various | All |
| 7.6 | Security audit | Various | All |

---

## 7. File Structure

### New Files

```
ai-workstation-environment/
├── components/
│   ├── workspace/
│   │   └── app/
│   │       ├── models/
│   │       │   └── worktree.py                    # NEW
│   │       ├── core/
│   │       │   └── worktree_manager.py            # NEW
│   │       ├── api/routes/
│   │       │   └── worktrees.py                   # NEW
│   │       ├── schemas/
│   │       │   └── worktree.py                    # NEW
│   │       ├── clients/
│   │       │   ├── __init__.py                    # NEW
│   │       │   └── gateway.py                     # NEW
│   │       └── adapters/
│   │           └── hermes_adapter.py              # REWRITE
│   │
│   ├── mimo/
│   │   ├── agents/
│   │   │   └── architect.md                       # NEW
│   │   ├── tools/
│   │   │   ├── workspace-bridge.ts                # NEW
│   │   │   └── terax-bridge.ts                    # NEW
│   │   ├── skills/
│   │   │   └── auto-orchestrate/
│   │   │       └── SKILL.md                       # NEW
│   │   └── n8n-workflows/
│   │       ├── telegram-receiver.json             # NEW
│   │       ├── telegram-notify.json               # NEW
│   │       ├── auto-orchestrate.json              # NEW
│   │       ├── task-distributor.json              # NEW
│   │       └── result-aggregator.json             # NEW
│   │
│   ├── terax/
│   │   ├── scripts/
│   │   │   └── mimo-bridge.sh                     # NEW
│   │   └── config/
│   │       └── TERAX.md                           # UPDATE
│   │
│   ├── telegram/                                  # NEW COMPONENT
│   │   ├── component.yaml
│   │   ├── check.sh
│   │   ├── install.sh
│   │   ├── uninstall.sh
│   │   └── bot/
│   │       ├── config.yaml
│   │       └── handler.py
│   │
│   └── hermes/                                    # NEW COMPONENT
│       ├── component.yaml
│       ├── check.sh
│       ├── install.sh
│       ├── uninstall.sh
│       └── config/
│           └── hermes-config.yaml
│
├── configs/
│   └── default.yaml                               # UPDATE (agent models)
│
├── mcp/
│   ├── registry.yaml                              # UPDATE (enable headroom)
│   └── servers/
│       └── headroom.yaml                          # UPDATE (if needed)
│
├── workflows/
│   └── auto-orchestrate.yaml                      # NEW
│
├── tests/
│   ├── test_workspace_worktree.py                 # NEW
│   ├── test_n8n_workflows.py                      # NEW
│   ├── test_telegram_e2e.py                       # NEW
│   └── test_terax_mimo_bridge.py                  # NEW
│
├── .serena/
│   └── config.yaml                                # NEW
│
└── docs/
    └── INTEGRATION-ARCHITECTURE.md                # THIS FILE
```

### Modified Files

```
packages/routing/src/routing/agent_registry.py     # Add architect agent
packages/pipeline/src/pipeline/service.py           # Add Headroom wrapper
components/workspace/app/main.py                    # Add worktree router
components/workspace/app/api/routes/tasks.py        # Add delegate endpoint
components/workspace/app/events/types.py            # Add new event types
components/workspace/app/events/handlers.py         # Add Telegram handler
components/workspace/app/config.py                  # Add gateway_url
components/workspace/app/models/task.py             # Add parent_id, depends_on
components/workspace/app/schemas/task.py            # Enhanced task schema
mcp/registry.yaml                                  # Enable headroom
configs/default.yaml                               # Add agent model mappings
```

---

## 8. Configuration

### 8.1 Environment Variables

```bash
# === ai-workstation Gateway ===
GATEWAY_URL=http://localhost:8000
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-awe}:${POSTGRES_PASSWORD:-}@localhost:5432/ai_workstation
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333

# === Workspace API ===
WORKSPACE_API_URL=http://localhost:8080
WORKSPACE_DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-awe}:${POSTGRES_PASSWORD:-}@localhost:5432/workspace
WORKSPACE_REDIS_URL=redis://localhost:6380

# === LiteLLM ===
LITELLM_URL=http://localhost:4000
LITELLM_API_KEY=<auto-generated-on-install>

# === Ollama ===
OLLAMA_URL=http://localhost:11434

# === n8n ===
N8N_URL=http://localhost:5678

# === Telegram ===
TELEGRAM_BOT_TOKEN=<from BotFather>
TELEGRAM_CHAT_ID=<your chat ID>
TELEGRAM_WEBHOOK_URL=http://localhost:5678/webhook/telegram-receive

# === API Keys ===
GOOGLE_API_KEY=<your-gemini-api-key>
OPENCODE_API_KEY=<your-openrouter-api-key>

# === Headroom ===
HEADROOM_MCP_URL=http://localhost:3001
HEADROOM_COMPRESSION_RATIO=0.3

# === Hermes ===
HERMES_WS_URL=ws://localhost:8081/ws
HERMES_API_URL=http://localhost:8081
```

### 8.2 configs/default.yaml — Updated

```yaml
environment:
  editor: zed
  shell: zsh

git:
  default_branch: main

docker:
  compose_version: v2

mcp:
  default_enabled:
    - filesystem
    - git
    - github
    - headroom        # ENABLED
    - codebase-memory
    - ponytail
    - terax

terax:
  enabled: true
  proxy_url: "http://localhost:4000"
  agent_detection: true
  default_model: "claude-sonnet-4-20250514"
  mimo_bridge: true
  osc777_markers: true

workspace:
  api_url: "http://localhost:8080"
  gateway_url: "http://localhost:8000"
  redis_url: "redis://localhost:6380"
  default_model: "auto"
  auto_mode_enabled: true

agents:
  architect:
    model: "ollama/qwen2.5-coder:7b"
    fallback: "gemini/gemini-2.5-pro"
  code:
    model: "ollama/qwen2.5-coder:7b"
    fallback: "gemini/gemini-2.5-flash"
  review:
    model: "gemini/gemini-2.5-flash"
    fallback: "claude-sonnet-4-20250514"
  docs:
    model: "ollama/qwen2.5-coder:1.5b"
    fallback: "gemini/gemini-2.5-flash"
  debug:
    model: "gemini/gemini-2.5-pro"
    fallback: "claude-sonnet-4-20250514"
  test:
    model: "ollama/phi3:mini"
    fallback: "gemini/gemini-2.5-flash"
  general:
    model: "ollama/phi3:mini"
    fallback: "gemini/gemini-2.5-flash"

telegram:
  enabled: true
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  chat_id: "${TELEGRAM_CHAT_ID}"
  commands:
    - /prompt
    - /approve
    - /commit
    - /status
    - /worktree
    - /agent
    - /model

hermes:
  enabled: false
  ws_url: "ws://localhost:8081/ws"
  api_url: "http://localhost:8081"

headroom:
  enabled: true
  mcp_url: "http://localhost:3001"
  compression_ratio: 0.3
  target_savings: "60-90%"

serena:
  models:
    fast: "ollama/qwen2.5-coder:1.5b"
    balanced: "ollama/phi3:mini"
    smart: "ollama/qwen2.5-coder:7b"
    free: "gemini/gemini-2.5-flash"
  resources:
    max_concurrent: 2
    max_context_tokens: 8192
    timeout_seconds: 300
```

### 8.3 LiteLLM Config Update

```yaml
# Add to LiteLLM config for architect agent
model_list:
  # Existing models...
  
  # Architect-specific routing
  - model_name: "architect"
    litellm_params:
      model: "ollama/qwen2.5-coder:7b"
      api_base: "http://localhost:11434"
  
  # Agent model aliases
  - model_name: "agent/code"
    litellm_params:
      model: "ollama/qwen2.5-coder:7b"
      api_base: "http://localhost:11434"
  
  - model_name: "agent/review"
    litellm_params:
      model: "gemini/gemini-2.5-flash"
      api_key: os.environ/GOOGLE_API_KEY
  
  - model_name: "agent/docs"
    litellm_params:
      model: "ollama/qwen2.5-coder:1.5b"
      api_base: "http://localhost:11434"
```

---

## 9. Error Handling

### 9.1 Error Categories

| Category | Examples | Strategy |
|----------|----------|----------|
| **Transient** | Network timeout, rate limit, Ollama cold start | Retry with exponential backoff (3 attempts) |
| **Permanent** | Invalid model, missing API key, bad request | Return error immediately |
| **Resource** | OOM, VRAM full, disk full | Evict oldest loaded model, reduce concurrency |
| **Dependency** | Service down (LiteLLM, Ollama, PostgreSQL) | Circuit breaker → fallback model |
| **Logic** | Bad plan from architect, failed subtask | Retry with simplified plan, or escalate to user |

### 9.2 Circuit Breaker Pattern

```python
# components/workspace/app/resilience/circuit_breaker.py
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "closed"  # closed = normal, open = blocking, half_open = testing
        self.last_failure_time = None
    
    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpenError("Service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise
```

### 9.3 Fallback Chain

```
Primary model fails
  │
  ├─ Try fallback model (same agent tier)
  │
  ├─ Try lower tier (free → local)
  │
  ├─ Try simplest local model (qwen2.5-coder:1.5b)
  │
  └─ Return graceful error to user
      "All models unavailable. Task queued. Will retry when services recover."
```

### 9.4 Task Failure Handling

```python
# In auto-orchestrate skill
async def handle_subtask_failure(task_id: str, error: str, subtask: dict):
    # 1. Log failure
    await workspace_api.put(f"/tasks/{task_id}", json={"status": "failed", "error": error})
    
    # 2. Notify user via Telegram
    await n8n.trigger("telegram-notify", {
        "message": f"❌ Subtask failed: {subtask['description']}\nError: {error}",
        "chat_id": TELEGRAM_CHAT_ID,
    })
    
    # 3. Check if other subtasks depend on this
    dependent_tasks = await workspace_api.get(f"/tasks?depends_on={task_id}")
    
    if dependent_tasks:
        # Block dependent tasks
        for dt in dependent_tasks:
            await workspace_api.put(f"/tasks/{dt['id']}", json={
                "status": "blocked",
                "error": f"Dependency {task_id} failed"
            })
    
    # 4. If critical path, try simplified retry
    if subtask.get("retry_count", 0) < 2:
        simplified = simplify_task(subtask)
        await create_and_execute_task(simplified, retry_count=subtask.get("retry_count", 0) + 1)
```

### 9.5 Workspace API Error Responses

```json
// Standard error format
{
  "error": {
    "code": "TASK_DELEGATION_FAILED",
    "message": "Could not delegate task to agent",
    "details": {
      "agent_type": "code",
      "reason": "Model ollama/qwen2.5-coder:7b unavailable",
      "fallback_used": "gemini/gemini-2.5-flash"
    },
    "retryable": true,
    "suggested_action": "Retry with different model or check Ollama status"
  }
}

// Task blocked due to dependency
{
  "error": {
    "code": "DEPENDENCY_BLOCKED",
    "message": "Task waiting for subtask sub-1 to complete",
    "details": {
      "blocked_by": "task-uuid-sub-1",
      "dependency_status": "failed"
    },
    "retryable": false
  }
}
```

---

## 10. Security

### 10.1 Authentication Layers

| Layer | Method | Scope |
|-------|--------|-------|
| Workspace API | API key header (`X-API-Key`) | All endpoints |
| Telegram Bot | Bot token validation | Webhook source verification |
| n8n | Webhook secret | Inbound webhook validation |
| LiteLLM | Master key (from LITELLM_API_KEY env var) | LLM API access |
| WebSocket | Token in first message | Real-time connections |
| Terax ↔ MiMo | OSC 777 markers (not auth, but identification) | Agent detection |

### 10.2 Secrets Management

```python
# components/workspace/app/config.py — secrets from env only
class Settings(BaseSettings):
    # Never hardcode secrets
    secret_key: str = Field(default_factory=lambda: os.environ.get("WORKSPACE_SECRET_KEY", "change-me"))
    telegram_bot_token: str = Field(default_factory=lambda: os.environ["TELEGRAM_BOT_TOKEN"])
    litellm_master_key: str = Field(default_factory=lambda: os.environ.get("LITELLM_API_KEY", ""))
    
    class Config:
        env_file = ".env"
```

### 10.3 Authorization Model

```
┌─────────────────────────────────────────────────────┐
│                   AUTH MODEL                         │
│                                                     │
│  Telegram User ──────► n8n ──────► Workspace API   │
│  (chat_id = identity)  (validates)  (checks perms)  │
│                                                     │
│  Terax User ──────────► LiteLLM ──► Models         │
│  (local session)        (master key)                 │
│                                                     │
│  Hermes User ─────────► Workspace API ──► Tasks     │
│  (device_id = identity) (checks workspace access)   │
│                                                     │
│  MiMo Agent ──────────► Workspace API ──► Tasks     │
│  (agent_id = identity)  (agent permissions)         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 10.4 Security Controls

| Control | Implementation | Location |
|---------|---------------|----------|
| Rate limiting | Redis-based token bucket | `components/workspace/app/api/middleware/` |
| Input validation | Pydantic models on all endpoints | `components/workspace/app/schemas/` |
| Command injection prevention | Sanitize all shell commands in n8n | n8n workflow nodes |
| API key rotation | Environment variable based | `.env` file |
| WebSocket auth | Token validation on connect | `components/workspace/app/api/websocket/handler.py` |
| Telegram webhook verification | HMAC signature check | n8n Telegram receiver workflow |
| Model output sanitization | Strip dangerous content | PipelineService evaluation step |
| OSC 777 injection prevention | Validate marker format | Terax bridge script |

### 10.5 Audit Trail

```python
# Every task gets a full audit trail
{
  "task_id": "uuid",
  "audit": [
    {"timestamp": "...", "action": "created", "actor": "telegram:user:123456789"},
    {"timestamp": "...", "action": "delegated", "actor": "system", "details": {"agent": "code", "model": "ollama/qwen2.5-coder:7b"}},
    {"timestamp": "...", "action": "started", "actor": "mimo:agent:code"},
    {"timestamp": "...", "action": "completed", "actor": "mimo:agent:code", "details": {"duration_ms": 12000, "tokens": 1500}},
  ]
}
```

---

## 11. Testing Strategy

### 11.1 Test Levels

| Level | Scope | Tools | Coverage Target |
|-------|-------|-------|----------------|
| Unit | Individual functions/classes | pytest, pytest-asyncio | 80% |
| Integration | Component interactions | httpx, websockets, testcontainers | Key flows |
| E2E | Full user journey | Real services (dev mode) | Happy paths |
| Contract | API compatibility | schemathesis, hypothesis | All endpoints |

### 11.2 Test Files

```python
# tests/test_workspace_worktree.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_worktree(client: AsyncClient):
    """Creating a worktree creates session and returns config."""
    resp = await client.post("/workspaces/w1/worktrees", json={
        "name": "frontend",
        "git_path": "/mnt/d/Projects/frontend",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "frontend"
    assert data["session_id"] is not None

@pytest.mark.asyncio
async def test_switch_worktree(client: AsyncClient):
    """Switching worktrees updates current context."""
    # Create two worktrees
    wt1 = await client.post("/workspaces/w1/worktrees", json={"name": "frontend", "git_path": "/a"})
    wt2 = await client.post("/workspaces/w1/worktrees", json={"name": "backend", "git_path": "/b"})
    
    # Switch to backend
    resp = await client.post(f"/workspaces/w1/worktrees/{wt2.json()['id']}/switch")
    assert resp.status_code == 200
    assert resp.json()["git_path"] == "/b"

@pytest.mark.asyncio
async def test_task_with_dependencies(client: AsyncClient):
    """Subtask with depends_on waits for parent."""
    parent = await client.post("/tasks", json={
        "workspace_id": "w1", "title": "Parent", "agent_type": "code"
    })
    child = await client.post("/tasks", json={
        "workspace_id": "w1", "title": "Child", "agent_type": "review",
        "depends_on": [parent.json()["id"]]
    })
    assert child.json()["status"] == "pending"
```

```python
# tests/test_n8n_workflows.py
import pytest

@pytest.mark.asyncio
async def test_telegram_receiver_creates_task():
    """Telegram webhook creates task in Workspace API."""
    resp = await httpx.post("http://localhost:5678/webhook/telegram-receive", json={
        "message_id": 1,
        "chat": {"id": 123456789},
        "text": "/prompt add auth",
    })
    assert resp.status_code == 200
    assert "task_id" in resp.json()

@pytest.mark.asyncio
async def test_health_monitor_alerts_on_failure():
    """Health monitor detects Ollama down and alerts."""
    # Simulate Ollama down
    with patch("httpx.get", side_effect=ConnectionError):
        resp = await httpx.post("http://localhost:5678/webhook/health-check")
        assert resp.status_code == 200
```

```python
# tests/test_telegram_e2e.py
import pytest

@pytest.mark.asyncio
async def test_full_telegram_flow():
    """User sends prompt → task created → result sent back."""
    # 1. Send prompt via Telegram
    resp = await send_telegram_message("/prompt list all Python files")
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]
    
    # 2. Wait for task completion (poll)
    for _ in range(30):  # 30 seconds max
        status = await httpx.get(f"http://localhost:8080/tasks/{task_id}")
        if status.json()["status"] == "completed":
            break
        await asyncio.sleep(1)
    
    # 3. Verify notification sent to Telegram
    notifications = await get_telegram_notifications()
    assert any(task_id in n["text"] for n in notifications)
```

```python
# tests/test_terax_mimo_bridge.py
import pytest

def test_osc777_marker_parsing():
    """OSC 777 markers are correctly parsed."""
    from terax_bridge import parse_osc777
    
    line = "\033]777;ai-complete;{\"result\":\"done\",\"task_id\":\"123\"}\007"
    marker = parse_osc777(line)
    assert marker["type"] == "ai-complete"
    assert marker["data"]["task_id"] == "123"

def test_mimo_bridge_launches_correctly():
    """MiMo launched with correct args."""
    from terax_bridge import build_mimo_command
    
    cmd = build_mimo_command("add auth", format="osc777")
    assert "mimo" in cmd
    assert "--format" in cmd
    assert "osc777" in cmd
```

### 11.3 Running Tests

```bash
# All tests
pytest tests/ -v

# Workspace API tests only
pytest tests/test_workspace_worktree.py -v

# n8n workflow tests (requires running services)
pytest tests/test_n8n_workflows.py -v -m integration

# E2E tests (requires all services)
pytest tests/test_telegram_e2e.py -v -m e2e

# With coverage
pytest tests/ --cov=components/workspace --cov-report=html
```

### 11.4 CI/CD Integration

```yaml
# .github/workflows/integration.yml
name: Integration Tests
on: [push, pull_request]

jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --ignore=tests/test_n8n* --ignore=tests/test_telegram* --ignore=tests/test_terax*

  integration:
    runs-on: ubuntu-latest
    services:
      postgres: {image: postgres:16, env: {POSTGRES_PASSWORD: test}}
      redis: {image: redis:7}
      qdrant: {image: qdrant/qdrant}
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[dev]"
      - run: pytest tests/test_workspace*.py -v -m integration
```

---

## Appendix: Quick Reference

### Port Map

| Port | Service | Protocol |
|------|---------|----------|
| 4000 | LiteLLM Proxy | HTTP (OpenAI) |
| 5432 | PostgreSQL | TCP |
| 5678 | n8n | HTTP |
| 6379 | Redis (main) | TCP |
| 6380 | Redis (workspace) | TCP |
| 6333 | Qdrant | HTTP |
| 8000 | ai-workstation Gateway | HTTP |
| 8080 | Workspace API | HTTP/WS |
| 8081 | Hermes | WS |
| 11434 | Ollama | HTTP |

### Service Health Check Commands

```bash
# LiteLLM
curl http://localhost:4000/health

# Workspace API
curl http://localhost:8080/health

# ai-workstation Gateway
curl http://localhost:8000/health

# Ollama
curl http://localhost:11434/api/tags

# PostgreSQL
docker exec awe-postgresql pg_isready

# Redis
docker exec awe-redis redis-cli ping

# Qdrant
curl http://localhost:6333/healthz

# n8n
curl http://localhost:5678/healthz
```

### Quick Start

```bash
# 1. Start all services
docker compose -f components/workspace/docker-compose.yaml up -d
docker exec awe-n8n n8n import:workflow --input=components/mimo/n8n-workflows/telegram-receiver.json

# 2. Generate MCP configs
./bootstrap mcp-generate mimo

# 3. Enable Headroom
./bootstrap mcp-enable headroom

# 4. Import n8n workflows
./bootstrap mcp-generate mimo

# 5. Start Telegram bot
TELEGRAM_BOT_TOKEN=<token> python components/telegram/bot/handler.py

# 6. Test
curl -X POST http://localhost:8080/tasks -H "Content-Type: application/json" \
  -d '{"workspace_id":"w1","title":"test","agent_type":"code"}'
```
