# Benchmark Leaderboard

- Generated: 2026-02-26T17:36:26-0500
- Runs: 2
- Scenarios: 7
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/Users/rianders/Documents/GitHub/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`

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

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 28.57% | 80.00% | 100.00% | 0.00% | 1149.6 | 12.7 | 6.67% | 1702.1 | 35222 |
| openrouter-mistral-small-3.1-24b | openrouter | mistralai/mistral-small-3.1-24b-instruct:free | LLM | 0.00% | 0.00% | 0.00% | 0.00% | 68.8 | 2.5 | 0.00% | 0.0 | 0 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 28.57% | 80.00% | 100.00% | 0.00% | 1149.6 | 12.7 | 6.67% | 1702.1 | 35222 |
| openrouter-mistral-small-3.1-24b | openrouter | mistralai/mistral-small-3.1-24b-instruct:free | LLM | 0.00% | 0.00% | 0.00% | 0.00% | 68.8 | 2.5 | 0.00% | 0.0 | 0 |

## Balanced Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 28.57% | 80.00% | 100.00% | 0.00% | 1149.6 | 12.7 | 6.67% | 1702.1 | 35222 | 37.340 |
| openrouter-mistral-small-3.1-24b | openrouter | mistralai/mistral-small-3.1-24b-instruct:free | LLM | 0.00% | 0.00% | 0.00% | 0.00% | 68.8 | 2.5 | 0.00% | 0.0 | 0 | -30.143 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 28.57% | 80.00% | 100.00% | 0.00% | 1149.6 | 12.7 | 6.67% | 1702.1 | 35222 | 37.366 |
| openrouter-mistral-small-3.1-24b | openrouter | mistralai/mistral-small-3.1-24b-instruct:free | LLM | 0.00% | 0.00% | 0.00% | 0.00% | 68.8 | 2.5 | 0.00% | 0.0 | 0 | -30.138 |

## Efficiency Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 28.57% | 80.00% | 100.00% | 0.00% | 1149.6 | 12.7 | 6.67% | 1702.1 | 35222 |
| openrouter-mistral-small-3.1-24b | openrouter | mistralai/mistral-small-3.1-24b-instruct:free | LLM | 0.00% | 0.00% | 0.00% | 0.00% | 68.8 | 2.5 | 0.00% | 0.0 | 0 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 0 | n/a | n/a | n/a |
| Remote | 2 | 609.2 | 68.8 | openrouter-mistral-small-3.1-24b |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 28.57% | 80.00% | 100.00% | 0.00% | 1149.6 | 12.7 | 6.67% | 1702.1 | 35222 | 37.340 |
| openrouter-mistral-small-3.1-24b | openrouter | mistralai/mistral-small-3.1-24b-instruct:free | LLM | 0.00% | 0.00% | 0.00% | 0.00% | 68.8 | 2.5 | 0.00% | 0.0 | 0 | -30.143 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

No matched LLM/Intent profile pairs found. Add profiles with the same model + context and `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` (LLM) and `1` (Intent).

## Recommendations

- Best overall quality: `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512)
- Best low-memory option: `openrouter-ministral-3b-2512` (12.7 MB peak)
- Best throughput option: `openrouter-ministral-3b-2512` (1702.1 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512, score=37.366)
