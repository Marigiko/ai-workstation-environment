#!/usr/bin/env bash
set -euo pipefail

if command -v opencode &>/dev/null; then
    exit 0
fi
exit 1
