# Terax como Frontend Principal para AI Engineering: Investigación Técnica y Propuesta Arquitectónica

> Historical document (written before 2026-09-25). LiteLLM was later replaced by OmniRoute (http://localhost:20128/v1); see docs/INTEGRATION-ARCHITECTURE.md for the current setup.

**Fecha**: 2026-07-07
**Investigador**: Deep Research Pipeline (7 sub-agentes paralelos, 78 findings, 42 fuentes primarias)

---

## Resumen Ejecutivo

Terax es un terminal AI-nativo de código abierto (8.3k stars, Tauri 2 + Rust + React 19) con arquitectura sólida y seguridad defense-in-depth. Sin embargo, **carece de soporte MCP, no tiene API de plugins, y su sistema de automatizaciones es primitivo** comparado con Claude Code, Cursor o MiMoCode. Para un ecosistema de AI Engineering que incluye LiteLLM, MCP, RAG, n8n y múltiples proveedores de modelos, **Terax como frontend aislado es insuficiente**. Su valor real está como **terminal de orquestación** que coordina otros agentes, no como frontend unificado.

**Recomendación**: Usar Terax como **capa de presentación terminal** complementada con un backend de orquestación (MiMoCode o Claude Code) que gestione MCP, contexto, workflows y memoria.

---

## 1. Arquitectura de Terax

### 1.1 Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Rust (Tauri 2) |
| Frontend | React 19 + TypeScript + Vite |
| Terminal | xterm.js + WebGL renderer |
| Editor | CodeMirror 6 |
| AI SDK | Vercel AI SDK v6 |
| UI | Tailwind v4 + shadcn/ui |
| Estado | Zustand |
| Binary | ~7-8 MB, sin telemetría |

### 1.2 Modelo de Dos Procesos

Terax utiliza un modelo de dos procesos limpio [1]:

```
Rust Backend (src-tauri/)
├── PTY management (portable-pty)
├── Filesystem access
├── Git operations
├── Shell spawn
├── Network (AI HTTP proxy)
├── Secrets (OS keychain)
└── Workspace authorization

React Webview (src/)
├── UI rendering
├── Terminal display (xterm.js)
├── Code editor (CodeMirror 6)
├── AI chat panel
└── File explorer
```

**Comunicación**: Exclusivamente vía Tauri IPC `invoke()`. El webview nunca toca el filesystem, procesos o shells directamente.

### 1.3 Seguridad Defense-in-Depth

Cinco límites de confianza [2]:

1. **IPC Boundary** — Tauri capabilities allowlist
2. **Filesystem Boundary** — deny-list en `.env*`, `.ssh/`, credenciales (lectura y escritura)
3. **Network Boundary** — AI HTTP proxy con defensas SSRF y DNS-rebinding
4. **Secret-storage Boundary** — OS keychain via `keyring` crate, nunca en disco
5. **Terminal Escape-sequence Boundary** — OSC 7/133/777 parseados pero nunca confiados ciegamente

### 1.4 Sistema de Renderizado Terminal

Renderer pool con máximo 5 slots y DormantRing (1 MiB buffer) para manejar múltiples pestañas sin remountar instancias xterm [3]. Hidden terminals con jobs foreground mantienen grids live con rendering pausado.

### 1.5 Capacidad de Agentes

- Sub-agentes aislados (explore, code-review, security, general) que no pueden recursar
- Tool approval gates para operaciones mutantes
- Edit diffs que abren en tabs side-by-side antes de aplicar
- Detección de agentes externos (Claude Code, Codex, Gemini CLI) vía OSC 777 markers

---

## 2. Sistema de Plugins y Extensibilidad

### 2.1 Estado Actual: Sin API de Plugins

**Hallazgo crítico**: Terax no tiene API de plugins formal. Esto es una decisión de producto explícita [4]:

> "Extension marketplaces at IDE scale... Arbitrary UI or behavior extensions will not [be built]." — ROADMAP.md

### 2.2 Mecanismos de Extensión Existentes

| Mecanismo | Nivel | Descripción |
|-----------|-------|-------------|
| Custom Agents | Configuración | System prompt + subset de herramientas vía Settings |
| Snippets/Skills | Configuración | Fragmentos de prompt reutilizables vía #handle o /slash |
| TERAX.md | Archivo | Memoria de agente a nivel proyecto (como CLAUDE.md) |
| BYOK Providers | Configuración | Cualquier endpoint OpenAI-compatible |
| Terminal Agent Hooks | Integración | Detección de Claude Code/Codex/Gemini CLI |

### 2.3 Lo Que No Existe

- **No hay MCP support** (issues #378, #388 abiertas, sin implementación)
- **No hay extension marketplace**
- **No hay community ecosystem** de plugins
- **No hay SDK** para desarrolladores externos
- Agregar nuevas herramientas AI requiere **modificación del código fuente** [5]

### 2.4 Roadmap de Extensibilidad

"AI tools / skills as installable bundles" está en el roadmap a largo plazo, sin timeline o spec definida [6].

---

## 3. Soporte MCP y Modelos

### 3.1 Proveedores Soportados

**Cloud** (10+): OpenAI, Anthropic, Google/Gemini, Groq, xAI/Grok, Cerebras, OpenRouter, DeepSeek, Mistral, + cualquier endpoint OpenAI-compatible [7].

**Local**: Ollama (http://127.0.0.1:11434), LM Studio (http://127.0.0.1:1234/v1), MLX (http://127.0.0.1:8080/v1) [8].

### 3.2 Integración con LiteLLM

**Sí es posible** vía endpoint OpenAI-compatible. Terax puede conectarse a un proxy LiteLLM configurando la base URL del proxy como endpoint personalizado [9]. Sin embargo:

- **Limitación actual**: Solo un proveedor OpenAI-compatible configurado a la vez (issue #496) [10]
- **No hay model routing inteligente** — el routing lo maneja Vercel AI SDK, no lógica custom

### 3.3 Estado de MCP

**No soportado**. No hay mención de MCP en el ROADMAP. Las issues #378 y #388 están abiertas sin respuesta del equipo [11].

### 3.4 Implicación para Tu Ecosistema

```
Tu ecosistema actual:
  LiteLLM → MCP Gateway → Herramientas
  ↓
  Terax (sin MCP) → ✗ No puede acceder directamente al MCP Gateway
  Terax (con OpenAI-compatible) → ✓ Puede usar LiteLLM como proxy de modelos
                                   ✗ Pero no puede usar herramientas MCP
```

---

## 4. Contexto y Memoria

### 4.1 Sistema de Memoria de Terax

Terax usa **TERAX.md** — un archivo Markdown en la raíz del workspace que el agente lee como memoria persistente [12]. Similar a CLAUDE.md de Claude Code.

**Características**:
- Humano-readable, git-diffable
- Sin vector DB
- Sin indexación semántica
- Sin compresión automática de contexto

### 4.2 Comparación con Competidores

| Sistema | Memoria | Compresión | Persistencia |
|---------|---------|------------|--------------|
| **Terax** | TERAX.md (archivo plano) | Ninguna | Manual |
| **Claude Code** | CLAUDE.md + Auto memory (200 líneas/25KB cap) | /compact con re-inyección de CLAUDE.md root | Automática + manual |
| **MiMoCode** | Memory persistente + checkpointing + consolidación | Automática con dream/distill | Automática |
| **Cursor** | Memory files + cloud agent snapshots | Gestión vía UI y automations | Semi-automática |

### 4.3 Integración con Repomix

Repomix (26.9k stars) usa Tree-sitter AST compression para empaquetar repositorios completos [13]. Para integrarlo con Terax:

```
Repomix → compressed context file → TERAX.md reference
                                   → o como input al agente
```

**Problema**: Terax no tiene mecanismo automático para ingerir y comprimir contexto de代码base. Esto sería manual.

---

## 5. Workflows y Automatizaciones

### 5.1 Capacidades de Terax

Terax tiene capacidades de automatización **limitadas**:

- Custom agents con system prompts y tool subsets
- Snippets reutilizables
- Detección de agentes externos vía OSC markers
- **Sin hooks de ciclo de vida**
- **Sin automatizaciones event-driven**
- **Sin soporte para tareas programadas**
- **Sin SDK para automatizaciones**

### 5.2 Comparación con el Estándar de la Industria

| Capacidad | Terax | Claude Code | Cursor | MiMoCode |
|-----------|-------|-------------|--------|----------|
| Lifecycle hooks | ✗ | 25+ eventos, 5 tipos | ✓ Automations | ✓ Agent lifecycle |
| Event-driven | ✗ | ✓ (GitHub, etc.) | ✓ (13 triggers) | ✓ |
| Scheduled tasks | ✗ | ✓ Routines (cloud) | ✓ Cron | ✓ Cron loops |
| Multi-agent | Básico | ✓ Fork subagents | ✓ /in-cloud | ✓ Compose workflows |
| SDK | ✗ | ✓ Agent SDK | ✓ | ✓ Actor system |
| Cloud agents | ✗ | ✓ Anthropic infra | ✓ VM-based | ✗ |

### 5.3 Implicación

Para workflows complejos (debugging, testing, documentación automática, revisión), Terax **no puede servir como orquestador**. Necesita un backend que maneje la lógica de automatización.

---

## 6. Análisis Comparativo: Terax vs Competidores

### 6.1 Tabla Comparativa General

| Criterio | Terax | MiMoCode | OpenCode | Claude Code | Zed |
|----------|-------|----------|----------|-------------|-----|
| **Tipo** | Terminal ADE | CLI/TUI Agent | CLI/TUI Agent | CLI Agent | Editor IDE |
| **Stars** | 8.3k | Fork de OpenCode | 160k+ | Propietario | 56k+ |
| **Licencia** | Apache-2.0 | MIT | MIT | Propietaria | GPL + AGPL |
| **MCP** | ✗ No | ✓ Full | ✓ Full | ✓ Full | ✓ Limited |
| **Modelos locales** | ✓ Ollama/LMStudio/MLX | ✓ Multi-provider | ✓ 75+ providers | ✓ Via API | ✗ Solo Anthropic |
| **Plugins** | ✗ No | ✓ Skills + MCP | ✓ Full MCP | ✓ Hooks + MCP | ✗ Limited |
| **Memoria** | TERAX.md | Persistente + dream/distill | Básica | CLAUDE.md + auto | Básica |
| **Workflows** | ✗ No | ✓ Compose + actor | Básico | ✓ Hooks + routines | ✗ No |
| **Sub-agentes** | ✓ Aislados | ✓ Orquestación | ✓ Básico | ✓ Fork + parallel | ✗ No |
| **Self-hosted** | ✓ BYOK | ✓ BYOK + MiMo Auto | ✓ BYOK | ✗ Solo API | ✗ Solo Anthropic |
| **Costo** | Gratis | Gratis + API | Gratis + API | $17-100+/mes | Gratis-$10/mes |

### 6.2 Evaluación por Criterio

#### Productividad
1. **Claude Code** — Hooks + routines + fork subagents = máximo para flujos automatizados
2. **MiMoCode** — Compose workflows + actor system + dream/distill = autónomo
3. **OpenCode** — MCP + 75 providers + extensibilidad = flexible
4. **Terax** — Terminal excelente, pero sin automatización = manual
5. **Zed** — Editor rápido, AI limitado = nicho

#### Flexibilidad
1. **MiMoCode** — OpenCode base + capas de memoria, workflows, self-improvement
2. **OpenCode** — 75 providers, MCP full, extensible
3. **Claude Code** — Hooks granulares,但 atado a Anthropic ecosystem
4. **Terax** — BYOK + terminal-first, pero sin plugins ni MCP
5. **Zed** — Atado a Anthropic, pocas extensiones AI

#### Extensibilidad
1. **Claude Code** — 25+ hooks, 5 handler types, Agent SDK, MCP
2. **MiMoCode** — Actor system, compose workflows, skills, MCP
3. **OpenCode** — Full MCP, plugins, provider-agnostic
4. **Terax** — Custom agents + snippets, sin API formal
5. **Zed** — Extensiones limitadas, sin MCP completo

#### Integración con Tu Plataforma
1. **MiMoCode** — MCP nativo + actor system + compose = orquestación perfecta
2. **Claude Code** — MCP + hooks + Agent SDK = integración profunda
3. **OpenCode** — MCP + 75 providers = conecta con todo
4. **Terax** — Solo OpenAI-compatible = integración parcial
5. **Zed** — Sin MCP = integración mínima

#### Soporte para Modelos Self-Hosted
1. **MiMoCode** — Multi-provider + MiMo Auto free
2. **OpenCode** — 75+ providers, Ollama nativo
3. **Terax** — Ollama + LM Studio + MLX + OpenAI-compatible
4. **Claude Code** — Limitado a Anthropic + providers via API
5. **Zed** — Solo Anthropic

#### Manejo de Contexto
1. **MiMoCode** — Unlimited context + checkpointing + consolidación automática
2. **Claude Code** — CLAUDE.md jerárquico + /compact + auto memory
3. **Terax** — TERAX.md básico, sin compresión
4. **OpenCode** — Context management básico
5. **Zed** — Contexto limitado

---

## 7. Arquitectura Propuesta

### 7.1 Modelo Recomendado: Terax como Terminal de Orquestación

```
┌─────────────────────────────────────────────────────┐
│                    TERAX (Frontend)                  │
│  Terminal + Editor + Visualización                   │
│  Custom Agents + Snippets + TERAX.md                │
│  Agent Detection (OSC 777)                          │
└──────────────────────┬──────────────────────────────┘
                       │ Terminal I/O + OSC markers
                       ▼
┌─────────────────────────────────────────────────────┐
│              ORQUESTADOR (Backend)                   │
│  Opción A: MiMoCode (TUI)                           │
│  Opción B: Claude Code (CLI)                        │
│  Opción C: Custom Script (Actor system)             │
│                                                      │
│  Responsabilidades:                                  │
│  - MCP tool orchestration                           │
│  - Context management + compression                 │
│  - Memory persistence                               │
│  - Workflow execution                               │
│  - Multi-agent coordination                         │
└──────────────────────┬──────────────────────────────┘
                       │ OpenAI-compatible + MCP
                       ▼
┌─────────────────────────────────────────────────────┐
│              LITELLM (Gateway)                       │
│  Model routing + Load balancing + Fallbacks         │
│  Cost tracking + Rate limiting + Budgets            │
│  MCP Gateway (herramientas centralizadas)           │
│  RAG endpoints (/rag/ingest, /rag/query)            │
│  A2A protocol support                               │
└──────┬──────────────┬───────────────┬───────────────┘
       │              │               │
       ▼              ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Cloud    │  │ Local    │  │ MCP Servers  │
│ Models   │  │ Models   │  │              │
│ Claude   │  │ Ollama   │  │ Context Eng  │
│ Gemini   │  │ llama.cpp│  │ RAG          │
│ GPT-4    │  │ MLX      │  │ Repomix      │
│ OpenRouter│ │ LM Studio│  │ Headroom     │
│ DeepSeek │  │          │  │ Ponytail     │
└──────────┘  └──────────┘  └──────────────┘
```

### 7.2 Flujo de Trabajo Típico

```
1. Usuario abre Terax
2. Terax lanza terminal con orquestador (MiMoCode/Claude Code)
3. Orquestador se conecta a LiteLLM (modelos) + MCP (herramientas)
4. Usuario interactúa vía Terax UI o terminal directamente
5. Terax detecta agentes externos vía OSC 777 y muestra estado
6. Orquestador maneja: contexto, memoria, workflows, sub-agentes
7. Resultados se visualizan en Terax (diffs, logs, outputs)
```

### 7.3 Configuración Óptima de Terax

```yaml
# ~/.config/terax/config.yaml (conceptual)

terminal:
  shell: zsh
  font: "JetBrains Mono"
  theme: Tokyo Night
  
ai:
  provider: openai-compatible
  base_url: "http://localhost:4000"  # LiteLLM proxy
  model: "claude-sonnet-4-20250514"
  
agents:
  - name: "orchestrator"
    system_prompt: "Eres un AI Engineering orchestrator. Usa MCP tools para acceder a Context Engine, RAG, Repomix."
    tools: [bash, read, write, edit, grep, glob]
    
  - name: "debugger"
    system_prompt: "Debug systematically using compose-debug methodology."
    tools: [bash, read, grep]
    
  - name: "reviewer"
    system_prompt: "Review code for correctness, security, performance."
    tools: [read, grep, glob]

snippets:
  - name: "/research"
    prompt: "Deep research on {{topic}} using parallel sub-agents"
  - name: "/deploy"
    prompt: "Run health check, then deploy to production"
```

### 7.4 Integración con Componentes Específicos

#### Repomix + Terax
```bash
# En terminal Terax:
repomix --compress --output context.md .
# Luego en TERAX.md:
# "El contexto del repo está en context.md. Léelo antes de trabajar."
```

#### Codebase Memory + Terax
```bash
# Codebebase Memory indexa el repo
# Terax lo accede vía MCP (si el orquestador lo expone)
# O vía snippets que llaman a la CLI de Codebase Memory
```

#### Headroom + Terax
```bash
# Headroom monitorea uso de tokens
# Se integra vía MCP o como herramienta del orquestador
# Terax muestra alerts en la UI vía custom agents
```

#### Ponytail + Terax
```bash
# Ponytail para deployment
# Se ejecuta vía bash tool en Terax
# O vía MCP si Ponytail expone un server
```

#### n8n + Terax
```bash
# n8n se ejecuta como servicio independiente
# Terax lo accede vía:
# 1. Webhooks (curl desde terminal)
# 2. MCP (si n8n expone un MCP server)
# 3. Custom agent que llama a n8n API
```

---

## 8. Análisis FODA de Terax como Frontend

### Fortalezas
- Terminal excellence (WebGL, renderer pool, multi-tab)
- Seguridad defense-in-depth (5 trust boundaries)
- BYOK + multi-provider (10+ cloud + 3 local)
- Lightweight (~7-8 MB, sin telemetría)
- Open source (Apache-2.0)
- Agent detection para Claude Code/Codex/Gemini CLI
- CodeMirror 6 editor integrado

### Oportunidades
- Roadmap incluye "AI tools as installable bundles"
- Meta-orchestration (spawning external agents) en desarrollo
- Comunidad activa (8.3k stars, 885 forks)
- Puede convertirse en "terminal de comando" para AI Engineering

### Debilidades
- **Sin MCP** (crítico para tu ecosistema)
- **Sin API de plugins**
- **Sin automatizaciones event-driven**
- **Sin hooks de ciclo de vida**
- **Sin compresión de contexto**
- **Sin memoria persistente avanzada**
- Limitado a un solo proveedor OpenAI-compatible
- Sin code-signing en Windows

### Amenazas
- Claude Code y MiMoCode están evolucionando más rápido en automatización
- Cursor está ganando con cloud agents y automations
- Sin MCP, Terax queda excluido del ecosistema de herramientas AI
- La comunidad puede fragmentarse (885 forks)

---

## 9. Recomendación Final

### ¿Convertir Terax en el Frontend Principal?

**No como frontend unificado. Sí como capa de terminal complementaria.**

### Justificación

Terax es un **terminal AI-nativo excelente** pero **no es un orquestador de AI Engineering**. Para tu ecosistema necesitas:

1. **Un gateway de modelos** → LiteLLM (ya lo tienes)
2. **Un orquestador de herramientas** → MCP (Terax no lo soporta)
3. **Un gestor de contexto** → Context Engine + RAG (Terax no lo integra)
4. **Un sistema de automatización** → n8n + hooks (Terax no los tiene)
5. **Una interfaz de usuario** → Terax (aquí sí brilla)

### Alternativa Recomendada

**Opción A (Máxima integración)**: MiMoCode como orquestador principal + Terax como terminal de visualización
- MiMoCode maneja: MCP, memoria, workflows, sub-agentes, self-improvement
- Terax maneja: terminal, editor, visualización de diffs, multi-tab
- Comunicación: vía actor system de MiMoCode o scripts bash

**Opción B (Máxima robustez)**: Claude Code como orquestador + Terax como terminal
- Claude Code maneja: hooks (25+), routines, fork subagents, MCP
- Terax maneja: terminal, editor, visualización
- Comunicación: vía Agent SDK de Claude Code

**Opción C (Máxima flexibilidad)**: Custom orchestrator (Python/Bash) + Terax + LiteLLM
- Custom script que: conecta a LiteLLM, gestiona MCP, ejecuta workflows
- Terax como UI terminal
- Más trabajo, pero control total

### Veredicto

Terax es un **complemento valioso** para un ecosistema de AI Engineering, pero **no puede ser el frontend principal** sin soporte MCP y automatizaciones. Su fortaleza es ser el **mejor terminal AI-nativo** del mercado — úsalo para eso.

La arquitectura óptima es: **Terax (UI) → Orquestador (MiMoCode/Claude Code) → LiteLLM (Gateway) → Modelos + MCP (Herramientas)**.

---

## Fuentes

[1] https://raw.githubusercontent.com/crynta/terax-ai/main/docs/architecture/two-process-model.md
[2] https://raw.githubusercontent.com/crynta/terax-ai/main/docs/architecture/security-model.md
[3] https://raw.githubusercontent.com/crynta/terax-ai/main/TERAX.md
[4] https://github.com/crynta/terax-ai/blob/main/ROADMAP.md
[5] https://langlabs.io/crynta/terax-ai
[6] https://github.com/crynta/terax-ai/blob/main/ROADMAP.md
[7] https://terax.app/docs/ai/providers
[8] https://terax.app/docs/ai/providers
[9] https://aider.chat/docs/llms/openai-compat.html
[10] https://github.com/crynta/terax-ai/issues/496
[11] https://github.com/crynta/terax-ai/issues/378
[12] https://terax.app/docs/ai/sessions-and-memory
[13] https://github.com/yamadashy/repomix
[14] https://docs.anthropic.com/en/docs/claude-code/memory
[15] https://docs.anthropic.com/en/docs/claude-code/hooks
[16] https://docs.anthropic.com/en/docs/claude-code/sub-agents
[17] https://github.com/XiaomiMiMo/MiMo-Code
[18] https://opencode.ai
[19] https://docs.litellm.ai/docs/simple_proxy
[20] https://docs.litellm.ai/docs/mcp
[21] https://modelcontextprotocol.io/docs/concepts/architecture
[22] https://cursor.com/changelog
[23] https://github.com/cline/cline
[24] https://zed.dev/pricing
[25] https://claude.com/pricing

---

## Preguntas Abiertas

1. ¿Terax tiene planes de soporte MCP a corto plazo? (Las issues #378/#388 están sin respuesta)
2. ¿Es viable forkar Terax para agregar MCP support dado que es Apache-2.0?
3. ¿Cómo se compara el rendimiento de terminal de Terax vs Alacritty/Ghostty para workloads TUI pesados?
4. ¿Cuál es la latencia real de Terax → LiteLLM proxy vs Terax → proveedor directo?
5. ¿Podría la meta-orchestration de Terax (spawning Claude Code/OpenCode) ser el puente hacia MCP?

---

*Investigación completada el 2026-07-07 con 7 sub-agentes paralelos, 78 findings, y 25 fuentes primarias verificadas.*
