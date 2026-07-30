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
# The npm package is `opencode-ai`; a bare `opencode` does not exist on the registry,
# so this used to print a warning and exit 0, reporting success without installing.
if npm install -g opencode-ai 2>/dev/null; then
    echo "OpenCode installed: $(opencode --version 2>/dev/null || echo 'installed')"
    exit 0
fi

echo "WARNING: OpenCode npm package not found. Skipping (optional)."
exit 0
