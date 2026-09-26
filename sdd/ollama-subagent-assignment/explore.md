# Exploration: Local Ollama Sub-Agent Assignment System

## Current State

### Architecture Summary

The `ai-workstation-environment` project uses a layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Auto Orchestrator                         │
│  (orchestrator.py → decomposer.py → assigner.py → aggregator.py) │
├─────────────────────────────────────────────────────────────┤
│                      AI Proxy (port 8090)                    │
│  (server.py → Headroom compression → MiMo/Claude backends)  │
├─────────────────────────────────────────────────────────────┤
│                     LiteLLM (port 4000)                      │
│  (litellm_config.yaml → Ollama/Gemini/Claude/OpenRouter)    │
├─────────────────────────────────────────────────────────────┤
│                   Ollama (port 11434)                        │
│  (Native install, GPU-accelerated, gemma4:12b loaded)        │
└─────────────────────────────────────────────────────────────┘
```

### Current Model Routing

The `assigner.py` already defines model tiers but they're **static and untested**:

```python
MODEL_TIERS = {
    "local_fast": {"models": ["qwen2.5-coder:1.5b", "phi3:mini", "gemma2:2b"], "vram": "~2GB"},
    "local_balanced": {"models": ["qwen2.5-coder:7b"], "vram": "~5GB"},
    "cloud_free": {"models": ["gemini-2.5-flash", "gemini-2.5-pro"], "vram": "N/A"},
    "cloud_paid": {"models": ["claude-sonnet-4-20250514", "gpt-4o"], "vram": "N/A"},
}
```

**Problem**: The orchestrator hardcodes model assignments per agent type (line 72-80 in orchestrator.py) without evaluating whether the local model can actually handle the task at acceptable quality/speed.

### Existing Integration Points

1. **LiteLLM** already routes to Ollama via `http://host.docker.internal:11434`
2. **AI Proxy** (port 8090) wraps MiMo/Claude with Headroom compression
3. **Auto Orchestrator** calls `_execute_via_proxy()` which routes to AI Proxy
4. **Headroom Wrapper** applies compression per agent type (coder/debugger = moderate, documenter = aggressive)

### What's Missing

- No runtime benchmark/evaluation of local model capabilities
- No task difficulty classifier (current `suggest_assignment` uses keyword matching only)
- No dynamic routing based on actual model performance
- No fallback logic when local model quality is insufficient

---

## Affected Areas

- `components/auto_orchestrator/assigner.py` — Currently static; needs dynamic capability evaluation
- `components/auto_orchestrator/orchestrator.py` — Needs to call capability evaluator before model selection
- `components/auto_orchestrator/config.yaml` — Needs capability profile storage
- `components/litellm/litellm_config.yaml` — Already has Ollama routing (no changes needed)
- `components/ai-proxy/server.py` — May need Ollama backend handler added

---

## Approaches

### Approach 1: Static Capability Profile (Simple)

**Description**: Pre-define what gemma4:12b can/cannot do based on benchmark results, store as config.

**Pros**:
- Zero runtime overhead
- Simple to implement
- Predictable behavior

**Cons**:
- Doesn't adapt to model changes (if you swap models)
- No quality feedback loop
- Requires manual benchmarking

**Effort**: Low

### Approach 2: Runtime Benchmark on Startup (Moderate)

**Description**: Run a short benchmark suite when orchestrator starts, measure tokens/sec and quality scores, auto-grade the model.

**Pros**:
- Adapts to different models automatically
- Provides real performance data
- Can detect VRAM pressure or thermal throttling

**Cons**:
- Adds 30-60s startup delay
- Benchmark quality may not reflect real task performance
- Requires predefined test cases

**Effort**: Medium

### Approach 3: Dynamic Task-Level Routing (Comprehensive)

**Description**: Classify each task's difficulty, then route to model that matches. Uses a combination of:
- Task metadata (agent type, complexity keywords, estimated tokens)
- Model capability profile (speed tier, quality tier, context window)
- Runtime feedback (track actual completion time, quality scores)

**Pros**:
- Most accurate routing
- Adapts per-task, not per-session
- Can learn over time

**Cons**:
- Most complex to implement
- Task classifier needs tuning
- Requires feedback collection infrastructure

**Effort**: High

### Approach 4: Hybrid — Static Profile + Runtime Fallback (Recommended)

**Description**: Use a pre-evaluated capability profile for initial routing, but monitor actual performance and adjust. If local model takes too long or returns poor quality, escalate to cloud.

**Pros**:
- Best of both worlds
- Fast startup (no benchmark delay)
- Self-correcting via feedback
- Graceful degradation

**Cons**:
- Medium complexity
- Needs quality heuristic (hard to measure without ground truth)

**Effort**: Medium

---

## Recommendation: Approach 4 (Hybrid)

### Architecture Design

```
┌──────────────────────────────────────────────────────────────────┐
│                    Capability Evaluator                           │
│  (new component: evaluator.py)                                    │
│                                                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐  │
│  │ Profile Store    │    │ Task Classifier │    │ Fallback     │  │
│  │ (YAML/JSON)     │    │ (rule-based)    │    │ Monitor      │  │
│  └────────┬────────┘    └────────┬────────┘    └──────┬───────┘  │
│           │                      │                     │          │
│           └──────────────────────┼─────────────────────┘          │
│                                  │                                │
│                          ┌───────▼───────┐                       │
│                          │ Route Decision │                       │
│                          └───────────────┘                       │
└──────────────────────────────────────────────────────────────────┘
```

### Component Structure Proposal

```
components/auto_orchestrator/
├── orchestrator.py          # Existing - add capability check before model selection
├── assigner.py              # Existing - refactor to use capability profiles
├── decomposer.py            # Existing - add task difficulty estimation
├── aggregator.py            # Existing - add quality scoring
├── headroom_wrapper.py      # Existing - no changes
├── evaluator.py             # NEW - capability evaluation engine
├── task_classifier.py       # NEW - task difficulty classification
├── capability_profile.py    # NEW - model capability data model
├── config.yaml              # Existing - add capability profiles section
└── component.yaml           # Existing - no changes
```

### Task Classification Scheme

```python
class TaskDifficulty(Enum):
    TRIVIAL = 1    # Formatting, whitespace fixes, simple renames
    SIMPLE = 2     # CRUD operations, basic functions, simple tests
    MEDIUM = 3     # Multi-file changes, API integration, complex logic
    HARD = 4       # Architecture decisions, performance optimization, security
    EXPERT = 5     # Novel algorithms, complex debugging, system design

# Classification rules (task_classifier.py)
CLASSIFICATION_RULES = {
    # Agent type base difficulty
    "agent_type": {
        "documenter": TaskDifficulty.SIMPLE,
        "tester": TaskDifficulty.SIMPLE,
        "coder": TaskDifficulty.MEDIUM,
        "reviewer": TaskDifficulty.MEDIUM,
        "debugger": TaskDifficulty.HARD,
        "architect": TaskDifficulty.EXPERT,
    },
    # Complexity keywords boost difficulty
    "keywords": {
        "simple": -1, "basic": -1, "quick": -1, "format": -1,
        "complex": +1, "architect": +2, "security": +2, "optimize": +1,
        "refactor": +1, "migrate": +2, "debug": +1,
    },
    # Estimated token count affects difficulty
    "token_thresholds": {
        500: TaskDifficulty.TRIVIAL,
        2000: TaskDifficulty.SIMPLE,
        5000: TaskDifficulty.MEDIUM,
        10000: TaskDifficulty.HARD,
    },
}
```

### Capability Profile Schema

```yaml
# config.yaml addition
capability_profiles:
  gemma4-12b:
    model: gemma4:12b
    hardware: "RTX 2060 6GB + 35GB RAM"
    
    # Measured performance
    performance:
      tokens_per_second: 5
      vram_usage_gb: 4.0
      ram_usage_gb: 4.0
      max_context_tokens: 8192
    
    # Task capability ratings (1-5 scale, 5 = excellent)
    capabilities:
      text_generation: 4
      code_generation: 3
      code_review: 2
      debugging: 2
      architecture: 1
      documentation: 4
      test_generation: 3
    
    # Routing rules
    routing:
      max_difficulty: 2  # TaskDifficulty.SIMPLE
      max_tokens: 2048
      timeout_seconds: 60
      fallback_model: "gemini-2.5-flash"
    
    # Quality gates
    quality:
      min_acceptable_score: 0.7
      max_retry_count: 1
```

### Integration Points

1. **Orchestrator.py** — Add `evaluate_capability()` call in `get_model_for_agent()`:
   ```python
   def get_model_for_agent(self, agent_type: AgentType, task_difficulty: TaskDifficulty) -> str:
       evaluator = CapabilityEvaluator(self.config)
       if evaluator.can_handle_locally(agent_type, task_difficulty):
           return "ollama/gemma4:12b"
       return self._get_cloud_model(agent_type)
   ```

2. **AI Proxy** — Add OllamaHandler to MODEL_REGISTRY:
   ```python
   class OllamaHandler:
       async def complete(self, messages, max_tokens):
           # Direct Ollama API call (bypass LiteLLM for speed)
           async with httpx.AsyncClient() as client:
               resp = await client.post(
                   "http://localhost:11434/api/chat",
                   json={"model": "gemma4:12b", "messages": messages},
                   timeout=60,
               )
               return resp.json()["message"]["content"]
   ```

3. **LiteLLM** — Already configured (no changes needed)

4. **Decomposer** — Add difficulty estimation to `DecomposedTask`:
   ```python
   @dataclass
   class DecomposedTask:
       # ... existing fields
       difficulty: TaskDifficulty = TaskDifficulty.MEDIUM
       estimated_tokens: int = 0
   ```

### Evaluation/Benchmark Structure

```python
# evaluator.py
class CapabilityEvaluator:
    BENCHMARK_SUITE = [
        {"name": "text_formatting", "prompt": "Reformat this code...", "difficulty": TRIVIAL},
        {"name": "simple_function", "prompt": "Write a function that...", "difficulty": SIMPLE},
        {"name": "multi_file", "prompt": "Refactor across these files...", "difficulty": MEDIUM},
        {"name": "architecture", "prompt": "Design a system for...", "difficulty": HARD},
    ]
    
    async def run_benchmark(self, model: str) -> CapabilityProfile:
        """Run benchmark suite and return capability profile."""
        results = []
        for test in self.BENCHMARK_SUITE:
            start = time.time()
            response = await self._call_model(model, test["prompt"])
            elapsed = time.time() - start
            quality = await self._score_response(response, test["expected"])
            results.append({
                "test": test["name"],
                "difficulty": test["difficulty"],
                "time_seconds": elapsed,
                "tokens_per_second": len(response.split()) / elapsed,
                "quality_score": quality,
            })
        return self._build_profile(results)
    
    def can_handle_locally(self, agent_type: str, difficulty: TaskDifficulty) -> bool:
        """Check if local model can handle this task."""
        profile = self.get_current_profile()
        if difficulty.value > profile.routing.max_difficulty:
            return False
        if profile.capabilities.get(agent_type, 0) < 3:
            return False
        return True
```

---

## Risks and Tradeoffs

### Risks

1. **Quality Measurement** — Hard to objectively measure LLM output quality without ground truth
   - Mitigation: Use heuristic scoring (length, structure, code validity) + human feedback loop

2. **VRAM Pressure** — Running gemma4:12b (4GB VRAM) may conflict with other GPU tasks
   - Mitigation: Monitor VRAM usage, fallback to CPU if < 1GB free

3. **Latency Variability** — 5 tokens/sec may spike under load
   - Mitigation: Timeout-based fallback (if > 2x expected time, escalate)

4. **Model Swapping** — User may change Ollama models without updating profiles
   - Mitigation: Auto-detect model via `ollama list` on startup

### Tradeoffs

| Decision | Choice | Tradeoff |
|----------|--------|----------|
| Static vs Dynamic profiles | Hybrid | Slightly more complex but self-correcting |
| Direct Ollama vs LiteLLM routing | Direct for local, LiteLLM for cloud | Lower latency for local, but bypasses LiteLLM's model management |
| Task classifier complexity | Rule-based (not ML) | Simpler but less accurate than ML classifier |
| Quality scoring | Heuristic (not human) | Faster but less reliable |

---

## Ready for Proposal

**Yes** — The exploration is complete. The orchestrator should:

1. Create `evaluator.py` with benchmark suite and capability profile management
2. Create `task_classifier.py` with rule-based difficulty estimation
3. Refactor `assigner.py` to use capability profiles instead of hardcoded tiers
4. Add OllamaHandler to AI Proxy's MODEL_REGISTRY
5. Update `config.yaml` with capability profile schema
6. Add fallback monitoring to track actual performance and adjust routing

The recommended approach (Hybrid) balances simplicity with adaptability, and integrates cleanly with the existing architecture without requiring major refactoring.
