# TalkBot Benchmark System

TalkBot measures a voice assistant as a **pipeline** — four stages that each contribute latency, accuracy, and cost. The goal is to find the optimal combination for a given hardware profile, and to build a cross-machine comparison so recommendations can be made per hardware class.

---

## The Pipeline

```
Microphone → STT → LLM (+tools) → TTS → Speaker
             ↓         ↓           ↓
           WER%    Success%    Synth ms
           RTF     Tool Sel%
           ms      Latency ms
```

**TTFA** (Time To First Audio) = `STT_ms + LLM_ms + TTS_ms`

This is the end-to-end metric that determines how responsive the assistant feels. Each stage has its own leaderboard, and the pipeline leaderboard composes them.

---

## The Four Evaluation Dimensions

### 1. STT — Speech-to-Text

Measures transcription accuracy and speed.

| Metric | Meaning |
|---|---|
| WER% | Word Error Rate — lower is better |
| Pass% | Fraction of prompts where WER < 10% |
| RTF | Realtime factor — `< 1.0` means faster than realtime |
| Avg ms | Time from audio end to transcript ready |

**Current results:** `benchmarks/published/stt_leaderboard.md`

Current bests on fubarsream (i7-10610U, CPU):

| Config | Pass% | Avg WER | Avg ms | RTF |
|---|---|---|---|---|
| small.en / int8 / cpu | **100%** | **0.0%** | 4,283 | 1.33x |
| tiny.en / int8 / cpu | 85.4% | 6.6% | **312** | **0.10x** |

> Trade-off: `small.en` is highly accurate but 13× slower. `tiny.en` is near-realtime but fails ~15% of prompts (mostly complex technical terms).

---

### 2. LLM — Base Language Model Quality

Measures whether the model can hold a coherent multi-turn conversation. Evaluated separately from tools to isolate model intelligence from tool-calling mechanics.

---

### 3. LLM + Tools — Tool-Calling Quality

The core benchmark. 10 scripted multi-turn scenarios covering:

| Category | Scenarios | What it tests |
|---|---|---|
| core | timer_basics, list_basics, memory_persistent_strict | Basic tool correctness |
| multistep | list_multistep_packing, cross_tool_mix | Chained tool workflows |
| recovery | recovery_timer_retry | Error handling + retry |
| context | memory_context_pressure, memory_context_flexible | Memory under distraction |
| robustness | calculator_basic, utility_time_date | Edge cases and math |

Key metrics:

| Metric | Meaning |
|---|---|
| Success% | End-to-end scenario pass rate |
| Tool Sel% | Did the model call the right tool? |
| Arg Acc% | Were arguments correct when tool was called? |
| Recovery% | Did the model recover from an error? |
| Avg ms | Average turn latency |
| Gen tok/s | Token generation speed |
| Mem MB | Peak model memory |

**Current results:** `benchmarks/published/latest/leaderboard.md`

---

### 4. TTS — Text-to-Speech

Measures synthesis speed and quality.

| Metric | Meaning |
|---|---|
| Synth ms | Time from text input to audio file ready |
| RTF | Realtime factor (< 1.0 = faster than realtime) |
| Audio ms | Duration of synthesized audio |

**Current results:** `benchmarks/published/tts_leaderboard.md`

Current bests on fubarsream:

| Config | Synth ms | RTF |
|---|---|---|
| pyttsx3 (system) | **14** | **0.01x** |
| KittenTTS default | 1,524 | 0.34x |
| KittenTTS Bella | 2,297 | 0.50x |

> pyttsx3 is fastest but lowest quality. KittenTTS default (nano model) is the best quality/speed trade-off.

---

## Pipeline Composition (TTFA)

The pipeline leaderboard (`benchmarks/published/pipeline_leaderboard.md`) composes all three stages to find the best end-to-end combinations.

Current best balanced config on fubarsream (100% LLM success, fast TTFA):

```
tiny.en/int8/cpu  +  gemini-2.5-flash-lite (remote)  +  kittentts/default
     312 ms       +           910 ms                  +      1,524 ms
                                               TTFA = 2,746 ms
```

Best fully-local config (combining fubarsream LLM results with pipeline data):

```
tiny.en/int8/cpu  +  qwen3.5-0.8b Q8_0 (llama-server)  +  kittentts/default
     312 ms       +          ~20,000 ms                 +      1,524 ms
                                               TTFA ≈ 21,836 ms
```

> The local LLM is the bottleneck on CPU-only hardware. For fully-local voice, the prefill cost (~2400 tokens ÷ 400 tok/s ≈ 6s) dominates TTFA.

---

## Multi-Machine Vision

Each machine gets a **runner label** that tags all its benchmark results. The cross-machine comparison (`benchmarks/published/comparison.md`) shows how each model performs on each machine — enabling hardware-class recommendations.

### Machines benchmarked so far

| Label | Hardware | CPU | Notes |
|---|---|---|---|
| fubarsream | i7-10610U | 15W, 4c/8t, ~40 GB/s BW | Primary dev machine; CPU-only |
| UOES-0002.local | — | — | Early comparison baseline |
| mudmachine | — | — | Early comparison baseline |
| win-dev | — | — | Windows dev machine |

### Adding a new machine

```bash
# 1. Start llama-server with your model
llama-server -m models/qwen3.5-0.8b-q8_0.gguf --port 8000 \
  --ctx-size 4096 --n-predict 512 --no-mmap -t <your-thread-count> \
  --reasoning-budget 0

# 2. Run the LLM+tools benchmark
uv run python scripts/benchmark_conversations.py \
  --provider local_server \
  --local-server-url "http://127.0.0.1:8000/v1" \
  --local-model-path "models/qwen3.5-0.8b-q8_0.gguf" \
  --model "qwen3.5-0.8b-q8_0" \
  --run-name "<machine>-qwen35-0.8b-q8_0" \
  --runner-label "<machine> / <cpu> / llama-server b8248"

# 3. Run the STT benchmark
uv run python scripts/run_stt_benchmark.py \
  --runner-label "<machine>"

# 4. Run the TTS benchmark
uv run python scripts/run_tts_benchmark.py \
  --runner-label "<machine>"
```

Results publish automatically to `benchmarks/published/`. The grand leaderboard and comparison doc regenerate on the next benchmark run.

---

## Current Status (fubarsream, 2026-03-09)

### LLM + Tools: Canonical result

| Model | Backend | Success | Tool Sel | Gen/s | Avg ms | Mem MB |
|---|---|---|---|---|---|---|
| **qwen3.5-0.8b Q8_0** | llama-server | **90%** | **100%** | 21 | 18,762 | 774 |
| qwen3.5-0.8b Q4_K_M | llama-server | 80% | 100% | 23 | 17,785 | 508 |
| qwen3.5-2b Q4_K_M | llama-server | 90% | 96% | 11 | 44,241 | 1,222 |
| qwen3.5-4b Q4_K_M | llama-server | 70% | 87% | 6 | 69,682 | 2,725 |

**Key finding:** Non-monotonic scaling — bigger models perform worse on this hardware class. The 0.8b Q8_0 matches or beats all larger local models while using 3–4× less memory.

**Ollama caveat:** Previous ollama-based results (20-30% success for 2b) were backend overhead artifacts, not model capability. llama-server results are the authoritative baseline.

### Remote Models (OpenRouter, any machine)

From `benchmarks/published/grand_leaderboard.md` — run these via the proxy network from any machine:

| Model | Success | Avg ms | Tool Sel |
|---|---|---|---|
| gemini-2.5-flash-lite | **100%** | 910 | 100% |
| gemini-2.5-pro | **100%** | 4,900 | 100% |
| gpt-4o-mini | 90% | 1,880 | 96% |
| claude-sonnet-4-6 | 90% | 3,026 | 100% |

---

## Decision Policy

See `benchmarks/decision_strategy.md` for hardware-specific decisions:
- Gen/s floor for voice (~4 tok/s minimum for interactive use)
- When to retire a model from the matrix
- Local vs remote trade-offs

See `benchmarks/LESSONS_LEARNED.md` for accumulated observations from all runs:
- Tool format quirks per model (Mistral `[TOOL_CALLS]` format, etc.)
- Backend reliability issues
- Prompt engineering findings

---

## Files Reference

| File | What it tracks |
|---|---|
| `published/latest/leaderboard.md` | Most recent LLM+tools run — check this first |
| `published/grand_leaderboard.md` | Best-ever per model across all runs and machines |
| `published/stt_leaderboard.md` | STT accuracy and speed per config |
| `published/tts_leaderboard.md` | TTS synthesis speed and quality |
| `published/pipeline_leaderboard.md` | TTFA compositions (STT + LLM + TTS) |
| `published/comparison.md` | Cross-machine: same model on different hardware |
| `published/runs/<name>/` | Per-run archived results |
| `decision_strategy.md` | Hardware-specific model retirement decisions |
| `LESSONS_LEARNED.md` | Accumulated debugging and tuning findings |
| `model_matrix.example.json` | Active model set for benchmark runs |
| `evaluation_values.json` | Rubric weights and scoring parameters |
