# Design: Local Ollama Sub-Agent Assignment System

## Technical Approach

Hybrid routing: static capability profiles for O(1) task-to-model decisions, runtime monitoring for quality drops, rule-based task classification (no ML). Two new modules—`evaluator.py` and `task_classifier.py`—slot between the existing decomposer and assigner without breaking the current proxy → Headroom → backend pipeline.

## Architecture Decisions

### Decision: Hybrid Profile + Runtime Fallback

**Choice**: Static YAML capability profiles for fast routing; runtime fallback on timeout/quality-drop.

**Alternatives considered**: (1) Pure static profiles — fast but no adaptation to model changes or VRAM pressure. (2) Full runtime benchmarks on every startup — adds 30-60s delay, unacceptable. (3) ML-based task classifier — overkill for 6 agent types and 5 difficulty levels.

**Rationale**: Static profiles keep startup under 5s. Runtime fallback catches degraded performance without re-benchmarking. O(1) classification overhead per task.

### Decision: Rule-Based Task Classifier Over Keyword Matching

**Choice**: Structured rule table with agent-type base difficulty + keyword modifiers + estimated token thresholds, replacing the current `suggest_assignment` keyword matching.

**Alternatives considered**: LLM-based classification (adds latency and cost), ML classifier (needs training data we don't have).

**Rationale**: Rule-based is deterministic, debuggable, and covers the full difficulty spectrum. The decomposer already produces structured `DecomposedTask` objects—we extend them with a `difficulty` field rather than re-querying the LLM.

### Decision: Evaluator On-Demand, Not On-Startup

**Choice**: Benchmarks run lazily on first use or explicitly via `evaluator.py --run`. Profiles cached to YAML; staleness tracked via model hash (`ollama show --modelfile`).

**Alternatives considered**: Startup benchmark (adds 30-60s), periodic background benchmark (wastes VRAM).

**Rationale**: Users rarely swap models. Detecting a model change via `ollama list` diff is cheap (<1s). When a new model is detected, trigger a single lightweight benchmark, not the full suite. Full benchmark available on-demand.

### Decision: Direct Ollama for Local, Proxy for Everything Else

**Choice**: `OllamaHandler` calls `http://localhost:11434/api/chat` directly. Cloud/proxy models continue through AI Proxy (port 8090) unchanged.

**Alternatives considered**: Route everything through LiteLLM (adds a hop for local calls, LiteLLM already configured for Ollama).

**Rationale**: Local calls should have minimum latency. Direct HTTP to Ollama bypasses LiteLLM's OpenAI compatibility layer, saving ~50ms per call. The AI Proxy's Headroom compression is not needed for local models that fit in VRAM.

## Data Flow

```
Task Prompt
    │
    ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Orchestrator │────▶│ Task Classifier   │────▶│ Capability      │
│ .get_model() │     │ .classify()       │     │ Evaluator       │
│              │     │                   │     │ .can_handle()   │
│              │     │ difficulty: HARD  │     │                 │
└─────────────┘     │ tokens_est: 2k    │     │ profile:        │
                    │ agent: debugger   │     │  max_diff=2     │
                    └──────────────────┘     │  caps: [3,2,1]  │
                                             └────────┬────────┘
                                                      │
                                         ┌────────────┴────────────┐
                                         │                         │
                                    CAN handle               CANNOT handle
                                         │                         │
                                         ▼                         ▼
                              ┌─────────────────┐     ┌─────────────────┐
                              │ OllamaHandler    │     │ Cloud fallback   │
                              │ localhost:11434  │     │ (MiMo/Claude)    │
                              └─────────────────┘     └─────────────────┘
                                         │                         │
                                         └────────────┬────────────┘
                                                      │
                                            ┌─────────▼─────────┐
                                            │ Result returned    │
                                            │ + quality metrics  │
                                            └───────────────────┘
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `components/auto_orchestrator/evaluator.py` | Create | Capability profile loader, benchmark runner, `can_handle()` decision function |
| `components/auto_orchestrator/task_classifier.py` | Create | Rule-based difficulty classifier with token estimation |
| `components/auto_orchestrator/assigner.py` | Modify | Replace static `DEFAULT_ASSIGNMENTS` with evaluator-driven `assign()` |
| `components/auto_orchestrator/orchestrator.py` | Modify | Call task classifier in `get_model_for_agent()`, add fallback escalation path |
| `components/auto_orchestrator/decomposer.py` | Modify | Add `difficulty` and `estimated_tokens` to `DecomposedTask` |
| `components/auto_orchestrator/config.yaml` | Modify | Add `capability_profiles` section, add `task_classification` rules |
| `components/ai-proxy/server.py` | Modify | Add `OllamaHandler` to `MODEL_REGISTRY` |
| `components/ai-proxy/config.yaml` | Modify | Add Ollama backend config |

## Interfaces / Contracts

### task_classifier.py

```python
from enum import IntEnum

class TaskDifficulty(IntEnum):
    TRIVIAL = 1
    SIMPLE = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5

@dataclass
class TaskClassification:
    difficulty: TaskDifficulty
    agent_type: str
    estimated_tokens: int
    confidence: float  # 0.0-1.0

def classify(task_description: str, agent_type: str) -> TaskClassification:
    """O(1) rule-based classification. No LLM calls."""
```

### evaluator.py

```python
@dataclass
class CapabilityProfile:
    model_name: str
    model_hash: str  # from ollama show --modelfile | sha256
    max_difficulty: TaskDifficulty
    capabilities: dict[str, int]  # agent_type -> score (1-5)
    tokens_per_second: float
    max_context_tokens: int
    fallback_model: str

def can_handle(profile: CapabilityProfile, difficulty: TaskDifficulty, agent_type: str) -> bool:
    """Check profile caps + difficulty ceiling. O(1)."""

def detect_model_change() -> bool:
    """Compare current ollama model list against cached hashes."""

async def run_benchmark(model: str) -> CapabilityProfile:
    """On-demand benchmark: 4 prompts, ~60s total."""
```

### Orchestrator integration

```python
# orchestrator.py — modified get_model_for_agent
def get_model_for_agent(self, agent_type: AgentType, difficulty: TaskDifficulty = TaskDifficulty.MEDIUM) -> str:
    profile = self.evaluator.get_current_profile()
    if profile and self.evaluator.can_handle(profile, difficulty, agent_type.value):
        return profile.model_name  # local Ollama
    return self._cloud_model_map.get(agent_type, "mimo-auto")
```

### DecomposedTask extension

```python
@dataclass
class DecomposedTask:
    # ... existing fields unchanged
    difficulty: TaskDifficulty = TaskDifficulty.MEDIUM
    estimated_tokens: int = 0
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Task classifier rules, profile loading, `can_handle()` logic | pytest with fixture profiles; assert difficulty for known task patterns |
| Unit | Evaluator benchmark parsing, model hash detection | Mock `httpx` calls to Ollama; assert profile shape |
| Integration | Orchestrator → classifier → evaluator → model selection | Mock Ollama + proxy; verify correct model chosen per difficulty |
| Integration | Fallback escalation path | Simulate `can_handle()` returning False; assert cloud model used |
| E2E | Full pipeline: prompt → classify → route → execute → result | Requires running Ollama; verify response quality within 60s |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary. This design only adds HTTP API calls to a local Ollama server and internal Python module changes.

## Migration / Rollout

No migration required. The new modules are additive. Existing hardcoded model assignments in `assigner.py` continue to work as defaults if the evaluator is not configured or profiles are missing. Feature flag: `config.yaml → capability_profiles.enabled: false` disables the new path entirely.

Rollout steps:
1. Deploy `task_classifier.py` and `evaluator.py` as standalone modules
2. Add `OllamaHandler` to AI Proxy (backward-compatible registry entry)
3. Wire orchestrator to call classifier/evaluator with fallback to existing behavior
4. Run on-demand benchmark, verify profile accuracy
5. Enable capability-based routing, monitor fallback rate

## Open Questions

- [ ] Should the evaluator store benchmark results in Engram for cross-session persistence, or only in `config.yaml`? Engram adds searchability but requires MCP tool calls at startup.
- [ ] What is the exact `ollama show --modelfile` output format for model hash detection across Ollama versions? Need to verify on target hardware.
- [ ] Should quality metrics (tokens/sec, completion time) feed into a running average stored in Engram, or reset per session?