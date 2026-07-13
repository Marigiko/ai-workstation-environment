#!/usr/bin/env bash
set -euo pipefail

if command -v git &>/dev/null; then
    echo "git is already installed"
    exit 0
fi

if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y git
elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm git
elif command -v brew &>/dev/null; then
    brew install git
else
    echo "ERROR: No supported package manager found" >&2
    exit 1
fi

echo "git installed successfully"

# Configure git defaults
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.autocrlf input

# Configure credential helper
if [ -n "${GITHUB_TOKEN:-}" ]; then
    git config --global credential.helper store
    echo "https://oauth2:${GITHUB_TOKEN}@github.com" >> ~/.git-credentials
    echo "Git credential helper configured with GITHUB_TOKEN."
elif command -v git-credential-manager &>/dev/null; then
    git config --global credential.helper manager
    echo "Git configured with Git Credential Manager."
elif [ -d "/mnt/c/Program Files/Git" ]; then
    # WSL with Windows Git Credential Manager
    git config --global credential.helper "/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe"
    echo "Git configured with Windows GCM (WSL)."
else
    git config --global credential.helper cache --timeout=3600
    echo "Git configured with in-memory credential cache."
fi

echo "Git configured successfully."
echo "  Branch: main"
echo "  Credential helper: $(git config --global credential.helper)"

echo "git installed successfully"
