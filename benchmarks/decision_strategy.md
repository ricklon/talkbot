# Benchmark Decision Strategy

Last updated: March 9, 2026

Use this guide with `benchmark_results/leaderboard.md` to choose between local and remote models.

## Core Goal

- Keep evaluations apples-to-apples for tool use.
- Prefer native OpenAI-style tool calling (`tools` + `tool_choice`) for comparison runs.
- Use intent routing only as a control ceiling, not as primary capability scoring.

## Key Metrics

- `task_success_rate`: end-to-end scenario success.
- `tool_selection_accuracy`: did it choose the correct tool.
- `argument_accuracy`: did it call tools with valid arguments.
- `avg_turn_latency_ms`: perceived responsiveness.
- `tool_call_error_rate`: tool execution reliability.
- `model_execution_error_rate`: provider/model transport failures.

Latency is a primary decision metric:
- Lower `avg_turn_latency_ms` improves UX immediately.
- Compare `Local` vs `Remote` with the leaderboard section:
  - `Latency Snapshot (Local vs Remote)`.

## Local vs Remote Decision Rules

1. Choose `Local` when:
- You need privacy/offline behavior.
- You can afford local RAM/CPU usage.
- You want stable, deterministic behavior without provider routing drift.

2. Choose `Remote` when:
- You want to avoid local memory pressure.
- You need easy model switching.
- You can tolerate provider/network variability.

3. For remote ranking:
- Use the leaderboard’s `Remote Rank (No Memory Penalty)`.
- Do not compare local memory numbers against remote process RSS.

## Standard Tool-Calling Policy

To force native tool-calling compatibility in OpenRouter benchmarks:

```bash
export TALKBOT_OPENROUTER_TOOL_TRANSPORT=native
export TALKBOT_OPENROUTER_TOOL_PREFLIGHT=1
```

This fails fast for models/routes that do not advertise native `tools` + `tool_choice`.

## Practical Workflow

1. Run matrix benchmark.
2. Check `Quality Rank` and `Remote Rank (No Memory Penalty)`.
3. Check `Latency Snapshot (Local vs Remote)`.
4. Validate failure modes in per-scenario assertions.
5. Pick one primary local and one primary remote model.
6. Re-run after prompt/tool updates and compare deltas.

---

## 2026-03-09 — Hardware-constrained model retirement (fubarsream / i7-10610U)

### Context

After establishing llama-server b8248 as the primary benchmark backend (PR #24),
we audited the active model matrix against the hardware constraints of the
primary test machine: i7-10610U, 15W TDP, CPU-only, ~40 GB/s memory bandwidth.

### Decision rule: gen/s floor for voice chat

Gen/s below ~4 tok/s makes voice responses feel unacceptably slow (>25s for a
modest 100-token reply before TTS can start). This sets a practical ceiling on
model size for interactive use on this hardware:

| Model | Est. Gen/s | Viable for voice? |
|---|---|---|
| qwen3.5-0.8b Q8_0 | 18.9 | ✓ |
| qwen3.5-0.8b Q4_K_M | 22.8 | ✓ |
| qwen3.5-2b Q4_K_M | ~8–10 (est.) | ✓ marginal |
| qwen3.5-4b Q4_K_M | 3.7 | ✗ borderline |
| qwen3-8b Q4_K_M | ~2–3 (est.) | ✗ |

### Retired

- **qwen3-1.7b** (qwen3 family): 40% success, beaten on quality and size by
  qwen3.5-0.8b. llama-cpp-python 0.3.16 cannot load qwen3.5, so there is no
  upgrade path on this provider. Retired permanently from this machine's matrix.
- **qwen3-8b**: 4.7 GB weights (~7–8 GB RSS with KV cache). Estimated ~2–3 tok/s
  gen on this hardware (memory-bandwidth-bound; ~4× the weight bytes of 0.8b).
  Not viable for interactive voice use. Quality ceiling role passed to
  qwen3.5-4b Q4_K_M (5.5 GB, 3.7 tok/s, 70% success).
- **qwen3.5-2b Q8_0 via ollama**: 20% success — worst result in the entire
  matrix. ollama overhead plus Q8_0 weight size (~1 GB per decode step) make
  this uncompetitive. Replaced by a single llama-server Q4_K_M run for a fair
  verdict on the 2b size class.
- **ollama as primary backend**: superseded by llama-server b8248, which
  delivers 3× lower latency, 2.5× lower memory, and +9pp tool selection
  accuracy on identical weights. Ollama results remain in published history
  as a comparison baseline but are no longer the default for new runs.

### Forward model set (fubarsream)

| Model | Backend | Quant | Role |
|---|---|---|---|
| qwen3.5-0.8b | llama-server | Q8_0 | canonical default |
| qwen3.5-0.8b | llama-server | Q4_K_M | speed/memory variant |
| qwen3.5-2b | llama-server | Q4_K_M | size scaling (one definitive run) |
| qwen3.5-4b | llama-server | Q4_K_M | quality ceiling |

Tracked in issue #25.
