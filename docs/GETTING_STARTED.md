# Distributed AI Workspace - Guía de Inicio

## Estado del Proyecto

### ✅ Completado
- **AI Engineering Platform**: LiteLLM, Ollama, Qdrant, n8n, PostgreSQL
- **Mimo Integration**: 10/10 etapas completadas
  - 6 agentes custom
  - 28 skills
  - 7 custom tools
  - 4 n8n workflows
  - 6 compose workflows

### 📋 Planificado
- **Distributed AI Workspace**: Arquitectura diseñada, lista para implementar
  - 8 fases de implementación
  - 12-18 semanas estimadas
  - 6 módulos principales

## Documentación

### Mimo Integration
- `mimo-architecture.md` - Análisis de capacidades de Mimo
- `mimo-platform-design.md` - Diseño de integración Mimo + Plataforma
- `mimo-implementation-plan.md` - Plan de implementación (COMPLETADO)

### Distributed Workspace
- `distributed-workspace-summary.md` - Resumen ejecutivo
- `distributed-workspace-architecture.md` - Arquitectura completa
- `distributed-workspace-hermes-analysis.md` - Análisis de Hermes
- `distributed-workspace-diagrams.md` - Diagramas de flujo

### Platform
- `architecture.md` - Arquitectura de la plataforma
- `profiles.md` - Perfiles disponibles
- `mcp-management.md` - Gestión de MCP servers
- `adding-components.md` - Cómo agregar componentes
- `HOW_TO.md` - Guía de uso

## Próximos Pasos

### Opción 1: Comenzar Distributed Workspace

Si quieres comenzar a implementar el Distributed AI Workspace:

1. **Revisar arquitectura** en `distributed-workspace-architecture.md`
2. **Confirmar requisitos** y priorizar fases
3. **Comenzar Phase 1**: Foundation (2-3 semanas)
   - Setup PostgreSQL + Redis
   - Workspace Manager básico
   - Session Manager básico
   - REST API + WebSocket

### Opción 2: Usar Mimo Primero

Si quieres usar Mimo antes de construir el workspace:

```bash
# Instalar Mimo y toda la plataforma
./bootstrap --profile notebook

# Iniciar Mimo
mimo

# Usar agentes custom
@security-auditor Revisa este código
@tdd-driver Implementa tests para esta función

# Usar skills
Use skill: system-design
Use skill: code-review

# Usar custom tools
health-check
benchmark --prompt "Explica quantum computing" --models "local,claude-sonnet,gpt-4"
```

### Opción 3: Ambos en Paralelo

Puedes usar Mimo mientras construyes el workspace:
- Usa Mimo para desarrollo diario
- Construye workspace en paralelo
- Migra gradualmente al workspace cuando esté listo

## Comandos Útiles

### Platform
```bash
# Detectar sistema
./bootstrap detect

# Listar componentes
./bootstrap list

# Ver estado
./bootstrap status

# Instalar perfil
./bootstrap bootstrap --profile notebook

# Actualizar
./bootstrap update

# MCP management
./bootstrap mcp-list
./bootstrap mcp-enable docker
./bootstrap mcp-generate mimo
```

### Mimo
```bash
# Iniciar
mimo

# Cambiar modelo
/models

# Usar agente
@security-auditor [tu petición]

# Usar skill
Use skill: [skill-name]

# Comandos custom
/review
/debug
/test
/doc
/architect
/benchmark
/dream
/distill
/memory
/checkpoint
```

### Custom Tools (en Mimo)
```typescript
// Verificar salud de servicios
health-check

// Benchmark de modelos
benchmark --prompt "..." --models "local,claude-sonnet,gpt-4"

// Cambiar modelo
model-router --model "claude-sonnet-4-20250514"

// Ejecutar workflow
workflow-runner --workflow "create-fastapi-project"

// Inyectar contexto RAG
context-injector --query "..." --limit 5

// Trigger n8n workflow
n8n-trigger --workflow "post-commit-tests" --data "{}"

// Gestionar memoria
memory-manager --action "read"
memory-manager --action "write" --content "..."
memory-manager --action "search" --query "..."
memory-manager --action "clean"
```

## Arquitectura Actual

```
┌─────────────────────────────────────────────────────────┐
│                    MIMO (Frontend)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Build   │  │  Plan    │  │ Compose  │  │ Custom  │ │
│  │  Agent   │  │  Agent   │  │  Mode    │  │ Agents  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │              │             │              │      │
│  ┌────┴──────────────┴─────────────┴──────────────┴───┐ │
│  │           Skills │ Custom Tools │ Rules             │ │
│  └───────────────────────┬────────────────────────────┘ │
└──────────────────────────┼──────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│              LITELLM (Model Router)                       │
│              http://localhost:4000/v1                     │
│                                                          │
│  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌────────────┐ │
│  │  Ollama  │ │ Claude   │ │   GPT-4   │ │ OpenRouter │ │
│  │ (Local)  │ │ Sonnet   │ │           │ │  (Auto)    │ │
│  └─────────┘ └──────────┘ └───────────┘ └────────────┘ │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│           AI WORKSTATION PLATFORM                        │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Qdrant   │  │   n8n    │  │PostgreSQL│  │ Docker  │ │
│  │ (Vector) │  │(Workflow)│  │  (Data)  │  │ (Infra) │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  MCP Servers (filesystem, git, github, headroom, │   │
│  │  codebase-memory, ponytail, docker, postgres,    │   │
│  │  sequential-thinking, browser, memory)            │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

## Arquitectura Futura (Distributed Workspace)

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENTS                           │
│  Hermes │ Mimo │ OpenCode │ Claude Code │ Web │ Android │
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

## Recursos

### Documentación Externa
- **Mimo**: https://mimo.xiaomi.com/mimocode/start
- **Hermes**: https://hermes-agent.nousresearch.com/docs/
- **LiteLLM**: https://docs.litellm.ai/
- **Qdrant**: https://qdrant.tech/documentation/
- **n8n**: https://docs.n8n.io/

### Repositorios
- **Mimo**: https://github.com/XiaomiMiMo/MiMo-Code
- **Hermes**: https://github.com/NousResearch/hermes-agent
- **LiteLLM**: https://github.com/BerriAI/litellm

## Soporte

Para problemas o preguntas:
1. Revisa la documentación en `docs/`
2. Verifica logs de componentes
3. Consulta `AGENTS.md` para convenciones
4. Revisa tests en `tests/` para ejemplos

---

**Última actualización**: 2026-07-06
**Versión**: 1.0.0
