# MCP Management

## Overview

MCP (Model Context Protocol) servers extend AI tools with additional capabilities.

## Registry

MCP servers are declared in `mcp/registry.yaml`:

```yaml
servers:
  - name: filesystem
    description: "File system operations"
    enabled: true
    priority: immediate

  - name: git
    description: "Git operations"
    enabled: true
    priority: immediate
```

## Priority Levels

- **immediate**: Essential for daily work (filesystem, git, github, headroom, codebase-memory, ponytail)
- **nice-to-have**: Useful but not critical (docker, postgres, playwright, browser)

## Enabling/Disabling MCPs

Edit `mcp/registry.yaml`:

```yaml
servers:
  - name: docker
    enabled: true  # Change to false to disable
```

Then re-run bootstrap or manually configure your AI tools.

## MCP Server Configuration

Each AI tool (OpenCode, Claude Code, Zed) has its own MCP configuration format.

### OpenCode

Config file: `~/.config/opencode/config.json` or project-level `opencode.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    }
  }
}
```

### Claude Code

Config file: `~/.claude/config.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    }
  }
}
```

### Zed

Config file: `~/.config/zed/settings.json`

```json
{
  "context_servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    }
  }
}
```

## Recommended MCPs

### Immediate Priority

| MCP | Purpose | Install Command |
|-----|---------|----------------|
| filesystem | File operations | `npx -y @modelcontextprotocol/server-filesystem` |
| git | Git operations | `npx -y @modelcontextprotocol/server-git` |
| github | GitHub API | `npx -y @modelcontextprotocol/server-github` |
| headroom | Context compression | See headroom docs |
| codebase-memory | Persistent memory | See codebase-memory docs |
| ponytail | Code quality | See ponytail docs |
| terax | Terminal integration | Config-only (connects via OpenAI-compatible) |

### Nice to Have

| MCP | Purpose | When to Add |
|-----|---------|-------------|
| docker | Container management | When working with Docker frequently |
| postgres | Database operations | When querying DBs from AI tools |
| playwright | Browser automation | For E2E testing, web scraping |
| sequential-thinking | Multi-step reasoning | For complex architecture decisions |
| browser | Web research | When needing to fetch docs online |

## Adding a New MCP

1. Add to `mcp/registry.yaml`:

```yaml
servers:
  - name: my-mcp
    description: "My custom MCP server"
    enabled: false
    priority: nice-to-have
```

2. Configure in your AI tool's config file (see examples above)

3. Test the MCP server works

## MCP Manager (Future)

A future version will include an `mcp-manager.sh` script to:

- Install MCP servers
- Update MCP servers
- Enable/disable MCPs
- Generate config for different AI tools
