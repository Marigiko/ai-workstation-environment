# HOW_TO.md — Guía Completa de Uso

## ¿Qué es AI Workstation Environment?

AI Workstation Environment es un sistema de **Infrastructure as Code** que transforma cualquier computadora (Linux, WSL, macOS) en un entorno profesional de AI Engineering completamente configurado.

En lugar de instalar herramientas manualmente, configurar dotfiles, o perder tiempo configurando MCP servers, este repositorio automatiza todo el proceso con un solo comando.

### ¿Para quién es esto?

- **AI Engineers** que necesitan un entorno reproducible
- **Desarrolladores** que trabajan con múltiples máquinas (notebook, desktop, servidor)
- **Equipos** que quieren estandarizar el entorno de desarrollo
- **Cualquiera** que quiera ahorrar tiempo en configuración y enfocarse en el trabajo real

---

## Casos de Uso

### Caso 1: Nuevo Desarrollador en el Equipo

**Problema**: Un nuevo desarrollador necesita configurar su laptop para trabajar en AI Engineering. Esto implica instalar Git, Docker, Node.js, Python, Zed, OpenCode, Claude Code, configurar dotfiles, MCP servers, etc. Normalmente toma 1-2 días.

**Solución con AWE**:
```bash
git clone https://github.com/TU_USUARIO/ai-workstation-environment.git
cd ai-workstation-environment
./bootstrap --profile notebook
```

**Resultado**: En 10-15 minutos, la máquina está completamente configurada con todas las herramientas, dotfiles, y MCP servers listos para trabajar.

### Caso 2: Cambiar de Computadora

**Problema**: Compraste una laptop nueva y necesitas migrar tu entorno de desarrollo.

**Solución con AWE**:
```bash
# En la máquina nueva
git clone https://github.com/TU_USUARIO/ai-workstation-environment.git
cd ai-workstation-environment
./bootstrap --profile notebook
```

**Resultado**: Tu entorno profesional se replica exactamente. No necesitas recordar qué herramientas tenías instaladas o cómo las configuraste.

### Caso 3: Configurar un Servidor de Infraestructura

**Problema**: Necesitas configurar un servidor para correr modelos locales (Ollama), vector DB (Qdrant), base de datos (PostgreSQL), y automatización (n8n).

**Solución con AWE**:
```bash
git clone https://github.com/TU_USUARIO/ai-workstation-environment.git
cd ai-workstation-environment
./bootstrap --profile host
```

**Resultado**: Todos los servicios se instalan en Docker con configuraciones óptimas, incluyendo el Distributed AI Workspace para gestión multi-dispositivo.

### Caso 4: Equipo con Estándares

**Problema**: Cada desarrollador en tu equipo tiene configuraciones diferentes, lo que causa inconsistencias y problemas de "en mi máquina sí funciona".

**Solución con AWE**:
```bash
# Todos los desarrolladores usan el mismo perfil
./bootstrap --profile desktop
```

**Resultado**: Entornos estandarizados, reproducibles, y versionados.

---

## Beneficios

### 1. **Ahorro de Tiempo**
- Configurar un entorno manualmente: 1-2 días
- Con AWE: 10-15 minutos
- **Ahorro**: ~95% del tiempo

### 2. **Reproducibilidad**
- Mismo comando = mismo resultado
- Versionado en Git (puedes hacer rollback)
- Documentación implícita (el código es la documentación)

### 3. **Consistencia**
- Todos en el equipo usan la misma configuración
- Menos problemas de "en mi máquina sí funciona"
- Onboarding más rápido para nuevos desarrolladores

### 4. **Mantenibilidad**
- Actualizaciones con un comando: `./bootstrap update`
- Agregar nuevas herramientas es fácil (crear un directorio)
- Configuración declarativa (YAML, no scripts complejos)

### 5. **Portabilidad**
- Funciona en Linux, WSL, macOS
- Perfiles para diferentes tipos de máquinas
- Migrar entre máquinas es trivial

---

## Cómo Empezar

### Requisitos Previos

- **Python 3.10+** (el bootstrap lo instala si no existe)
- **Git** (para clonar el repositorio)
- **Bash** (en Linux/WSL/macOS)
- **Conexión a internet** (para descargar herramientas)

### Instalación Paso a Paso

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/ai-workstation-environment.git ~/ai-workstation-environment
cd ~/ai-workstation-environment
```

#### 2. Verificar el Entorno

```bash
./bootstrap detect
```

Esto te muestra qué herramientas ya tienes instaladas y qué falta.

#### 3. Elegir un Perfil

| Perfil | Para qué sirve | Qué instala |
|--------|----------------|-------------|
| `notebook` | Laptop de desarrollo | Git, SSH, Node, Python, Zed, Mimo, OpenCode, Claude Code, Terax, Tailscale, Docker |
| `desktop` | Workstation completa | notebook + Rust, VSCode, Workspace API |
| `host` | Servidor de infraestructura | Git, SSH, Docker, Tailscale, Node, Python, Ollama, LiteLLM, Qdrant, PostgreSQL, n8n, Workspace |
| `minimal` | Bare minimum | Solo Git y SSH |

#### 4. Ejecutar el Bootstrap

```bash
./bootstrap --profile notebook
```

El bootstrap:
1. Crea un virtual environment de Python
2. Detecta tu sistema operativo y hardware
3. Instala las herramientas que faltan
4. Configura los dotfiles (symlinks)
5. Instala y configura los MCP servers
6. Genera configs para Mimo, OpenCode, Claude Code, Zed
7. Instala agentes custom, skills y custom tools de Mimo

#### 5. Verificar la Instalación

```bash
./bootstrap status          # Ver qué se instaló
./bootstrap list            # Ver todos los componentes disponibles
./scripts/health-check.sh   # Verificar que todo funciona
```

---

## Flujos de Trabajo Recomendados

### Flujo 1: Desarrollo Diario con AI Tools

```bash
# 1. Iniciar Mimo (frontend principal)
mimo

# 2. Conversar con el agente Build (default)
> Crea un endpoint FastAPI para autenticación JWT

# 3. Cambiar al agente Plan (solo análisis, sin cambios)
# Presiona Tab para cambiar de agente

# 4. Usar un agente especializado
@security-auditor Revisa este código por vulnerabilidades

# 5. Usar un skill
Use skill: system-design

# 6. Ejecutar un comando custom
/review
/debug
/test
/doc
/architect
/benchmark
```

**OpenCode y Claude Code** (alternativos):
```bash
# OpenCode también está configurado con MCP servers
opencode

# Claude Code también está listo
claude
```

Los MCP servers (filesystem, git, github) ya están configurados automáticamente.

### Flujo 2: Agregar una Nueva Herramienta

Supongamos que quieres agregar `ripgrep` como componente:

```bash
# 1. Crear el directorio del componente
mkdir -p components/ripgrep

# 2. Crear component.yaml
cat > components/ripgrep/component.yaml <<EOF
name: ripgrep
version: "14.0"
description: "Fast search tool"
platforms: [linux, darwin]
profiles: [notebook, desktop]
depends_on: []
optional: false
packages:
  apt: [ripgrep]
  pacman: [ripgrep]
  brew: [ripgrep]
EOF

# 3. Crear check.sh
cat > components/ripgrep/check.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
command -v rg &>/dev/null
EOF

# 4. Crear install.sh
cat > components/ripgrep/install.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if command -v rg &>/dev/null; then
    echo "ripgrep already installed"
    exit 0
fi

if command -v apt-get &>/dev/null; then
    sudo apt-get install -y ripgrep
elif command -v pacman &>/dev/null; then
    sudo pacman -S --noconfirm ripgrep
elif command -v brew &>/dev/null; then
    brew install ripgrep
fi
EOF

# 5. Crear uninstall.sh
cat > components/ripgrep/uninstall.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if command -v apt-get &>/dev/null; then
    sudo apt-get remove -y ripgrep
elif command -v pacman &>/dev/null; then
    sudo pacman -Rns --noconfirm ripgrep
elif command -v brew &>/dev/null; then
    brew uninstall ripgrep
fi
EOF

# 6. Hacer los scripts ejecutables
chmod +x components/ripgrep/*.sh

# 7. Agregar al perfil (opcional)
# Editar profiles/notebook.yaml y agregar "- ripgrep" en la lista de components

# 8. Instalar
./bootstrap bootstrap --only ripgrep
```

### Flujo 3: Actualizar el Entorno

```bash
# Actualizar el repositorio y re-ejecutar bootstrap
./bootstrap update

# O solo actualizar herramientas específicas
./bootstrap update-tools
```

### Flujo 4: Gestionar MCP Servers

```bash
# Listar todos los MCP servers
./bootstrap mcp-list

# Habilitar un MCP server
./bootstrap mcp-enable docker

# Deshabilitar un MCP server
./bootstrap mcp-disable postgres

# Regenerar configs para AI tools
./bootstrap mcp-generate mimo
./bootstrap mcp-generate opencode
./bootstrap mcp-generate claude-code
./bootstrap mcp-generate zed
```

### Flujo 5: Crear un Perfil Personalizado

```bash
# 1. Copiar un perfil existente
cp profiles/notebook.yaml profiles/mi-perfil.yaml

# 2. Editar el perfil
vim profiles/mi-perfil.yaml
```

Ejemplo de perfil personalizado:
```yaml
name: mi-perfil
description: "Mi configuración personalizada"

components:
  - git
  - ssh
  - node
  - python
  - docker
  - zed
  - mimo
  - opencode
  - ripgrep  # Tu componente personalizado

config_overrides:
  environment:
    editor: zed
```

```bash
# 3. Usar el perfil
./bootstrap --profile mi-perfil
```

---

## Integración con Otras Herramientas

### 1. **OpenCode**

AWE genera automáticamente la configuración de MCP servers para OpenCode en `~/.config/opencode/config.json` y los comandos personalizados en `~/.config/opencode/commands/`.

**Formato del config.json**:
```json
{
  "mcp": {
    "filesystem": {
      "enabled": true,
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
    }
  }
}
```

**Comandos personalizados**:

Los comandos se definen como archivos markdown en `~/.config/opencode/commands/`:

| Comando | Archivo | Descripción |
|---------|---------|-------------|
| `/compact` | `commands/compact.md` | Comprime el contexto de la conversación usando headroom MCP para liberar espacio en la ventana de contexto |

**Uso**: En OpenCode, escribe `/compact` para comprimir el contexto de la conversación actual. Esto es útil cuando la conversación se vuelve muy larga y necesitas liberar espacio.

**Regenerar config**:
```bash
./bootstrap mcp-generate opencode
```

### 2. **Claude Code**

AWE genera la configuración en `~/.config/claude/config.json`.

**Regenerar config**:
```bash
./bootstrap mcp-generate claude-code
```

### 3. **Zed Editor**

AWE genera la configuración en `~/.config/zed/settings.json`.

**Regenerar config**:
```bash
./bootstrap mcp-generate zed
```

### 4. **Mimo (Frontend Principal)**

Mimo es el frontend principal de tu AI Engineering Platform. Es un agente AI terminal-native (fork de OpenCode) con memoria persistente, agentes custom, skills, compose mode, y self-improvement.

**Iniciar Mimo**:
```bash
mimo
```

**Configuración generada automáticamente**:
```bash
./bootstrap mcp-generate mimo
```

Esto genera `~/.config/mimocode/mimocode.json` con:
- **Provider**: LiteLLM como gateway unificado (http://localhost:4000/v1)
- **Modelos**: Claude Sonnet, GPT-4, Ollama local, Gemini, OpenRouter
- **MCP servers**: filesystem, git, github, docker, sequential-thinking
- **Skills**: 28 skills migrados de la biblioteca de prompts
- **Custom commands**: /review, /debug, /test, /doc, /architect, /benchmark, /dream, /distill
- **Agentes custom**: security-auditor, docs-writer, perf-analyzer, tdd-driver, refactor, infra

#### Flujo de Trabajo con Mimo

**Sesión básica**:
```bash
# 1. Iniciar Mimo
mimo

# 2. Conversar con el agente Build (default)
> Crea un endpoint FastAPI para autenticación JWT

# 3. Cambiar al agente Plan (solo análisis, sin cambios)
# Presiona Tab para cambiar de agente

# 4. Usar un agente especializado
@security-auditor Revisa este código por vulnerabilidades

# 5. Usar un skill
Use skill: system-design

# 6. Ejecutar un comando custom
/review
/debug
/test
/doc
/architect
/benchmark
```

**Gestión de sesiones**:
```bash
# Ver sesiones activas
mimo sessions

# Reanudar una sesión anterior
mimo session <session-id>

# Limpiar contexto actual
/clear
```

**Modelos**:
```bash
# Cambiar modelo
/models

# Seleccionar modelo específico
/models litellm/claude-sonnet-4-20250514
/models litellm/local        # Ollama (CPU)
/models litellm/gpt-4
/models litellm/gemini-2.5-pro
/models litellm/fast         # Alias para Ollama
/models litellm/smart        # Alias para Claude Sonnet
/models litellm/reasoning    # Alias para GPT-4
```

**Agentes custom**:
| Agente | Tipo | Uso |
|--------|------|-----|
| `@security-auditor` | subagent | Auditoría de seguridad (read-only) |
| `@docs-writer` | subagent | Documentación (modelo local) |
| `@perf-analyzer` | subagent | Análisis de rendimiento |
| `@tdd-driver` | subagent | TDD estricto (Red-Green-Refactor) |
| `@refactor` | subagent | Refactoring seguro |
| `@infra` | subagent | Infraestructura y Docker |

**Skills disponibles** (28):
```
# Architecture
system-design, component-design, tradeoff-analysis

# Coding
clean-implementation, refactoring, pattern-implementation

# Review
code-review, pr-review, security-audit

# Planning
project-planning, sprint-planning, task-estimation

# Debug
systematic-debugging, performance-debugging, log-analysis

# Documentation
readme-generation, api-documentation, inline-documentation

# Security
threat-modeling, secure-coding-review

# Compose Workflows
compose-fastapi, compose-scraper, compose-pr-review,
compose-tests, compose-rag-pipeline, compose-debug

# Memory
dream-distill, checkpoint-management
```

**Custom tools**:
| Tool | Función |
|------|---------|
| `health-check` | Verificar estado de servicios (LiteLLM, Ollama, Qdrant) |
| `benchmark` | Comparar modelos (tiempo + tokens) |
| `model-router` | Verificar modelos disponibles en LiteLLM |
| `workflow-runner` | Ejecutar workflows de la plataforma |
| `context-injector` | Inyectar contexto RAG desde Qdrant |
| `n8n-trigger` | Disparar automatizaciones n8n |
| `memory-manager` | Gestionar MEMORY.md (read/write/search/clean) |

**Memory y Dream/Distill**:
```bash
# Extraer conocimiento de la sesión a memoria
/dream

# Detectar patrones y crear skills/commands
/distill

# Gestionar memoria
/memory read
/memory write "Nueva convención: usar type hints en todo"
/memory search "convención"
/memory clean

# Crear checkpoint manual
/checkpoint
```

**Compose mode** (specs-driven development):
```bash
# Iniciar modo compose
/compose

# Workflows disponibles:
# - fastapi: Crear proyecto FastAPI completo
# - scraper: Crear web scraper async
# - pr-review: Review completo de PR
# - tests: Generar suite de tests
# - rag-pipeline: Crear pipeline RAG
# - debug: Debug sistemático
```

**Notificaciones n8n**:
Mimo puede disparar workflows de n8n para:
- Ejecutar tests post-commit
- Monitorear salud de servicios (cada 5 min)
- Log de resúmenes de sesión
- Notificar commits

```bash
# Desde Mimo, usar el tool n8n-trigger
n8n-trigger --workflow "post-commit-tests"
n8n-trigger --workflow "health-monitor"
```

### 5. **Terax (Terminal AI-Nativo)**

Terax es un terminal AI-nativo que sirve como la **capa de presentación visual** en la plataforma. Se conecta a LiteLLM vía endpoint OpenAI-compatible y detecta agentes externos (MiMoCode, Claude Code) vía marcadores OSC 777.

**Arquitectura**:
```
Terax (Terminal/UI) → Orquestador (MiMoCode/ClaudeCode) → LiteLLM (Gateway) → Modelos + MCP
```

**Instalación**:
```bash
./bootstrap bootstrap --profile notebook  # Incluye Terax
# O instalar solo Terax:
./components/terax/install.sh
```

**Configuración**: Terax se configura automáticamente para conectarse a LiteLLM:
```yaml
# ~/.config/terax/config.yaml
ai:
  provider: openai-compatible
  base_url: "http://localhost:4000"
  api_key: "sk-litellm"
  model: "claude-sonnet-4-20250514"
```

**Agentes Custom**:
- `/orchestrator` — Orquestación completa de AI Engineering
- `/debugger` — Debugging sistemático
- `/reviewer` — Revisión de código con auditoría de seguridad

**Snippets**:
- `/research` — Investigación profunda con sub-agentes paralelos
- `/deploy` — Health check + deployment
- `/benchmark` — Comparación de rendimiento de modelos
- `/review-pr` — Revisión de pull requests

**Detección de Agentes**: Terax detecta automáticamente MiMoCode y Claude Code vía marcadores OSC 777. Cuando ejecutas estos agentes en terminales de Terax, su estado aparece en el panel de notificaciones.

**Documentación completa**: Ver `docs/terax-integration.md`

### 7. **Distributed AI Workspace**

El Distributed AI Workspace es un **sistema de gestión de sesiones, tareas y workspaces multi-dispositivo** que permite iniciar, continuar, monitorear y finalizar workflows desde cualquier dispositivo sin perder contexto.

**Arquitectura**:
```
Clients (Hermes/MiMo/OpenCode/Claude/Web)
    ↓ REST + WebSocket
API Gateway (FastAPI :8080)
    ↓
Workspace Layer
├── Workspace Manager (workspaces, dispositivos, usuarios)
├── Session Manager (sesiones, checkpoints, sync, migración)
├── Task Manager (tareas, progreso, métricas)
├── Workflow Engine (workflows, pasos, eventos)
├── Notification Service (alertas, push, historial)
└── Presence Service (heartbeat, actividad, idle detection)
    ↓ Event Bus (Redis Pub/Sub)
AI Engineering Platform (LiteLLM, Ollama, Qdrant, n8n, MCP)
    ↓
Storage (PostgreSQL + Redis)
```

**Instalación**:
```bash
# Incluir workspace en el perfil
./bootstrap bootstrap --profile host    # Incluye workspace
./bootstrap bootstrap --profile desktop # Incluye workspace

# O instalar solo workspace
./bootstrap bootstrap --only workspace
```

**Iniciar servicios**:
```bash
cd components/workspace
docker compose up -d

# Verificar
curl http://localhost:8080/health
# {"status":"ok","version":"0.1.0"}
```

**API Documentation**:
```bash
# Swagger UI
http://localhost:8080/docs

# ReDoc
http://localhost:8080/redoc
```

**Endpoints principales**:

| Categoría | Endpoints | Descripción |
|-----------|-----------|-------------|
| Workspaces | 8 | CRUD workspaces, dispositivos |
| Sessions | 13 | Lifecycle, mensajes, checkpoints, sync, migración |
| Tasks | 14 | Cola, progreso, métricas, acciones remotas |
| Workflows | 8 | Ejecución, pasos, pausa/resumen |
| Notifications | 8 | Alertas, reglas, historial |
| Presence | 4 | Heartbeat, actividad, idle detection |
| WebSocket | 1 | Eventos real-time |

**Ejemplo: Crear Workspace y Sesión**:
```bash
# Crear workspace
WS=$(curl -s -X POST http://localhost:8080/workspaces/ \
  -H "Content-Type: application/json" \
  -d '{"name":"AI Engineering","description":"Main workspace","owner_id":"user-1"}')
WS_ID=$(echo "$WS" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Crear sesión
curl -s -X POST http://localhost:8080/sessions/ \
  -H "Content-Type: application/json" \
  -d "{\"workspace_id\":\"$WS_ID\",\"title\":\"Debug Session\"}"

# Agregar mensaje
curl -s -X POST "http://localhost:8080/sessions/$SESS_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"role":"user","content":"Help me debug this error"}'
```

**Ejemplo: Crear y Ejecutar Tarea**:
```bash
# Crear tarea
TASK=$(curl -s -X POST http://localhost:8080/tasks/ \
  -H "Content-Type: application/json" \
  -d "{\"workspace_id\":\"$WS_ID\",\"title\":\"Run benchmark\",\"priority\":5}")
TASK_ID=$(echo "$TASK" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Ver progreso
curl -s "http://localhost:8080/tasks/$TASK_ID"
```

**WebSocket para Eventos Real-Time**:
```javascript
const ws = new WebSocket('ws://localhost:8080/ws?workspace_id=<uuid>');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.payload);
};

// Event types:
// session.created, session.message.new, session.paused, session.resumed
// task.created, task.started, task.progress, task.completed, task.failed
// device.online, device.offline
```

**Documentación completa**: Ver `docs/distributed-workspace-api.md`, `docs/distributed-workspace-deployment.md`, `docs/distributed-workspace-integration.md`

### 8. **Docker**

Los componentes de infraestructura (Ollama, Qdrant, PostgreSQL, n8n) corren en Docker.

**Ver contenedores**:
```bash
docker ps
```

**Ver logs**:
```bash
docker logs awe-ollama
```

**Detener un servicio**:
```bash
docker stop awe-ollama
```

### 6. **Tailscale**

Tailscale se instala pero no se configura automáticamente (requiere autenticación).

**Configurar Tailscale**:
```bash
sudo tailscale up
```

Esto te dará un URL para autenticarte en tu cuenta de Tailscale.

### 7. **Git**

Los dotfiles de Git se configuran automáticamente con symlinks.

**Personalizar configuración**:
```bash
# Editar el archivo en el repo
vim ~/ai-workstation-environment/dotfiles/git/.gitconfig

# Los cambios se reflejan instantáneamente (symlink)
```

### 8. **SSH**

Los dotfiles de SSH también se configuran con symlinks.

**Agregar claves SSH**:
```bash
./scripts/setup-ssh-keys.sh
```

---

## Prompts y Workflows

### Biblioteca de Prompts

El directorio `prompts/` contiene prompts organizados por categoría:

```
prompts/
├── architecture/      # system-design, tradeoff-analysis, component-design
├── coding/            # clean-implementation, refactoring, pattern-implementation
├── review/            # code-review, pr-review, security-audit
├── planning/          # project-planning, task-estimation, sprint-planning
├── debug/             # systematic-debugging, log-analysis, performance-debugging
├── documentation/     # readme-generation, api-documentation, inline-documentation
└── security/          # threat-modeling, secure-coding-review
```

**Uso**: Copia el prompt y úsalo con tu AI tool favorito.

Ejemplo:
```bash
cat prompts/architecture/system-design.md
# Copia el contenido y pégalo en OpenCode/Claude Code
```

### Workflows

El directorio `workflows/` contiene workflows componibles:

```
workflows/
├── create-fastapi-project.yaml
├── create-scraper.yaml
├── review-pr.yaml
├── generate-tests.yaml
├── create-rag.yaml
└── debug-python.yaml
```

**Uso**: Cada workflow define pasos, herramientas requeridas, y MCP servers necesarios.

Ejemplo de workflow:
```yaml
name: create-fastapi-project
description: "Scaffold a production-ready FastAPI project"
steps:
  - name: "Project Structure"
    action: "Create directory structure"
  - name: "Core Application"
    action: "Create FastAPI app"
  # ... más pasos
```

Puedes seguir estos pasos manualmente o usarlos como guía para tus AI tools.

---

## Scripts Útiles

### 1. **Health Check**

Verifica que todos los componentes estén funcionando:

```bash
./scripts/health-check.sh
```

Salida esperada:
```
=== AI Workstation Environment - Health Check ===

--- Core Tools ---
✓ Git
✓ SSH
✓ Python 3
✓ Node.js
✓ Docker
✓ Docker running

--- AI Tools ---
✓ OpenCode
✓ Claude Code
✓ Zed
✓ Terax

--- Infrastructure ---
✓ Tailscale
✓ Ollama
✓ LiteLLM
✓ Qdrant
✓ PostgreSQL
✓ n8n
✓ Workspace API
✓ Workspace Redis

--- MCP Configs ---
✓ OpenCode MCP
✓ Claude MCP
✓ Terax Config

=== Summary ===
Passed: 20
Failed: 0
Warnings: 0
```

### 2. **Setup SSH Keys**

Genera y configura claves SSH para GitHub/GitLab:

```bash
./scripts/setup-ssh-keys.sh
```

Te pedirá tu email y generará claves Ed25519.

### 3. **Backup**

Crea un backup de tus configuraciones:

```bash
./scripts/backup.sh
```

Los backups se guardan en `~/awe-backups/` y se mantienen los últimos 5.

---

## Tips y Mejores Prácticas

### 1. **Usa el Perfil Correcto**

- **Laptop**: `notebook`
- **Desktop potente**: `desktop`
- **Servidor**: `host`
- **Máquina minimal**: `minimal`

### 2. **Personaliza con `configs/local.yaml`**

Este archivo es gitignored, perfecto para configuraciones específicas de tu máquina:

```yaml
# configs/local.yaml
environment:
  editor: vscode  # Override para esta máquina

git:
  user_name: "Tu Nombre"
  user_email: "tu@email.com"
```

### 3. **Mantén el Repositorio Actualizado**

```bash
./bootstrap update
```

Esto hace `git pull` y re-ejecuta el bootstrap para instalar cualquier componente nuevo.

### 4. **Prueba los Componentes Individualmente**

Si algo falla, puedes instalar componentes uno por uno:

```bash
./bootstrap bootstrap --only docker
./bootstrap bootstrap --only zed
```

### 5. **Revisa el Estado**

```bash
./bootstrap status    # Qué está instalado
./bootstrap list      # Qué está disponible
```

### 6. **Usa los Prompts**

No reinventes la rueda. Los prompts en `prompts/` están optimizados para tareas comunes:

```bash
# Antes de hacer un code review
cat prompts/review/code-review.md

# Antes de diseñar un sistema
cat prompts/architecture/system-design.md
```

### 7. **Contribuye Componentes**

Si agregas un componente útil, considera hacer un PR al repositorio principal para que otros se beneficien.

---

## Troubleshooting

### Problema: "Python not found"

**Solución**:
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-venv

# Arch
sudo pacman -S python

# macOS
brew install python
```

### Problema: "Permission denied" al ejecutar bootstrap

**Solución**:
```bash
chmod +x bootstrap
chmod +x components/*/check.sh
chmod +x components/*/install.sh
chmod +x components/*/uninstall.sh
```

### Problema: Docker no corre

**Solución**:
```bash
# Iniciar Docker
sudo systemctl start docker

# Agregar tu usuario al grupo docker (requiere logout/login)
sudo usermod -aG docker $USER
```

### Problema: MCP servers no funcionan

**Solución**:
```bash
# Regenerar configs
./bootstrap mcp-generate mimo
./bootstrap mcp-generate opencode
./bootstrap mcp-generate claude-code
./bootstrap mcp-generate zed

# Verificar que los MCP servers están habilitados
./bootstrap mcp-list
```

### Problema: Mimo no funciona

**Solución**:
```bash
# Verificar que Mimo está instalado
mimo --version

# Regenerar configuración
./bootstrap mcp-generate mimo

# Verificar que LiteLLM está corriendo (necesario para Mimo)
docker ps | grep litellm

# Si LiteLLM no está corriendo:
./bootstrap bootstrap --only litellm
```

### Problema: Dotfiles no se actualizan

**Solución**:
```bash
# Forzar recreación de symlinks
./bootstrap bootstrap --force
```

### Problema: Workspace API no inicia

**Solución**:
```bash
# Verificar que Docker está corriendo
docker info

# Verificar que PostgreSQL está accesible
docker exec awe-postgresql psql -U awe -d awe -c "SELECT 1;"

# Recrear contenedores
cd components/workspace
docker compose down
docker compose up -d --build

# Verificar salud
curl http://localhost:8080/health
```

### Problema: Puerto 8080 ya en uso

**Solución**:
```bash
# Encontrar qué usa el puerto
ss -tlnp | grep 8080

# Cambiar puerto en docker-compose.yaml
# Editar components/workspace/docker-compose.yaml
# Cambiar "8080:8080" a "8081:8080"
```

---

## Preguntas Frecuentes

### ¿Puedo usar esto en Windows nativo?

No está soportado oficialmente. Recomendamos WSL2 para Windows.

### ¿Puedo agregar mis propias herramientas?

Sí, sigue el flujo en "Flujo 2: Agregar una Nueva Herramienta" arriba.

### ¿Qué pasa si ya tengo algunas herramientas instaladas?

El bootstrap es idempotente. Si una herramienta ya está instalada, la detecta y la salta.

### ¿Puedo desinstalar algo?

Sí, cada componente tiene un `uninstall.sh`. Puedes ejecutarlo manualmente:

```bash
bash components/docker/uninstall.sh
```

### ¿Cómo actualizo una herramienta específica?

```bash
# Re-instalar un componente (si hay update.sh, lo usa)
bash components/docker/install.sh
```

### ¿Puedo usar esto sin Git?

Sí, puedes descargar el ZIP del repositorio y ejecutar el bootstrap. Pero perderás la capacidad de hacer `./bootstrap update`.

### ¿Qué hace exactamente el bootstrap?

1. Verifica que Python 3.10+ esté instalado
2. Crea un virtual environment en `.venv/`
3. Instala dependencias (PyYAML)
4. Detecta tu sistema (OS, WSL, GPU, Docker, etc.)
5. Carga la configuración (default → profile → local)
6. Resuelve dependencias entre componentes
7. Instala cada componente (si no está ya instalado)
8. Aplica dotfiles (symlinks)
9. Instala y configura MCP servers (13 servers definidos)
10. Genera configs para Mimo, OpenCode, Claude Code, Zed, Terax
11. Instala agentes custom, skills y custom tools de Mimo
12. Inicia Workspace API (si profile lo incluye)

---

## Recursos Adicionales

- **README.md**: Visión general del proyecto
- **AGENTS.md**: Guía para agentes de IA
- **docs/architecture.md**: Arquitectura técnica
- **docs/adding-components.md**: Cómo agregar componentes
- **docs/profiles.md**: Sistema de perfiles
- **docs/mcp-management.md**: Gestión de MCP servers
- **docs/GETTING_STARTED.md**: Guía de inicio rápido
- **docs/mimo-architecture.md**: Análisis de capacidades de Mimo
- **docs/mimo-platform-design.md**: Diseño de integración Mimo + Plataforma
- **docs/mimo-implementation-plan.md**: Plan de implementación Mimo
- **docs/distributed-workspace-summary.md**: Diseño de Distributed AI Workspace
- **docs/distributed-workspace-architecture.md**: Arquitectura completa del Workspace
- **docs/distributed-workspace-diagrams.md**: Diagramas de flujo del Workspace
- **docs/distributed-workspace-api.md**: API Reference del Workspace
- **docs/distributed-workspace-deployment.md**: Guía de deployment del Workspace
- **docs/distributed-workspace-integration.md**: Guía de integración de clientes
- **docs/terax-integration.md**: Integración de Terax

---

## Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de Troubleshooting arriba
2. Ejecuta `./scripts/health-check.sh` para diagnosticar
3. Abre un issue en el repositorio de GitHub

---

## Conclusión

AI Workstation Environment transforma la configuración de entornos de desarrollo de un proceso manual, lento y propenso a errores, en un comando automatizado, rápido y reproducible.

Con **Mimo como frontend principal**, tienes un agente AI terminal-native con:
- **28 skills** para tareas especializadas
- **6 agentes custom** para diferentes roles
- **7 custom tools** para interactuar con tu plataforma
- **6 compose workflows** para desarrollo guiado
- **Memory persistente** con dream/distill para auto-mejora
- **Integración completa** con LiteLLM, Ollama, Qdrant, n8n y todos tus MCP servers

Con **Distributed AI Workspace**, tienes un sistema multi-dispositivo con:
- **57 endpoints REST** para workspaces, sesiones, tareas, workflows, notificaciones
- **WebSocket real-time** para sincronización entre dispositivos
- **Session migration** para cambiar de notebook a desktop sin perder contexto
- **Task management** con progreso, métricas y acciones remotas
- **Notification system** con alertas multi-canal (WebSocket, SSE, webhooks)
- **Presence service** con heartbeat y detección de idle

**Empieza ahora**:
```bash
git clone https://github.com/TU_USUARIO/ai-workstation-environment.git
cd ai-workstation-environment
./bootstrap --profile notebook
```

En 10 minutos tendrás un entorno profesional de AI Engineering completamente configurado con Mimo como tu interfaz inteligente.
