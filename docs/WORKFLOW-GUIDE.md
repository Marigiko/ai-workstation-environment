# Guía de Flujo de Trabajo — AI Workstation Environment

## Estado Actual del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    TU ESTACIÓN DE TRABAJO AI                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Terax     │    │   MiMo      │    │   Claude    │     │
│  │  (Terminal) │    │  (Orquest.) │    │  (Backend)  │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│                    ┌───────▼───────┐                        │
│                    │  AI Proxy     │                        │
│                    │  (Puerto 8090)│                        │
│                    │  + Headroom   │                        │
│                    └───────┬───────┘                        │
│                            │                                │
│         ┌──────────────────┼──────────────────┐             │
│         │                  │                  │             │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐     │
│  │   LiteLLM   │    │   Ollama    │    │   Gemini    │     │
│  │  (Gateway)  │    │  (Local)    │    │  (Cloud)    │     │
│  │  Puerto 4000│    │  Puerto     │    │  API Key    │     │
│  └─────────────┘    │  11434      │    └─────────────┘     │
│                     └─────────────┘                        │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   n8n       │    │  Telegram   │    │  Workspace  │     │
│  │ (Automat.)  │    │    Bot      │    │    API      │     │
│  │  Puerto 5678│    │  (Pendiente)│    │  Puerto 8080│     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Servicios Activos

| Servicio | Puerto | Estado | Descripción |
|----------|--------|--------|-------------|
| AI Proxy | 8090 | ✅ ACTIVO | Proxy con Headroom compression |
| LiteLLM | 4000 | ✅ ACTIVO | Gateway de modelos (18 modelos) |
| Ollama | 11434 | ✅ ACTIVO | Modelos locales (GPU) |
| n8n | 5678 | ✅ ACTIVO | Automatizaciones |
| Redis | 6380 | ✅ ACTIVO | Cache y pub/sub |
| PostgreSQL | 5432 | ✅ ACTIVO | Base de datos |
| Qdrant | - | ✅ ACTIVO | Vector database |

## Cómo Empezar

### Opción 1: Usar Terax como Terminal AI

```bash
# 1. Abre Terax
terax

# 2. Configura el provider (en Terax, presiona Ctrl+,)
#    - Provider: OpenAI Compatible
#    - URL: http://localhost:8090
#    - API Key: (dejar vacío)
#    - Model: mimo-auto

# 3. Ahora puedes usar Terax con MiMo/Claude
# Escribe tu prompt y Terax lo enviará al proxy
```

### Opción 2: Usar MiMo directamente

```bash
# 1. Inicia MiMo
mimo

# 2. MiMo ya está configurado para usar:
#    - Modelos locales vía Ollama
#    - Modelos cloud vía LiteLLM
#    - MCP servers (headroom, codebase-memory, ponytail)

# 3. En MiMo, puedes usar /compact para comprimir contexto
```

### Opción 3: Usar Claude Code

```bash
# 1. Asegúrate de estar logueado
claude login

# 2. Inicia Claude
claude

# 3. Claude ya tiene acceso a:
#    - Herramientas de código
#    - MCP servers
#    - Headroom compression
```

### Opción 4: Llamadas HTTP directas al Proxy

```bash
# Con MiMo
curl -X POST http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mimo-auto",
    "messages": [{"role": "user", "content": "hola"}],
    "headroom": true
  }'

# Con Claude
curl -X POST http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude",
    "messages": [{"role": "user", "content": "hola"}],
    "headroom": true
  }'
```

## Flujo de Trabajo Recomendado

### Para Desarrollo de Código

```
1. Escribe tu tarea en Terax/MiMo/Claude
   ↓
2. Headroom comprime el contexto (60-90% ahorro)
   ↓
3. El proxy envía a MiMo (gratis) o Claude (Max)
   ↓
4. Recibes la respuesta
   ↓
5. Si necesitas más contexto, usa /compact
```

### Para Tareas Complejas (Auto Mode)

```
1. Envía una tarea compleja
   ↓
2. AutoOrchestrator planifica:
   - Architect → mimo-auto (planificación)
   - Coder → mimo-auto (implementación)
   - Reviewer → claude (revisión)
   - Documenter → mimo-fast (docs)
   - Tester → mimo-fast (pruebas)
   ↓
3. Cada agente ejecuta en paralelo
   ↓
4. Resultados se agregan
   ↓
5. Notificación vía Telegram (cuando esté configurado)
```

### Para Automatizaciones (n8n)

```
1. Accede a n8n: http://localhost:5678
   ↓
2. Importa workflows de components/n8n/workflows/
   ↓
3. Configura triggers:
   - Webhook → envía prompt al proxy
   - Cron → ejecuta tareas periódicas
   - Telegram → recibe notificaciones
   ↓
4. n8n orquesta el flujo automáticamente
```

## Modelos Disponibles

### Vía AI Proxy (Puerto 8090) — SIN API Keys

| Modelo | Backend | Costo | Uso Recomendado |
|--------|---------|-------|-----------------|
| mimo | MiMo Auto | Gratis | General |
| mimo-auto | MiMo Auto | Gratis | General |
| mimo-fast | MiMo Auto | Gratis | Rápido |
| claude | Claude Max | Gratis* | Razonamiento |
| claude-code | Claude Max | Gratis* | Código |

*Requiere `claude login` (suscripción Claude Max)

### Vía LiteLLM (Puerto 4000) — Con API Keys

| Modelo | Provider | Costo |
|--------|----------|-------|
| qwen2.5-coder:7b | Ollama (local) | Gratis |
| phi3:mini | Ollama (local) | Gratis |
| gemini-2.5-flash | Google | Gratis |
| gemini-2.5-pro | Google | Gratis |
| claude-sonnet-4-20250514 | Anthropic | Pago |

## Comandos Útiles

```bash
# Gestión del AI Proxy
./components/ai-proxy/start.sh start    # Iniciar
./components/ai-proxy/start.sh stop     # Detener
./components/ai-proxy/start.sh status   # Ver estado
./components/ai-proxy/start.sh restart  # Reiniciar

# Prueba rápida
./components/ai-proxy/client.sh mimo-auto "hola"
./components/ai-proxy/client.sh claude "hola"

# Ver modelos disponibles
curl -s http://localhost:8090/v1/models | python3 -m json.tool

# Verificar compresión
curl -X POST http://localhost:8090/v1/compress \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo","messages":[{"role":"user","content":"test"}]}'
```

## Próximos Pasos

### Prioridad Alta
1. **Configurar Telegram Bot**
   ```bash
   # Crear bot con @BotFather
   # Guardar token en components/telegram-bot/.env
   # Iniciar bot
   ```

2. **Iniciar Workspace API**
   ```bash
   cd components/workspace
   # Configurar .env
   # Iniciar API en puerto 8080
   ```

### Prioridad Media
3. **Configurar Terax Provider**
   - Abre Terax
   - Ctrl+, → Settings
   - Agregar provider: http://localhost:8090

4. **Importar workflows n8n**
   - Accede a http://localhost:5678
   - Importa components/n8n/workflows/*.json

### Prioridad Baja
5. **Configurar notificaciones**
   - Telegram bot para alertas
   - n8n para automatizaciones

## Solución de Problemas

### AI Proxy no responde
```bash
# Verificar si está corriendo
lsof -ti:8090

# Reiniciar
./components/ai-proxy/start.sh restart

# Ver logs
cat /tmp/ai-proxy.log
```

### MiMo no responde
```bash
# Probar directamente
mimo run "hola"

# Verificar modelo
mimo models
```

### Claude no responde
```bash
# Verificar login
claude login

# Probar directamente
claude -p "hola"
```

### LiteLLM no responde
```bash
# Verificar contenedor
docker ps | grep litellm

# Ver logs
docker logs awe-litellm
```

## Arquitectura de Compresión

```
Tu Prompt → Headroom Compressor → Backend (MiMo/Claude)
     │              │                    │
     │         ┌────▼────┐              │
     │         │ 6       │              │
     │         │ estrat. │              │
     │         └────┬────┘              │
     │              │                    │
     │    ┌─────────▼─────────┐         │
     │    │ • Whitespace norm │         │
     │    │ • Strip comments  │         │
     │    │ • Dedup lines     │         │
     │    │ • Aggressive      │         │
     │    │ • Noise removal   │         │
     │    │ • Code preserve   │         │
     │    └─────────┬─────────┘         │
     │              │                    │
     │         ┌────▼────┐              │
     │         │ 60-90%  │              │
     │         │ ahorro  │              │
     │         └────┬────┘              │
     │              │                    │
     └──────────────┼────────────────────┘
                    │
              ┌─────▼─────┐
              │ Respuesta │
              │  del LLM  │
              └───────────┘
```

## Resumen

Tu estación de trabajo AI está **operativa**. Puedes:

1. **Usar Terax** como terminal AI (con proxy en puerto 8090)
2. **Usar MiMo** directamente (ya configurado)
3. **Usar Claude Code** (con login)
4. **Hacer llamadas HTTP** al proxy
5. **Automatizar** con n8n

**Headroom** comprime automáticamente TODOS los prompts antes de enviarlos a cualquier modelo, ahorrando 60-90% de tokens.

¿Qué te gustaría hacer primero?
