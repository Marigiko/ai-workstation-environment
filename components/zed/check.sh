#!/usr/bin/env bash

# Check PATH including common Zed locations
export PATH="/mnt/d/Software/Zed/bin:$HOME/.local/bin:/usr/local/bin:$PATH"

if command -v zed &>/dev/null; then
    exit 0
fi

# Check known Zed install paths
if [ -x "/mnt/d/Software/Zed/bin/zed" ]; then
    exit 0
fi

if [ -x "$HOME/.local/bin/zed" ]; then
    exit 0
fi

exit 1
