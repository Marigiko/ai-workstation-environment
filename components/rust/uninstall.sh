#!/usr/bin/env bash
set -euo pipefail

if command -v rustup &>/dev/null; then
    rustup self uninstall -y
else
    echo "Rust not found"
fi
