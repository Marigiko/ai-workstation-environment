# Performance Debugging Prompt

Investigate and resolve the performance issue:

## Issue
**Metric**: [Response time/Throughput/Memory/CPU]
**Current**: [Current value]
**Expected**: [Target value]
**Regression**: [When did it get worse]

## Context
- **Application**: [What app]
- **Load**: [Request rate, concurrent users]
- **Environment**: [Hardware, resources]

## Available Data
- **Metrics**: [Grafana/dashboard screenshots]
- **Profiling**: [CPU/memory profiles]
- **Slow Queries**: [Database query times]
- **Logs**: [Relevant log entries]

## Investigation Steps

### 1. Identify Bottleneck
- CPU bound or I/O bound?
- Memory pressure?
- Network latency?
- Database slow?

### 2. Drill Down
- Which endpoint/function is slow?
- What's the call stack?
- Where is time spent?

### 3. Root Cause
- Algorithmic complexity?
- N+1 queries?
- Missing cache?
- Resource contention?
- Memory leak?

### 4. Solution
- Optimize algorithm
- Add caching
- Fix queries
- Scale resources
- Async processing

## Deliverables

1. **Bottleneck Identified**: Where is the slowdown?
2. **Root Cause**: Why is it slow?
3. **Fix**: Specific code/config changes
4. **Verification**: How to measure improvement
5. **Prevention**: How to catch this earlier
