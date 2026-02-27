# Benchmark Leaderboard

- Generated: 2026-02-27T15:15:10-0500
- Runs: 8
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
| openrouter | https://openrouter.ai/api/v1/models | 100.8 | 95.8 | 184.2 | 200 |
| ollama-local | http://localhost:11434/api/tags | 21.1 | 19.9 | 36.7 | 200 |
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
| qwen3-8b-intent-no-reminder-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 100.00% | 13753.5 | 4051.2 | 0.00% | 27.3 | 9392 |
| qwen3-1.7b-llm-full-tools-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 18576.6 | 1296.9 | 0.00% | 21.0 | 9775 |
| ministral-3b-full-tools | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 95.45% | 100.00% | 0.00% | 1573.5 | 0.5 | 0.00% | 1480.0 | 58217 |
| qwen3-8b-intent-full-tools-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 2190.8 | 4395.4 | 4.55% | 179.9 | 9852 |
| ministral-3b-simple-lists | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1142.0 | 2.5 | 0.00% | 1132.9 | 32344 |
| ollama-llama3.2-3b-full-tools | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2023.0 | 0.4 | 0.00% | 186.7 | 9442 |
| qwen3-1.7b-llm-noise-removed-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 18569.2 | 1477.8 | 0.00% | 21.6 | 10036 |
| ollama-llama3.2-3b-core-only | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 50.00% | 100.00% | 100.00% | 1347.9 | 0.3 | 4.00% | 217.5 | 7330 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3-1.7b-llm-full-tools-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 18576.6 | 1296.9 | 0.00% | 21.0 | 9775 |
| qwen3-8b-intent-no-reminder-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 100.00% | 13753.5 | 4051.2 | 0.00% | 27.3 | 9392 |
| ministral-3b-full-tools | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 95.45% | 100.00% | 0.00% | 1573.5 | 0.5 | 0.00% | 1480.0 | 58217 |
| ministral-3b-simple-lists | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1142.0 | 2.5 | 0.00% | 1132.9 | 32344 |
| qwen3-8b-intent-full-tools-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 2190.8 | 4395.4 | 4.55% | 179.9 | 9852 |
| ollama-llama3.2-3b-core-only | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 50.00% | 100.00% | 100.00% | 1347.9 | 0.3 | 4.00% | 217.5 | 7330 |
| ollama-llama3.2-3b-full-tools | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2023.0 | 0.4 | 0.00% | 186.7 | 9442 |
| qwen3-1.7b-llm-noise-removed-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 18569.2 | 1477.8 | 0.00% | 21.6 | 10036 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ministral-3b-simple-lists | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1142.0 | 2.5 | 0.00% | 1132.9 | 32344 | 67.498 |
| ollama-llama3.2-3b-full-tools | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2023.0 | 0.4 | 0.00% | 186.7 | 9442 | 58.907 |
| ministral-3b-full-tools | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 95.45% | 100.00% | 0.00% | 1573.5 | 0.5 | 0.00% | 1480.0 | 58217 | 58.609 |
| ollama-llama3.2-3b-core-only | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 50.00% | 100.00% | 100.00% | 1347.9 | 0.3 | 4.00% | 217.5 | 7330 | 54.003 |
| qwen3-8b-intent-full-tools-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 2190.8 | 4395.4 | 4.55% | 179.9 | 9852 | 53.282 |
| qwen3-8b-intent-no-reminder-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 100.00% | 13753.5 | 4051.2 | 0.00% | 27.3 | 9392 | 39.496 |
| qwen3-1.7b-llm-full-tools-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 18576.6 | 1296.9 | 0.00% | 21.0 | 9775 | 37.784 |
| qwen3-1.7b-llm-noise-removed-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 18569.2 | 1477.8 | 0.00% | 21.6 | 10036 | 25.285 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ministral-3b-simple-lists | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1142.0 | 2.5 | 0.00% | 1132.9 | 32344 | 67.503 |
| ministral-3b-full-tools | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 95.45% | 100.00% | 0.00% | 1573.5 | 0.5 | 0.00% | 1480.0 | 58217 | 58.610 |

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3-8b-intent-no-reminder-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 100.00% | 13753.5 | 4051.2 | 0.00% | 27.3 | 9392 |
| qwen3-1.7b-llm-full-tools-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 18576.6 | 1296.9 | 0.00% | 21.0 | 9775 |
| ministral-3b-full-tools | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 95.45% | 100.00% | 0.00% | 1573.5 | 0.5 | 0.00% | 1480.0 | 58217 |
| ministral-3b-simple-lists | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1142.0 | 2.5 | 0.00% | 1132.9 | 32344 |
| qwen3-8b-intent-full-tools-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 2190.8 | 4395.4 | 4.55% | 179.9 | 9852 |
| ollama-llama3.2-3b-core-only | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 50.00% | 100.00% | 100.00% | 1347.9 | 0.3 | 4.00% | 217.5 | 7330 |
| ollama-llama3.2-3b-full-tools | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2023.0 | 0.4 | 0.00% | 186.7 | 9442 |
| qwen3-1.7b-llm-noise-removed-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 18569.2 | 1477.8 | 0.00% | 21.6 | 10036 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 6 | 7972.1 | 1347.9 | ollama-llama3.2-3b-core-only |
| Remote | 2 | 1357.7 | 1142.0 | ministral-3b-simple-lists |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ministral-3b-simple-lists | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1142.0 | 2.5 | 0.00% | 1132.9 | 32344 | 67.498 |
| ollama-llama3.2-3b-full-tools | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2023.0 | 0.4 | 0.00% | 186.7 | 9442 | 58.907 |
| ministral-3b-full-tools | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 95.45% | 100.00% | 0.00% | 1573.5 | 0.5 | 0.00% | 1480.0 | 58217 | 58.609 |
| ollama-llama3.2-3b-core-only | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 50.00% | 100.00% | 100.00% | 1347.9 | 0.3 | 4.00% | 217.5 | 7330 | 54.003 |
| qwen3-8b-intent-no-reminder-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 70.00% | 86.36% | 100.00% | 100.00% | 13753.5 | 4051.2 | 0.00% | 27.3 | 9392 | 39.496 |
| qwen3-1.7b-llm-full-tools-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 18576.6 | 1296.9 | 0.00% | 21.0 | 9775 | 37.784 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

No matched LLM/Intent profile pairs found. Add profiles with the same model + context and `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` (LLM) and `1` (Intent).

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local | 1 | qwen3-8b-intent-full-tools-ctx4096 | qwen/qwen3-8b | 0.0 | 60.00% | 53.282 |
| local | 2 | qwen3-8b-intent-no-reminder-ctx4096 | qwen/qwen3-8b | 0.0 | 70.00% | 39.496 |
| local | 3 | qwen3-1.7b-llm-full-tools-ctx2048 | qwen/qwen3-1.7b | 0.0 | 70.00% | 37.784 |
| local_server | 1 | ollama-llama3.2-3b-full-tools | llama3.2:3b | 0.3 | 50.00% | 58.907 |
| local_server | 2 | ollama-llama3.2-3b-core-only | llama3.2:3b | 0.3 | 50.00% | 54.003 |
| openrouter | 1 | ministral-3b-simple-lists | mistralai/ministral-3b-2512 | 0.0 | 60.00% | 67.498 |
| openrouter | 2 | ministral-3b-full-tools | mistralai/ministral-3b-2512 | 0.0 | 60.00% | 58.609 |

## Recommendations

- Best overall quality: `qwen3-8b-intent-no-reminder-ctx4096` (qwen/qwen3-8b)
- Best low-memory option: `qwen3-1.7b-llm-full-tools-ctx2048` (1296.9 MB peak)
- Best throughput option: `qwen3-8b-intent-no-reminder-ctx4096` (27.3 tokens/sec)
- Best remote option (memory-agnostic): `ministral-3b-simple-lists` (mistralai/ministral-3b-2512, score=67.503)
