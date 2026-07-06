# Plan de Implementacion: Mimo como Frontend

## Etapas

| Etapa | Que | Esfuerzo | Estado |
|---|---|---|---|
| **1** | Instalar Mimo + componente en la plataforma | Bajo | COMPLETADO |
| **2** | Configurar `mimocode.json` con LiteLLM como provider | Bajo | COMPLETADO |
| **3** | Migrar MCP servers a formato Mimo | Bajo | COMPLETADO (via _gen_mimo) |
| **4** | Crear agentes custom (security, docs, perf, tdd, infra) | Medio | COMPLETADO |
| **5** | Migrar prompts -> skills (SKILL.md format) | Medio | COMPLETADO |
| **6** | Expandir LiteLLM config con todos los providers | Bajo | COMPLETADO |
| **7** | Crear custom tools (model-router, health-check, benchmark) | Medio | COMPLETADO |
| **8** | Configurar compose mode workflows | Medio | COMPLETADO |
| **9** | Integrar n8n automatizaciones | Alto | COMPLETADO |
| **10** | Configurar dream/distill + memory persistence | Bajo | COMPLETADO |

---

## Etapa 1: Instalar Mimo + Componente

### Archivos a crear

```
components/mimo/
  component.yaml
  check.sh
  install.sh
  uninstall.sh
```

### Cambios en perfiles

- `profiles/notebook.yaml`: agregar `mimo`
- `profiles/desktop.yaml`: agregar `mimo`

### Cambios en core/mcp.py

- Agregar generador de config para Mimo (formato JSON con `mcp` key)

---

## Etapa 2: Configurar mimocode.json

- Crear template de config global
- LiteLLM como provider unico
- Deshabilitar providers directos
- Configurar MCP servers

---

## Etapa 3: Migrar MCP Servers

- Reutilizar definiciones de `mcp/servers/`
- Generar config Mimo-compatible
- Habilitar servers segun perfil

---

## Etapa 4: Agentes Custom

Crear en `~/.config/mimocode/agents/`:
- security-auditor.md
- docs-writer.md
- perf-analyzer.md
- tdd-driver.md
- refactor.md
- infra.md

---

## Etapa 5: Migrar Prompts -> Skills

Convertir los 21 prompts de `prompts/` a formato SKILL.md:
- Frontmatter YAML (name, description)
- Contenido markdown
- Ubicar en `~/.config/mimocode/skills/`

---

## Etapa 6: Expandir LiteLLM

Actualizar `components/litellm/litellm_config.yaml`:
- Agregar todos los providers
- Crear aliases (fast, smart, reasoning)
- Configurar fallbacks

---

## Etapa 7: Custom Tools

Crear en `.mimocode/tools/`:
- model-router.ts
- health-check.ts
- workflow-runner.ts
- benchmark.ts
- context-injector.ts

---

## Etapa 8: Compose Workflows

Mapear workflows existentes a compose skills:
- create-fastapi-project -> fastapi
- create-scraper -> scraper
- review-pr -> pr-review
- generate-tests -> tests
- create-rag -> rag-pipeline
- debug-python -> debug

---

## Etapa 9: n8n Automatizaciones

- Webhook triggers post-workflow
- Auto-documentacion post-merge
- Auto-tests post-commit
- Notifications

---

## Etapa 10: Dream/Distill + Memory

- Configurar dream automatico
- Configurar distill para detectar patrones
- Integrar con codebase-memory MCP
- Configurar checkpoint thresholds

---

## Resumen Final

**Estado:** COMPLETADO (10/10 etapas)

**Fecha:** 2026-07-06

### Componentes Creados

#### Componente Mimo
- `components/mimo/component.yaml`
- `components/mimo/check.sh`
- `components/mimo/install.sh`
- `components/mimo/uninstall.sh`

#### Agentes (6)
- security-auditor
- docs-writer
- perf-analyzer
- tdd-driver
- refactor
- infra

#### Skills (28)
- 20 skills de prompts existentes
- 6 compose workflows
- 2 memory management skills

#### Custom Tools (7)
- model-router
- health-check
- benchmark
- workflow-runner
- context-injector
- n8n-trigger
- memory-manager

#### n8n Workflows (4)
- post-commit-tests
- health-monitor
- session-summary
- git-notifier

### Configuracion
- `configs/mimo-template.json`
- `components/litellm/litellm_config.yaml` (expandido)
- `core/mcp.py` (generador Mimo)
- `profiles/notebook.yaml` (Mimo agregado)
- `profiles/desktop.yaml` (Mimo agregado)

### Verificacion
- **ruff**: All checks passed
- **pytest**: 29 passed, 2 skipped
- **shellcheck**: No warnings

### Siguiente Paso

Ejecutar bootstrap para instalar todo:
```bash
./bootstrap --profile notebook
```

Luego iniciar Mimo:
```bash
mimo
```
