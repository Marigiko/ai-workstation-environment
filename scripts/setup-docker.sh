#!/usr/bin/env bash
set -euo pipefail
# Run this script once with sudo access to install Docker and start infrastructure services

echo "=== Docker + AI Infrastructure Setup ==="
echo ""

# Install Docker
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y ca-certificates curl gnupg
        sudo install -m 0755 -d /etc/apt/keyrings
        . /etc/os-release
        curl -fsSL "https://download.docker.com/linux/${ID}/gpg" | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" | \
            sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update -qq
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker "$USER"
    elif command -v dnf &>/dev/null; then
        sudo dnf -y install dnf-plugins-core
        sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
        sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker "$USER"
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy --noconfirm docker docker-compose
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker "$USER"
    fi
    echo "Docker installed. Log out and back in for docker group to take effect."
else
    echo "Docker already installed: $(docker --version)"
fi

# Start infrastructure services
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo ""
echo "=== Starting AI Infrastructure Services ==="

cd "$PROJECT_ROOT"

# OmniRoute (cloud AI gateway)
echo "Checking OmniRoute..."
if curl -sf http://localhost:20128/v1/models >/dev/null 2>&1; then
    echo "OmniRoute already running on port 20128"
else
    echo "OmniRoute not running — run components/omniroute/install.sh"
fi

# Ollama (native - direct GPU access)
echo "Setting up Ollama (native)..."
bash components/ollama/install.sh 2>/dev/null || echo "Ollama install skipped"

# Qdrant
echo "Starting Qdrant..."
docker compose -f components/qdrant/docker-compose.yaml up -d 2>/dev/null || echo "Qdrant compose not found, skipping"

# PostgreSQL
echo "Starting PostgreSQL..."
docker compose -f components/postgresql/docker-compose.yaml up -d 2>/dev/null || echo "PostgreSQL compose not found, skipping"

# n8n
echo "Starting n8n..."
docker compose -f components/n8n/docker-compose.yaml up -d 2>/dev/null || echo "n8n compose not found, skipping"

# Workspace API
echo "Starting Workspace API..."
docker compose -f components/workspace/docker-compose.yaml up -d 2>/dev/null || echo "Workspace compose not found, skipping"

echo ""
echo "=== Infrastructure services started ==="
echo "Verify with: docker ps"
echo ""
echo "Service endpoints:"
echo "  OmniRoute:   http://localhost:20128"
echo "  Ollama:      http://localhost:11434"
echo "  Qdrant:      http://localhost:6335"
echo "  PostgreSQL:  localhost:5433"
echo "  n8n:         http://localhost:5678"
echo "  Workspace:   http://localhost:8080"
