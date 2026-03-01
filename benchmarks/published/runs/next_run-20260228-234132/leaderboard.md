# Benchmark Leaderboard

- Generated: 2026-03-01T00:40:56-0500
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
| openrouter | https://openrouter.ai/api/v1/models | 119.5 | 106.1 | 178.0 | 200 |
| ollama-local | http://172.19.95.193:11434/api/tags | 37.5 | 30.6 | 39.1 | 200 |
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
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 910.3 | 2.5 | 0.00% | 1380.7 | 31423 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4900.4 | 2.5 | 0.00% | 279.8 | 34276 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3026.3 | 8.0 | 0.00% | 998.1 | 75512 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2009.8 | 8.4 | 0.00% | 1521.4 | 76442 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 1128.4 | 2.5 | 0.00% | 2192.4 | 61848 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 49526.7 | 0.2 | 2.70% | 0.0 | 0 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 13634.6 | 0.2 | 7.27% | 0.0 | 0 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 40.00% | 54.55% | 100.00% | 0.00% | 18645.8 | 0.2 | 10.91% | 0.0 | 0 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1130.2 | 0.4 | 8.00% | 324.0 | 9156 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 30.00% | 50.00% | 100.00% | 0.00% | 26358.7 | 0.3 | 22.39% | 0.0 | 0 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 20.00% | 45.45% | 100.00% | 0.00% | 21285.6 | 0.2 | 17.24% | 0.0 | 0 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 910.3 | 2.5 | 0.00% | 1380.7 | 31423 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4900.4 | 2.5 | 0.00% | 279.8 | 34276 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3026.3 | 8.0 | 0.00% | 998.1 | 75512 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2009.8 | 8.4 | 0.00% | 1521.4 | 76442 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 49526.7 | 0.2 | 2.70% | 0.0 | 0 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 1128.4 | 2.5 | 0.00% | 2192.4 | 61848 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 13634.6 | 0.2 | 7.27% | 0.0 | 0 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 40.00% | 54.55% | 100.00% | 0.00% | 18645.8 | 0.2 | 10.91% | 0.0 | 0 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 30.00% | 50.00% | 100.00% | 0.00% | 26358.7 | 0.3 | 22.39% | 0.0 | 0 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1130.2 | 0.4 | 8.00% | 324.0 | 9156 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 20.00% | 45.45% | 100.00% | 0.00% | 21285.6 | 0.2 | 17.24% | 0.0 | 0 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 910.3 | 2.5 | 0.00% | 1380.7 | 31423 | 98.174 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3026.3 | 8.0 | 0.00% | 998.1 | 75512 | 90.432 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4900.4 | 2.5 | 0.00% | 279.8 | 34276 | 90.194 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 1128.4 | 2.5 | 0.00% | 2192.4 | 61848 | 78.905 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2009.8 | 8.4 | 0.00% | 1521.4 | 76442 | 78.812 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 13634.6 | 0.2 | 7.27% | 0.0 | 0 | 41.063 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1130.2 | 0.4 | 8.00% | 324.0 | 9156 | 36.185 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 40.00% | 54.55% | 100.00% | 0.00% | 18645.8 | 0.2 | 10.91% | 0.0 | 0 | 0.436 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 20.00% | 45.45% | 100.00% | 0.00% | 21285.6 | 0.2 | 17.24% | 0.0 | 0 | -14.930 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 30.00% | 50.00% | 100.00% | 0.00% | 26358.7 | 0.3 | 22.39% | 0.0 | 0 | -18.363 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 49526.7 | 0.2 | 2.70% | 0.0 | 0 | -31.155 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 910.3 | 2.5 | 0.00% | 1380.7 | 31423 | 98.179 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3026.3 | 8.0 | 0.00% | 998.1 | 75512 | 90.447 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4900.4 | 2.5 | 0.00% | 279.8 | 34276 | 90.199 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 1128.4 | 2.5 | 0.00% | 2192.4 | 61848 | 78.910 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2009.8 | 8.4 | 0.00% | 1521.4 | 76442 | 78.829 |

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 910.3 | 2.5 | 0.00% | 1380.7 | 31423 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4900.4 | 2.5 | 0.00% | 279.8 | 34276 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3026.3 | 8.0 | 0.00% | 998.1 | 75512 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2009.8 | 8.4 | 0.00% | 1521.4 | 76442 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 100.00% | 100.00% | 100.00% | 1128.4 | 2.5 | 0.00% | 2192.4 | 61848 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 49526.7 | 0.2 | 2.70% | 0.0 | 0 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 13634.6 | 0.2 | 7.27% | 0.0 | 0 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 40.00% | 54.55% | 100.00% | 0.00% | 18645.8 | 0.2 | 10.91% | 0.0 | 0 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1130.2 | 0.4 | 8.00% | 324.0 | 9156 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 30.00% | 50.00% | 100.00% | 0.00% | 26358.7 | 0.3 | 22.39% | 0.0 | 0 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 20.00% | 45.45% | 100.00% | 0.00% | 21285.6 | 0.2 | 17.24% | 0.0 | 0 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 6 | 19965.7 | 1130.2 | ollama-llama3.2-3b |
| Remote | 5 | 2009.8 | 910.3 | openrouter-gemini-2.5-flash-lite |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 910.3 | 2.5 | 0.00% | 1380.7 | 31423 | 98.174 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 13634.6 | 0.2 | 7.27% | 0.0 | 0 | 41.063 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 72.73% | 100.00% | 0.00% | 1130.2 | 0.4 | 8.00% | 324.0 | 9156 | 36.185 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 49526.7 | 0.2 | 2.70% | 0.0 | 0 | -31.155 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx2048 | 25.00% | 60.00% | +35.00% | 47.73% | 77.27% | +29.55% | -16.646 | 41.063 | +57.710 |

## Context Window Coherence Sweep

- Near-peak ratio: 0.95
- Dropoff ratio: 0.90

| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) | 2048, 4096 | 46.570 @ 2048 | 2.590 | 2048 | 4096 | 36.67% | 20426.3 | 0.2 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local | 1 | local-qwen3-1.7b-intent-ctx2048 | qwen/qwen3-1.7b | 0.0 | 60.00% | 41.063 |
| local | 2 | local-qwen3-1.7b-llm-ctx4096 | qwen/qwen3-1.7b | 0.0 | 40.00% | 0.436 |
| local | 3 | local-qwen3-1.7b-llm-t0.3-ctx2048 | qwen/qwen3-1.7b | 0.3 | 20.00% | -14.930 |
| local_server | 1 | ollama-llama3.2-3b | llama3.2:3b | 0.3 | 30.00% | 36.185 |
| openrouter | 1 | openrouter-gemini-2.5-flash-lite | google/gemini-2.5-flash-lite | 0.0 | 100.00% | 98.174 |
| openrouter | 2 | openrouter-claude-sonnet-4-6 | anthropic/claude-sonnet-4-6 | 0.0 | 90.00% | 90.432 |
| openrouter | 3 | openrouter-gemini-2.5-pro | google/gemini-2.5-pro | 0.0 | 100.00% | 90.194 |

## Recommendations

- Best overall quality: `openrouter-gemini-2.5-flash-lite` (google/gemini-2.5-flash-lite)
- Best low-memory option: `openrouter-gemini-2.5-flash-lite` (2.5 MB peak)
- Best throughput option: `openrouter-gemini-2.5-flash-lite` (1380.7 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-gemini-2.5-flash-lite` (google/gemini-2.5-flash-lite, score=98.179)
- Context recommendations (near-peak quality at lowest context):
  - `local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf)` -> `n_ctx=2048` (dropoff: 4096)
- Routing gap summary: intent minus llm avg success delta = +35.00%
- Routing gap summary: intent minus llm avg score delta = +57.710
