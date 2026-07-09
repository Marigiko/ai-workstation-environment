#!/usr/bin/env bash
set -euo pipefail

if command -v docker &>/dev/null; then
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q awe-workspace-api; then
        exit 0
    fi
fi
exit 1
