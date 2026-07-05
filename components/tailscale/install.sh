#!/usr/bin/env bash
set -euo pipefail

if command -v tailscale &>/dev/null; then
    echo "Tailscale is already installed: $(tailscale version | head -1)"
    exit 0
fi

echo "Installing Tailscale..."

if command -v apt-get &>/dev/null || command -v pacman &>/dev/null; then
    curl -fsSL https://tailscale.com/install.sh | sh
elif command -v brew &>/dev/null; then
    brew install tailscale
else
    echo "ERROR: No supported package manager found" >&2
    exit 1
fi

echo "Tailscale installed. Run 'sudo tailscale up' to authenticate."
