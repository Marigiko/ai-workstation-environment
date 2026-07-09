#!/usr/bin/env bash

if command -v terax &>/dev/null; then
    exit 0
fi

# Check common installation paths
TERAX_PATHS=(
    "$HOME/.local/bin/terax"
    "/usr/local/bin/terax"
    "/usr/bin/terax"
    "/mnt/d/Software/Terax/terax"
)

for path in "${TERAX_PATHS[@]}"; do
    if [ -x "$path" ]; then
        exit 0
    fi
done

# Check if installed via dpkg
if dpkg -l terax 2>/dev/null | grep -q "^ii"; then
    exit 0
fi

exit 1
