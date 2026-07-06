---
name: log-analysis
description: Analyze logs to identify errors, bottlenecks, patterns, and correlations with actionable recommendations
---

# Log Analysis Prompt

Analyze the following logs to identify issues:

## Log Source
- **Application**: [App name]
- **Time Range**: [Start - End]
- **Environment**: [Production/Staging/Dev]

## Logs
```
[Paste logs here]
```

## Analysis Goals
- [ ] Identify errors and exceptions
- [ ] Find performance bottlenecks
- [ ] Detect unusual patterns
- [ ] Correlate events across components

## Deliverables

### 1. Error Summary
| Timestamp | Error | Component | Impact |
|-----------|-------|-----------|--------|
| [Time] | [Error message] | [Where] | [What broke] |

### 2. Timeline
Reconstruct the sequence of events:
- [Time]: [Event]
- [Time]: [Event]

### 3. Patterns
- **Frequency**: How often do errors occur?
- **Correlation**: Do errors cluster together?
- **Triggers**: What precedes the errors?

### 4. Root Causes
Based on the logs, what are the likely root causes?

### 5. Recommendations
- Immediate actions to stabilize
- Long-term fixes to prevent recurrence
- Monitoring improvements needed
