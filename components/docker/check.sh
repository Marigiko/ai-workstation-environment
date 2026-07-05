#!/usr/bin/env bash
set -euo pipefail

if command -v docker &>/dev/null; then
    if docker info &>/dev/null; then
        exit 0
    fi
fi
exit 1
