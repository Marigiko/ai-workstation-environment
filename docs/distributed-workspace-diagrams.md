# Distributed AI Workspace - Diagramas de Flujo

## 1. Flujo Completo: Inicio de Sesión en Notebook, Continuación en Desktop

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FLUJO DE SESIÓN MULTI-DISPOSITIVO               │
└─────────────────────────────────────────────────────────────────────────┘

NOTEBOOK                              WORKSPACE MANAGER                     DESKTOP
    │                                        │                                  │
    │  1. POST /sessions                     │                                  │
    │  { workspace_id: "ws_123" }            │                                  │
    ├───────────────────────────────────────→│                                  │
    │                                        │                                  │
    │  2. 201 Created                        │                                  │
    │  { session_id: "sess_abc" }            │                                  │
    │←───────────────────────────────────────┤                                  │
    │                                        │                                  │
    │  3. POST /sessions/sess_abc/messages   │                                  │
    │  { role: "user", content: "..." }      │                                  │
    ├───────────────────────────────────────→│                                  │
    │                                        │  4. Save message                 │
    │                                        │  5. Load context                 │
    │                                        │  6. Call LiteLLM                 │
    │                                        │  7. Save response                │
    │                                        │                                  │
    │  8. WebSocket: session.message.new     │                                  │
    │←───────────────────────────────────────┤                                  │
    │                                        │                                  │
    │  9. User switches to Desktop           │                                  │
    │                                        │                                  │
    │                                        │  10. POST /sessions/sess_abc/    │
    │                                        │      migrate                     │
    │                                        │  { target_device: "desktop" }    │
    │                                        ├─────────────────────────────────→│
    │                                        │                                  │
    │                                        │  11. Pause on notebook           │
    │                                        │  12. Create checkpoint           │
    │                                        │  13. Transfer state              │
    │                                        │                                  │
    │                                        │  14. WebSocket: session.migrated │
    │  15. Notify notebook                   │←─────────────────────────────────┤
    │←───────────────────────────────────────┤                                  │
    │                                        │                                  │
    │                                        │  16. WebSocket: session.resumed  │
    │                                        │─────────────────────────────────→│
    │                                        │                                  │
    │                                        │  17. POST /sessions/sess_abc/    │
    │                                        │      messages                    │
    │                                        │  { role: "user", content: "..." }│
    │                                        ├─────────────────────────────────→│
    │                                        │                                  │
    │                                        │  18. Continue conversation       │
    │                                        │  (same context, same history)    │
    │                                        │                                  │
    │                                        │  19. WebSocket: session.message  │
    │                                        │─────────────────────────────────→│
    │                                        │                                  │
```

## 2. Flujo de Tarea con Notificaciones

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE TAREA CON NOTIFICACIONES                    │
└─────────────────────────────────────────────────────────────────────────┘

ANDROID                           WORKSPACE MANAGER                      NOTEBOOK
    │                                        │                                │
    │  1. POST /tasks                        │                                │
    │  { title: "Run benchmark",             │                                │
    │    workflow: "benchmark" }             │                                │
    ├───────────────────────────────────────→│                                │
    │                                        │                                │
    │  2. 201 Created                        │                                │
    │  { task_id: "task_xyz" }               │                                │
    │←───────────────────────────────────────┤                                │
    │                                        │                                │
    │                                        │  3. Assign to agent            │
    │                                        │  4. Start execution            │
    │                                        │                                │
    │  5. WebSocket: task.started            │                                │
    │←───────────────────────────────────────┤                                │
    │                                        │                                │
    │  6. User puts phone away               │                                │
    │                                        │                                │
    │                                        │  7. Execute benchmark          │
    │                                        │  8. Progress: 25%              │
    │                                        │  9. Progress: 50%              │
    │                                        │  10. Progress: 75%             │
    │                                        │  11. Progress: 100%            │
    │                                        │                                │
    │                                        │  12. Emit task.completed       │
    │                                        │                                │
    │                                        │  13. Notification Service      │
    │                                        │      receives event            │
    │                                        │                                │
    │                                        │  14. Evaluate alert rules      │
    │                                        │                                │
    │                                        │  15. Send to notebook          │
    │                                        │───────────────────────────────→│
    │                                        │                                │
    │                                        │  16. Push notification         │
    │                                        │  "Benchmark completed"         │
    │                                        │                                │
    │  17. Push notification                 │                                │
    │  "Benchmark completed"                 │                                │
    │←───────────────────────────────────────┤                                │
    │                                        │                                │
    │  18. User taps notification            │                                │
    │  on notebook                           │                                │
    │                                        │                                │
    │                                        │  19. GET /tasks/task_xyz       │
    │                                        │←───────────────────────────────┤
    │                                        │                                │
    │                                        │  20. Return task details       │
    │                                        │  + results + logs              │
    │                                        │───────────────────────────────→│
    │                                        │                                │
```

## 3. Flujo de Migración de Dispositivo con Offline

```
┌─────────────────────────────────────────────────────────────────────────┐
│              FLUJO DE MIGRACIÓN CON PERIODO OFFLINE                     │
└─────────────────────────────────────────────────────────────────────────┘

NOTEBOOK (ONLINE)              WORKSPACE MANAGER              DESKTOP (OFFLINE)
    │                                    │                              │
    │  1. Active session                 │                              │
    │  2. Working on task                │                              │
    │                                    │                              │
    │  3. Lose connection                │                              │
    │  ╳ ╳ ╳ ╳ ╳ ╳ ╳ ╳ ╳ ╳ ╳           │                              │
    │                                    │                              │
    │  4. Queue operations locally       │                              │
    │  - message_1                       │                              │
    │  - message_2                       │                              │
    │                                    │                              │
    │  5. Desktop comes online           │                              │
    │                                    │                              │
    │                                    │  6. Device registered        │
    │                                    │←─────────────────────────────┤
    │                                    │                              │
    │                                    │  7. Load session state       │
    │                                    │  8. Ready to receive         │
    │                                    │                              │
    │  9. Notebook reconnects            │                              │
    │                                    │                              │
    │  10. Sync queued operations        │                              │
    │  POST /sessions/sess_abc/sync      │                              │
    │  { messages: [msg_1, msg_2],       │                              │
    │    last_sequence: 5 }              │                              │
    ├───────────────────────────────────→│                              │
    │                                    │                              │
    │                                    │  11. Validate sequence       │
    │                                    │  12. Apply messages          │
    │                                    │  13. Check for conflicts     │
    │                                    │  14. Return new sequence     │
    │                                    │                              │
    │  15. 200 OK                        │                              │
    │  { sequence: 7,                    │                              │
    │    new_messages: [] }              │                              │
    │←───────────────────────────────────┤                              │
    │                                    │                              │
    │                                    │  16. WebSocket: sync update  │
    │                                    │─────────────────────────────→│
    │                                    │                              │
    │                                    │  17. Desktop receives        │
    │                                    │      latest state            │
    │                                    │                              │
    │  18. Migrate to desktop            │                              │
    │  POST /sessions/sess_abc/migrate   │                              │
    ├───────────────────────────────────→│                              │
    │                                    │                              │
    │                                    │  19. Complete migration      │
    │                                    │─────────────────────────────→│
    │                                    │                              │
```

## 4. Arquitectura de Componentes con Flujos de Datos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA COMPLETA CON FLUJOS                     │
└─────────────────────────────────────────────────────────────────────────┘

CLIENTS
──────────────────────────────────────────────────────────────────────────
│ Hermes │ Mimo │ OpenCode │ Claude Code │ Web UI │ Android │ CLI │
└────┬───┴──┬───┴────┬─────┴──────┬──────┴───┬────┴────┬────┴──┬───┘
     │      │        │            │          │         │       │
     └──────┴────────┴────────────┴──────────┴─────────┴───────┘
                                    │
                           ┌────────┴────────┐
                           │   API Gateway   │
                           │  (Load Balance) │
                           └────────┬────────┘
                                    │
WORKSPACE LAYER
──────────────────────────────────────────────────────────────────────────
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│  Workspace  │            │   Session   │            │    Task     │
│   Manager   │            │   Manager   │            │   Manager   │
└──────┬──────┘            └──────┬──────┘            └──────┬──────┘
       │                          │                          │
       │    ┌─────────────────────┼─────────────────────┐    │
       │    │                     │                     │    │
       ▼    ▼                     ▼                     ▼    ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│  Presence   │            │    Sync     │            │ Notification│
│   Service   │            │   Engine    │            │   Service   │
└──────┬──────┘            └──────┬──────┘            └──────┬──────┘
       │                          │                          │
       └──────────────────────────┼──────────────────────────┘
                                  │
                                  ▼
                           ┌─────────────┐
                           │  Event Bus  │
                           │ (Redis Pub/ │
                           │   Sub)      │
                           └──────┬──────┘
                                  │
AI ENGINEERING PLATFORM
──────────────────────────────────────────────────────────────────────────
                                  │
     ┌────────────────────────────┼────────────────────────────┐
     │                            │                            │
     ▼                            ▼                            ▼
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│   Context   │          │     RAG     │          │   Workflow  │
│   Engine    │          │   Engine    │          │   Engine    │
└──────┬──────┘          └──────┬──────┘          └──────┬──────┘
       │                        │                        │
       ▼                        ▼                        ▼
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│   Memory    │          │   Qdrant    │          │    n8n      │
│   System    │          │  (Vector)   │          │ (Automate)  │
└──────┬──────┘          └─────────────┘          └─────────────┘
       │
       ▼
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│   Model     │          │   LiteLLM   │          │    MCP      │
│   Router    │─────────→│   (Proxy)   │          │   Servers   │
└─────────────┘          └──────┬──────┘          └─────────────┘
                                │
       ┌────────────────────────┼────────────────────────┐
       │                        │                        │
       ▼                        ▼                        ▼
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│   Ollama    │          │   Claude    │          │    GPT-4    │
│   (Local)   │          │             │          │             │
└─────────────┘          └─────────────┘          └─────────────┘

STORAGE LAYER
──────────────────────────────────────────────────────────────────────────
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│ PostgreSQL  │          │    Redis    │          │   Qdrant    │
│ (Sessions,  │          │  (Cache,    │          │  (Vectors,  │
│  Tasks,     │          │   Pub/Sub,  │          │   Context,  │
│  Workflows) │          │   Queue)    │          │   RAG)      │
└─────────────┘          └─────────────┘          └─────────────┘
```

## 5. Flujo de Eventos (Event-Driven Architecture)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE EVENTOS (EVENT BUS)                         │
└─────────────────────────────────────────────────────────────────────────┘

PRODUCERS                    EVENT BUS                    CONSUMERS
─────────────                ─────────                    ─────────

Session Manager              ┌─────────────┐              Notification Service
  │                          │             │                │
  │ session.message.new      │   Redis     │                │
  ├─────────────────────────→│   Pub/Sub   │───────────────→│
  │                          │             │                │
  │                          │             │                Task Manager
  │                          │             │                │
  │                          │             │←───────────────┤
  │                          │             │  task.progress │
  │                          │             │                │
  │                          │             │                Presence Service
  │                          │             │                │
  │                          │             │←───────────────┤
  │                          │             │  device.online │
  │                          │             │                │
  │                          │             │                Workflow Engine
  │                          │             │                │
  │                          │             │←───────────────┤
  │                          │             │  task.completed│
  │                          │             │                │
  │                          └─────────────┘                │
  │                                                         │
  │                                                         │
  └─────────────────────────────────────────────────────────┘

EVENT TYPES
─────────────

Session Events:
  • session.created
  • session.message.new
  • session.paused
  • session.resumed
  • session.migrated
  • session.checkpoint.created
  • session.archived

Task Events:
  • task.created
  • task.started
  • task.progress
  • task.paused
  • task.resumed
  • task.completed
  • task.failed
  • task.cancelled

Workflow Events:
  • workflow.started
  • workflow.step.completed
  • workflow.completed
  • workflow.failed

Presence Events:
  • device.online
  • device.offline
  • user.active
  • user.idle

Notification Events:
  • notification.sent
  • notification.delivered
  • notification.read
```

## 6. Estado de Sesión y Transiciones

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MÁQUINA DE ESTADOS DE SESIÓN                         │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────────┐
                    │                                  │
                    ▼                                  │
              ┌──────────┐                             │
              │ Created  │                             │
              └────┬─────┘                             │
                   │                                   │
                   │ start()                           │
                   ▼                                   │
              ┌──────────┐                             │
         ┌───→│  Active  │◄────────────────┐          │
         │    └────┬─────┘                 │          │
         │         │                       │          │
         │         │ pause()               │          │
         │         │                       │          │
         │         ▼                       │          │
         │    ┌──────────┐                 │          │
         │    │  Paused  │─────────────────┘          │
         │    └────┬─────┘      resume()              │
         │         │                                   │
         │         │ migrate()                         │
         │         │                                   │
         │         ▼                                   │
         │    ┌──────────┐                             │
         │    │ Migrating│─────────────────────────────┘
         │    └──────────┘      migrated()
         │
         │ archive()
         │
         ▼
    ┌──────────┐
    │ Archived │
    └──────────┘

TRANSITIONS
───────────

Created → Active:
  Trigger: First message sent
  Action: Initialize context, assign device

Active → Paused:
  Trigger: User pauses or device switches
  Action: Save checkpoint, release resources

Paused → Active:
  Trigger: User resumes
  Action: Load checkpoint, restore context

Active → Migrating:
  Trigger: User switches device
  Action: Prepare state transfer

Migrating → Active:
  Trigger: State transferred successfully
  Action: Resume on new device

Active → Archived:
  Trigger: Session completed or expired
  Action: Final checkpoint, cleanup resources
```

## 7. Estado de Tarea y Transiciones

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MÁQUINA DE ESTADOS DE TAREA                          │
└─────────────────────────────────────────────────────────────────────────┘

              ┌──────────┐
              │ Pending  │
              └────┬─────┘
                   │
                   │ assign()
                   ▼
              ┌──────────┐
         ┌───→│ Running  │◄────────────────┐
         │    └────┬─────┘                 │
         │         │                       │
    ┌────┴────┐    │ pause()         resume()
    │         │    │                       │
    │         ▼    │                       │
    │    ┌──────────┐                      │
    │    │  Paused  │──────────────────────┘
    │    └────┬─────┘
    │         │
    │         │ cancel()
    │         │
    │         ▼
    │    ┌──────────┐
    │    │Cancelled │
    │    └──────────┘
    │
    │         │ complete()
    │         │
    │         ▼
    │    ┌──────────┐
    │    │Completed │
    │    └──────────┘
    │
    │         │ fail()
    │         │
    └────────→┌──────────┐
              │  Failed  │
              └──────────┘

TRANSITIONS
───────────

Pending → Running:
  Trigger: Agent assigned and starts
  Action: Record start time, emit task.started

Running → Paused:
  Trigger: User pauses or resource constraint
  Action: Save intermediate state, emit task.paused

Paused → Running:
  Trigger: User resumes
  Action: Restore state, emit task.resumed

Running → Completed:
  Trigger: Task finishes successfully
  Action: Calculate metrics, save results, emit task.completed

Running → Failed:
  Trigger: Error or timeout
  Action: Save error info, emit task.failed

Running → Cancelled:
  Trigger: User cancels
  Action: Cleanup resources, emit task.cancelled

Failed → Running:
  Trigger: User restarts
  Action: Reset state, re-queue, emit task.restarted
```

## 8. Flujo de Notificaciones

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE NOTIFICACIONES                              │
└─────────────────────────────────────────────────────────────────────────┘

EVENT OCCURS
     │
     ▼
┌─────────────┐
│ Event Bus   │
│ (Redis)     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Notification Service                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Receive event                                               │
│     │                                                           │
│     ▼                                                           │
│  2. Load alert rules                                            │
│     │                                                           │
│     ▼                                                           │
│  3. Evaluate conditions                                         │
│     │                                                           │
│     ├─→ No match → Discard                                      │
│     │                                                           │
│     ▼                                                           │
│  4. Determine targets                                           │
│     │                                                           │
│     ├─→ Users                                                   │
│     ├─→ Devices                                                 │
│     └─→ Channels                                                │
│     │                                                           │
│     ▼                                                           │
│  5. Format notifications                                        │
│     │                                                           │
│     ├─→ Push (WebSocket/SSE)                                    │
│     ├─→ Email                                                   │
│     ├─→ SMS                                                     │
│     └─→ Webhook (Slack, Discord, Telegram)                      │
│     │                                                           │
│     ▼                                                           │
│  6. Send notifications                                          │
│     │                                                           │
│     ├─→ Track delivery status                                   │
│     ├─→ Retry on failure (exponential backoff)                  │
│     └─→ Log results                                             │
│     │                                                           │
│     ▼                                                           │
│  7. Emit notification.sent event                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Delivery Channels                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  WebSocket  │  │     SSE     │  │    Email    │            │
│  │  (Real-time)│  │  (Fallback) │  │   (Async)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │     SMS     │  │    Slack    │  │  Telegram   │            │
│  │  (Critical) │  │  (Webhook)  │  │  (Webhook)  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

**Nota:** Estos diagramas muestran los flujos principales del sistema. Cada flujo está diseñado para ser:
- **Confiable**: Con reintentos y confirmaciones
- **Escalable**: Event-driven y desacoplado
- **Observable**: Con logs y métricas en cada paso
- **Resiliente**: Con manejo de errores y fallbacks
