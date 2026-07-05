#!/usr/bin/env bash
set -euo pipefail

if command -v claude &>/dev/null; then
    echo "Claude Code is already installed"
    exit 0
fi

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "$NVM_DIR/nvm.sh"
fi

if ! command -v npm &>/dev/null; then
    echo "ERROR: npm not found. Install node first." >&2
    exit 1
fi

echo "Installing Claude Code..."
npm install -g @anthropic-ai/claude-code

echo "Claude Code installed: $(claude --version 2>/dev/null || echo 'installed')"
