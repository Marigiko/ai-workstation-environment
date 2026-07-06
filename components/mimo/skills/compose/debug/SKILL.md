---
name: compose-debug
description: Compose workflow for systematic debugging following reproduce-isolate-hypothesize-fix-verify methodology
---

# Compose Workflow: Systematic Debug

You are orchestrating a systematic debugging session.

## Phase 1: Reproduce
- Verify the bug exists
- Create minimal reproduction case
- Document exact steps to reproduce
- Identify affected versions/environment

## Phase 2: Isolate
- Narrow down affected component
- Identify failing module/function
- Check recent changes (git log)
- Review error logs and stack traces

## Phase 3: Hypothesize
Generate hypotheses:
1. What could cause this symptom?
2. List top 3 most likely causes
3. Rank by probability and ease of testing

## Phase 4: Test Hypotheses
For each hypothesis:
- Design a test to verify
- Execute the test
- Record results
- Accept or reject hypothesis

## Phase 5: Root Cause
- Confirm actual root cause
- Understand why it happened
- Identify contributing factors
- Check for similar issues elsewhere

## Phase 6: Fix
- Implement minimal fix
- Ensure fix doesn't break other things
- Add regression test
- Update related documentation

## Phase 7: Verify
- Confirm bug is fixed
- Run full test suite
- Check for side effects
- Test edge cases

## Phase 8: Prevent
- Add monitoring/alerting if needed
- Update coding guidelines
- Add to known issues list
- Document for future reference

## Deliverables
- Root cause analysis
- Working fix with tests
- Prevention measures
- Updated documentation

Use `@perf-analyzer` if performance-related, `@security-auditor` if security-related.
