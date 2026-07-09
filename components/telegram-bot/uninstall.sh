#!/usr/bin/env bash
set -euo pipefail
pip3 uninstall -y python-telegram-bot 2>/dev/null || true
rm -rf "${HOME}/.config/telegram-bot"
echo "Telegram bot uninstalled"