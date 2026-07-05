# Profiles System

## Overview

Profiles define which components to install for different machine types.

## Available Profiles

### `notebook`

Lightweight AI dev environment for laptops.

**Components**: git, ssh, node, python, zed, opencode, claude-code, tailscale, docker

**Use case**: Daily AI development on a laptop with limited resources.

### `desktop`

Full AI dev environment for workstations.

**Components**: notebook + rust, vscode

**Use case**: Heavy development with additional tools.

### `host`

Infrastructure server for AI services.

**Components**: git, ssh, docker, tailscale, node, python, ollama, litellm, qdrant, postgresql, n8n

**Use case**: Server running AI infrastructure (models, vector DBs, automation).

### `minimal`

Bare minimum for any machine.

**Components**: git, ssh

**Use case**: Quick setup on any machine, or as a base for custom profiles.

## Profile Structure

```yaml
name: profile-name
description: "What this profile is for"

components:
  - git
  - ssh
  - node
  # ... list of component names

config_overrides:
  environment:
    editor: zed
  docker:
    resource_limits: true
```

## Creating a Custom Profile

1. Copy an existing profile:

```bash
cp profiles/notebook.yaml profiles/my-profile.yaml
```

2. Edit the components list:

```yaml
name: my-profile
description: "My custom setup"

components:
  - git
  - ssh
  - node
  - python
  - docker
  - my-custom-tool  # Add your own components
```

3. Run bootstrap with your profile:

```bash
./bootstrap --profile my-profile
```

## Profile Resolution

When you run `./bootstrap --profile X`:

1. Load `configs/default.yaml`
2. Load `profiles/X.yaml` and merge (overrides default)
3. Load `configs/local.yaml` and merge (overrides profile)
4. Extract component list from merged config
5. Resolve dependencies (topological sort)
6. Install each component in order

## Excluding Components

If a profile includes a component you don't want, you can:

1. Create a custom profile without it
2. Use `--only` to install specific components:

```bash
./bootstrap bootstrap --only git
```
