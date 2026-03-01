# Benchmark Leaderboard

- Generated: 2026-02-28T18:38:27-0500
- Runs: 11
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `D:\Projects\GitHub\talkbot\benchmark_results\latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `win-dev` (Windows 11, AMD64, py 3.12.12, win32+wsl2)
- Network: `unknown`


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 112.3 | 84.2 | 1114.6 | 200 |
| ollama-local | http://172.19.95.193:11434/api/tags | 31.1 | 29.9 | 31.7 | 200 |
## Rubric

| Metric | Weight |
|---|---:|
| argument_accuracy | 0.150 |
| context_success_rate | 0.050 |
| multistep_success_rate | 0.100 |
| recovery_success_rate | 0.100 |
| robustness_success_rate | 0.050 |
| task_success_rate | 0.350 |
| tool_selection_accuracy | 0.200 |

| Penalty | Multiplier |
|---|---:|
| latency_ms_multiplier | 0.002 |
| memory_mb_multiplier | 0.002 |
| model_error_rate_multiplier | 30.000 |
| tool_error_rate_multiplier | 20.000 |

## Quality Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3074.8 | 8.0 | 0.00% | 979.7 | 75305 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 918.0 | 2.5 | 0.00% | 1370.8 | 31460 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 4356.0 | 2.5 | 0.00% | 296.8 | 32321 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2024.7 | 8.0 | 0.00% | 1510.0 | 76429 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 736.0 | 2.5 | 0.00% | 3354.9 | 61732 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 30.00% | 100.00% | 100.00% | 0.00% | 8.1 | 0.1 | 0.00% | 0.0 | 0 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1117.8 | 0.4 | 6.90% | 248.2 | 6937 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 13.0 | 0.1 | 0.00% | 0.0 | 0 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 0.00% | 0.00% | 0.00% | 0.00% | 13.3 | 0.1 | 0.00% | 0.0 | 0 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 13.3 | 0.1 | 0.00% | 0.0 | 0 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 918.0 | 2.5 | 0.00% | 1370.8 | 31460 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3074.8 | 8.0 | 0.00% | 979.7 | 75305 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 4356.0 | 2.5 | 0.00% | 296.8 | 32321 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2024.7 | 8.0 | 0.00% | 1510.0 | 76429 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 736.0 | 2.5 | 0.00% | 3354.9 | 61732 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 30.00% | 100.00% | 100.00% | 0.00% | 8.1 | 0.1 | 0.00% | 0.0 | 0 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1117.8 | 0.4 | 6.90% | 248.2 | 6937 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 0.00% | 0.00% | 0.00% | 0.00% | 13.3 | 0.1 | 0.00% | 0.0 | 0 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 13.0 | 0.1 | 0.00% | 0.0 | 0 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 13.3 | 0.1 | 0.00% | 0.0 | 0 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 918.0 | 2.5 | 0.00% | 1370.8 | 31460 | 90.416 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3074.8 | 8.0 | 0.00% | 979.7 | 75305 | 90.335 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 736.0 | 2.5 | 0.00% | 3354.9 | 61732 | 79.690 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2024.7 | 8.0 | 0.00% | 1510.0 | 76429 | 78.784 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 4356.0 | 2.5 | 0.00% | 296.8 | 32321 | 75.950 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1117.8 | 0.4 | 6.90% | 248.2 | 6937 | 36.430 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 30.00% | 100.00% | 100.00% | 0.00% | 8.1 | 0.1 | 0.00% | 0.0 | 0 | 29.884 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 13.0 | 0.1 | 0.00% | 0.0 | 0 | -30.026 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 13.3 | 0.1 | 0.00% | 0.0 | 0 | -30.027 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 0.00% | 0.00% | 0.00% | 0.00% | 13.3 | 0.1 | 0.00% | 0.0 | 0 | -30.027 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 918.0 | 2.5 | 0.00% | 1370.8 | 31460 | 90.421 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3074.8 | 8.0 | 0.00% | 979.7 | 75305 | 90.350 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 736.0 | 2.5 | 0.00% | 3354.9 | 61732 | 79.695 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2024.7 | 8.0 | 0.00% | 1510.0 | 76429 | 78.800 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 4356.0 | 2.5 | 0.00% | 296.8 | 32321 | 75.955 |

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 918.0 | 2.5 | 0.00% | 1370.8 | 31460 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3074.8 | 8.0 | 0.00% | 979.7 | 75305 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2024.7 | 8.0 | 0.00% | 1510.0 | 76429 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 4356.0 | 2.5 | 0.00% | 296.8 | 32321 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 736.0 | 2.5 | 0.00% | 3354.9 | 61732 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1117.8 | 0.4 | 6.90% | 248.2 | 6937 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 30.00% | 100.00% | 100.00% | 0.00% | 8.1 | 0.1 | 0.00% | 0.0 | 0 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 13.0 | 0.1 | 0.00% | 0.0 | 0 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 0.00% | 0.00% | 0.00% | 0.00% | 13.3 | 0.1 | 0.00% | 0.0 | 0 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 13.3 | 0.1 | 0.00% | 0.0 | 0 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 5 | 13.3 | 8.1 | local-qwen3-1.7b-intent-ctx2048 |
| Remote | 5 | 2024.7 | 736.0 | openrouter-ministral-3b-2512 |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 918.0 | 2.5 | 0.00% | 1370.8 | 31460 | 90.416 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3074.8 | 8.0 | 0.00% | 979.7 | 75305 | 90.335 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 736.0 | 2.5 | 0.00% | 3354.9 | 61732 | 79.690 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 4356.0 | 2.5 | 0.00% | 296.8 | 32321 | 75.950 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1117.8 | 0.4 | 6.90% | 248.2 | 6937 | 36.430 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 30.00% | 100.00% | 100.00% | 0.00% | 8.1 | 0.1 | 0.00% | 0.0 | 0 | 29.884 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 13.0 | 0.1 | 0.00% | 0.0 | 0 | -30.026 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 0.00% | 0.00% | 0.00% | 0.00% | 13.3 | 0.1 | 0.00% | 0.0 | 0 | -30.027 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx2048 | 0.00% | 30.00% | +30.00% | 0.00% | 100.00% | +100.00% | -30.027 | 29.884 | +59.911 |

## Context Window Coherence Sweep

- Near-peak ratio: 0.95
- Dropoff ratio: 0.90

| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) | 2048, 4096 | 15.167 @ 2048 | -10.057 | 2048 | 4096 | 10.00% | 11.6 | 0.1 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local | 1 | local-qwen3-1.7b-intent-ctx2048 | qwen/qwen3-1.7b | 0.0 | 30.00% | 29.884 |
| local | 2 | local-qwen3-1.7b-llm-ctx4096 | qwen/qwen3-1.7b | 0.0 | 0.00% | -30.026 |
| local | 3 | local-qwen3-1.7b-llm-ctx2048 | qwen/qwen3-1.7b | 0.0 | 0.00% | -30.027 |
| local_server | 1 | ollama-llama3.2-3b | llama3.2:3b | 0.3 | 30.00% | 36.430 |
| openrouter | 1 | openrouter-gemini-2.5-flash-lite | google/gemini-2.5-flash-lite | 0.0 | 90.00% | 90.416 |
| openrouter | 2 | openrouter-claude-sonnet-4-6 | anthropic/claude-sonnet-4-6 | 0.0 | 90.00% | 90.335 |
| openrouter | 3 | openrouter-ministral-3b-2512 | mistralai/ministral-3b-2512 | 0.0 | 70.00% | 79.690 |

## Recommendations

- Best overall quality: `openrouter-claude-sonnet-4-6` (anthropic/claude-sonnet-4-6)
- Best low-memory option: `openrouter-gemini-2.5-flash-lite` (2.5 MB peak)
- Best throughput option: `openrouter-gemini-2.5-flash-lite` (1370.8 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-gemini-2.5-flash-lite` (google/gemini-2.5-flash-lite, score=90.421)
- Context recommendations (near-peak quality at lowest context):
  - `local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf)` -> `n_ctx=2048` (dropoff: 4096)
- Routing gap summary: intent minus llm avg success delta = +30.00%
- Routing gap summary: intent minus llm avg score delta = +59.911
