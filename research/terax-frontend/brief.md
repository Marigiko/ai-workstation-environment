# Research Brief: Terax as AI Engineering Frontend

> Historical document (written before 2026-09-25). LiteLLM was later replaced by OmniRoute (http://localhost:20128/v1); see docs/INTEGRATION-ARCHITECTURE.md for the current setup.

**Date**: 2026-07-07
**Depth**: deep (5-8 sub-agents, 25+ sources)
**Language**: Spanish output requested, English research sources

## Question

Can Terax serve as the primary professional frontend for a comprehensive AI Engineering ecosystem that already includes: AI Engineering Platform, ai-workstation, LiteLLM, Ollama, llama.cpp, Claude Max, Gemini, OpenRouter, MCP, Context Engine, RAG, Repomix, Headroom, Ponytail, Codebase Memory, n8n?

## Scope

### In scope
- Terax architecture, capabilities, plugins, extensibility
- MCP support in Terax
- OpenAI-compatible API support
- LiteLLM, Ollama, self-hosted model integration
- Context management, memory, workflows
- Competitor comparison: MiMo (MiMoCode), OpenCode, Claude Code, Zed
- Architecture design for Terax-as-frontend over existing infrastructure
- Productivity, flexibility, extensibility evaluation
- Final recommendation

### Out of scope
- Writing implementation code (user explicitly said "no code yet")
- Detailed pricing comparison
- Non-AI coding editors (VS Code, Vim, etc.)

## Assumptions
- User is a Principal AI Systems Engineer
- Existing infrastructure is mature and production-grade
- Terax would need to orchestrate, not replace, existing tools
- User wants maximum productivity and integration depth

## Angles

1. **Terax Core Architecture** — What is Terax? Tech stack, architecture, rendering, terminal emulation, extensibility model
2. **Terax Plugin/Extension System** — Plugin API, extension types, community ecosystem, custom tool integration
3. **Terax MCP & Model Support** — MCP protocol support, OpenAI-compatible endpoints, LiteLLM/Ollama integration, local model support
4. **Context & Memory Systems** — How Terax handles context windows, memory, codebase awareness, RAG integration points
5. **Workflow & Automation** — Task management, automation, scripting, hooks, event-driven workflows
6. **Competitor Analysis** — MiMo, OpenCode, Claude Code, Zed: architecture, features, extensibility, AI-native capabilities
7. **Integration Architecture Patterns** — How AI tools integrate as frontends to existing infrastructure (patterns from Claude Code, Cursor, etc.)
