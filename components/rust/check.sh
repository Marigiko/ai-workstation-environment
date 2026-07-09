#!/usr/bin/env bash

# Check PATH including cargo bin
export PATH="$HOME/.cargo/bin:$PATH"

if command -v rustc &>/dev/null; then
    exit 0
fi
exit 1
