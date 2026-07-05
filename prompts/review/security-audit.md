# Security Audit Prompt

Perform a security audit of the following code/system:

## Scope
[Describe what's being audited: API, auth system, data processing, etc.]

## Code/Architecture
```
[Paste code or describe architecture]
```

## Audit Checklist

### Input Validation
- [ ] All user input validated
- [ ] Type checking enforced
- [ ] Length limits enforced
- [ ] Format validation (regex, etc.)
- [ ] Sanitization where needed

### Authentication & Authorization
- [ ] Authentication required for protected routes
- [ ] Authorization checks in place
- [ ] Role-based access control
- [ ] Session management secure
- [ ] Password storage secure (bcrypt, etc.)

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] TLS for data in transit
- [ ] Secrets not in code/config
- [ ] PII handled according to policy
- [ ] Logging doesn't expose secrets

### Injection Prevention
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (output encoding)
- [ ] Command injection prevented
- [ ] Path traversal prevented
- [ ] LDAP injection prevented

### Dependencies
- [ ] No known vulnerable dependencies
- [ ] Dependencies up to date
- [ ] Minimal attack surface

## Deliverables

1. **Vulnerabilities Found**: Severity (Critical/High/Medium/Low)
2. **Attack Vectors**: How each vulnerability could be exploited
3. **Remediation**: Specific fixes for each issue
4. **Security Recommendations**: Best practices to adopt
