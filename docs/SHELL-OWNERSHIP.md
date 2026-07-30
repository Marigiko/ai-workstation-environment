# Shell configuration ownership

Two repositories manage this machine's shell. The boundary is deliberate — decided
2026-07-29 after both were found fighting over `~/.zshrc`.

| File | Owner | Mechanism |
|---|---|---|
| `~/.zshrc` | the **dotfiles** repo | copied by `hosts/wsl/apply.sh` |
| `~/.zshrc.local` | the **dotfiles** repo | per-host layer, copied |
| `~/.bashrc`, `~/.bashrc.local` | the **dotfiles** repo | copied |
| `~/.config/nvim`, `alacritty`, `qtile`, `picom`, `~/.xprofile` | the **dotfiles** repo | symlinks |
| `~/.zshenv` | **this repo** (AWE) | symlink via its `dotfiles/manifest.yaml` |
| `~/.zsh_aliases` | **this repo** (AWE) | symlink |
| `~/.gitconfig` | **this repo** (AWE) | symlink |
| `~/.gitignore_global` | **this repo** (AWE) | symlink |
| `~/.config/starship.toml` | **this repo** (AWE) | symlink (currently unused — prompt is powerlevel10k) |

Rules:
- Do **not** add `.zshrc` to `dotfiles/manifest.yaml` in this repo.
- Do **not** add `.zshenv`/`.zsh_aliases`/`.gitconfig` to this repo.
- `~/.zshrc` sources `~/.zsh_aliases` so AWE's aliases stay live.
