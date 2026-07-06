---
name: compose-fastapi
description: Compose workflow for creating production-ready FastAPI projects with authentication, database, and deployment
---

# Compose Workflow: FastAPI Project

You are orchestrating the creation of a production-ready FastAPI project.

## Phase 1: Specification
Gather requirements:
- Project name and purpose
- Authentication method (JWT, OAuth2, API keys)
- Database choice (PostgreSQL, SQLite, MongoDB)
- Key endpoints and resources
- Deployment target (Docker, cloud provider)

## Phase 2: Planning
Break down into tasks:
1. Project structure setup
2. Database models and migrations
3. Authentication system
4. Core API endpoints
5. Error handling and validation
6. Testing setup
7. Docker configuration
8. Documentation

## Phase 3: Execution
Execute tasks in order:
- Use `clean-implementation` skill for each component
- Run tests after each major component
- Generate documentation as you go

## Phase 4: Verification
- Run full test suite
- Check code coverage
- Verify Docker build
- Test API endpoints manually

## Phase 5: Documentation
- Generate README with installation, usage, deployment
- Add API documentation (OpenAPI/Swagger)
- Include environment configuration guide

## Deliverables
- Complete FastAPI project structure
- Working API with authentication
- Database models and migrations
- Docker configuration
- Comprehensive tests
- Full documentation

Use `@tdd-driver` for test writing, `@security-auditor` for auth review, `@docs-writer` for documentation.
