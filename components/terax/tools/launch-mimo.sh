#!/bin/bash
# Launch MiMo in Terax terminal
# Usage: launch-mimo.sh [worktree_id]

set -euo pipefail

WORKTREE_ID="${1:-default}"
CONFIG_DIR="${HOME}/.config/mimocode"

echo "Launching MiMo in worktree: $WORKTREE_ID"

# Check if MiMo is installed
if ! command -v mimo &>/dev/null; then
    echo "ERROR: MiMo not installed. Run: ./bootstrap bootstrap --only mimo"
    exit 1
fi

# Check if Terax is running
if ! pgrep -x "terax" &>/dev/null; then
    echo "WARNING: Terax not detected. Launching MiMo directly."
fi

# Set environment for worktree
export MIMO_WORKTREE="$WORKTREE_ID"
export MIMO_CONFIG="$CONFIG_DIR/mimocode.json"

# Launch MiMo
echo "Starting MiMo agent..."
exec mimo
