# PR Review Prompt

Review this pull request for merge readiness:

## PR Context
- **Title**: [PR title]
- **Description**: [PR description]
- **Related Issues**: [Issue numbers]
- **Files Changed**: [List of files]

## Review Focus

### 1. Requirements Met
- [ ] All acceptance criteria satisfied
- [ ] Tests added/updated
- [ ] Documentation updated if needed

### 2. Code Quality
- [ ] Follows project style guide
- [ ] No obvious bugs or logic errors
- [ ] Error handling appropriate
- [ ] No security issues

### 3. Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests if needed
- [ ] Edge cases tested
- [ ] Tests are readable and maintainable

### 4. Performance
- [ ] No performance regressions
- [ ] Database queries optimized
- [ ] No N+1 queries
- [ ] Appropriate use of caching

### 5. Deployment
- [ ] Migration scripts if needed
- [ ] Backward compatible
- [ ] Rollback plan if needed
- [ ] Feature flags if needed

## Deliverables

1. **Approval Status**: Approve / Request Changes / Comment
2. **Critical Issues**: Must fix before merge
3. **Suggestions**: Nice to have improvements
4. **Questions**: Clarifications needed
