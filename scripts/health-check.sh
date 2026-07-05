#!/usr/bin/env bash
# Health check: verify all components are working
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0
warn=0

check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        printf "${GREEN}✓${NC} %s\n" "$name"
        ((pass++))
    else
        printf "${RED}✗${NC} %s\n" "$name"
        ((fail++))
    fi
}

warn_check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        printf "${GREEN}✓${NC} %s\n" "$name"
        ((pass++))
    else
        printf "${YELLOW}!${NC} %s (warning)\n" "$name"
        ((warn++))
    fi
}

echo "=== AI Workstation Environment - Health Check ==="
echo

echo "--- Core Tools ---"
check "Git" "command -v git"
check "SSH" "command -v ssh"
check "Python 3" "command -v python3"
check "Node.js" "command -v node"
check "Docker" "command -v docker"
check "Docker running" "docker info"

echo
echo "--- AI Tools ---"
warn_check "OpenCode" "command -v opencode"
warn_check "Claude Code" "command -v claude"
warn_check "Zed" "command -v zed"

echo
echo "--- Infrastructure ---"
warn_check "Tailscale" "command -v tailscale"
warn_check "Ollama" "docker ps --format '{{.Names}}' | grep -q awe-ollama"
warn_check "LiteLLM" "docker ps --format '{{.Names}}' | grep -q awe-litellm"
warn_check "Qdrant" "docker ps --format '{{.Names}}' | grep -q awe-qdrant"
warn_check "PostgreSQL" "docker ps --format '{{.Names}}' | grep -q awe-postgresql"
warn_check "n8n" "docker ps --format '{{.Names}}' | grep -q awe-n8n"

echo
echo "--- Dotfiles ---"
warn_check ".zshrc" "[ -L ~/.zshrc ]"
warn_check ".gitconfig" "[ -L ~/.gitconfig ]"

echo
echo "--- MCP Configs ---"
warn_check "OpenCode MCP" "[ -f ~/.config/opencode/config.json ]"
warn_check "Claude MCP" "[ -f ~/.claude/config.json ] || [ -f ~/.config/claude/config.json ]"

echo
echo "=== Summary ==="
printf "${GREEN}Passed: %d${NC}\n" "$pass"
printf "${RED}Failed: %d${NC}\n" "$fail"
printf "${YELLOW}Warnings: %d${NC}\n" "$warn"

if [ "$fail" -gt 0 ]; then
    exit 1
fi
