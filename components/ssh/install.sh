#!/usr/bin/env bash
set -euo pipefail

if command -v ssh &>/dev/null; then
    echo "ssh is already installed"
    exit 0
fi

if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y openssh-client openssh-server
elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm openssh
elif command -v brew &>/dev/null; then
    brew install openssh
else
    echo "ERROR: No supported package manager found" >&2
    exit 1
fi

echo "ssh installed successfully"
