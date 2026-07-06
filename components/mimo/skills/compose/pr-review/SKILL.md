---
name: compose-pr-review
description: Compose workflow for comprehensive pull request review covering correctness, security, performance, and maintainability
---

# Compose Workflow: PR Review

You are orchestrating a comprehensive pull request review.

## Phase 1: Context Gathering
- Read PR description and linked issues
- Understand the scope and intent
- Identify affected components
- Check for related documentation

## Phase 2: Code Analysis
Use specialized agents:
- `@security-auditor` for security review
- `@perf-analyzer` for performance issues
- `@refactor` for code quality suggestions

## Phase 3: Correctness Review
- Verify logic correctness
- Check edge cases handling
- Review error handling
- Validate input sanitization
- Check for race conditions (if concurrent)

## Phase 4: Quality Review
- Code style and naming
- Function size and complexity
- Duplication detection
- Test coverage adequacy
- Documentation updates

## Phase 5: Integration Review
- Backward compatibility
- Migration requirements
- Configuration changes
- Dependency updates
- Deployment considerations

## Phase 6: Summary
Compile findings:
- Critical issues (must fix)
- Major suggestions (should fix)
- Minor improvements (nice to have)
- Positive aspects (what's done well)

## Deliverables
- Detailed review report
- Specific code suggestions
- Security findings (if any)
- Performance recommendations
- Approval/Request changes decision

Coordinate with `@security-auditor`, `@perf-analyzer`, and `@refactor` agents for specialized analysis.
