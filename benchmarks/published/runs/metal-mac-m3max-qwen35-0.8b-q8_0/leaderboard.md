# Benchmark Leaderboard

- Generated: 2026-03-10T08:36:14-0400
- Runs: 1
- Scenarios: 10
- Rubric version: 2026.1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/Users/rianders/Documents/GitHub/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `mac-m3max-metal` (Darwin 25.3.0, arm64, py 3.12.8, macos-native)
- Network: `wifi (Wi-Fi)`


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 146.6 | 132.1 | 190.0 | 200 |
| ollama-local | http://localhost:11434/api/tags | 23.7 | 20.7 | 46.5 | 200 |
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

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server-qwen3.5-0.8b-q8_0 | local_server | qwen3.5-0.8b-q8_0 | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 0.00% | 1305.2 | 775.9 | 0.00% | 16747.0 | 107.2 | 59445 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server-qwen3.5-0.8b-q8_0 | local_server | qwen3.5-0.8b-q8_0 | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 0.00% | 1305.2 | 775.9 | 0.00% | 16747.0 | 107.2 | 59445 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server-qwen3.5-0.8b-q8_0 | local_server | qwen3.5-0.8b-q8_0 | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 0.00% | 1305.2 | 775.9 | 0.00% | 16747.0 | 107.2 | 59445 | 72.638 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

No remote-provider runs found in this report.

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server-qwen3.5-0.8b-q8_0 | local_server | qwen3.5-0.8b-q8_0 | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 0.00% | 1305.2 | 775.9 | 0.00% | 16747.0 | 107.2 | 59445 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 1 | 1305.2 | 1305.2 | local_server-qwen3.5-0.8b-q8_0 |
| Remote | 0 | n/a | n/a | n/a |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server-qwen3.5-0.8b-q8_0 | local_server | qwen3.5-0.8b-q8_0 | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 0.00% | 1305.2 | 775.9 | 0.00% | 16747.0 | 107.2 | 59445 | 72.638 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

No matched LLM/Intent profile pairs found. Add profiles with the same model + context and `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` (LLM) and `1` (Intent).

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local_server | 1 | local_server-qwen3.5-0.8b-q8_0 | qwen3.5-0.8b-q8_0 | 0.0 | 80.00% | 72.638 |

## Recommendations

- Best overall quality: `local_server-qwen3.5-0.8b-q8_0` (qwen3.5-0.8b-q8_0)
- Best low-memory option: `local_server-qwen3.5-0.8b-q8_0` (775.9 MB peak)
- Best throughput option: `local_server-qwen3.5-0.8b-q8_0` (107.2 gen tok/s)
