#!/usr/bin/env bash
set -euo pipefail

if command -v opencode &>/dev/null; then
    echo "OpenCode is already installed"
    exit 0
fi

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "$NVM_DIR/nvm.sh"
fi

if ! command -v npm &>/dev/null; then
    echo "WARNING: npm not found. Skip OpenCode." >&2
    exit 0
fi

echo "Installing OpenCode..."
if npm install -g opencode 2>/dev/null; then
    echo "OpenCode installed: $(opencode --version 2>/dev/null || echo 'installed')"
    exit 0
fi

echo "WARNING: OpenCode npm package not found. Skipping (optional)."
exit 0
