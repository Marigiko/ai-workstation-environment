#!/usr/bin/env bash
set -euo pipefail

if command -v code &>/dev/null; then
    echo "VSCode is already installed"
    exit 0
fi

echo "Installing VSCode..."

if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y wget gpg

    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
    rm -f packages.microsoft.gpg

    sudo apt-get update -qq
    sudo apt-get install -y code

elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm code

elif command -v brew &>/dev/null; then
    brew install --cask visual-studio-code

else
    echo "ERROR: No supported package manager found" >&2
    exit 1
fi

echo "VSCode installed"
