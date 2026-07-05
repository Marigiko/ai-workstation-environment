#!/usr/bin/env bash
set -euo pipefail

if command -v apt-get &>/dev/null; then
    sudo apt-get remove -y code || true
elif command -v pacman &>/dev/null; then
    sudo pacman -Rns --noconfirm code || true
elif command -v brew &>/dev/null; then
    brew uninstall --cask visual-studio-code || true
else
    echo "WARNING: VSCode uninstall not implemented"
fi
