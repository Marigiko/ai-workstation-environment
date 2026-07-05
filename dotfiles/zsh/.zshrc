# Zsh configuration for AI Workstation Environment
# Managed by ai-workstation-environment — do not edit manually

# History
HISTFILE=~/.zsh_history
HISTSIZE=50000
SAVEHIST=50000
setopt APPEND_HISTORY SHARE_HISTORY HIST_IGNORE_DUPS HIST_IGNORE_SPACE

# Key bindings
bindkey -e

# Completion
autoload -Uz compinit && compinit

# Source aliases
[ -f ~/.zsh_aliases ] && source ~/.zsh_aliases

# Starship prompt
if command -v starship &>/dev/null; then
    eval "$(starship init zsh)"
fi

# Environment from ai-workstation-environment
for env_file in "$HOME"/.config/awe/env/*.env; do
    [ -f "$env_file" ] && source "$env_file"
done
