#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Installing Telegram bot dependencies..."
pip3 install python-telegram-bot aiohttp 2>/dev/null || pip install python-telegram-bot aiohttp
echo "Copying bot configuration..."
CONFIG_DIR="${HOME}/.config/telegram-bot"
mkdir -p "$CONFIG_DIR"
if [ -f "$SCRIPT_DIR/config/bot.yaml" ]; then
    cp -f "$SCRIPT_DIR/config/bot.yaml" "$CONFIG_DIR/bot.yaml"
    echo "Config installed to $CONFIG_DIR/bot.yaml"
fi
echo "Telegram bot installed!"
echo "Configure TELEGRAM_BOT_TOKEN in $CONFIG_DIR/bot.yaml"