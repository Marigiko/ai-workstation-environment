#!/usr/bin/env bash
set -euo pipefail

if command -v python3 &>/dev/null; then
    exit 0
fi
exit 1
