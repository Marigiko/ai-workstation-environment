---
name: checkpoint-management
description: Manage session checkpoints for seamless context preservation and resumption across sessions
---

# Checkpoint Management Guide

You are orchestrating the checkpoint system for session state preservation.

## What Are Checkpoints?

Checkpoints are structured snapshots of your session state that enable seamless continuation across sessions. They capture:

- Current task progress
- Recent context and decisions
- Active files and their states
- Pending work items
- Key learnings from the session

## Automatic Checkpoints

Mimo automatically creates checkpoints when:

- Context window approaches its limit (70% threshold)
- Session is ending naturally
- Significant progress has been made
- User explicitly requests `/checkpoint`

### Automatic Checkpoint Contents
- Task tree status (T1, T1.1, T1.2, etc.)
- Recent conversation turns (last 3 by default)
- Project memory references
- Active file changes
- Pending TODOs

## Manual Checkpoints

Use `/checkpoint` command to manually save state:

### When to Create Manual Checkpoints
- Before long breaks
- When switching to different work
- After completing major milestones
- Before risky operations
- End of work day

### Checkpoint Best Practices
- Create checkpoints at natural stopping points
- Include clear notes about next steps
- Verify checkpoint saved successfully
- Test resumption in a new session

## Resuming from Checkpoint

When you start a new session, Mimo automatically:

1. Loads the latest checkpoint
2. Injects relevant project memory
3. Restores task progress
4. Provides context summary

### Resume Workflow
1. Start new Mimo session
2. Review checkpoint summary
3. Continue work or adjust plan
4. Use `/clear` to start fresh if needed

## Checkpoint Storage

Checkpoints are stored in:
- `.mimocode/checkpoints/` (project-level)
- `~/.config/mimocode/checkpoints/` (global)

### Checkpoint File Structure
```
checkpoint.md
├── Session metadata (timestamp, model, agent)
├── Task progress (tree structure)
├── Recent context (last N turns)
├── Active files list
├── Pending work items
└── Key decisions made
```

## Configuration

Checkpoint behavior is configured in `mimocode.json`:

```json
{
  "checkpoint": {
    "auto": true,
    "threshold": 0.7,
    "reserved_tokens": 2000
  }
}
```

### Configuration Options
- `auto`: Enable automatic checkpoints (default: true)
- `threshold`: Context usage threshold for auto-checkpoint (0.0-1.0)
- `reserved_tokens`: Tokens to reserve for checkpoint data

## Integration with Memory System

Checkpoints work with the memory system:

1. **MEMORY.md**: Persistent project knowledge
2. **Checkpoints**: Session-specific state
3. **Dream**: Extracts learnings to MEMORY.md
4. **Distill**: Creates reusable patterns

### Workflow Integration
```
Work Session → Checkpoint → Dream → Memory Update
     ↓
Resume Session → Load Checkpoint → Continue Work
```

## Troubleshooting

### Checkpoint Not Loading
- Verify checkpoint file exists
- Check file permissions
- Ensure checkpoint format is valid
- Try manual checkpoint creation

### Context Lost After Resume
- Check checkpoint threshold settings
- Verify reserved_tokens is sufficient
- Review compaction settings
- Consider manual checkpoint before critical work

### Checkpoint Too Large
- Reduce tail_turns in compaction config
- Clean up MEMORY.md regularly
- Use /clear to start fresh sessions
- Adjust reserved_tokens downward

## Advanced Usage

### Multiple Checkpoints
Keep multiple checkpoints for different work streams:
- `checkpoint-feature-a.md`
- `checkpoint-bug-fix.md`
- `checkpoint-exploration.md`

### Checkpoint Review
Before resuming, review checkpoint:
```bash
cat .mimocode/checkpoints/checkpoint.md
```

### Checkpoint Cleanup
Remove old checkpoints:
```bash
rm .mimocode/checkpoints/checkpoint-*.md
```

## Best Practices Summary

1. **Create checkpoints at natural boundaries**
2. **Review checkpoints before resuming**
3. **Keep MEMORY.md clean and current**
4. **Use /dream to extract learnings**
5. **Test resume workflow regularly**
6. **Backup important checkpoints**
7. **Clean up old checkpoints periodically**
