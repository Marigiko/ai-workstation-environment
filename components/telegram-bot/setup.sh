#!/usr/bin/env bash
set -euo pipefail

# Telegram Bot Setup Script
# This script guides you through setting up the Telegram bot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║        Telegram Bot — Setup para AI Workstation         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if token already exists
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
    echo -e "${GREEN}✓${NC} Token ya configurado: ${TELEGRAM_BOT_TOKEN:0:10}..."
    echo ""
    read -p "¿Deseas usar este token? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "Usando token existente."
    else
        echo ""
        echo "Ingresa tu nuevo token:"
        read -p "> " NEW_TOKEN
        export TELEGRAM_BOT_TOKEN="$NEW_TOKEN"
    fi
else
    echo -e "${YELLOW}⚠${NC} No se encontró TELEGRAM_BOT_TOKEN"
    echo ""
    echo "Pasos para crear tu bot:"
    echo ""
    echo "  1. Abre Telegram y busca @BotFather"
    echo "  2. Envía /newbot"
    echo "  3. Elige un nombre (ej: AI Workstation Bot)"
    echo "  4. Elige un username (ej: ai_workstation_bot)"
    echo "  5. Copia el token que te dé BotFather"
    echo ""
    echo -e "${BLUE}Token se ve así:${NC} 7123456789:AAH1bGciOiJSUzI1NiIs..."
    echo ""
    read -p "Pega tu token aquí: " TELEGRAM_BOT_TOKEN

    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        echo -e "${RED}✗${NC} No se proporcionó token. Saliendo."
        exit 1
    fi
fi

echo ""

# Check dependencies
echo "📦 Verificando dependencias..."
echo ""

check_package() {
    local pkg=$1
    if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $pkg"
        return 0
    else
        echo -e "  ${RED}✗${NC} $pkg (instalando...)"
        return 1
    fi
}

MISSING=0
check_package "telegram" || MISSING=1
check_package "aiohttp" || MISSING=1
check_package "yaml" || MISSING=1

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "Instalando dependencias faltantes..."
    pip install python-telegram-bot aiohttp pyyaml
    echo ""
fi

# Create .env file
echo "📝 Creando archivo .env..."
echo ""

cat > "$SCRIPT_DIR/.env" << EOF
# Telegram Bot Configuration
# Created: $(date)

TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN

# Optional: Restrict to specific user IDs
# Get your ID from @userinfobot
TELEGRAM_USER_ID=
EOF

echo -e "${GREEN}✓${NC} Archivo .env creado en $SCRIPT_DIR/.env"
echo ""

# Update bot.yaml with token
echo "📝 Actualizando configuración..."
echo ""

cat > "$SCRIPT_DIR/config/bot.yaml" << EOF
# Telegram Bot Configuration
# Created: $(date)

bot:
  token: "$TELEGRAM_BOT_TOKEN"
  webhook_url: ""  # Set for production
  allowed_users: []  # Telegram user IDs (empty = allow all)

# n8n integration
n8n:
  webhook_url: "http://localhost:5678/webhook/telegram"
  api_url: "http://localhost:5678/api/v1"
  api_key: ""

# Workspace API
workspace:
  api_url: "http://localhost:8080"
  api_key: ""

# Gateway API
gateway:
  api_url: "http://localhost:8000"
  api_key: ""

# Session settings
session:
  timeout: 3600  # 1 hour
  max_concurrent: 5
EOF

echo -e "${GREEN}✓${NC} Configuración actualizada"
echo ""

# Test bot connection
echo "🔗 Probando conexión con Telegram..."
echo ""

export TELEGRAM_BOT_TOKEN

python3 -c "
import os
import asyncio
from telegram import Bot

async def test():
    bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    me = await bot.get_me()
    print(f'  Bot: @{me.username}')
    print(f'  Nombre: {me.first_name}')
    print(f'  ID: {me.id}')
    return True

try:
    asyncio.run(test())
    print()
    print('  Conexión exitosa!')
except Exception as e:
    print(f'  Error: {e}')
    print()
    print('  Verifica que el token sea válido.')
    exit(1)
" 2>&1

echo ""

# Ask to start bot
echo "🚀 ¿Deseas iniciar el bot ahora?"
echo ""
echo "  1. Sí, iniciar en background"
echo "  2. Sí, iniciar en foreground (ver logs)"
echo "  3. No, iniciar después manualmente"
echo ""
read -p "Selecciona (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Iniciando bot en background..."
        cd "$SCRIPT_DIR/../../.."
        nohup python3 "$SCRIPT_DIR/bot.py" > /tmp/telegram-bot.log 2>&1 &
        echo $! > /tmp/telegram-bot.pid
        sleep 2
        if kill -0 $(cat /tmp/telegram-bot.pid) 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Bot iniciado (PID: $(cat /tmp/telegram-bot.pid))"
            echo "  Logs: /tmp/telegram-bot.log"
        else
            echo -e "${RED}✗${NC} Error al iniciar bot"
            echo "  Revisa: /tmp/telegram-bot.log"
        fi
        ;;
    2)
        echo ""
        echo "Iniciando bot (Ctrl+C para detener)..."
        cd "$SCRIPT_DIR/../../.."
        python3 "$SCRIPT_DIR/bot.py"
        ;;
    3)
        echo ""
        echo "Para iniciar manualmente:"
        echo "  cd /mnt/d/Projects/ai-workstation-environment"
        echo "  python3 components/telegram-bot/bot.py"
        ;;
esac

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    ¡Configuración Lista!                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📱 Abre Telegram y busca tu bot"
echo ""
echo "Comandos para probar:"
echo "  /start    — Ver menú"
echo "  /status   — Estado del sistema"
echo "  /models   — Modelos disponibles"
echo "  /prompt <tarea> — Enviar tarea"
echo "  /auto     — Modo automático"
echo ""
echo "📚 Documentación: $SCRIPT_DIR/SETUP.md"
echo ""
