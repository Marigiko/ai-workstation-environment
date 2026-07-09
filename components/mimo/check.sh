#!/usr/bin/env bash

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "$NVM_DIR/nvm.sh"
fi

if command -v mimo &>/dev/null; then
    exit 0
fi
exit 1
