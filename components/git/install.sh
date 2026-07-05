#!/usr/bin/env bash
set -euo pipefail

if command -v git &>/dev/null; then
    echo "git is already installed"
    exit 0
fi

if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y git
elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm git
elif command -v brew &>/dev/null; then
    brew install git
else
    echo "ERROR: No supported package manager found" >&2
    exit 1
fi

echo "git installed successfully"
