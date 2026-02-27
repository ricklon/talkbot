# Benchmark Leaderboard

- Generated: 2026-02-27T12:32:25-0500
- Runs: 11
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/Users/rianders/Documents/GitHub/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `UOES-0002.local` (Darwin 25.3.0, arm64, py 3.12.8)
- Network: `wifi (Wi-Fi)`


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 167.9 | 143.1 | 200.3 | 200 |
| ollama-local | http://localhost:11434/api/tags | 20.8 | 19.6 | 34.8 | 200 |
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
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 1142.1 | 2.5 | 0.00% | 1704.3 | 48662 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3286.8 | 8.0 | 0.00% | 742.6 | 61021 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2630.7 | 8.0 | 0.00% | 924.4 | 60795 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 547.0 | 301.0 | 0.00% | 739.4 | 10110 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 909.3 | 1478.6 | 0.00% | 430.8 | 9794 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 916.1 | 301.0 | 0.00% | 428.5 | 9814 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 939.5 | 1546.2 | 0.00% | 417.0 | 9794 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 100.00% | 100.00% | 972.8 | 2.5 | 0.00% | 783.0 | 19043 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 1687.2 | 3798.3 | 4.55% | 233.6 | 9852 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 50.00% | 95.45% | 100.00% | 0.00% | 7593.9 | 2.5 | 0.00% | 151.2 | 28712 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 77.27% | 100.00% | 0.00% | 1780.1 | 0.4 | 4.00% | 162.3 | 7222 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 1142.1 | 2.5 | 0.00% | 1704.3 | 48662 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3286.8 | 8.0 | 0.00% | 742.6 | 61021 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2630.7 | 8.0 | 0.00% | 924.4 | 60795 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 547.0 | 301.0 | 0.00% | 739.4 | 10110 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 916.1 | 301.0 | 0.00% | 428.5 | 9814 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 909.3 | 1478.6 | 0.00% | 430.8 | 9794 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 939.5 | 1546.2 | 0.00% | 417.0 | 9794 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 100.00% | 100.00% | 972.8 | 2.5 | 0.00% | 783.0 | 19043 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 1687.2 | 3798.3 | 4.55% | 233.6 | 9852 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 50.00% | 95.45% | 100.00% | 0.00% | 7593.9 | 2.5 | 0.00% | 151.2 | 28712 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 77.27% | 100.00% | 0.00% | 1780.1 | 0.4 | 4.00% | 162.3 | 7222 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 1142.1 | 2.5 | 0.00% | 1704.3 | 48662 | 81.468 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 100.00% | 100.00% | 972.8 | 2.5 | 0.00% | 783.0 | 19043 | 81.321 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 547.0 | 301.0 | 0.00% | 739.4 | 10110 | 80.243 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2630.7 | 8.0 | 0.00% | 924.4 | 60795 | 77.572 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3286.8 | 8.0 | 0.00% | 742.6 | 61021 | 77.167 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 916.1 | 301.0 | 0.00% | 428.5 | 9814 | 75.097 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 909.3 | 1478.6 | 0.00% | 430.8 | 9794 | 72.755 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 939.5 | 1546.2 | 0.00% | 417.0 | 9794 | 72.560 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 1687.2 | 3798.3 | 4.55% | 233.6 | 9852 | 55.483 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 50.00% | 95.45% | 100.00% | 0.00% | 7593.9 | 2.5 | 0.00% | 151.2 | 28712 | 43.064 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 77.27% | 100.00% | 0.00% | 1780.1 | 0.4 | 4.00% | 162.3 | 7222 | 36.593 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 1142.1 | 2.5 | 0.00% | 1704.3 | 48662 | 81.473 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 100.00% | 100.00% | 972.8 | 2.5 | 0.00% | 783.0 | 19043 | 81.326 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2630.7 | 8.0 | 0.00% | 924.4 | 60795 | 77.588 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3286.8 | 8.0 | 0.00% | 742.6 | 61021 | 77.183 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 50.00% | 95.45% | 100.00% | 0.00% | 7593.9 | 2.5 | 0.00% | 151.2 | 28712 | 43.069 |

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 1142.1 | 2.5 | 0.00% | 1704.3 | 48662 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2630.7 | 8.0 | 0.00% | 924.4 | 60795 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3286.8 | 8.0 | 0.00% | 742.6 | 61021 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 547.0 | 301.0 | 0.00% | 739.4 | 10110 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 909.3 | 1478.6 | 0.00% | 430.8 | 9794 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 916.1 | 301.0 | 0.00% | 428.5 | 9814 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 939.5 | 1546.2 | 0.00% | 417.0 | 9794 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 100.00% | 100.00% | 972.8 | 2.5 | 0.00% | 783.0 | 19043 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 1687.2 | 3798.3 | 4.55% | 233.6 | 9852 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 50.00% | 95.45% | 100.00% | 0.00% | 7593.9 | 2.5 | 0.00% | 151.2 | 28712 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 77.27% | 100.00% | 0.00% | 1780.1 | 0.4 | 4.00% | 162.3 | 7222 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 6 | 927.8 | 547.0 | local-qwen3-1.7b-intent-ctx2048 |
| Remote | 5 | 2630.7 | 972.8 | openrouter-gemini-2.5-flash-lite |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 1142.1 | 2.5 | 0.00% | 1704.3 | 48662 | 81.468 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 100.00% | 100.00% | 972.8 | 2.5 | 0.00% | 783.0 | 19043 | 81.321 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 547.0 | 301.0 | 0.00% | 739.4 | 10110 | 80.243 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 916.1 | 301.0 | 0.00% | 428.5 | 9814 | 75.097 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 30.00% | 77.27% | 100.00% | 0.00% | 1780.1 | 0.4 | 4.00% | 162.3 | 7222 | 36.593 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx2048 | 70.00% | 80.00% | +10.00% | 81.82% | 86.36% | +4.54% | 73.926 | 80.243 | +6.317 |

## Context Window Coherence Sweep

- Near-peak ratio: 0.95
- Dropoff ratio: 0.90

| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) | 2048, 4096 | 79.000 @ 2048 | 76.032 | 2048 | none | 73.33% | 790.8 | 693.5 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local | 1 | local-qwen3-1.7b-intent-ctx2048 | qwen/qwen3-1.7b | 0.0 | 80.00% | 80.243 |
| local | 2 | local-qwen3-1.7b-llm-t0.3-ctx2048 | qwen/qwen3-1.7b | 0.3 | 70.00% | 75.097 |
| local | 3 | local-qwen3-1.7b-llm-ctx2048 | qwen/qwen3-1.7b | 0.0 | 70.00% | 72.755 |
| local_server | 1 | ollama-llama3.2-3b | llama3.2:3b | 0.3 | 30.00% | 36.593 |
| openrouter | 1 | openrouter-ministral-3b-2512 | mistralai/ministral-3b-2512 | 0.0 | 80.00% | 81.468 |
| openrouter | 2 | openrouter-gemini-2.5-flash-lite | google/gemini-2.5-flash-lite | 0.0 | 60.00% | 81.321 |
| openrouter | 3 | openrouter-claude-haiku-4-5 | anthropic/claude-haiku-4-5 | 0.0 | 80.00% | 77.572 |

## Recommendations

- Best overall quality: `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512)
- Best low-memory option: `openrouter-ministral-3b-2512` (2.5 MB peak)
- Best throughput option: `openrouter-ministral-3b-2512` (1704.3 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512, score=81.473)
- Context recommendations (near-peak quality at lowest context):
  - `local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf)` -> `n_ctx=2048` (dropoff: not observed)
- Routing gap summary: intent minus llm avg success delta = +10.00%
- Routing gap summary: intent minus llm avg score delta = +6.317
