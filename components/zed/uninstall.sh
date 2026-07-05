#!/usr/bin/env bash
set -euo pipefail

if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &>/dev/null; then
    brew uninstall --cask zed || true
else
    echo "WARNING: Zed uninstall not fully implemented"
fi
