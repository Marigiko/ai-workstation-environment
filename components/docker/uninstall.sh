#!/usr/bin/env bash
set -euo pipefail

if command -v apt-get &>/dev/null; then
    sudo apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || true
    sudo rm -rf /etc/apt/keyrings/docker.gpg /etc/apt/sources.list.d/docker.list
elif command -v pacman &>/dev/null; then
    sudo pacman -Rns --noconfirm docker docker-compose || true
else
    echo "WARNING: Docker uninstall not implemented for this package manager"
fi
