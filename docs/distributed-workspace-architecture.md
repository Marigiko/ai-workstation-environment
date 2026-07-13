# Distributed AI Workspace - Arquitectura Completa

## 1. Visión y Objetivos

### Visión
Construir un **Distributed AI Workspace** donde toda la infraestructura funcione como un único entorno de trabajo distribuido. Cualquier dispositivo puede iniciar, continuar, supervisar o finalizar cualquier flujo de trabajo sin perder contexto y sin depender de una interfaz específica.

### Objetivos

| Objetivo | Descripción |
|----------|-------------|
| **Stateless Clients** | Los clientes NO almacenan estado, solo visualizan e interactúan |
| **Platform-Centric State** | Todo el estado vive en la plataforma |
| **Device Agnostic** | Cualquier dispositivo puede continuar cualquier flujo |
| **Real-Time Sync** | Sincronización en tiempo real de sesiones, tareas y contexto |
| **Event-Driven** | Arquitectura basada en eventos para desacoplamiento |
| **Observable** | Monitoreo, métricas y logs centralizados |
| **Extensible** | Fácil agregar nuevos clientes y capacidades |

### Anti-Patterns a Evitar

- ❌ Sincronización manual de chats
- ❌ Control remoto de escritorio
- ❌ Clientes como fuente de verdad
- ❌ Acoplamiento fuerte con un frontend específico
- ❌ Estado efímero en memoria

---

## 2. Principios de Diseño

### 2.1 Single Source of Truth

**Principio:** Todo el estado vive en la plataforma. Los clientes son vistas.

```
┌─────────────┐
│   Client    │ ──→ Lee estado
│  (Hermes)   │ ←── Recibe actualizaciones
└─────────────┘
        │
        ▼
┌─────────────────────┐
│  Workspace Manager  │ ←── Fuente de verdad
│   (Backend)         │
└─────────────────────┘
```

**Tradeoff:** Mayor latencia vs. consistencia garantizada.

### 2.2 Event-Driven Architecture

**Principio:** Los módulos se comunican via eventos, no llamadas directas.

```
┌──────────┐    Event    ┌──────────┐
│  Module  │ ──────────→ │  Module  │
│    A     │             │    B     │
└──────────┘             └──────────┘
```

**Beneficios:**
- Desacoplamiento
- Escalabilidad
- Observabilidad
- Replay de eventos

**Tradeoff:** Mayor complejidad vs. flexibilidad.

### 2.3 CQRS (Command Query Responsibility Segregation)

**Principio:** Separar operaciones de escritura (commands) de lectura (queries).

```
┌─────────┐         ┌──────────────┐
│ Client  │ ──────→ │ Command Side │ ──→ Write DB
└─────────┘         └──────────────┘
                            │
                          Event
                            │
                            ▼
┌─────────┐         ┌──────────────┐
│ Client  │ ←────── │  Query Side  │ ←── Read DB
└─────────┘         └──────────────┘
```

**Beneficios:**
- Optimización independiente
- Escalabilidad
- Consistencia eventual

**Tradeoff:** Complejidad adicional vs. rendimiento.

### 2.4 Offline-First con Conflict Resolution

**Principio:** Los clientes pueden operar offline y sincronizar después.

**Estrategia:**
- Operaciones en cola local
- Timestamps y vector clocks
- Conflict resolution strategies (last-write-wins, merge, manual)

**Tradeoff:** Complejidad de resolución de conflictos vs. resiliencia.

---

## 3. Arquitectura General

### 3.1 Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTS LAYER                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Hermes  │  │  Mimo    │  │ OpenCode │  │  Claude  │   │
│  │ Desktop  │  │   CLI    │  │   CLI    │  │   Code   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │  Hermes  │  │  Web UI  │  │   CLI    │  │  Future  │   │
│  │ Android  │  │          │  │          │  │ Clients  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
└───────┼──────────────┼──────────────┼──────────────┼─────────┘
        │              │              │              │
        └──────────────┴──────────────┴──────────────┘
                           │
                    ┌──────┴──────┐
                    │   Gateway   │
                    │   (API)     │
                    └──────┬──────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                   WORKSPACE LAYER                            │
├──────────────────────────┼──────────────────────────────────┤
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐ │
│  │              Workspace Manager                         │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │ Workspace│  │  Device  │  │  User    │            │ │
│  │  │ Registry │  │ Registry │  │  Manager │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └───────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐ │
│  │               Session Manager                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │ Session  │  │ Checkpoint│ │  Sync    │            │ │
│  │  │  State   │  │  Manager │  │  Engine  │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └───────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐ │
│  │                Task Manager                            │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │   Task   │  │ Progress │  │  Agent   │            │ │
│  │  │  Queue   │  │ Tracker  │  │ Registry │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └───────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐ │
│  │              Workflow Engine                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │ Workflow │  │  Step    │  │  Event   │            │ │
│  │  │  Runner  │  │ Executor │  │  Handler │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └───────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐ │
│  │            Notification Service                        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │  Event   │  │  Push    │  │  Alert   │            │ │
│  │  │  Router  │  │ Service  │  │  Rules   │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └───────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐ │
│  │              Presence Service                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │  Device  │  │  User    │  │ Activity │            │ │
│  │  │  Status  │  │  Status  │  │  Monitor │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └───────────────────────────────────────────────────────┘ │
│                          │                                   │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                AI ENGINEERING PLATFORM                       │
├──────────────────────────┼──────────────────────────────────┤
│                          │                                   │
│  ┌──────────┐  ┌─────────┴────────┐  ┌──────────┐         │
│  │  Model   │  │    Context       │  │   RAG    │         │
│  │  Router  │  │    Engine        │  │  Engine  │         │
│  │(LiteLLM) │  │                  │  │(Qdrant)  │         │
│  └──────────┘  └──────────────────┘  └──────────┘         │
│                          │                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Memory  │  │   MCP    │  │   Eval   │  │   Obs    │   │
│  │  System  │  │  Servers │  │  Engine  │  │  System  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                          │                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Ollama  │  │  Claude  │  │   GPT    │  │  Gemini  │   │
│  │ (Local)  │  │          │  │          │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                          │                                   │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Storage   │
                    │             │
                    │ PostgreSQL  │
                    │   Redis     │
                    │   Qdrant    │
                    └─────────────┘
```

### 3.2 Flujo de Datos Típico

```
Usuario en Notebook                Workspace Manager
     │                                    │
     │  1. Iniciar sesión                 │
     ├───────────────────────────────────→│
     │                                    │
     │  2. Session created                │
     │←───────────────────────────────────┤
     │                                    │
     │  3. Enviar mensaje                 │
     ├───────────────────────────────────→│
     │                                    │
     │                              4. Guardar mensaje
     │                              5. Seleccionar modelo
     │                              6. Ejecutar inference
     │                              7. Guardar respuesta
     │                                    │
     │  8. Streaming response             │
     │←───────────────────────────────────┤
     │                                    │
     │  9. Cambiar a Desktop              │
     ├───────────────────────────────────→│
     │                                    │
     │                              10. Load session state
     │                              11. Resume context
     │                                    │
     │  12. Continuar conversación        │
     │←───────────────────────────────────┤
     │                                    │
```

---

## 4. Módulos y Responsabilidades

### 4.1 Workspace Manager

**Responsabilidad:** Administrar workspaces, dispositivos, usuarios y su relación.

```
┌─────────────────────────────────────────┐
│         Workspace Manager               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │      Workspace Registry          │  │
│  │  - CRUD workspaces               │  │
│  │  - Workspace metadata            │  │
│  │  - Access control                │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Device Registry            │  │
│  │  - Device registration           │  │
│  │  - Device capabilities           │  │
│  │  - Device status                 │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │        User Manager              │  │
│  │  - User profiles                 │  │
│  │  - Preferences                   │  │
│  │  - Authentication                │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │     Workspace Context            │  │
│  │  - Shared files                  │  │
│  │  - Shared variables              │  │
│  │  - Shared configuration          │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**APIs:**
```
POST   /workspaces
GET    /workspaces
GET    /workspaces/{id}
PUT    /workspaces/{id}
DELETE /workspaces/{id}

POST   /workspaces/{id}/devices
GET    /workspaces/{id}/devices
DELETE /workspaces/{id}/devices/{device_id}

POST   /workspaces/{id}/invite
```

**Eventos Emitidos:**
- `workspace.created`
- `workspace.updated`
- `workspace.deleted`
- `device.registered`
- `device.online`
- `device.offline`

### 4.2 Session Manager

**Responsabilidad:** Gestionar el ciclo de vida completo de las sesiones.

```
┌─────────────────────────────────────────┐
│          Session Manager                │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │        Session State             │  │
│  │  - Session metadata              │  │
│  │  - Message history               │  │
│  │  - Tool calls                    │  │
│  │  - Agent state                   │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │      Checkpoint Manager          │  │
│  │  - Auto checkpoints              │  │
│  │  - Manual checkpoints            │  │
│  │  - Checkpoint restore            │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │        Sync Engine               │  │
│  │  - Real-time sync                │  │
│  │  - Conflict resolution           │  │
│  │  - Offline queue                 │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │      Session Migration           │  │
│  │  - Device migration              │  │
│  │  - State transfer                │  │
│  │  - Context preservation          │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**Estados de Sesión:**
```
     ┌─────────┐
     │ Created │
     └────┬────┘
          │
          ▼
     ┌─────────┐
     │  Active │◄───────┐
     └────┬────┘        │
          │             │
     ┌────┴────┐        │
     │         │        │
     ▼         ▼        │
┌────────┐ ┌────────┐   │
│Paused  │ │Migrating│───┘
└────┬───┘ └────────┘
     │
     ▼
┌─────────┐
│Archived │
└─────────┘
```

**APIs:**
```
POST   /sessions
GET    /sessions
GET    /sessions/{id}
DELETE /sessions/{id}

POST   /sessions/{id}/messages
GET    /sessions/{id}/messages

POST   /sessions/{id}/pause
POST   /sessions/{id}/resume
POST   /sessions/{id}/migrate

POST   /sessions/{id}/checkpoints
GET    /sessions/{id}/checkpoints
POST   /sessions/{id}/checkpoints/{id}/restore
```

**Eventos Emitidos:**
- `session.created`
- `session.message.added`
- `session.paused`
- `session.resumed`
- `session.migrated`
- `session.checkpoint.created`
- `session.archived`

### 4.3 Task Manager

**Responsabilidad:** Gestionar tareas, progreso, agentes y métricas.

```
┌─────────────────────────────────────────┐
│           Task Manager                  │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │         Task Queue               │  │
│  │  - Task creation                 │  │
│  │  - Priority management           │  │
│  │  - Task assignment               │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Progress Tracker           │  │
│  │  - Real-time progress            │  │
│  │  - Percentage tracking           │  │
│  │  - ETA calculation               │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Agent Registry             │  │
│  │  - Available agents              │  │
│  │  - Agent capabilities            │  │
│  │  - Agent assignment              │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │        Metrics Collector         │  │
│  │  - Duration tracking             │  │
│  │  - Cost tracking                 │  │
│  │  - Token usage                   │  │
│  │  - Success/failure rates         │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**Estados de Tarea:**
```
     ┌─────────┐
     │ Pending │
     └────┬────┘
          │
          ▼
     ┌─────────┐
     │ Running │◄───────┐
     └────┬────┘        │
          │             │
     ┌────┴────┐        │
     │         │        │
     ▼         ▼        │
┌────────┐ ┌────────┐   │
│Paused  │ │ Failed │───┘
└────┬───┘ └────────┘
     │
     ▼
┌─────────┐
│Completed│
└─────────┘
```

**APIs:**
```
POST   /tasks
GET    /tasks
GET    /tasks/{id}
PUT    /tasks/{id}
DELETE /tasks/{id}

POST   /tasks/{id}/pause
POST   /tasks/{id}/resume
POST   /tasks/{id}/cancel
POST   /tasks/{id}/restart

GET    /tasks/{id}/logs
GET    /tasks/{id}/metrics

POST   /tasks/{id}/approve
POST   /tasks/{id}/reject
```

**Eventos Emitidos:**
- `task.created`
- `task.started`
- `task.progress`
- `task.paused`
- `task.resumed`
- `task.completed`
- `task.failed`
- `task.cancelled`

### 4.4 Workflow Engine

**Responsabilidad:** Ejecutar workflows complejos con múltiples pasos.

```
┌─────────────────────────────────────────┐
│         Workflow Engine                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Workflow Runner            │  │
│  │  - Workflow execution            │  │
│  │  - Step orchestration            │  │
│  │  - Error handling                │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Step Executor              │  │
│  │  - Step execution                │  │
│  │  - Input/output mapping          │  │
│  │  - Condition evaluation          │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Event Handler              │  │
│  │  - Event subscriptions           │  │
│  │  - Event routing                 │  │
│  │  - Event transformation          │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │     Workflow Templates           │  │
│  │  - Template registry             │  │
│  │  - Template instantiation        │  │
│  │  - Template versioning           │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**APIs:**
```
POST   /workflows
GET    /workflows
GET    /workflows/{id}

POST   /workflows/{id}/execute
POST   /workflows/{id}/pause
POST   /workflows/{id}/resume
POST   /workflows/{id}/cancel

GET    /workflows/{id}/steps
GET    /workflows/{id}/steps/{id}
```

### 4.5 Notification Service

**Responsabilidad:** Gestionar notificaciones push a todos los dispositivos.

```
┌─────────────────────────────────────────┐
│      Notification Service               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │        Event Router              │  │
│  │  - Event filtering               │  │
│  │  - Event transformation          │  │
│  │  - Routing rules                 │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Push Service               │  │
│  │  - WebSocket push                │  │
│  │  - SSE push                      │  │
│  │  - Webhook delivery              │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Alert Rules                │  │
│  │  - Rule definitions              │  │
│  │  - Condition evaluation          │  │
│  │  - Alert templates               │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    Notification History          │  │
│  │  - Sent notifications            │  │
│  │  - Delivery status               │  │
│  │  - Read receipts                 │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**Tipos de Notificación:**
- Task completion
- Task failure
- Workflow completion
- Benchmark results
- Test results
- System alerts
- Presence changes

**APIs:**
```
GET    /notifications
GET    /notifications/{id}
POST   /notifications/{id}/read
POST   /notifications/{id}/dismiss

POST   /notification-rules
GET    /notification-rules
PUT    /notification-rules/{id}
DELETE /notification-rules/{id}

WS     /notifications/stream
SSE    /notifications/events
```

### 4.6 Presence Service

**Responsabilidad:** Rastrear dispositivos activos, usuarios conectados y actividad.

```
┌─────────────────────────────────────────┐
│        Presence Service                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Device Status              │  │
│  │  - Online/offline tracking       │  │
│  │  - Last seen timestamp           │  │
│  │  - Device capabilities           │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       User Status                │  │
│  │  - Active user tracking          │  │
│  │  - Current device                │  │
│  │  - Activity status               │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │     Activity Monitor             │  │
│  │  - User activity tracking        │  │
│  │  - Idle detection                │  │
│  │  - Activity aggregation          │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**APIs:**
```
POST   /presence/heartbeat
GET    /presence/devices
GET    /presence/users
GET    /presence/activity
```

**Eventos Emitidos:**
- `device.online`
- `device.offline`
- `user.active`
- `user.idle`
- `user.switched_device`

---

## 5. Protocolos de Comunicación

### 5.1 Análisis de Protocolos

| Protocolo | Caso de Uso | Ventajas | Desventajas |
|-----------|-------------|----------|-------------|
| **REST** | CRUD operations, commands | Simple, cacheable, universal | Request-response, no push |
| **WebSocket** | Real-time sync, streaming | Bidirectional, low latency | Stateful, complex |
| **SSE** | Server→client events | Simple, HTTP-based, auto-reconnect | Unidirectional |
| **MQTT** | IoT, low-bandwidth | Lightweight, QoS, pub/sub | Overkill for web apps |
| **gRPC** | High-performance RPC | Fast, typed, streaming | Complex, not browser-friendly |

### 5.2 Estrategia Híbrida (Recomendada)

```
┌─────────────────────────────────────────────────────────┐
│                    Protocol Strategy                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Commands (Client → Server)                              │
│  ─────────────────────────────                           │
│  • REST API (JSON)                                       │
│  • POST /sessions/{id}/messages                          │
│  • POST /tasks/{id}/pause                                │
│  • Idempotency keys for reliability                      │
│                                                          │
│  Real-time Updates (Server → Client)                     │
│  ─────────────────────────────────                       │
│  • WebSocket (primary)                                   │
│  • SSE (fallback for restricted networks)                │
│  • Message types:                                        │
│    - session.message.new                                 │
│    - task.progress                                       │
│    - presence.update                                     │
│    - notification.new                                    │
│                                                          │
│  Streaming (Server → Client)                             │
│  ─────────────────────────────                           │
│  • WebSocket with streaming frames                       │
│  • Chunked transfer for LLM responses                    │
│  • Progress indicators for long operations               │
│                                                          │
│  Bulk Operations (Server ↔ Server)                       │
│  ─────────────────────────────────                       │
│  • gRPC for internal services                            │
│  • Event bus (Redis Streams / Kafka)                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 5.3 WebSocket Message Protocol

```json
{
  "type": "session.message.new",
  "id": "msg_abc123",
  "timestamp": "2026-07-06T10:30:00Z",
  "workspace_id": "ws_xyz",
  "payload": {
    "session_id": "sess_123",
    "message": {
      "role": "assistant",
      "content": "Processing your request...",
      "tool_calls": [...]
    }
  },
  "metadata": {
    "model": "claude-sonnet-4-20250514",
    "tokens": 150,
    "latency_ms": 450
  }
}
```

### 5.4 Connection Management

```
┌─────────────────────────────────────────────────────────┐
│              Connection Lifecycle                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Connect                                              │
│     └─→ WebSocket handshake                              │
│     └─→ Authentication (JWT)                             │
│     └─→ Subscribe to channels                            │
│                                                          │
│  2. Active                                               │
│     └─→ Receive real-time updates                        │
│     └─→ Send commands via REST                           │
│     └─→ Heartbeat every 30s                              │
│                                                          │
│  3. Reconnect                                            │
│     └─→ Exponential backoff                              │
│     └─→ Resume from last sequence number                 │
│     └─→ Catch up on missed events                        │
│                                                          │
│  4. Disconnect                                           │
│     └─→ Graceful close                                   │
│     └─→ Mark device offline                              │
│     └─→ Queue messages for later delivery                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Sincronización de Sesiones

### 6.1 Modelo de Datos

```
┌─────────────────────────────────────────────────────────┐
│                   Session Schema                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Session                                                 │
│  ├─ id: UUID                                             │
│  ├─ workspace_id: UUID                                   │
│  ├─ title: String                                        │
│  ├─ status: Enum (active, paused, archived)              │
│  ├─ created_at: Timestamp                                │
│  ├─ updated_at: Timestamp                                │
│  ├─ current_device_id: UUID                              │
│  ├─ checkpoint_id: UUID                                  │
│  ├─ metadata: JSON                                       │
│  │                                                       │
│  ├─ Messages[]                                           │
│  │  ├─ id: UUID                                          │
│  │  ├─ session_id: UUID                                  │
│  │  ├─ role: Enum (user, assistant, system, tool)        │
│  │  ├─ content: String                                   │
│  │  ├─ tool_calls: JSON[]                                │
│  │  ├─ tool_results: JSON[]                              │
│  │  ├─ created_at: Timestamp                             │
│  │  └─ sequence: Integer                                 │
│  │                                                       │
│  ├─ Checkpoints[]                                        │
│  │  ├─ id: UUID                                          │
│  │  ├─ session_id: UUID                                  │
│  │  ├─ state: JSON                                       │
│  │  ├─ created_at: Timestamp                             │
│  │  └─ auto: Boolean                                     │
│  │                                                       │
│  └─ Context                                              │
│     ├─ files: String[]                                   │
│     ├─ variables: JSON                                   │
│     └─ memory_refs: String[]                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Estrategia de Sincronización

```
┌─────────────────────────────────────────────────────────┐
│            Session Sync Strategy                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Option A: Full State Transfer                           │
│  ─────────────────────────────                           │
│  Pros: Simple, consistent                                │
│  Cons: High bandwidth, slow for large sessions           │
│  Use case: Small sessions, initial sync                  │
│                                                          │
│  Option B: Incremental Sync (Recommended)                │
│  ─────────────────────────────────                       │
│  • Track sequence numbers per message                    │
│  • Sync only new messages since last sync                │
│  • Use vector clocks for conflict detection              │
│  • Merge strategy: append-only for messages              │
│                                                          │
│  Option C: CRDT-based Sync                               │
│  ─────────────────────────────                           │
│  • Use CRDTs for collaborative editing                   │
│  • Automatic conflict resolution                         │
│  • Complex to implement                                  │
│  Use case: Real-time collaborative editing               │
│                                                          │
│  Recommended: Option B + CRDT for specific fields        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 6.3 Migración de Dispositivo

```
┌─────────────────────────────────────────────────────────┐
│              Device Migration Flow                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. User initiates migration                             │
│     └─→ POST /sessions/{id}/migrate                      │
│     └─→ { target_device_id: "device_xyz" }               │
│                                                          │
│  2. Workspace Manager validates                          │
│     └─→ Check session status                             │
│     └─→ Check target device online                       │
│     └─→ Create migration record                          │
│                                                          │
│  3. State transfer                                       │
│     └─→ Pause session on source device                   │
│     └─→ Create final checkpoint                          │
│     └─→ Transfer state to target device                  │
│     └─→ Notify target device                             │
│                                                          │
│  4. Resume on target                                     │
│     └─→ Load session state                               │
│     └─→ Restore context                                  │
│     └─→ Resume session                                   │
│     └─→ Notify all devices                               │
│                                                          │
│  5. Cleanup                                              │
│     └─→ Update current_device_id                         │
│     └─→ Remove migration record                          │
│     └─→ Emit session.migrated event                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Sincronización de Tareas

### 7.1 Modelo de Datos

```
┌─────────────────────────────────────────────────────────┐
│                    Task Schema                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Task                                                    │
│  ├─ id: UUID                                             │
│  ├─ workspace_id: UUID                                   │
│  ├─ session_id: UUID (optional)                          │
│  ├─ parent_task_id: UUID (optional)                      │
│  ├─ title: String                                        │
│  ├─ description: String                                  │
│  ├─ status: Enum (pending, running, paused, completed,   │
│  │               failed, cancelled)                       │
│  ├─ priority: Integer                                    │
│  ├─ agent_id: String                                     │
│  ├─ model: String                                        │
│  ├─ progress: Float (0.0 - 1.0)                          │
│  ├─ started_at: Timestamp                                │
│  ├─ completed_at: Timestamp                              │
│  ├─ duration_ms: Integer                                 │
│  ├─ cost_usd: Float                                      │
│  ├─ tokens_used: Integer                                 │
│  ├─ input: JSON                                          │
│  ├─ output: JSON                                         │
│  ├─ error: JSON                                          │
│  ├─ logs: String[]                                       │
│  ├─ metadata: JSON                                       │
│  ├─ created_at: Timestamp                                │
│  └─ updated_at: Timestamp                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Task Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│              Task Execution Flow                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Task Creation                                        │
│     └─→ Client creates task via REST                     │
│     └─→ Task Manager validates and persists              │
│     └─→ Emit task.created event                          │
│                                                          │
│  2. Task Assignment                                      │
│     └─→ Task Queue selects agent                         │
│     └─→ Check agent availability                         │
│     └─→ Assign task to agent                             │
│     └─→ Emit task.assigned event                         │
│                                                          │
│  3. Task Execution                                       │
│     └─→ Agent starts execution                           │
│     └─→ Emit task.started event                          │
│     └─→ Stream progress updates                          │
│     └─→ Emit task.progress events                        │
│     └─→ Log all actions                                  │
│                                                          │
│  4. Task Completion                                      │
│     └─→ Agent completes or fails                         │
│     └─→ Calculate metrics (duration, cost, tokens)       │
│     └─→ Persist results                                  │
│     └─→ Emit task.completed or task.failed               │
│                                                          │
│  5. Notification                                         │
│     └─→ Notification Service receives event              │
│     └─→ Evaluate alert rules                             │
│     └─→ Send notifications to subscribed devices         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 7.3 Remote Actions

```
┌─────────────────────────────────────────────────────────┐
│               Remote Actions on Tasks                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Pause Task                                              │
│  ────────────                                            │
│  POST /tasks/{id}/pause                                  │
│  └─→ Validate task is running                            │
│  └─→ Signal agent to pause                               │
│  └─→ Save intermediate state                             │
│  └─→ Emit task.paused                                    │
│                                                          │
│  Resume Task                                             │
│  ──────────────                                          │
│  POST /tasks/{id}/resume                                 │
│  └─→ Validate task is paused                             │
│  └─→ Restore state                                       │
│  └─→ Signal agent to resume                              │
│  └─→ Emit task.resumed                                   │
│                                                          │
│  Cancel Task                                             │
│  ───────────────                                         │
│  POST /tasks/{id}/cancel                                 │
│  └─→ Signal agent to cancel                              │
│  └─→ Cleanup resources                                   │
│  └─→ Save partial results                                │
│  └─→ Emit task.cancelled                                 │
│                                                          │
│  Restart Task                                            │
│  ────────────────                                        │
│  POST /tasks/{id}/restart                                │
│  └─→ Reset task state                                    │
│  └─→ Clear previous results                              │
│  └─→ Re-queue task                                       │
│  └─→ Emit task.restarted                                 │
│                                                          │
│  Approve/Reject (Human-in-the-loop)                      │
│  ─────────────────────────────                           │
│  POST /tasks/{id}/approve                                │
│  POST /tasks/{id}/reject                                 │
│  └─→ Validate task requires approval                     │
│  └─→ Update task state                                   │
│  └─→ Continue or abort workflow                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Sincronización de Contexto

### 8.1 Tipos de Contexto

```
┌─────────────────────────────────────────────────────────┐
│                 Context Types                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Session Context                                         │
│  ────────────────                                        │
│  • Message history                                       │
│  • Tool call results                                     │
│  • Agent state                                           │
│  • Current files                                         │
│                                                          │
│  Project Context                                         │
│  ─────────────────                                       │
│  • Project files                                         │
│  • Dependencies                                          │
│  • Configuration                                         │
│  • Environment variables                                 │
│                                                          │
│  User Context                                            │
│  ──────────────                                          │
│  • User preferences                                      │
│  • User model (Honcho)                                   │
│  • Past interactions                                     │
│  • Learned patterns                                      │
│                                                          │
│  Shared Context                                          │
│  ────────────────                                        │
│  • Workspace variables                                   │
│  • Shared knowledge base                                 │
│  • Team memories                                         │
│  • Shared workflows                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Context Injection Strategy

```
┌─────────────────────────────────────────────────────────┐
│              Context Injection Flow                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Client sends message                                 │
│     └─→ Include context hints (files, variables)         │
│                                                          │
│  2. Workspace Manager receives                           │
│     └─→ Load session context                             │
│     └─→ Load project context                             │
│     └─→ Load user context                                │
│     └─→ Load shared context                              │
│                                                          │
│  3. Context Engine processes                             │
│     └─→ Relevance scoring                                │
│     └─→ Token budget allocation                          │
│     └─→ Context compression (Headroom)                   │
│     └─→ RAG retrieval (Qdrant)                           │
│                                                          │
│  4. Build final prompt                                   │
│     └─→ System prompt                                    │
│     └─→ User model                                       │
│     └─→ Project context                                  │
│     └─→ Session history                                  │
│     └─→ Retrieved context                                │
│     └─→ User message                                     │
│                                                          │
│  5. Send to LLM                                          │
│     └─→ Model Router selects model                       │
│     └─→ LiteLLM proxies request                          │
│     └─→ Stream response back                             │
│                                                          │
│  6. Update context                                       │
│     └─→ Save new messages                                │
│     └─→ Update memory (if needed)                        │
│     └─→ Update user model                                │
│     └─→ Sync to all devices                              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 8.3 Context Synchronization

```
┌─────────────────────────────────────────────────────────┐
│            Context Sync Strategy                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Eventual Consistency Model                              │
│  ──────────────────────────                              │
│  • Context updates propagate asynchronously              │
│  • Clients receive updates via WebSocket                 │
│  • Conflicts resolved by timestamp (last-write-wins)     │
│  • Critical operations use strong consistency            │
│                                                          │
│  Context Versioning                                      │
│  ────────────────────                                    │
│  • Each context update has version number                │
│  • Clients track last seen version                       │
│  • Sync only new versions                                │
│  • Support rollback to previous versions                 │
│                                                          │
│  Context Compression                                     │
│  ─────────────────────                                   │
│  • Use Headroom for context compression                  │
│  • Compress old context to save tokens                   │
│  • Keep recent context in full detail                    │
│  • Compressed context stored in database                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 9. Sistema de Notificaciones

### 9.1 Notification Types

```
┌─────────────────────────────────────────────────────────┐
│              Notification Types                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Task Notifications                                      │
│  ────────────────────                                    │
│  • task.completed - Tarea finalizada                     │
│  • task.failed - Tarea falló                             │
│  • task.requires_approval - Requiere aprobación          │
│  • task.progress - Progreso significativo                │
│                                                          │
│  Workflow Notifications                                  │
│  ──────────────────────────                              │
│  • workflow.completed - Workflow finalizado              │
│  • workflow.failed - Workflow falló                      │
│  • workflow.step_completed - Paso completado             │
│  • workflow.waiting_input - Esperando input              │
│                                                          │
│  System Notifications                                    │
│  ────────────────────────                                │
│  • system.error - Error del sistema                      │
│  • system.warning - Advertencia                          │
│  • system.maintenance - Mantenimiento programado         │
│  • system.update - Actualización disponible              │
│                                                          │
│  Presence Notifications                                  │
│  ──────────────────────────                              │
│  • device.online - Dispositivo conectado                 │
│  • device.offline - Dispositivo desconectado             │
│  • user.active - Usuario activo                          │
│  • user.idle - Usuario inactivo                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 9.2 Notification Delivery

```
┌─────────────────────────────────────────────────────────┐
│            Notification Delivery                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Delivery Channels                                       │
│  ────────────────────                                    │
│  • WebSocket (real-time)                                 │
│  • SSE (fallback)                                        │
│  • Email (async)                                         │
│  • Push notifications (mobile)                           │
│  • Slack/Discord/Telegram (webhooks)                     │
│                                                          │
│  Delivery Strategy                                       │
│  ────────────────────                                    │
│  1. Event occurs                                         │
│  2. Notification Service receives event                  │
│  3. Evaluate alert rules                                 │
│  4. Determine target devices/users                       │
│  5. Select delivery channel per device                   │
│  6. Send notification                                    │
│  7. Track delivery status                                │
│  8. Retry on failure (exponential backoff)               │
│                                                          │
│  Notification Payload                                    │
│  ────────────────────────                                │
│  {                                                       │
│    "id": "notif_123",                                    │
│    "type": "task.completed",                             │
│    "title": "Task completed",                            │
│    "message": "Benchmark task finished",                 │
│    "severity": "info",                                   │
│    "timestamp": "2026-07-06T10:30:00Z",                  │
│    "workspace_id": "ws_xyz",                             │
│    "task_id": "task_abc",                                │
│    "actions": [                                          │
│      { "label": "View Results", "url": "/tasks/abc" },  │
│      { "label": "Dismiss", "action": "dismiss" }        │
│    ]                                                     │
│  }                                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 9.3 Alert Rules

```
┌─────────────────────────────────────────────────────────┐
│                Alert Rules                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Rule Definition                                         │
│  ────────────────                                        │
│  {                                                       │
│    "id": "rule_123",                                     │
│    "name": "Task failure alert",                         │
│    "condition": {                                        │
│      "event": "task.failed",                             │
│      "filters": {                                        │
│        "workspace_id": "ws_xyz",                         │
│        "priority": { "$gte": 5 }                         │
│      }                                                   │
│    },                                                    │
│    "actions": [                                          │
│      {                                                   │
│        "type": "push",                                   │
│        "targets": ["device_notebook", "device_android"]  │
│      },                                                  │
│      {                                                   │
│        "type": "email",                                  │
│        "targets": ["user@example.com"]                   │
│      }                                                   │
│    ],                                                    │
│    "enabled": true                                       │
│  }                                                       │
│                                                          │
│  Built-in Rules                                          │
│  ────────────────                                        │
│  • All task failures                                     │
│  • High-priority task completion                         │
│  • Workflow completion                                   │
│  • System errors                                         │
│  • Benchmark results                                     │
│  • Test suite results                                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 10. Estructura del Módulo

### 10.1 Directory Structure

```
components/
└── workspace/
    ├── component.yaml
    ├── check.sh
    ├── install.sh
    ├── uninstall.sh
    ├── docker-compose.yaml
    │
    ├── api/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── routes/
    │   │   ├── __init__.py
    │   │   ├── workspaces.py
    │   │   ├── sessions.py
    │   │   ├── tasks.py
    │   │   ├── workflows.py
    │   │   ├── notifications.py
    │   │   └── presence.py
    │   ├── websocket/
    │   │   ├── __init__.py
    │   │   ├── handler.py
    │   │   └── channels.py
    │   └── middleware/
    │       ├── __init__.py
    │       ├── auth.py
    │       └── logging.py
    │
    ├── core/
    │   ├── __init__.py
    │   ├── workspace_manager.py
    │   ├── session_manager.py
    │   ├── task_manager.py
    │   ├── workflow_engine.py
    │   ├── notification_service.py
    │   └── presence_service.py
    │
    ├── models/
    │   ├── __init__.py
    │   ├── workspace.py
    │   ├── session.py
    │   ├── task.py
    │   ├── workflow.py
    │   ├── notification.py
    │   └── device.py
    │
    ├── events/
    │   ├── __init__.py
    │   ├── bus.py
    │   ├── handlers.py
    │   └── types.py
    │
    ├── sync/
    │   ├── __init__.py
    │   ├── engine.py
    │   ├── conflict_resolution.py
    │   └── vector_clock.py
    │
    ├── storage/
    │   ├── __init__.py
    │   ├── postgres.py
    │   ├── redis.py
    │   └── migrations/
    │
    ├── adapters/
    │   ├── __init__.py
    │   ├── hermes_adapter.py
    │   ├── mimo_adapter.py
    │   ├── opencode_adapter.py
    │   └── base_adapter.py
    │
    └── tests/
        ├── __init__.py
        ├── test_workspace_manager.py
        ├── test_session_manager.py
        ├── test_task_manager.py
        └── test_integration.py
```

### 10.2 Component Definition

```yaml
# component.yaml
name: workspace
version: "0.1.0"
description: "Distributed AI Workspace Manager"
platforms: [linux, darwin]
profiles: [host, desktop]
depends_on: [docker, postgresql]
optional: false

packages:
  apt: [python3, python3-pip]
  pacman: [python, python-pip]
```

### 10.3 Docker Compose

```yaml
# docker-compose.yaml
services:
  workspace-api:
    container_name: awe-workspace-api
    build: .
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://awe:${POSTGRES_PASSWORD:-}@awe-postgresql:5432/awe
      - REDIS_URL=redis://awe-redis:6379
      - QDRANT_URL=http://awe-qdrant:6333
      - LITELLM_URL=http://awe-litellm:4000
    depends_on:
      - postgresql
      - redis
    volumes:
      - workspace_data:/app/data

  workspace-worker:
    container_name: awe-workspace-worker
    build: .
    command: python -m core.worker
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://awe:${POSTGRES_PASSWORD:-}@awe-postgresql:5432/awe
      - REDIS_URL=redis://awe-redis:6379
    depends_on:
      - postgresql
      - redis

  redis:
    container_name: awe-redis
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  workspace_data:
  redis_data:
```

---

## 11. Tradeoffs

### 11.1 Arquitectura

| Decisión | Tradeoff | Justificación |
|----------|----------|---------------|
| **Platform-centric state** | Mayor latencia vs. consistencia | Consistencia es crítica para multi-dispositivo |
| **Event-driven** | Complejidad vs. flexibilidad | Flexibilidad para escalar y extender |
| **WebSocket + REST** | Complejidad vs. real-time | Necesitamos ambos: commands y updates |
| **PostgreSQL + Redis** | Complejidad vs. rendimiento | PostgreSQL para persistencia, Redis para cache/pub-sub |
| **CQRS** | Complejidad vs. escalabilidad | Separar lecturas/escrituras permite optimizar cada una |

### 11.2 Sincronización

| Decisión | Tradeoff | Justificación |
|----------|----------|---------------|
| **Incremental sync** | Complejidad vs. bandwidth | Sesiones pueden ser grandes |
| **Last-write-wins** | Posible pérdida de datos vs. simplicidad | Suficiente para la mayoría de casos |
| **Vector clocks** | Overhead vs. conflict detection | Necesario para detectar conflictos |
| **Offline-first** | Complejidad vs. resiliencia | Dispositivos móviles pueden perder conexión |

### 11.3 Protocolos

| Decisión | Tradeoff | Justificación |
|----------|----------|---------------|
| **WebSocket primary** | Stateful vs. real-time | Necesitamos push en tiempo real |
| **SSE fallback** | Redundancia vs. compatibilidad | Algunos networks bloquean WebSocket |
| **JSON over binary** | Size vs. debuggability | JSON es más fácil de debuggear |

### 11.4 Integración con Hermes

| Decisión | Tradeoff | Justificación |
|----------|----------|---------------|
| **Adapter layer** | Overhead vs. no modificar Hermes | Mantener Hermes upstream |
| **External state** | Duplicación vs. single source of truth | Plataforma es la fuente de verdad |
| **MCP for tools** | Limitación vs. estándar | MCP es estándar para herramientas |

---

## 12. Roadmap de Implementación

### Phase 1: Foundation (2-3 semanas)

**Objetivo:** Core infrastructure funcionando

- [ ] Setup PostgreSQL + Redis
- [ ] Implementar Workspace Manager básico
- [ ] Implementar Session Manager básico
- [ ] REST API para workspaces y sessions
- [ ] WebSocket básico para real-time updates
- [ ] Tests unitarios e integración

**Entregables:**
- API funcional para crear/listar workspaces y sessions
- WebSocket connection funcional
- Tests pasando

### Phase 2: Task Management (2-3 semanas)

**Objetivo:** Sistema de tareas completo

- [ ] Implementar Task Manager
- [ ] Task queue con prioridades
- [ ] Progress tracking
- [ ] Metrics collection (duration, cost, tokens)
- [ ] Remote actions (pause, resume, cancel)
- [ ] Integration con LiteLLM

**Entregables:**
- Sistema de tareas funcional
- Métricas de tareas
- Remote actions funcionando

### Phase 3: Sync & Migration (2-3 semanas)

**Objetivo:** Sincronización multi-dispositivo

- [ ] Incremental sync engine
- [ ] Conflict resolution
- [ ] Device migration
- [ ] Offline queue
- [ ] Vector clocks
- [ ] Checkpoint management

**Entregables:**
- Sincronización funcional entre dispositivos
- Migración de sesiones sin pérdida de contexto
- Soporte offline

### Phase 4: Notifications & Presence (1-2 semanas)

**Objetivo:** Sistema de notificaciones y presencia

- [ ] Notification Service
- [ ] Alert rules engine
- [ ] Push notifications (WebSocket, SSE)
- [ ] Presence tracking
- [ ] Activity monitoring

**Entregables:**
- Notificaciones en tiempo real
- Alert rules configurables
- Presence de dispositivos

### Phase 5: Workflow Engine (2-3 semanas)

**Objetivo:** Ejecución de workflows complejos

- [ ] Workflow definition language
- [ ] Workflow runner
- [ ] Step executor
- [ ] Event handling
- [ ] Workflow templates
- [ ] Integration con n8n

**Entregables:**
- Motor de workflows funcional
- Templates de workflows
- Integración con n8n

### Phase 6: Client Adapters (2-3 semanas)

**Objetivo:** Integración con clientes existentes

- [ ] Hermes adapter
- [ ] Mimo adapter
- [ ] OpenCode adapter
- [ ] Base adapter interface
- [ ] Documentation para nuevos adapters

**Entregables:**
- Adapters funcionando para Hermes, Mimo, OpenCode
- Documentación para crear nuevos adapters

### Phase 7: Observability & Polish (1-2 semanas)

**Objetivo:** Monitoreo y calidad de producción

- [ ] Metrics export (Prometheus)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Logging centralizado
- [ ] Error tracking
- [ ] Performance optimization
- [ ] Documentation completa

**Entregables:**
- Sistema observable
- Documentación completa
- Ready para producción

### Phase 8: Advanced Features (ongoing)

**Objetivo:** Features avanzadas

- [ ] Collaborative editing (CRDTs)
- [ ] Advanced conflict resolution
- [ ] AI-powered context management
- [ ] Predictive task scheduling
- [ ] Multi-user workspaces
- [ ] Advanced analytics

---

## 13. Conclusión

Esta arquitectura proporciona una base sólida para un **Distributed AI Workspace** verdadero, donde:

✅ **Stateless clients** - Los clientes son solo interfaces
✅ **Platform-centric state** - Todo el estado vive en la plataforma
✅ **Device agnostic** - Cualquier dispositivo puede continuar cualquier flujo
✅ **Real-time sync** - Sincronización en tiempo real
✅ **Event-driven** - Arquitectura desacoplada y escalable
✅ **Observable** - Monitoreo y métricas completas
✅ **Extensible** - Fácil agregar nuevos clientes y capacidades

La implementación está dividida en 8 fases manejables, con la Phase 1 entregando valor en 2-3 semanas.

**Próximo paso:** Comenzar Phase 1 - Foundation.
