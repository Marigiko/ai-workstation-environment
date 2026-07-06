---
name: code-review
description: Review code for correctness, readability, maintainability, performance, and security with constructive feedback
---

# Code Review Prompt

Review the following code for quality, correctness, and maintainability:

## Code to Review
```
[Paste code here]
```

## Review Checklist

### Correctness
- [ ] Logic is correct
- [ ] Edge cases handled
- [ ] Error handling appropriate
- [ ] No race conditions (if concurrent)

### Readability
- [ ] Names are clear and descriptive
- [ ] Functions are small and focused
- [ ] Complex logic is explained
- [ ] Consistent style

### Maintainability
- [ ] No unnecessary duplication
- [ ] Dependencies are clear
- [ ] Easy to test
- [ ] Follows project conventions

### Performance
- [ ] No obvious bottlenecks
- [ ] Appropriate data structures
- [ ] No unnecessary allocations
- [ ] Consider caching if needed

### Security
- [ ] Input validation
- [ ] No SQL injection
- [ ] No XSS vulnerabilities
- [ ] Secrets not hardcoded

## Deliverables

1. **Issues Found**: Categorized by severity (critical/major/minor)
2. **Suggestions**: Specific improvements
3. **Positive Aspects**: What's done well
4. **Refactoring Ideas**: Optional improvements

Be constructive. Explain the "why" behind suggestions.
