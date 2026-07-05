#!/usr/bin/env bash
set -euo pipefail

if command -v zed &>/dev/null; then
    echo "Zed is already installed"
    exit 0
fi

echo "Installing Zed editor..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    curl -f https://zed.dev/install.sh | sh
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &>/dev/null; then
        brew install --cask zed
    else
        echo "ERROR: Homebrew required for Zed on macOS" >&2
        exit 1
    fi
else
    echo "ERROR: Unsupported platform for Zed" >&2
    exit 1
fi

echo "Zed installed successfully"
