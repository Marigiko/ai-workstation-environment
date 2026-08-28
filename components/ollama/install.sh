#!/usr/bin/env bash
set -euo pipefail

OLLAMA_BIN="/usr/local/bin/ollama"
OLLAMA_SERVICE="ollama"

if [ -f "$OLLAMA_BIN" ]; then
    if systemctl is-active --quiet "$OLLAMA_SERVICE" 2>/dev/null; then
        echo "Ollama is already running"
        exit 0
    fi
    echo "Ollama installed but not running, starting service..."
    sudo systemctl start "$OLLAMA_SERVICE"
    exit 0
fi

echo "Installing Ollama (native, with GPU support)..."

if command -v apt-get &>/dev/null; then
    curl -fsSL https://ollama.com/install.sh | sudo sh
elif command -v dnf &>/dev/null; then
    curl -fsSL https://ollama.com/install.sh | sudo sh
elif command -v pacman &>/dev/null; then
    curl -fsSL https://ollama.com/install.sh | sudo sh
else
    echo "ERROR: Unsupported package manager. Install Ollama manually:" >&2
    echo "  curl -fsSL https://ollama.com/install.sh | sh" >&2
    exit 1
fi

if ! command -v "$OLLAMA_BIN" &>/dev/null; then
    echo "ERROR: Ollama installation failed" >&2
    exit 1
fi

echo "Ollama installed successfully"

if nvidia-smi &>/dev/null 2>&1; then
    echo "NVIDIA GPU detected - Ollama will use CUDA for inference"
else
    echo "WARNING: No NVIDIA GPU detected - Ollama will use CPU mode" >&2
fi
