#!/usr/bin/env bash
set -euo pipefail

if command -v apt-get &>/dev/null; then
    sudo apt-get remove -y tailscale || true
elif command -v pacman &>/dev/null; then
    sudo pacman -Rns --noconfirm tailscale || true
elif command -v brew &>/dev/null; then
    brew uninstall tailscale || true
else
    echo "WARNING: Tailscale uninstall not implemented"
fi
