# Secure Coding Review Prompt

Review the following code for security vulnerabilities:

## Code
```
[Paste code here]
```

## Context
- **Language/Framework**: [Tech stack]
- **Purpose**: [What this code does]
- **Trust Level**: [User input? Internal? External API?]

## Security Checklist

### Input Validation
- [ ] All inputs validated and sanitized
- [ ] Type checking enforced
- [ ] Length limits enforced
- [ ] Allowlist over denylist

### Injection
- [ ] SQL injection prevented (parameterized queries)
- [ ] Command injection prevented (no shell=True)
- [ ] XSS prevented (output encoding)
- [ ] Path traversal prevented (no user-controlled paths)
- [ ] LDAP/XML injection prevented

### Authentication & Authorization
- [ ] Authentication required for protected resources
- [ ] Authorization checks on every request
- [ ] Role-based access control implemented
- [ ] Session management secure

### Cryptography
- [ ] Strong algorithms (AES-256, RSA-2048+)
- [ ] Proper key management
- [ ] Secure random number generation
- [ ] No hardcoded secrets

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] TLS for data in transit
- [ ] Secrets not in logs
- [ ] PII handled per policy

### Error Handling
- [ ] Errors don't leak sensitive info
- [ ] Stack traces not exposed to users
- [ ] Graceful degradation

## Deliverables

1. **Vulnerabilities**: Severity, location, description
2. **Exploits**: How each could be attacked
3. **Fixes**: Specific code changes
4. **Best Practices**: Recommendations for the future
