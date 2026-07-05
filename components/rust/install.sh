#!/usr/bin/env bash
set -euo pipefail

if command -v rustc &>/dev/null; then
    echo "Rust is already installed: $(rustc --version)"
    exit 0
fi

echo "Installing Rust via rustup..."
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Source the environment
# shellcheck disable=SC1091
source "$HOME/.cargo/env"

echo "Rust installed: $(rustc --version)"
echo "Cargo installed: $(cargo --version)"
