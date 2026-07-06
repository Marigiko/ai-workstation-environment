---
name: dream-distill
description: Extract persistent knowledge from sessions and discover reusable patterns for skills and commands
---

# Dream & Distill Guide

You are orchestrating the memory persistence and self-improvement workflow.

## Dream Command

The `/dream` command extracts persistent knowledge from recent sessions into project memory.

### When to Use
- After completing a complex task
- When you've learned something new about the codebase
- At the end of a productive session
- When you notice patterns worth preserving

### What Dream Does
1. Scans recent session traces
2. Identifies persistent knowledge (architecture decisions, conventions, gotchas)
3. Extracts learnings into MEMORY.md
4. Removes outdated or redundant entries
5. Consolidates related knowledge

### Best Practices
- Run `/dream` after significant work sessions
- Review MEMORY.md periodically to ensure accuracy
- Keep entries concise and actionable
- Remove entries that are no longer relevant

## Distill Command

The `/distill` command discovers repeated manual workflows and packages them into reusable skills, subagents, or commands.

### When to Use
- When you notice yourself doing the same steps repeatedly
- After completing a workflow you'd want to automate
- When you find yourself giving similar instructions multiple times
- When a pattern emerges across multiple sessions

### What Distill Does
1. Analyzes recent work patterns
2. Identifies high-confidence repeated workflows
3. Packages them as:
   - **Skills**: Reusable instructions (SKILL.md files)
   - **Commands**: Quick-access templates (/command)
   - **Subagents**: Specialized agents for specific tasks

### Best Practices
- Run `/distill` when you notice repetition
- Review generated skills/commands for accuracy
- Test new skills before relying on them
- Iterate on skill descriptions for better discovery

## Memory Management

### MEMORY.md Structure
Keep MEMORY.md organized with clear sections:

```markdown
# Project Memory

## Architecture Decisions
- [Decision]: [Rationale]

## Code Conventions
- [Convention]: [Example]

## Common Gotchas
- [Issue]: [Solution]

## Key Workflows
- [Workflow]: [Steps]
```

### Memory Hygiene
- Remove outdated entries
- Consolidate duplicate knowledge
- Keep entries actionable and specific
- Update entries when conventions change

## Checkpoint System

Checkpoints save session state for later resumption.

### Automatic Checkpoints
- Triggered when context approaches limit
- Save task progress and recent context
- Enable seamless session continuation

### Manual Checkpoints
Use `/checkpoint` to save state before:
- Long breaks
- Context switches
- Risky operations
- End of work day

### Resuming from Checkpoint
- Mimo automatically loads latest checkpoint on session start
- Review checkpoint to understand where you left off
- Continue work or start fresh with `/clear`

## Integration with codebase-memory MCP

The `codebase-memory` MCP server provides persistent memory across sessions.

### Features
- Full-text search via SQLite FTS5
- Automatic context injection
- Cross-session knowledge retention
- Project-specific memory

### Best Practices
- Let Mimo auto-inject relevant memory
- Use memory for project-specific knowledge
- Keep global knowledge in AGENTS.md
- Reference memory entries in conversations

## Workflow Example

1. **Work Session**: Complete a complex task
2. **Dream**: Run `/dream` to extract learnings
3. **Distill**: Run `/distill` if patterns emerged
4. **Review**: Check MEMORY.md for accuracy
5. **Checkpoint**: Save state with `/checkpoint`
6. **Resume**: Next session auto-loads context

## Troubleshooting

### Memory Not Saving
- Check MEMORY.md exists in project root
- Verify codebase-memory MCP is enabled
- Ensure write permissions

### Dream Not Extracting
- Complete meaningful work before dreaming
- Provide clear context in conversations
- Check session length (too short = nothing to extract)

### Distill Creating Poor Skills
- Ensure pattern is truly repeated
- Provide clear examples in sessions
- Review and refine generated skills manually
