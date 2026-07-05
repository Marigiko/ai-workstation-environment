# Adding Components

## Step-by-Step Guide

### 1. Create Component Directory

```bash
mkdir -p components/my-tool
```

### 2. Create `component.yaml`

```yaml
name: my-tool
version: "1.0"
description: "My awesome tool"
platforms: [linux, darwin]  # linux, darwin, or both
profiles: [notebook, desktop]  # Which profiles include this
depends_on: [git]  # Dependencies (must be installed first)
optional: false  # If true, not installed by default

# Optional: system packages
packages:
  apt: [my-tool-package]
  pacman: [my-tool]
  brew: [my-tool]
```

### 3. Create `check.sh`

Must exit 0 if installed, 1 if not:

```bash
#!/usr/bin/env bash
set -euo pipefail

if command -v my-tool &>/dev/null; then
    exit 0
fi
exit 1
```

### 4. Create `install.sh`

Must be idempotent (safe to run multiple times):

```bash
#!/usr/bin/env bash
set -euo pipefail

if command -v my-tool &>/dev/null; then
    echo "my-tool is already installed"
    exit 0
fi

echo "Installing my-tool..."
# Installation logic here

echo "my-tool installed successfully"
```

### 5. Create `uninstall.sh`

Optional but recommended:

```bash
#!/usr/bin/env bash
set -euo pipefail

if command -v apt-get &>/dev/null; then
    sudo apt-get remove -y my-tool || true
elif command -v pacman &>/dev/null; then
    sudo pacman -Rns --noconfirm my-tool || true
fi
```

### 6. Make Scripts Executable

```bash
chmod +x components/my-tool/*.sh
```

### 7. Test

```bash
./bootstrap list  # Should show my-tool
./bootstrap bootstrap --only my-tool
./bootstrap status  # Should show my-tool as installed
```

### 8. Add to Profiles (Optional)

Edit `profiles/<profile>.yaml`:

```yaml
components:
  - my-tool
```

## Best Practices

- **Idempotency**: Always check before installing
- **Error handling**: Use `set -euo pipefail`
- **Platform detection**: Check `$OSTYPE` or use `command -v`
- **Logging**: Echo progress messages
- **Cleanup**: Provide uninstall script when possible
