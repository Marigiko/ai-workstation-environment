#!/usr/bin/env bash
set -euo pipefail

if command -v python3 &>/dev/null; then
    echo "python3 is already installed: $(python3 --version)"
    exit 0
fi

if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip python3-venv
elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm python python-pip
elif command -v brew &>/dev/null; then
    brew install python
else
    echo "ERROR: No supported package manager found" >&2
    exit 1
fi

echo "Python installed: $(python3 --version)"
