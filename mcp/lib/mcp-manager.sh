#!/usr/bin/env bash
# MCP Manager - Install, update, enable, disable MCP servers
# Part of ai-workstation-environment

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REGISTRY="$PROJECT_ROOT/mcp/registry.yaml"
SERVERS_DIR="$PROJECT_ROOT/mcp/servers"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"

log() { printf '[mcp-manager] %s\n' "$*"; }
die() { printf '[mcp-manager] ERROR: %s\n' "$*" >&2; exit 1; }

# Check if yq is available, fallback to python
parse_yaml() {
    local file="$1"
    local query="$2"
    
    if command -v yq &>/dev/null; then
        yq "$query" "$file"
    else
        python3 -c "
import yaml, sys
with open('$file') as f:
    data = yaml.safe_load(f)
# Simple query parser for basic paths
parts = '$query'.strip('$').split('.')
result = data
for part in parts:
    if '[' in part:
        key, idx = part.split('[')
        idx = int(idx.rstrip(']'))
        result = result[key][idx]
    else:
        result = result[part]
if isinstance(result, list):
    for item in result:
        print(item)
elif isinstance(result, dict):
    for k, v in result.items():
        print(f'{k}: {v}')
else:
    print(result)
"
    fi
}

get_enabled_servers() {
    python3 -c "
import yaml
with open('$REGISTRY') as f:
    data = yaml.safe_load(f)
for server in data.get('servers', []):
    if server.get('enabled', False):
        print(server['name'])
"
}

get_server_config() {
    local server_name="$1"
    local server_file="$SERVERS_DIR/$server_name.yaml"
    
    if [ ! -f "$server_file" ]; then
        die "Server definition not found: $server_file"
    fi
    
    cat "$server_file"
}

install_mcp() {
    local server_name="$1"
    local server_file="$SERVERS_DIR/$server_name.yaml"
    
    if [ ! -f "$server_file" ]; then
        die "Server definition not found: $server_name"
    fi
    
    log "Installing MCP server: $server_name"
    
    # Extract install command from server definition
    local install_cmd
    install_cmd=$(python3 -c "
import yaml
with open('$server_file') as f:
    data = yaml.safe_load(f)
print(data.get('install', ''))
")
    
    if [ -n "$install_cmd" ]; then
        eval "$install_cmd"
        log "MCP server installed: $server_name"
    else
        log "No install command for $server_name (may be built-in)"
    fi
}

enable_mcp() {
    local server_name="$1"
    
    python3 -c "
import yaml
with open('$REGISTRY') as f:
    data = yaml.safe_load(f)

found = False
for server in data.get('servers', []):
    if server['name'] == '$server_name':
        server['enabled'] = True
        found = True
        break

if not found:
    print('Server not found in registry')
    exit(1)

with open('$REGISTRY', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
print('Enabled: $server_name')
"
}

disable_mcp() {
    local server_name="$1"
    
    python3 -c "
import yaml
with open('$REGISTRY') as f:
    data = yaml.safe_load(f)

found = False
for server in data.get('servers', []):
    if server['name'] == '$server_name':
        server['enabled'] = False
        found = True
        break

if not found:
    print('Server not found in registry')
    exit(1)

with open('$REGISTRY', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
print('Disabled: $server_name')
"
}

list_mcp() {
    python3 -c "
import yaml
with open('$REGISTRY') as f:
    data = yaml.safe_load(f)

print(f\"{'Server':<25} {'Enabled':<10} {'Priority':<15} Description\")
print('-' * 80)
for server in data.get('servers', []):
    name = server['name']
    enabled = 'yes' if server.get('enabled', False) else 'no'
    priority = server.get('priority', 'unknown')
    desc = server.get('description', '')
    print(f'{name:<25} {enabled:<10} {priority:<15} {desc}')
"
}

generate_config() {
    local tool="$1"
    local output_dir="$CONFIG_DIR"
    
    case "$tool" in
        opencode)
            generate_opencode_config "$output_dir"
            ;;
        claude-code)
            generate_claude_config "$output_dir"
            ;;
        zed)
            generate_zed_config "$output_dir"
            ;;
        *)
            die "Unknown tool: $tool (supported: opencode, claude-code, zed)"
            ;;
    esac
}

generate_opencode_config() {
    local output_dir="$1"
    local config_file="$output_dir/opencode/config.json"
    
    mkdir -p "$(dirname "$config_file")"
    
    python3 -c "
import yaml, json, os

with open('$REGISTRY') as f:
    registry = yaml.safe_load(f)

servers_dir = '$SERVERS_DIR'
mcp_servers = {}

for server in registry.get('servers', []):
    if not server.get('enabled', False):
        continue
    
    name = server['name']
    server_file = os.path.join(servers_dir, f'{name}.yaml')
    
    if not os.path.exists(server_file):
        continue
    
    with open(server_file) as f:
        server_def = yaml.safe_load(f)
    
    config = server_def.get('config', {})
    if config:
        mcp_servers[name] = {
            'command': config.get('command', ''),
            'args': config.get('args', [])
        }

config = {'mcpServers': mcp_servers}

with open('$config_file', 'w') as f:
    json.dump(config, f, indent=2)

print(f'Generated: $config_file')
"
}

generate_claude_config() {
    local output_dir="$1"
    local config_file="$output_dir/claude/config.json"
    
    mkdir -p "$(dirname "$config_file")"
    
    python3 -c "
import yaml, json, os

with open('$REGISTRY') as f:
    registry = yaml.safe_load(f)

servers_dir = '$SERVERS_DIR'
mcp_servers = {}

for server in registry.get('servers', []):
    if not server.get('enabled', False):
        continue
    
    name = server['name']
    server_file = os.path.join(servers_dir, f'{name}.yaml')
    
    if not os.path.exists(server_file):
        continue
    
    with open(server_file) as f:
        server_def = yaml.safe_load(f)
    
    config = server_def.get('config', {})
    if config:
        mcp_servers[name] = {
            'command': config.get('command', ''),
            'args': config.get('args', [])
        }

config = {'mcpServers': mcp_servers}

with open('$config_file', 'w') as f:
    json.dump(config, f, indent=2)

print(f'Generated: $config_file')
"
}

generate_zed_config() {
    local output_dir="$1"
    local config_file="$output_dir/zed/settings.json"
    
    mkdir -p "$(dirname "$config_file")"
    
    python3 -c "
import yaml, json, os

with open('$REGISTRY') as f:
    registry = yaml.safe_load(f)

servers_dir = '$SERVERS_DIR'
context_servers = {}

for server in registry.get('servers', []):
    if not server.get('enabled', False):
        continue
    
    name = server['name']
    server_file = os.path.join(servers_dir, f'{name}.yaml')
    
    if not os.path.exists(server_file):
        continue
    
    with open(server_file) as f:
        server_def = yaml.safe_load(f)
    
    config = server_def.get('config', {})
    if config:
        context_servers[name] = {
            'command': config.get('command', ''),
            'args': config.get('args', [])
        }

config = {'context_servers': context_servers}

with open('$config_file', 'w') as f:
    json.dump(config, f, indent=2)

print(f'Generated: $config_file')
"
}

update_all() {
    log "Updating all enabled MCP servers..."
    
    python3 -c "
import yaml, subprocess, sys

with open('$REGISTRY') as f:
    registry = yaml.safe_load(f)

servers_dir = '$SERVERS_DIR'

for server in registry.get('servers', []):
    if not server.get('enabled', False):
        continue
    
    name = server['name']
    server_file = f'{servers_dir}/{name}.yaml'
    
    try:
        with open(server_file) as f:
            server_def = yaml.safe_load(f)
        
        update_cmd = server_def.get('update', '')
        if update_cmd:
            print(f'Updating {name}...')
            subprocess.run(update_cmd, shell=True, check=True)
        else:
            print(f'No update command for {name}')
    except Exception as e:
        print(f'Error updating {name}: {e}')
"
    
    log "Update complete"
}

usage() {
    cat <<EOF
MCP Manager - Manage MCP servers for AI tools

Usage:
    $0 install <server-name>     Install a specific MCP server
    $0 enable <server-name>      Enable an MCP server in registry
    $0 disable <server-name>     Disable an MCP server in registry
    $0 list                      List all MCP servers
    $0 generate <tool>           Generate config for tool (opencode|claude-code|zed)
    $0 update                    Update all enabled MCP servers
    $0 help                      Show this help

Examples:
    $0 list
    $0 enable filesystem
    $0 install git
    $0 generate opencode
    $0 update
EOF
}

# Main command router
case "${1:-help}" in
    install)
        [ -z "${2:-}" ] && die "Usage: $0 install <server-name>"
        install_mcp "$2"
        ;;
    enable)
        [ -z "${2:-}" ] && die "Usage: $0 enable <server-name>"
        enable_mcp "$2"
        ;;
    disable)
        [ -z "${2:-}" ] && die "Usage: $0 disable <server-name>"
        disable_mcp "$2"
        ;;
    list)
        list_mcp
        ;;
    generate)
        [ -z "${2:-}" ] && die "Usage: $0 generate <tool>"
        generate_config "$2"
        ;;
    update)
        update_all
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        die "Unknown command: $1 (try '$0 help')"
        ;;
esac
