#!/usr/bin/env bash
set -euo pipefail

if command -v docker &>/dev/null; then
    echo "Docker is already installed: $(docker --version)"
    if ! docker info &>/dev/null; then
        echo "WARNING: Docker is installed but not running. Start with: sudo systemctl start docker"
    fi
    exit 0
fi

echo "Installing Docker..."

if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y ca-certificates curl gnupg

    sudo install -m 0755 -d /etc/apt/keyrings
    # shellcheck disable=SC1091
    . /etc/os-release
    curl -fsSL "https://download.docker.com/linux/${ID}/gpg" | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -qq
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    sudo systemctl enable docker
    sudo systemctl start docker

    if ! groups | grep -q docker; then
        echo "Adding user to docker group..."
        sudo usermod -aG docker "$USER"
        echo "NOTE: Log out and back in for docker group to take effect"
    fi

elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm docker docker-compose
    sudo systemctl enable docker
    sudo systemctl start docker
    if ! groups | grep -q docker; then
        sudo usermod -aG docker "$USER"
    fi

elif command -v dnf &>/dev/null; then
    sudo dnf -y install dnf-plugins-core
    sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo systemctl enable docker
    sudo systemctl start docker
    if ! groups | grep -q docker; then
        sudo usermod -aG docker "$USER"
    fi

elif command -v zypper &>/dev/null; then
    sudo zypper install -y docker docker-compose
    sudo systemctl enable docker
    sudo systemctl start docker
    if ! groups | grep -q docker; then
        sudo usermod -aG docker "$USER"
    fi

else
    echo "No supported package manager found, trying official Docker script..."
    curl -fsSL https://get.docker.com | sh
    sudo systemctl enable docker 2>/dev/null || true
    sudo systemctl start docker 2>/dev/null || true
fi

echo "Docker installed: $(docker --version)"
echo "Docker Compose: $(docker compose version)"
