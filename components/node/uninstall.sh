#!/usr/bin/env bash
set -euo pipefail

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

if [ -d "$NVM_DIR" ]; then
    echo "Removing nvm and node..."
    rm -rf "$NVM_DIR"
    echo "nvm removed. Remove nvm references from your shell config manually."
else
    echo "nvm not found"
fi
