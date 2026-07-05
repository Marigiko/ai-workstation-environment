#!/usr/bin/env bash
set -euo pipefail

if command -v ssh &>/dev/null; then
    exit 0
fi
exit 1
