# Workflows Library
# Reusable, composable workflows for common tasks

## Available Workflows

- `create-fastapi-project.yaml` — Scaffold a FastAPI project with best practices
- `create-scraper.yaml` — Build a web scraper with error handling
- `review-pr.yaml` — Comprehensive PR review checklist
- `generate-tests.yaml` — Generate test suite for existing code
- `create-rag.yaml` — Set up RAG pipeline with embeddings
- `debug-python.yaml` — Systematic Python debugging workflow

## Workflow Structure

Each workflow is a YAML file containing:

```yaml
name: workflow-name
description: "What this workflow does"
prompt: "@prompts/path/to/prompt.md"
context:
  - "Additional context files or variables"
tools:
  - filesystem
  - git
mcp_required:
  - git
  - github
model_recommended: "claude-sonnet-4-20250514"
steps:
  - name: "Step 1"
    action: "..."
  - name: "Step 2"
    action: "..."
```

## Usage

Workflows can be invoked via AI tools or referenced manually.
