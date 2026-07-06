---
name: compose-tests
description: Compose workflow for generating comprehensive test suites covering unit, integration, and edge cases
---

# Compose Workflow: Test Generation

You are orchestrating the creation of a comprehensive test suite.

## Phase 1: Analysis
- Identify code to test
- Map public APIs and interfaces
- Identify dependencies to mock
- List edge cases and error paths

## Phase 2: Test Planning
Break down test categories:
1. Unit tests (isolated functions/methods)
2. Integration tests (component interactions)
3. Error path tests (exception handling)
4. Edge case tests (boundary values, empty inputs)
5. Performance tests (if applicable)

## Phase 3: Test Implementation
Use TDD approach:
- Write failing test first
- Implement minimal code to pass
- Refactor while keeping tests green
- Repeat for each scenario

## Phase 4: Coverage Analysis
- Run coverage report
- Identify untested paths
- Add tests for missing coverage
- Ensure critical paths are covered

## Phase 5: Test Quality
- Verify tests are independent
- Check for test duplication
- Ensure clear test names
- Validate assertions are specific
- Remove flaky tests

## Phase 6: Documentation
- Document test setup requirements
- Explain how to run tests
- Add examples for complex scenarios
- Document mocking strategy

## Deliverables
- Comprehensive test suite
- High code coverage (>80%)
- Clear test documentation
- Mocking fixtures/helpers
- CI integration examples

Use `@tdd-driver` agent for strict TDD discipline.
