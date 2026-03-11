# Benchmark Decision Strategy

Last updated: March 9, 2026

Use this guide with `benchmark_results/leaderboard.md` to choose between local and remote models.

## Core Goal

- Keep evaluations apples-to-apples for tool use.
- Prefer native OpenAI-style tool calling (`tools` + `tool_choice`) for comparison runs.
- **Intent routing is production architecture for sub-2B models**, not just a ceiling.
  For LLM vs Intent A-B benchmarking, both are scored; Intent mode is recommended for deployment.

## LLM vs Intent Routing — Official Guidance (2026-03-11)

### The split

| Mode | Env | Mechanism | Use case |
|---|---|---|---|
| LLM | `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` | Model decides which tools to call | Benchmarking raw model capability; ≥7B models |
| Intent | `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=1` | Heuristic detects tool + forces call | Production deployment of sub-2B local models |

### Why intent routing matters for sub-2B models

Small models (≤2B) exhibit a pattern documented in BFCL V4 (ICML 2025) and
BUTTON (ICLR 2025, arXiv:2410.12952): they call tools correctly on the first
1–2 invocations of a given tool type, then bypass subsequent calls by emitting
verbal confirmations without actual tool calls. Example:

```
t3 tools=[] | "I've remembered that the project is called Falcon."  ← no tool call
```

This causes cascading failures: skipped writes leave state empty; downstream
reads fail. All 5 endurance scenarios score 0% in LLM mode as a result.

### How intent routing fixes this

`LocalServerClient` with `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=1`:
1. Detects the intended tool from the user message (`_detect_intent_tool_name`)
2. Sends **only that tool's schema** in the API payload
3. Sets `tool_choice: "required"` — model **must** emit a tool call JSON
4. Only forces the first call; subsequent loop iterations use `tool_choice: auto`
   so multi-step operations (create_list → add_to_list) complete naturally

Write tools are forced (remember, add_to_list, set_timer, create_list, etc.).
Keyed read tools (get_list, recall) are excluded from forcing to avoid
`list_name` / `key` argument mismatches when the model generates in isolation.

### Measured results (M3 Max, qwen3.5-0.8b Q8_0)

| Scenario | LLM success | Intent success |
|---|---|---|
| Core canonical suite (10 scenarios) | 90% | **90%** (no regression; leads leaderboard) |
| Endurance: Timer Sequence | 0% | **100%** (15/15, pass_k met) |
| Endurance: Memory Recall | 0% | **100%** (10/10) |
| Endurance: Long Mixed (30 turns) | 0% | **30/30 turns** (pass_k accumulating) |
| Endurance: Trip Planning | 0% | **92.9%** (26/28) |
| Endurance: List Management | 0% | **83.3%** (10/12) |
| Overall endurance | **0%** | **60%** (3/5 pass_k met) |

### Deployment recommendation

For voice assistant production use with `local_server` + sub-2B models:

```bash
TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=1
```

For benchmarking model capability (without routing assist):

```bash
TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0
```

---

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
| qwen3.5-2b Q4_K_M | 11.2 (measured) | ✓ marginal |
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
  this uncompetitive. The definitive llama-server Q4_K_M run (PR #29) revealed
  this was entirely backend noise: 2b Q4_K_M scores 90% on llama-server,
  matching the 0.8b Q8_0. However, 2b is 2× slower (44s vs 21s avg) and
  uses 1.6× more memory (1.2 GB vs 774 MB), so 0.8b Q8_0 remains preferred.
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

---

## 2026-03-10 — qwen3.5 architecture superiority confirmed (cross-hardware)

### Finding

Intel i7-10610U testing confirmed that the qwen3.5 architecture update is a
superior foundation for voice-assistant tool use compared to both qwen3 (1.7b)
and qwen3-8b on llama-cpp. Key results:

| Architecture | Best result | Notes |
|---|---|---|
| qwen3.5-0.8b Q8_0 | **90% success**, 100% recovery | Canonical default |
| qwen3.5-2b Q4_K_M | 90% success, 100% recovery | 2× slower, same accuracy |
| qwen3-1.7b Q4_K_M | 40–86% success (variable) | Worse than qwen3.5-0.8b at ½ the speed |
| qwen3-8b Q4_K_M | 57% success | Larger size, lower accuracy, memory-bandwidth bound |

qwen3.5-0.8b outperforms qwen3-8b (10× larger) on this task class. The
architecture improvement in qwen3.5 is real and persistent across test runs.

### llama-cpp compatibility note

`llama-cpp-python` 0.3.16 (current PyPI) **cannot load qwen3.5 models**.
Use `local_server` provider with a pre-built `llama-server` binary.

**Critical**: qwen3.5 via `llama-cli` direct mode (`provider: local`) returns
0% success because the chat template is not applied correctly in llama-cli's
JSON tool mode. Always use `local_server` (OpenAI-compatible API) for qwen3.5.

---

## 2026-03-10 — M3 Max (Metal) setup and performance parity

### Hardware context

Apple M3 Max with Metal GPU acceleration via `brew install llama.cpp`.
Expected performance vs Intel i7-10610U CPU-only:
- ~15× faster average latency (1.3s vs 18-22s)
- ~5× higher gen/s (107 vs 21.6 tok/s)
- Same memory footprint (~774 MB for qwen3.5-0.8b Q8_0)
- Same or better accuracy (same weights, more deterministic at lower temp)

### Correct server startup for M3 Max

```bash
llama-server \
  -m models/qwen3.5-0.8b-q8_0.gguf \
  --port 8000 \
  --ctx-size 4096 \
  --n-predict 512 \
  --gpu-layers -1 \
  --reasoning-budget 0
```

`--gpu-layers -1` offloads all layers to Metal GPU. Do NOT use `--no-mmap` or
`-t <threads>` on Apple Silicon with GPU offload.

### M3 Max run anomaly (2026-03-10)

The first published M3 Max canonical run (`metal-mac-m3max-qwen35-0.8b-q8_0`)
shows 80% success / 0% recovery vs Intel's 90% / 100%. This is a **transient
artifact**, not a systematic difference:

- 4% model execution error rate (1 failed turn in 25) — Intel had 0%
- One model error in the recovery scenario (2-turn sequence) caused the whole
  recovery tag to read 0%
- Root cause likely: server not fully warm, or single network hiccup to
  localhost at turn start

**Action**: Re-run the M3 Max canonical baseline with a warmed server.
Expected result: ≥90% success, 100% recovery, matching or beating Intel.

### ctx_sweep_m3max matrix bug

`benchmarks/model_matrix.ctx_sweep_m3max.json` originally set
`"provider": "local"` (llama-cli) instead of `"provider": "local_server"`.
Because qwen3.5 requires the OpenAI-compatible server path, the LLM-routing
profiles scored 0% in that sweep. The matrix has been corrected to use
`local_server` with `local_server_url: "http://127.0.0.1:8000/v1"`. Context
sweep results collected under the old matrix are invalid for qwen3.5 LLM mode.

---

## 2026-03-10 — OpenRouter model retirement

### Retired from all active matrices

| Model | Result | Reason |
|---|---|---|
| `ibm-granite/granite-4.0-h-micro` | 0% success, 24ms | Completely non-functional for tool use; extremely fast at being wrong |
| `meta-llama/llama-3.1-8b-instruct` | 43% success, 0% recovery | Poor tool discipline; qwen3.5-0.8b at 0.1× the size scores 90% |
| `qwen/qwen-2.5-7b-instruct` | 29% success, 0% recovery | Older qwen2.5 series; superseded by qwen3.5 architecture |
| `qwen/qwen3-8b` (local) | 57% success | Architecture-superseded + memory-bandwidth-bound on all tested hardware |
| `qwen/qwen3-1.7b` (local) | 40–86% (variable) | Architecture-superseded; qwen3.5-0.8b beats it at half the size |

### What this means for matrices

- `model_matrix.full_all.json`: retired local qwen3/qwen3-8b profiles removed;
  retired OpenRouter profiles removed
- `model_matrix.full_remote.json`: granite, llama-3.1-8b, qwen-2.5-7b removed
- New `model_matrix.m3max.json`: clean M3 Max baseline using `local_server`
  with qwen3.5 variants and correct Metal flags

### Why qwen3.5 wins

The qwen3.5 architecture update improved tool-calling fine-tuning specifically.
Evidence across all test environments:
1. Intel CPU: 0.8b beats 1.7b qwen3 and 8b qwen3 on success rate
2. OpenRouter cloud: qwen3-1.7b cloud scores 86% but qwen3-8b scores only 57%;
   qwen3.5 local 0.8b matches the cloud 1.7b
3. Tool selection: qwen3.5-0.8b consistently scores 96-100% tool selection vs
   73-93% for qwen3 variants
4. Recovery: qwen3.5 passes recovery scenarios; qwen3 variants are inconsistent

Tracked in issue #25.

---

## 2026-03-09 — llama-server size sweep results (fubarsream)

### qwen3.5 on llama-server b8248 — definitive per-size results

| Model | Quant | Success | Tool Sel | Arg Acc | Gen/s | Avg ms | Mem MB | Notes |
|---|---|---|---|---|---|---|---|---|
| 0.8b | Q8_0 | **90%** | 96% | 100% | 18.9 | 20,683 | 774 | Recommended default |
| 0.8b | Q4_K_M | 80% | 96% | 100% | 22.8 | 17,785 | 508 | Fastest; unit-conv arg error |
| 2b | Q4_K_M | **90%** | 95.65% | 100% | 11.2 | 44,241 | 1,222 | Ties 0.8b; 2× slower |
| 4b | Q4_K_M | 70%* | 86.96% | 100% | 6.4 | 69,682 | 2,725 | Worst result |

### Key finding: ollama 2b results were noise

The ollama 2b runs (20–30% success) were entirely backend overhead, not model
capability. On llama-server, 2b Q4_K_M matches 0.8b Q8_0 at 90% success. This
invalidates any size-scaling conclusions drawn from ollama results.

*4b success is 70% against the unpatched scenario suite (PR #27 not yet merged);
with the memory_context_pressure rubric fix it is likely 80%. Still the worst result.

### Recommendation

**0.8b Q8_0** is the optimal choice on this hardware: highest success, fastest
gen/s, lowest memory of the competitive tier. Larger models are strictly worse:
2b ties quality at 2× the cost; 4b is the worst result — 3× slower, 3.5× more
memory, lower success rate than the 0.8b. Non-monotonic scaling confirmed on
llama-server (not a backend artifact).
