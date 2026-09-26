# TERAX.md - AI Engineering Workstation

## Architecture

This workspace is part of a layered AI Engineering platform:

```
Terax (Terminal/UI) → Orquestador (MiMoCode/ClaudeCode) → OmniRoute (Gateway) → Modelos + MCP
```

- **Gateway**: OmniRoute (OpenAI-compatible) at http://localhost:20128/v1 (dashboard: http://localhost:20128/dashboard, bearer key in `OMNIROUTE_API_KEY`)
- **Orchestrator**: MiMoCode (primary) / Claude Code (alternative)
- **MCP Tools**: Available via orchestrator (filesystem, git, github, headroom, codebase-memory, ponytail)
- **Models**: Routed through OmniRoute combos (`agente` for hard/coding work, `liviano` for light work) plus Ollama local models

## Quick Commands

```bash
# Platform management
./bootstrap detect                    # Detect system environment
./bootstrap bootstrap --profile X     # Install profile (notebook|desktop|host|minimal)
./bootstrap list                      # List available components
./bootstrap status                    # Show installed components
./bootstrap mcp-list                  # List MCP servers
./bootstrap mcp-enable <name>         # Enable an MCP server
./bootstrap mcp-generate mimo         # Generate MCP config for MiMoCode

# Development
pytest tests/ -v                      # Run tests
ruff check core/ tests/               # Lint code
```

## Custom Agents

- `/orchestrator` — Full AI Engineering orchestration across all infrastructure
- `/debugger` — Systematic debugging with compose-debug methodology
- `/reviewer` — Code review with security audit

## Snippets

- `/research` — Deep research using parallel sub-agents
- `/deploy` — Health check + deployment workflow
- `/benchmark` — Model performance comparison
- `/review-pr` — Pull request review

## Context Management

- Use Repomix for codebase compression: `repomix --compress --output context.md .`
- Headroom handles context compression automatically via MCP
- Codebase Memory persists across sessions via MCP server
- OmniRoute tracks token usage per model

## Available Models (via OmniRoute)

- Combo `agente`: GLM Coding Plan → Gemini 2.5 Flash → Groq gpt-oss-120b (hard/coding work)
- Combo `liviano` (free first): Gemini 2.5 Flash → Groq gpt-oss-120b → GLM (light work)
- Local: Ollama with `qwen2.5-coder:7b` (fits the 6 GB GPU); HARD tasks go to `agente`, never to a local model

## MCP Servers

Enabled by default:
- filesystem — File operations
- git — Git diff/blame/log
- github — PRs, issues, checks
- headroom — Context compression
- codebase-memory — Persistent memory
- ponytail — Code quality
- terax — Terminal integration

Enable more: `./bootstrap mcp-enable <server-name>`
