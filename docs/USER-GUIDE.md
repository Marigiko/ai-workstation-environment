# AI Engineering Platform - User Guide

## Quick Start

### 1. Start Services
```bash
# Start all infrastructure
cd components/workspace && docker compose up -d
cd components/n8n && docker compose up -d

# Verify
curl http://localhost:8080/health
curl http://localhost:20128/v1/models \
  -H "Authorization: Bearer $OMNIROUTE_API_KEY"
```

### 2. Configure Telegram Bot
```bash
# 1. Create bot via @BotFather on Telegram
# 2. Get bot token
# 3. Edit config
vim components/telegram-bot/config/bot.yaml
# Set bot.token: "YOUR_BOT_TOKEN"

# 4. Start bot
cd components/telegram-bot
python3 bot.py
```

### 3. Send First Task
```
# In Telegram:
/prompt Create a Python FastAPI endpoint for user authentication
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show help | `/start` |
| `/prompt <text>` | Send task to orchestrator | `/prompt Create a REST API` |
| `/status` | System status | `/status` |
| `/status <id>` | Task status | `/status abc123` |
| `/approve <id>` | Approve task | `/approve abc123` |
| `/reject <id>` | Reject task | `/reject abc123` |
| `/commit <msg>` | Git commit | `/commit Initial implementation` |
| `/worktrees` | List worktrees | `/worktrees` |
| `/model <name>` | Switch model | `/model qwen2.5-coder:7b` |
| `/agent <name>` | Switch agent | `/agent coder` |
| `/auto` | Toggle auto mode | `/auto` |

## Auto Mode

When auto mode is enabled, all messages are automatically sent to the orchestrator:

```
/auto
# Now typing any message sends it as a task
Create a web scraper for news articles
```

The orchestrator will:
1. Plan the task
2. Decompose into subtasks
3. Assign optimal models to each agent
4. Execute in parallel
5. Aggregate results
6. Send notification via Telegram

## Worktrees

Worktrees allow you to work on multiple projects simultaneously:

```
/worktrees  # List all worktrees
/worktree project-a  # Switch to project-a
```

Each worktree has:
- Independent git repository
- Separate session
- Configurable model and agent
- Isolated state

## Models

Available models (via Ollama on RTX 2060):

| Model | Size | Best For |
|-------|------|----------|
| qwen2.5-coder:1.5b | 986MB | Fast responses |
| phi3:mini | 2.2GB | Balanced |
| gemma2:2b | 1.6GB | General |
| qwen2.5-coder:7b | 4.7GB | Best code |

Cloud models (via OmniRoute, http://localhost:20128/v1, bearer key in `OMNIROUTE_API_KEY`):
- Combo `agente`: GLM Coding Plan → Gemini 2.5 Flash → Groq gpt-oss-120b (hard/coding work)
- Combo `liviano` (free first): Gemini 2.5 Flash → Groq gpt-oss-120b → GLM (light work)

## Agent Types

| Agent | Model | Use Case |
|-------|-------|----------|
| architect | qwen2.5-coder:7b | Planning, architecture |
| coder | qwen2.5-coder:7b | Code implementation |
| reviewer | gemini-2.5-flash | Code review |
| documenter | qwen2.5-coder:1.5b | Documentation |
| tester | phi3:mini | Test generation |
| debugger | qwen2.5-coder:7b | Debugging |

## Troubleshooting

### Bot not responding
```bash
# Check bot logs
tail -f /var/log/telegram-bot.log

# Check n8n
curl http://localhost:5678/healthz
```

### Tasks not executing
```bash
# Check workspace API
curl http://localhost:8080/health

# Check OmniRoute
curl http://localhost:20128/v1/models \
  -H "Authorization: Bearer $OMNIROUTE_API_KEY"
```

### Model not available
```bash
# Check Ollama
docker exec awe-ollama ollama list

# Pull model
docker exec awe-ollama ollama pull qwen2.5-coder:7b
```
