# Benchmark Leaderboard

- Generated: 2026-02-27T15:13:50-0500
- Runs: 6
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
| openrouter | https://openrouter.ai/api/v1/models | 132.3 | 95.5 | 153.0 | 200 |
| ollama-local | http://localhost:11434/api/tags | 21.1 | 19.8 | 36.7 | 200 |
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
| ministral-3b-schema-standard | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 100.00% | 707.9 | 0.4 | 0.00% | 2085.9 | 36913 |
| ministral-3b-schema-examples | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1095.1 | 0.4 | 0.00% | 1286.1 | 35208 |
| ministral-3b-schema-minimal | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 3568.5 | 2.5 | 0.00% | 345.8 | 30851 |
| qwen3-1.7b-schema-examples-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 15830.7 | 301.0 | 0.00% | 22.9 | 9064 |
| qwen3-1.7b-schema-minimal-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 16290.1 | 1477.0 | 0.00% | 22.3 | 9064 |
| qwen3-1.7b-schema-standard-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 18607.9 | 1296.2 | 0.00% | 19.5 | 9064 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ministral-3b-schema-standard | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 100.00% | 707.9 | 0.4 | 0.00% | 2085.9 | 36913 |
| ministral-3b-schema-examples | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1095.1 | 0.4 | 0.00% | 1286.1 | 35208 |
| ministral-3b-schema-minimal | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 3568.5 | 2.5 | 0.00% | 345.8 | 30851 |
| qwen3-1.7b-schema-examples-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 15830.7 | 301.0 | 0.00% | 22.9 | 9064 |
| qwen3-1.7b-schema-standard-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 18607.9 | 1296.2 | 0.00% | 19.5 | 9064 |
| qwen3-1.7b-schema-minimal-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 16290.1 | 1477.0 | 0.00% | 22.3 | 9064 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ministral-3b-schema-standard | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 100.00% | 707.9 | 0.4 | 0.00% | 2085.9 | 36913 | 83.840 |
| ministral-3b-schema-examples | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1095.1 | 0.4 | 0.00% | 1286.1 | 35208 | 70.324 |
| ministral-3b-schema-minimal | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 3568.5 | 2.5 | 0.00% | 345.8 | 30851 | 64.173 |
| qwen3-1.7b-schema-examples-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 15830.7 | 301.0 | 0.00% | 22.9 | 9064 | 36.616 |
| qwen3-1.7b-schema-minimal-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 16290.1 | 1477.0 | 0.00% | 22.3 | 9064 | 33.345 |
| qwen3-1.7b-schema-standard-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 18607.9 | 1296.2 | 0.00% | 19.5 | 9064 | 29.071 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ministral-3b-schema-standard | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 100.00% | 707.9 | 0.4 | 0.00% | 2085.9 | 36913 | 83.841 |
| ministral-3b-schema-examples | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1095.1 | 0.4 | 0.00% | 1286.1 | 35208 | 70.325 |
| ministral-3b-schema-minimal | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 3568.5 | 2.5 | 0.00% | 345.8 | 30851 | 64.178 |

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ministral-3b-schema-standard | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 100.00% | 707.9 | 0.4 | 0.00% | 2085.9 | 36913 |
| ministral-3b-schema-examples | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1095.1 | 0.4 | 0.00% | 1286.1 | 35208 |
| ministral-3b-schema-minimal | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 3568.5 | 2.5 | 0.00% | 345.8 | 30851 |
| qwen3-1.7b-schema-examples-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 15830.7 | 301.0 | 0.00% | 22.9 | 9064 |
| qwen3-1.7b-schema-minimal-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 16290.1 | 1477.0 | 0.00% | 22.3 | 9064 |
| qwen3-1.7b-schema-standard-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 100.00% | 18607.9 | 1296.2 | 0.00% | 19.5 | 9064 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 3 | 16290.1 | 15830.7 | qwen3-1.7b-schema-examples-ctx2048 |
| Remote | 3 | 1095.1 | 707.9 | ministral-3b-schema-standard |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ministral-3b-schema-standard | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 100.00% | 707.9 | 0.4 | 0.00% | 2085.9 | 36913 | 83.840 |
| ministral-3b-schema-examples | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1095.1 | 0.4 | 0.00% | 1286.1 | 35208 | 70.324 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

No matched LLM/Intent profile pairs found. Add profiles with the same model + context and `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` (LLM) and `1` (Intent).

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local | 1 | qwen3-1.7b-schema-examples-ctx2048 | qwen/qwen3-1.7b | 0.0 | 60.00% | 36.616 |
| local | 2 | qwen3-1.7b-schema-minimal-ctx2048 | qwen/qwen3-1.7b | 0.0 | 60.00% | 33.345 |
| local | 3 | qwen3-1.7b-schema-standard-ctx2048 | qwen/qwen3-1.7b | 0.0 | 60.00% | 29.071 |
| openrouter | 1 | ministral-3b-schema-standard | mistralai/ministral-3b-2512 | 0.0 | 70.00% | 83.840 |
| openrouter | 2 | ministral-3b-schema-examples | mistralai/ministral-3b-2512 | 0.0 | 60.00% | 70.324 |
| openrouter | 3 | ministral-3b-schema-minimal | mistralai/ministral-3b-2512 | 0.0 | 60.00% | 64.173 |

## Recommendations

- Best overall quality: `ministral-3b-schema-standard` (mistralai/ministral-3b-2512)
- Best low-memory option: `ministral-3b-schema-standard` (0.4 MB peak)
- Best throughput option: `ministral-3b-schema-standard` (2085.9 tokens/sec)
- Best remote option (memory-agnostic): `ministral-3b-schema-standard` (mistralai/ministral-3b-2512, score=83.841)
