# Zsh environment
export EDITOR="nvim"
export VISUAL="zed --wait"

# Micromamba (user-space package manager)
export PATH="$HOME/.micromamba/bin:$PATH"

# NVM (Node.js)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Cargo (Rust)
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"

# Local bin
export PATH="$HOME/.local/bin:$PATH"
