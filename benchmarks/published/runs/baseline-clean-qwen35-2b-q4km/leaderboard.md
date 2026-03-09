# Benchmark Leaderboard

- Generated: 2026-03-09T07:45:08-0500
- Runs: 1
- Scenarios: 10
- Rubric version: 2026.1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/home/ra/Projects/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `fubarsream / i7-10610U / Linux` (Linux 6.8.0-101-generic, x86_64, py 3.12.3, linux-native)
- Network: `unknown`


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 154.6 | 137.5 | 183.0 | 200 |
| ollama-local | http://127.0.0.1:11434/api/tags | 30.6 | 26.2 | 53.2 | 200 |
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
| local_server-qwen3.5:2b-q4_k_m | local_server | qwen3.5:2b-q4_k_m | LLM | 0.0 | 30.00% | 56.52% | 100.00% | 100.00% | 94760.5 | 3031.4 | 0.00% | 41.5 | 8.3 | 53915 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server-qwen3.5:2b-q4_k_m | local_server | qwen3.5:2b-q4_k_m | LLM | 0.0 | 30.00% | 56.52% | 100.00% | 100.00% | 94760.5 | 3031.4 | 0.00% | 41.5 | 8.3 | 53915 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server-qwen3.5:2b-q4_k_m | local_server | qwen3.5:2b-q4_k_m | LLM | 0.0 | 30.00% | 56.52% | 100.00% | 100.00% | 94760.5 | 3031.4 | 0.00% | 41.5 | 8.3 | 53915 | -140.447 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

No remote-provider runs found in this report.

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server-qwen3.5:2b-q4_k_m | local_server | qwen3.5:2b-q4_k_m | LLM | 0.0 | 30.00% | 56.52% | 100.00% | 100.00% | 94760.5 | 3031.4 | 0.00% | 41.5 | 8.3 | 53915 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 1 | 94760.5 | 94760.5 | local_server-qwen3.5:2b-q4_k_m |
| Remote | 0 | n/a | n/a | n/a |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server-qwen3.5:2b-q4_k_m | local_server | qwen3.5:2b-q4_k_m | LLM | 0.0 | 30.00% | 56.52% | 100.00% | 100.00% | 94760.5 | 3031.4 | 0.00% | 41.5 | 8.3 | 53915 | -140.447 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

No matched LLM/Intent profile pairs found. Add profiles with the same model + context and `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` (LLM) and `1` (Intent).

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local_server | 1 | local_server-qwen3.5:2b-q4_k_m | qwen3.5:2b-q4_k_m | 0.0 | 30.00% | -140.447 |

## Recommendations

- Best overall quality: `local_server-qwen3.5:2b-q4_k_m` (qwen3.5:2b-q4_k_m)
- Best low-memory option: `local_server-qwen3.5:2b-q4_k_m` (3031.4 MB peak)
- Best throughput option: `local_server-qwen3.5:2b-q4_k_m` (8.3 gen tok/s)
