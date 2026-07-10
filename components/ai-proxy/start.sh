#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-/mnt/d/Projects/ai-workstation-environment/.venv/bin/python3}"
LOG="/tmp/ai-proxy.log"
PIDFILE="/tmp/ai-proxy.pid"

usage() {
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
}

is_running() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

do_stop() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Stopping AI Proxy Server (PID: $PID)..."
            kill "$PID" 2>/dev/null || true
            sleep 2
            kill -9 "$PID" 2>/dev/null || true
        fi
        rm -f "$PIDFILE"
    fi
    # Also kill any orphaned processes
    lsof -ti:8090 2>/dev/null | xargs kill -9 2>/dev/null || true
    echo "Stopped"
}

do_start() {
    if is_running; then
        echo "AI Proxy Server already running (PID: $(cat $PIDFILE))"
        return 0
    fi

    echo "Starting AI Proxy Server on port 8090..."
    cd "$SCRIPT_DIR" || exit
    nohup "$PYTHON" server.py > "$LOG" 2>&1 &
    echo $! > "$PIDFILE"

    # Wait for readiness
    for _ in $(seq 1 15); do
        if curl -s http://localhost:8090/health > /dev/null 2>&1; then
            echo "Server ready (PID: $(cat $PIDFILE))"
            return 0
        fi
        sleep 1
    done

    echo "Server failed to start. Check $LOG"
    tail -20 "$LOG"
    return 1
}

do_status() {
    if is_running; then
        echo "AI Proxy Server: RUNNING (PID: $(cat $PIDFILE))"
        curl -s http://localhost:8090/health 2>/dev/null | python3 -m json.tool 2>/dev/null || true
    else
        echo "AI Proxy Server: STOPPED"
    fi
}

case "${1:-start}" in
    start)   do_start ;;
    stop)    do_stop ;;
    restart) do_stop; sleep 1; do_start ;;
    status)  do_status ;;
    *)       usage ;;
esac
