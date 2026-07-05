#!/usr/bin/env bash
# Backup important configs and state
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-$HOME/awe-backups}"
BACKUP_FILE="$BACKUP_DIR/awe-backup-$TIMESTAMP.tar.gz"

log() { printf '[backup] %s\n' "$*"; }

mkdir -p "$BACKUP_DIR"

FILES_TO_BACKUP=()

# AWE state
if [ -d "$HOME/ai-workstation-environment/.state" ]; then
    FILES_TO_BACKUP+=("$HOME/ai-workstation-environment/.state")
fi

# Dotfiles
for f in .zshrc .zsh_aliases .zshenv .gitconfig .gitignore_global; do
    if [ -f "$HOME/$f" ] || [ -L "$HOME/$f" ]; then
        FILES_TO_BACKUP+=("$HOME/$f")
    fi
done

# Starship
if [ -d "$HOME/.config/starship.toml" ] || [ -f "$HOME/.config/starship.toml" ]; then
    FILES_TO_BACKUP+=("$HOME/.config/starship.toml")
fi

# SSH config (not keys — too sensitive)
if [ -f "$HOME/.ssh/config" ]; then
    FILES_TO_BACKUP+=("$HOME/.ssh/config")
fi

# MCP configs
for f in .config/opencode/config.json .config/claude/config.json .config/zed/settings.json; do
    if [ -f "$HOME/$f" ]; then
        FILES_TO_BACKUP+=("$HOME/$f")
    fi
done

# Local config overrides
if [ -f "$HOME/ai-workstation-environment/configs/local.yaml" ]; then
    FILES_TO_BACKUP+=("$HOME/ai-workstation-environment/configs/local.yaml")
fi

if [ ${#FILES_TO_BACKUP[@]} -eq 0 ]; then
    log "Nothing to backup"
    exit 0
fi

log "Backing up ${#FILES_TO_BACKUP[@]} items..."
for f in "${FILES_TO_BACKUP[@]}"; do
    log "  $f"
done

tar -czf "$BACKUP_FILE" "${FILES_TO_BACKUP[@]}" 2>/dev/null || true

log "Backup created: $BACKUP_FILE"
log "Size: $(du -h "$BACKUP_FILE" | cut -f1)"

# Cleanup old backups (keep last 5)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/awe-backup-*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 5 ]; then
    log "Cleaning old backups (keeping last 5)..."
    ls -1t "$BACKUP_DIR"/awe-backup-*.tar.gz | tail -n +6 | xargs rm -f
fi

log "Done"
