#!/usr/bin/env bash
set -euo pipefail

if command -v claude &>/dev/null; then
    exit 0
fi
exit 1
