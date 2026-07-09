# Telegram Bot — Guía de Configuración

## Paso 1: Crear el Bot en Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía el comando `/newbot`
3. Elige un nombre para tu bot (ej: "AI Workstation Bot")
4. Elige un username único (ej: `ai_workstation_bot`)
5. BotFather te dará un **token**. Cópialo.

Ejemplo de token:
```
7123456789:AAH1bGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Paso 2: Configurar el Token

### Opción A: Variable de entorno (Recomendado)

```bash
export TELEGRAM_BOT_TOKEN="TU_TOKEN_AQUI"
```

Para hacerlo permanente, agrega a tu `~/.bashrc` o `~/.zshrc`:
```bash
echo 'export TELEGRAM_BOT_TOKEN="TU_TOKEN_AQUI"' >> ~/.zshrc
```

### Opción B: Archivo .env

Crea el archivo `components/telegram-bot/.env`:
```bash
TELEGRAM_BOT_TOKEN=TU_TOKEN_AQUI
TELEGRAM_USER_ID=TU_USER_ID  # Opcional: para restringir acceso
```

### Opción C: Archivo de configuración

Edita `components/telegram-bot/config/bot.yaml`:
```yaml
bot:
  token: "TU_TOKEN_AQUI"
```

## Paso 3: Obtener tu User ID (Opcional)

Para restringir el bot solo a ti:

1. Busca **@userinfobot** en Telegram
2. Envía cualquier mensaje
3. Copia tu **User ID**

## Paso 4: Instalar Dependencias

```bash
cd /mnt/d/Projects/ai-workstation-environment
pip install -r components/telegram-bot/requirements.txt
```

O manualmente:
```bash
pip install python-telegram-bot aiohttp pyyaml
```

## Paso 5: Iniciar el Bot

```bash
cd /mnt/d/Projects/ai-workstation-environment
python3 components/telegram-bot/bot.py
```

## Paso 6: Probar el Bot

1. Busca tu bot en Telegram (ej: `@ai_workstation_bot`)
2. Envía `/start`
3. Prueba los comandos:
   - `/status` — Ver estado del sistema
   - `/models` — Listar modelos disponibles
   - `/prompt escribe una función fibonacci` — Enviar tarea
   - `/auto` — Activar modo automático

## Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `/start` | Ver menú de comandos |
| `/prompt <tarea>` | Enviar tarea al orquestador |
| `/status` | Estado del sistema |
| `/status <task_id>` | Estado de una tarea |
| `/approve <task_id>` | Aprobar tarea |
| `/reject <task_id>` | Rechazar tarea |
| `/commit <mensaje>` | Git commit |
| `/worktrees` | Listar worktrees |
| `/model <nombre>` | Cambiar modelo |
| `/agent <nombre>` | Cambiar agente |
| `/auto` | Modo automático ON/OFF |
| `/models` | Listar modelos |

## Solución de Problemas

### "No Telegram bot token configured!"
- Verifica que la variable de entorno esté configurada
- O que el token esté en el archivo de configuración

### "Error al enviar tarea"
- Verifica que n8n esté corriendo (puerto 5678)
- Verifica que el webhook exista en n8n

### El bot no responde
- Verifica que el token sea válido
- Revisa los logs en la consola
- Asegúrate de que no haya otro bot usando el mismo token

## Producción

Para uso en producción:

1. Usa un servicio como systemd o Docker
2. Configura un webhook en lugar de polling
3. Agrega tu User ID a `allowed_users`
4. Configura n8n con los workflows necesarios

### Ejemplo con systemd

Crea `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=AI Telegram Bot
After=network.target

[Service]
Type=simple
User=keyz
WorkingDirectory=/mnt/d/Projects/ai-workstation-environment
ExecStart=/usr/bin/python3 components/telegram-bot/bot.py
Restart=always
Environment=TELEGRAM_BOT_TOKEN=TU_TOKEN

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```
