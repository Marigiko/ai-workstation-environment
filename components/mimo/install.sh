#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "$NVM_DIR/nvm.sh"
fi

if ! command -v mimo &>/dev/null; then
    if ! command -v npm &>/dev/null; then
        echo "ERROR: npm not found. Install node first." >&2
        exit 1
    fi

    echo "Installing Mimo..."
    npm install -g @mimo-ai/cli
    echo "Mimo installed: $(mimo --version 2>/dev/null || echo 'installed')"
else
    echo "Mimo is already installed"
fi

AGENTS_DIR="${HOME}/.config/mimocode/agents"
mkdir -p "$AGENTS_DIR"

if [ -d "$SCRIPT_DIR/agents" ]; then
    echo "Installing Mimo agents..."
    cp -f "$SCRIPT_DIR/agents/"*.md "$AGENTS_DIR/"
    echo "Agents installed: $(find "$AGENTS_DIR" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l) files"
fi

SKILLS_DIR="${HOME}/.config/mimocode/skills"
mkdir -p "$SKILLS_DIR"

if [ -d "$SCRIPT_DIR/skills" ]; then
    echo "Installing Mimo skills..."
    cp -rf "$SCRIPT_DIR/skills/"* "$SKILLS_DIR/"
    echo "Skills installed: $(find "$SKILLS_DIR" -name 'SKILL.md' | wc -l) skills"
fi

TOOLS_DIR="${HOME}/.config/mimocode/tools"
mkdir -p "$TOOLS_DIR"

if [ -d "$SCRIPT_DIR/tools" ]; then
    echo "Installing Mimo tools..."
    cp -f "$SCRIPT_DIR/tools/"*.ts "$TOOLS_DIR/"
    echo "Tools installed: $(find "$TOOLS_DIR" -maxdepth 1 -name '*.ts' 2>/dev/null | wc -l) files"
fi

N8N_WORKFLOWS_DIR="${HOME}/.config/mimocode/n8n-workflows"
mkdir -p "$N8N_WORKFLOWS_DIR"

if [ -d "$SCRIPT_DIR/n8n-workflows" ]; then
    echo "Installing n8n workflows..."
    cp -f "$SCRIPT_DIR/n8n-workflows/"*.json "$N8N_WORKFLOWS_DIR/"
    echo "n8n workflows installed: $(find "$N8N_WORKFLOWS_DIR" -maxdepth 1 -name '*.json' 2>/dev/null | wc -l) workflows"
    echo "Import these workflows in n8n UI: http://localhost:5678"
fi
