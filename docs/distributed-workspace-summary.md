# Distributed AI Workspace - Resumen Ejecutivo

> Historical document (written before 2026-09-25). LiteLLM was later replaced by OmniRoute (http://localhost:20128/v1); see docs/INTEGRATION-ARCHITECTURE.md for the current setup.

## Visión

Transformar tu AI Engineering Platform en un **Distributed AI Workspace** donde cualquier dispositivo puede iniciar, continuar, supervisar o finalizar cualquier flujo de trabajo sin perder contexto y sin depender de una interfaz específica.

## Estado Actual

### Infraestructura Existente
- ✅ AI Engineering Platform (LiteLLM, Ollama, Qdrant, n8n, PostgreSQL)
- ✅ Mimo integrado como frontend (10/10 etapas completadas)
- ✅ Tailscale para conectividad multi-dispositivo
- ✅ Hermes como cliente en todos los dispositivos
- ✅ MCP servers configurados
- ✅ 28 skills, 6 agentes custom, 7 custom tools

### Dispositivos
- Notebook
- Desktop
- Host AI
- Celular Android

## Propuesta: Distributed AI Workspace

### Concepto Central

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTES                              │
│  Hermes  |  Mimo  |  OpenCode  |  Claude Code  |  Web   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              WORKSPACE LAYER (NUEVO)                     │
│                                                          │
│  Workspace Manager  │  Session Manager  │  Task Manager  │
│  Presence Service   │  Notification Svc │  Workflow Eng  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           AI ENGINEERING PLATFORM (EXISTENTE)            │
│                                                          │
│  Model Router  │  Context Engine  │  RAG  │  MCP        │
│  Memory System │  Evaluation      │  Obs  │  Models     │
└─────────────────────────────────────────────────────────┘
```

### Principios Clave

1. **Stateless Clients** - Los clientes NO almacenan estado
2. **Platform-Centric State** - Todo el estado vive en la plataforma
3. **Event-Driven** - Comunicación via eventos desacoplados
4. **Real-Time Sync** - Sincronización en tiempo real
5. **Device Agnostic** - Cualquier dispositivo puede continuar cualquier flujo

## Análisis de Hermes

### ✅ Altamente Compatible

| Capacidad | Compatibilidad |
|-----------|----------------|
| MCP Support | ✅ Perfecto para herramientas distribuidas |
| ACP Support | ✅ Ideal para multi-agente |
| Multi-Platform | ✅ Ya lo usas en todos tus dispositivos |
| Persistent Memory | ✅ Base para sincronización |
| Provider Agnostic | ✅ Funciona con LiteLLM |
| Open Source (MIT) | ✅ Podemos extender |

### ⚠️ Limitaciones

- Single agent process (necesitamos capa intermedia)
- No explicit sync protocol (debemos construirlo)
- Local state (debemos externalizar a plataforma)

### Estrategia

**Hermes como cliente** con adapter layer que sincroniza con Workspace Manager. No modificamos Hermes core, mantenemos compatibilidad upstream.

## Módulos del Workspace Layer

### 1. Workspace Manager
- Administrar workspaces, dispositivos, usuarios
- Access control
- Shared context

### 2. Session Manager
- Ciclo de vida completo de sesiones
- Checkpoints automáticos
- Migración entre dispositivos
- Sync en tiempo real

### 3. Task Manager
- Task queue con prioridades
- Progress tracking
- Agent registry
- Metrics (duration, cost, tokens)

### 4. Workflow Engine
- Ejecución de workflows complejos
- Step orchestration
- Event handling
- Integration con n8n

### 5. Notification Service
- Event routing
- Push notifications (WebSocket, SSE)
- Alert rules
- Delivery tracking

### 6. Presence Service
- Device status tracking
- User activity monitoring
- Idle detection

## Protocolos de Comunicación

### Estrategia Híbrida

| Tipo | Protocolo | Caso de Uso |
|------|-----------|-------------|
| **Commands** | REST (JSON) | CRUD operations, idempotencia |
| **Real-time** | WebSocket (primary) | Session updates, task progress |
| **Real-time** | SSE (fallback) | Networks restrictivas |
| **Internal** | gRPC / Event Bus | Service-to-service |

### WebSocket Message Example

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
      "content": "Processing your request..."
    }
  }
}
```

## Sincronización

### Sesiones
- **Incremental sync** con sequence numbers
- **Vector clocks** para conflict detection
- **Last-write-wins** para resolución
- **Offline queue** para resiliencia

### Tareas
- **Event-driven** progress updates
- **Remote actions**: pause, resume, cancel, restart
- **Human-in-the-loop**: approve/reject
- **Metrics tracking**: duration, cost, tokens

### Contexto
- **Eventual consistency** para updates
- **Context versioning** con rollback
- **Headroom compression** para eficiencia
- **RAG retrieval** desde Qdrant

## Notificaciones

### Tipos
- Task completion/failure
- Workflow completion
- System alerts
- Presence changes

### Delivery
- WebSocket (real-time)
- SSE (fallback)
- Email (async)
- Push notifications (mobile)
- Slack/Discord/Telegram (webhooks)

### Alert Rules
```json
{
  "condition": {
    "event": "task.failed",
    "filters": {
      "priority": { "$gte": 5 }
    }
  },
  "actions": [
    { "type": "push", "targets": ["device_notebook"] }
  ]
}
```

## Estructura del Módulo

```
components/workspace/
├── component.yaml
├── docker-compose.yaml
├── api/
│   ├── routes/ (workspaces, sessions, tasks, etc.)
│   ├── websocket/
│   └── middleware/
├── core/
│   ├── workspace_manager.py
│   ├── session_manager.py
│   ├── task_manager.py
│   ├── workflow_engine.py
│   ├── notification_service.py
│   └── presence_service.py
├── models/
├── events/
├── sync/
├── storage/
├── adapters/ (hermes, mimo, opencode)
└── tests/
```

## Roadmap de Implementación

### Phase 1: Foundation (2-3 semanas)
- PostgreSQL + Redis setup
- Workspace Manager básico
- Session Manager básico
- REST API + WebSocket básico
- **Entrega:** API funcional para workspaces y sessions

### Phase 2: Task Management (2-3 semanas)
- Task Manager completo
- Task queue con prioridades
- Progress tracking
- Metrics collection
- Remote actions
- **Entrega:** Sistema de tareas funcional

### Phase 3: Sync & Migration (2-3 semanas)
- Incremental sync engine
- Conflict resolution
- Device migration
- Offline queue
- **Entrega:** Sincronización multi-dispositivo

### Phase 4: Notifications & Presence (1-2 semanas)
- Notification Service
- Alert rules
- Push notifications
- Presence tracking
- **Entrega:** Notificaciones en tiempo real

### Phase 5: Workflow Engine (2-3 semanas)
- Workflow runner
- Step executor
- Event handling
- Integration con n8n
- **Entrega:** Motor de workflows funcional

### Phase 6: Client Adapters (2-3 semanas)
- Hermes adapter
- Mimo adapter
- OpenCode adapter
- Documentation
- **Entrega:** Adapters para clientes existentes

### Phase 7: Observability & Polish (1-2 semanas)
- Metrics (Prometheus)
- Tracing (OpenTelemetry)
- Logging centralizado
- Documentation
- **Entrega:** Sistema observable y documentado

### Phase 8: Advanced Features (ongoing)
- Collaborative editing (CRDTs)
- AI-powered context management
- Multi-user workspaces
- Advanced analytics

**Total estimado:** 12-18 semanas para producción

## Tradeoffs Clave

| Decisión | Tradeoff | Justificación |
|----------|----------|---------------|
| Platform-centric state | Mayor latencia vs. consistencia | Consistencia crítica para multi-dispositivo |
| Event-driven | Complejidad vs. flexibilidad | Necesario para escalar |
| WebSocket + REST | Complejidad vs. real-time | Necesitamos ambos |
| Adapter layer | Overhead vs. no modificar Hermes | Mantener upstream |
| Incremental sync | Complejidad vs. bandwidth | Sesiones pueden ser grandes |

## Beneficios

✅ **Continuidad total** - Cambia de dispositivo sin perder contexto
✅ **Supervisión remota** - Monitorea tareas desde cualquier lugar
✅ **Colaboración** - Múltiples dispositivos trabajando juntos
✅ **Resiliencia** - Funciona offline, sincroniza después
✅ **Escalabilidad** - Arquitectura preparada para crecer
✅ **Flexibilidad** - Fácil agregar nuevos clientes

## Próximos Pasos

1. **Revisar arquitectura** - Confirmar diseño con tus requisitos
2. **Priorizar fases** - Decidir qué fases implementar primero
3. **Comenzar Phase 1** - Foundation (2-3 semanas)
4. **Iterar** - Entregar valor incrementalmente

## Documentos de Referencia

- `docs/distributed-workspace-hermes-analysis.md` - Análisis de Hermes
- `docs/distributed-workspace-architecture.md` - Arquitectura completa
- `docs/mimo-implementation-plan.md` - Estado de integración Mimo

---

**Conclusión:** Tu AI Engineering Platform está lista para evolucionar hacia un Distributed AI Workspace. La arquitectura propuesta es sólida, escalable y respeta tu infraestructura existente. Hermes es altamente compatible y puede seguir siendo tu cliente principal mientras construimos la capa de workspace.
