# Threat Modeling Prompt

Perform threat modeling for the following system:

## System Description
[Describe the system, its components, and data flows]

## Assets
- **Data**: [What sensitive data is stored/processed]
- **Services**: [Critical services]
- **Infrastructure**: [Servers, databases, etc.]

## Threat Model (STRIDE)

### Spoofing
- Can an attacker impersonate a user/service?
- Are identities verified?
- **Mitigations**: [Authentication mechanisms]

### Tampering
- Can data be modified in transit/at rest?
- Can code be tampered with?
- **Mitigations**: [Integrity checks, signatures]

### Repudiation
- Can actions be denied?
- Is there an audit trail?
- **Mitigations**: [Logging, digital signatures]

### Information Disclosure
- Can sensitive data be exposed?
- Are there data leaks?
- **Mitigations**: [Encryption, access controls]

### Denial of Service
- Can the system be overwhelmed?
- Are there resource limits?
- **Mitigations**: [Rate limiting, scaling]

### Elevation of Privilege
- Can a user gain unauthorized access?
- Are there privilege escalation paths?
- **Mitigations**: [Authorization, least privilege]

## Deliverables

### Threat Matrix
| Threat | Category | Likelihood | Impact | Risk | Mitigation |
|--------|----------|------------|--------|------|------------|
| [Threat] | STRIDE | H/M/L | H/M/L | Score | [Plan] |

### Data Flow Diagram
[Mermaid diagram showing data flows and trust boundaries]

### Attack Trees
[Visual representation of attack paths]

### Recommendations
1. **Critical**: Must fix immediately
2. **High**: Fix before launch
3. **Medium**: Fix in next sprint
4. **Low**: Backlog
