# Terax Integration Guide

## Overview

Terax es un terminal AI-nativo de código abierto que se integra como la **capa de presentación visual** en la plataforma de AI Engineering. No reemplaza al orquestador — se conecta a LiteLLM vía endpoint OpenAI-compatible y detecta agentes externos (MiMoCode, Claude Code) vía marcadores OSC 777.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TERAX (Frontend)                      │
│  Terminal + Editor + Visualización                       │
│  Custom Agents + Snippets + TERAX.md                    │
│  Agent Detection (OSC 777)                              │
└──────────────────────┬──────────────────────────────────┘
                       │ Terminal I/O + OSC markers
                       ▼
┌─────────────────────────────────────────────────────────┐
│              ORQUESTADOR (Backend)                       │
│  Opción A: MiMoCode (TUI)                               │
│  Opción B: Claude Code (CLI)                            │
│                                                      │
│  Responsabilidades:                                      │
│  - MCP tool orchestration                               │
│  - Context management + compression                     │
│  - Memory persistence                                   │
│  - Workflow execution                                   │
│  - Multi-agent coordination                             │
└──────────────────────┬──────────────────────────────────┘
                       │ OpenAI-compatible + MCP
                       ▼
┌─────────────────────────────────────────────────────────┐
│              LITELLM (Gateway)                           │
│  Model routing + Load balancing + Fallbacks             │
│  Cost tracking + Rate limiting + Budgets                │
│  MCP Gateway (herramientas centralizadas)               │
│  RAG endpoints (/rag/ingest, /rag/query)                │
│  A2A protocol support                                   │
└──────┬──────────────┬───────────────┬───────────────────┘
       │              │               │
       ▼              ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Cloud    │  │ Local    │  │ MCP Servers  │
│ Models   │  │ Models   │  │              │
│ Claude   │  │ Ollama   │  │ Context Eng  │
│ Gemini   │  │ llama.cpp│  │ RAG          │
│ GPT-4    │  │ MLX      │  │ Repomix      │
│ OpenRouter│ │ LM Studio│  │ Headroom     │
│ DeepSeek │  │          │  │ Ponytail     │
└──────────┘  └──────────┘  └──────────────┘
```

## Installation

### Via Bootstrap

```bash
# Install with notebook profile (includes Terax)
./bootstrap bootstrap --profile notebook

# Or with desktop profile
./bootstrap bootstrap --profile desktop
```

### Manual Installation

```bash
# Install Terax binary
./components/terax/install.sh

# Or download directly
curl -sL https://github.com/crynta/terax-ai/releases/latest/download/terax-linux-x86_64.tar.gz | tar -xz -C ~/.local/bin/
```

## Configuration

### LiteLLM Connection

Terax connects to LiteLLM via the OpenAI-compatible endpoint:

```yaml
# ~/.config/terax/config.yaml
ai:
  provider: openai-compatible
  base_url: "http://localhost:4000"
  api_key: "sk-litellm"
  model: "claude-sonnet-4-20250514"
```

### Agent Detection

Terax detects MiMoCode and Claude Code automatically via OSC 777 markers. When you run these agents in Terax terminals, their status appears in the notification panel.

### Custom Agents

Define custom agents in `~/.config/terax/config.yaml`:

```yaml
agents:
  - name: "orchestrator"
    system_prompt: "Full AI Engineering orchestration..."
    tools: [bash, read, write, edit, grep, glob]
```

### Snippets

Reusable prompt fragments callable via `/snippet-name`:

```yaml
snippets:
  - name: "/research"
    prompt: "Deep research on {{topic}} using parallel sub-agents"
```

## Workflow Examples

### 1. Full Stack Development

```
1. Open Terax
2. Launch MiMoCode in a terminal tab
3. MiMoCode connects to LiteLLM + MCP
4. Use /orchestrator agent for complex tasks
5. View diffs and results in Terax editor
```

### 2. Model Benchmarking

```
1. Use /benchmark snippet
2. Terax calls LiteLLM with different models
3. Compare latency, quality, cost
4. Results displayed in terminal
```

### 3. Code Review

```
1. Use /review-pr snippet
2. Agent reads PR via GitHub MCP
3. Reviews code with security audit
4. Comments posted via GitHub API
```

## MCP Integration

Terax itself does NOT support MCP natively. MCP tools are accessed through the orchestrator layer:

```
Terax → MiMoCode → MCP Gateway (LiteLLM) → MCP Servers
```

The MCP servers available through the orchestrator:
- filesystem, git, github (enabled by default)
- headroom, codebase-memory, ponytail (optional)
- docker, postgres, playwright, browser, memory (optional)

## Context Management

### Repomix Integration

```bash
# Compress codebase for AI context
repomix --compress --output context.md .

# Reference in TERAX.md
# "Read context.md for full codebase context"
```

### Headroom

Context compression handled automatically via MCP server. No manual configuration needed.

### Codebase Memory

Persistent memory across sessions via MCP server. Enable with:

```bash
./bootstrap mcp-enable codebase-memory
```

## Troubleshooting

### Terax can't connect to LiteLLM

```bash
# Check LiteLLM is running
docker ps | grep litellm

# Test the endpoint
curl http://localhost:4000/health

# Check Terax config
cat ~/.config/terax/config.yaml
```

### Agent detection not working

```bash
# Verify OSC 777 markers are enabled
# MiMoCode and Claude Code emit these automatically
# Check Terax notification panel for agent status
```

### MCP tools not available

```bash
# MCP tools are accessed through the orchestrator, not directly from Terax
# Ensure MiMoCode/ClaudeCode is running and connected to MCP
./bootstrap mcp-list
```

## References

- [Terax GitHub](https://github.com/crynta/terax-ai)
- [Terax Documentation](https://terax.app/docs)
- [LiteLLM Documentation](https://docs.litellm.ai)
- [MCP Specification](https://modelcontextprotocol.io)
- [Platform Architecture](./architecture.md)
