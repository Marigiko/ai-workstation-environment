# n8n

Workflow automation, backed by the AWE PostgreSQL component.

## Install

```bash
./bootstrap bootstrap --profile <profile>   # or directly:
bash components/postgresql/install.sh       # dependency, must be healthy first
bash components/n8n/install.sh
```

Then open http://127.0.0.1:5678 — the first visit creates the owner account.

## Using OmniRoute from AI nodes

From inside the container, OmniRoute is reachable at
`http://host.docker.internal:20128/v1` (already wired as `OMNIROUTE_BASE_URL`).

1. Create a credential of type **OpenAI**:
   - Base URL: `http://host.docker.internal:20128/v1`
   - API key: your OmniRoute API key
2. In **OpenAI** / **AI Agent** nodes, use model `liviano` or `agente`.
