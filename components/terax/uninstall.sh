#!/usr/bin/env bash
set -euo pipefail

echo "Uninstalling Terax..."

if [ -f "$HOME/.local/bin/terax" ]; then
    rm -f "$HOME/.local/bin/terax"
    echo "Removed ~/.local/bin/terax"
fi

if [ -d "$HOME/.config/terax" ]; then
    rm -rf "$HOME/.config/terax"
    echo "Removed ~/.config/terax/"
fi

if command -v npm &>/dev/null && npm list -g terax-ai &>/dev/null 2>&1; then
    npm uninstall -g terax-ai
    echo "Removed terax-ai npm package"
fi

echo "Terax uninstalled"
