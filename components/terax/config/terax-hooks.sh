#!/bin/bash
# Terax agent detection hooks for MiMo, Claude Code, Codex
# Install: source this in .zshrc or .bashrc

# Check if running inside Terax terminal (supports OSC 777)
_is_terax_terminal() {
    # Terax sets TERM_PROGRAM=terax or uses OSC 777 marker detection
    [[ "$TERM_PROGRAM" == "terax" ]] || \
    [[ -n "$TERAX_SESSION" ]] || \
    [[ "$TERMINAL_EMULATOR" == "Terax"* ]]
}

# Function to notify Terax of agent events
terax_notify() {
    local agent="$1"
    local event="$2"
    # Only send if inside Terax terminal; skip in WSL/other terminals
    if _is_terax_terminal; then
        printf "\033]777;notify;Terax;%s;%s\007" "$agent" "$event" > /dev/tty
    fi
}

# Claude Code hooks (only in Terax terminal)
if _is_terax_terminal && [ -f "$HOME/.claude/settings.json" ]; then
    if [[ "$PS1" == *"claude"* ]]; then
        terax_notify "claude" "started"
    fi
fi

# MiMo hooks (only in Terax terminal)
if _is_terax_terminal && command -v mimo &>/dev/null; then
    if pgrep -x "mimo" &>/dev/null; then
        terax_notify "mimo" "started"
    fi
fi
