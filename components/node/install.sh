#!/usr/bin/env bash
set -euo pipefail

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

if [ -s "$NVM_DIR/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "$NVM_DIR/nvm.sh"
    if command -v node &>/dev/null; then
        echo "node is already installed via nvm: $(node --version)"
        exit 0
    fi
fi

if [ ! -d "$NVM_DIR" ]; then
    echo "Installing nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi

# shellcheck disable=SC1091
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

echo "Installing Node.js LTS..."
nvm install --lts || nvm install node
nvm use --lts 2>/dev/null || nvm use node 2>/dev/null || true
nvm alias default lts/* 2>/dev/null || nvm alias default node 2>/dev/null || true

echo "Node.js installed: $(node --version)"
echo "npm installed: $(npm --version)"
