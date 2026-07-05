#!/usr/bin/env bash
set -euo pipefail

if command -v zed &>/dev/null; then
    exit 0
fi
exit 1
