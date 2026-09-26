#!/usr/bin/env bash
set -euo pipefail

# Resolve the OmniRoute checkout the same way install.sh does.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECTS_DIR="${AWE_PROJECTS_DIR:-$(dirname "$REPO_ROOT")}"
OMNIROUTE_DIR="${OMNIROUTE_DIR:-$PROJECTS_DIR/OmniRoute}"

if [ ! -d "$OMNIROUTE_DIR" ]; then
    echo "OmniRoute checkout not found at: $OMNIROUTE_DIR — nothing to stop"
    exit 0
fi

cd "$OMNIROUTE_DIR"
echo "Stopping OmniRoute (volumes kept)..."
docker compose --profile base down
