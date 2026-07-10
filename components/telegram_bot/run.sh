#!/usr/bin/env bash

# Telegram Bot Runner - Handles signals properly

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
PYTHON="$PROJECT_DIR/.venv/bin/python3"
LOG="/tmp/telegram-bot.log"
PIDFILE="/tmp/telegram-bot.pid"

# Load token
if [ -f "$SCRIPT_DIR/.env" ]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

TOKEN="${TELEGRAM_BOT_TOKEN:-}"

if [ -z "$TOKEN" ]; then
    echo "❌ No TELEGRAM_BOT_TOKEN"
    exit 1
fi

case "${1:-start}" in
    start)
        # Kill existing
        if [ -f "$PIDFILE" ]; then
            kill "$(cat $PIDFILE)" 2>/dev/null || true
            sleep 1
        fi

        echo "Starting bot..."
        cd "$SCRIPT_DIR" || exit
        export TELEGRAM_BOT_TOKEN="$TOKEN"

        # Use setsid to detach from terminal
        setsid "$PYTHON" "$SCRIPT_DIR/bot.py" > "$LOG" 2>&1 &
        echo $! > "$PIDFILE"
        sleep 3

        if grep -q "Application started" "$LOG" 2>/dev/null; then
            echo "✅ Bot running (PID: $(cat $PIDFILE))"
        else
            echo "⚠️  Bot may have issues. Check: $LOG"
            tail -5 "$LOG"
        fi
        ;;
    stop)
        if [ -f "$PIDFILE" ]; then
            kill "$(cat $PIDFILE)" 2>/dev/null || true
            rm -f "$PIDFILE"
            echo "Stopped"
        fi
        ;;
    status)
        if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then
            echo "Running (PID: $(cat $PIDFILE))"
        else
            echo "Stopped"
        fi
        ;;
    logs)
        tail -f "$LOG"
        ;;
esac
