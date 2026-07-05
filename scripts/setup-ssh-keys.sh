#!/usr/bin/env bash
# Setup SSH keys for common services
set -euo pipefail

SSH_DIR="$HOME/.ssh"
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

log() { printf '[ssh-setup] %s\n' "$*"; }

generate_key() {
    local name="$1"
    local email="$2"
    local key_file="$SSH_DIR/$name"

    if [ -f "$key_file" ]; then
        log "Key already exists: $key_file"
        return
    fi

    log "Generating SSH key: $name"
    ssh-keygen -t ed25519 -C "$email" -f "$key_file" -N ""
    log "Generated: $key_file.pub"
}

add_to_agent() {
    local key_file="$1"
    if command -v ssh-add &>/dev/null; then
        eval "$(ssh-agent -s)" &>/dev/null || true
        ssh-add "$key_file" 2>/dev/null || true
    fi
}

show_public_key() {
    local key_file="$1"
    if [ -f "${key_file}.pub" ]; then
        echo
        log "Public key for $key_file:"
        cat "${key_file}.pub"
        echo
    fi
}

read -rp "Enter your email: " EMAIL

if [ -z "$EMAIL" ]; then
    echo "Email is required"
    exit 1
fi

echo
log "Generating SSH keys for: $EMAIL"
echo

# GitHub
read -rp "Generate GitHub SSH key? [Y/n] " ans
if [[ "$ans" != [nN]* ]]; then
    generate_key "id_ed25519_github" "$EMAIL"
    add_to_agent "$SSH_DIR/id_ed25519_github"
    show_public_key "$SSH_DIR/id_ed25519_github"
fi

# GitLab
read -rp "Generate GitLab SSH key? [y/N] " ans
if [[ "$ans" == [yY]* ]]; then
    generate_key "id_ed25519_gitlab" "$EMAIL"
    add_to_agent "$SSH_DIR/id_ed25519_gitlab"
    show_public_key "$SSH_DIR/id_ed25519_gitlab"
fi

# Create SSH config
SSH_CONFIG="$SSH_DIR/config"
if [ ! -f "$SSH_CONFIG" ]; then
    log "Creating SSH config..."
    cat > "$SSH_CONFIG" <<'EOF'
# GitHub
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github
    AddKeysToAgent yes

# GitLab
Host gitlab.com
    HostName gitlab.com
    User git
    IdentityFile ~/.ssh/id_ed25519_gitlab
    AddKeysToAgent yes

# Default
Host *
    AddKeysToAgent yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
    chmod 600 "$SSH_CONFIG"
    log "SSH config created: $SSH_CONFIG"
else
    log "SSH config already exists: $SSH_CONFIG"
fi

echo
log "Done! Add the public keys to your GitHub/GitLab accounts."
