---
name: systematic-debugging
description: Debug systematically by reproducing, isolating, hypothesizing, testing, finding root cause, and fixing
---

# Systematic Debugging Prompt

Debug the following issue systematically:

## Issue Description
**Symptom**: [What's happening]
**Expected**: [What should happen]
**Actual**: [What is happening]
**Frequency**: [Always/Sometimes/Rare]
**Started**: [When did this start]

## Environment
- **OS**: [Operating system]
- **Language/Runtime**: [Version]
- **Dependencies**: [Relevant versions]
- **Recent Changes**: [What changed recently]

## Reproduction Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Available Information
- **Logs**: [Paste relevant logs]
- **Error Messages**: [Exact error text]
- **Stack Trace**: [If available]
- **Screenshots**: [If applicable]

## Debugging Approach

### 1. Reproduce
- Can we reproduce consistently?
- Minimal reproduction case?

### 2. Isolate
- Which component is failing?
- Can we test in isolation?

### 3. Hypothesize
- What could cause this symptom?
- List top 3 hypotheses

### 4. Test Hypotheses
For each hypothesis:
- **Hypothesis**: [What we think]
- **Test**: [How we'll verify]
- **Result**: [What we found]

### 5. Root Cause
- What is the actual root cause?
- Why did this happen?

### 6. Fix
- What's the minimal fix?
- How to prevent recurrence?

## Deliverables

1. **Root Cause Analysis**: Clear explanation
2. **Fix**: Code change or configuration update
3. **Prevention**: How to avoid this in the future
4. **Testing**: How to verify the fix works
