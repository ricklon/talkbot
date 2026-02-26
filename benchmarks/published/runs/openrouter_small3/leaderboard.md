# Benchmark Leaderboard

- Generated: 2026-02-26T13:15:01-0500
- Runs: 18
- Scenarios: 7
- Rubric version: 2026.small-models.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/Users/rianders/Documents/GitHub/talkbot/benchmark_results/openrouter_small3`
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
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1208.6 | 1484.8 | 4.17% | 340.0 | 7397 |
| local-qwen3-1.7b-llm-ctx32768 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1275.3 | 2367.5 | 4.17% | 322.2 | 7397 |
| local-qwen3-1.7b-llm-ctx8192 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1282.2 | 2158.5 | 4.17% | 320.5 | 7397 |
| local-qwen3-1.7b-llm-ctx16384 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1299.2 | 2878.7 | 4.17% | 316.3 | 7397 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1430.2 | 1541.8 | 4.17% | 287.3 | 7397 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 1301.7 | 8.4 | 5.56% | 1656.6 | 38815 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 686.5 | 301.0 | 4.55% | 632.3 | 7813 |
| local-qwen3-1.7b-intent-ctx8192 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 728.7 | 301.0 | 4.55% | 595.7 | 7813 |
| local-qwen3-1.7b-intent-ctx16384 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 747.3 | 301.0 | 4.55% | 580.8 | 7813 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 775.2 | 301.0 | 4.55% | 559.9 | 7813 |
| local-qwen3-1.7b-intent-ctx32768 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 846.9 | 319.6 | 4.55% | 512.5 | 7813 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1640.8 | 301.0 | 6.25% | 242.8 | 7170 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1690.5 | 301.1 | 6.25% | 235.6 | 7170 |
| local-qwen3-8b-llm-ctx8192 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3302.2 | 4679.3 | 11.11% | 118.3 | 7033 |
| local-qwen3-8b-llm-ctx4096 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3368.5 | 4092.7 | 11.11% | 116.0 | 7033 |
| openrouter-llama-3.1-8b-instruct | openrouter | meta-llama/llama-3.1-8b-instruct | LLM | 42.86% | 86.67% | 80.00% | 0.00% | 7615.0 | 1.2 | 2.80% | 373.1 | 51138 |
| openrouter-qwen-2.5-7b-instruct | openrouter | qwen/qwen-2.5-7b-instruct | LLM | 28.57% | 86.67% | 100.00% | 0.00% | 2986.8 | 1.0 | 5.88% | 729.0 | 39191 |
| openrouter-granite-4.0-h-micro | openrouter | ibm-granite/granite-4.0-h-micro | LLM | 0.00% | 100.00% | 100.00% | 0.00% | 23.5 | 8.0 | 0.00% | 0.0 | 0 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1208.6 | 1484.8 | 4.17% | 340.0 | 7397 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1430.2 | 1541.8 | 4.17% | 287.3 | 7397 |
| local-qwen3-1.7b-llm-ctx8192 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1282.2 | 2158.5 | 4.17% | 320.5 | 7397 |
| local-qwen3-1.7b-llm-ctx32768 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1275.3 | 2367.5 | 4.17% | 322.2 | 7397 |
| local-qwen3-1.7b-llm-ctx16384 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1299.2 | 2878.7 | 4.17% | 316.3 | 7397 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 1301.7 | 8.4 | 5.56% | 1656.6 | 38815 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 775.2 | 301.0 | 4.55% | 559.9 | 7813 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 686.5 | 301.0 | 4.55% | 632.3 | 7813 |
| local-qwen3-1.7b-intent-ctx8192 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 728.7 | 301.0 | 4.55% | 595.7 | 7813 |
| local-qwen3-1.7b-intent-ctx16384 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 747.3 | 301.0 | 4.55% | 580.8 | 7813 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1640.8 | 301.0 | 6.25% | 242.8 | 7170 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1690.5 | 301.1 | 6.25% | 235.6 | 7170 |
| local-qwen3-1.7b-intent-ctx32768 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 846.9 | 319.6 | 4.55% | 512.5 | 7813 |
| local-qwen3-8b-llm-ctx4096 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3368.5 | 4092.7 | 11.11% | 116.0 | 7033 |
| local-qwen3-8b-llm-ctx8192 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3302.2 | 4679.3 | 11.11% | 118.3 | 7033 |
| openrouter-llama-3.1-8b-instruct | openrouter | meta-llama/llama-3.1-8b-instruct | LLM | 42.86% | 86.67% | 80.00% | 0.00% | 7615.0 | 1.2 | 2.80% | 373.1 | 51138 |
| openrouter-qwen-2.5-7b-instruct | openrouter | qwen/qwen-2.5-7b-instruct | LLM | 28.57% | 86.67% | 100.00% | 0.00% | 2986.8 | 1.0 | 5.88% | 729.0 | 39191 |
| openrouter-granite-4.0-h-micro | openrouter | ibm-granite/granite-4.0-h-micro | LLM | 0.00% | 100.00% | 100.00% | 0.00% | 23.5 | 8.0 | 0.00% | 0.0 | 0 |

## Balanced Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1208.6 | 1484.8 | 4.17% | 340.0 | 7397 | 77.444 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1430.2 | 1541.8 | 4.17% | 287.3 | 7397 | 76.887 |
| local-qwen3-1.7b-llm-ctx8192 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1282.2 | 2158.5 | 4.17% | 320.5 | 7397 | 75.950 |
| local-qwen3-1.7b-llm-ctx32768 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1275.3 | 2367.5 | 4.17% | 322.2 | 7397 | 75.545 |
| local-qwen3-1.7b-llm-ctx16384 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1299.2 | 2878.7 | 4.17% | 316.3 | 7397 | 74.475 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 1301.7 | 8.4 | 5.56% | 1656.6 | 38815 | 71.269 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1640.8 | 301.0 | 6.25% | 242.8 | 7170 | 67.201 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1690.5 | 301.1 | 6.25% | 235.6 | 7170 | 67.102 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 686.5 | 301.0 | 4.55% | 632.3 | 7813 | 59.450 |
| local-qwen3-1.7b-intent-ctx8192 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 728.7 | 301.0 | 4.55% | 595.7 | 7813 | 59.366 |
| local-qwen3-1.7b-intent-ctx16384 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 747.3 | 301.0 | 4.55% | 580.8 | 7813 | 59.328 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 775.2 | 301.0 | 4.55% | 559.9 | 7813 | 59.273 |
| local-qwen3-1.7b-intent-ctx32768 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 846.9 | 319.6 | 4.55% | 512.5 | 7813 | 59.092 |
| local-qwen3-8b-llm-ctx4096 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3368.5 | 4092.7 | 11.11% | 116.0 | 7033 | 48.854 |
| local-qwen3-8b-llm-ctx8192 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3302.2 | 4679.3 | 11.11% | 118.3 | 7033 | 47.814 |
| openrouter-qwen-2.5-7b-instruct | openrouter | qwen/qwen-2.5-7b-instruct | LLM | 28.57% | 86.67% | 100.00% | 0.00% | 2986.8 | 1.0 | 5.88% | 729.0 | 39191 | 45.182 |
| openrouter-llama-3.1-8b-instruct | openrouter | meta-llama/llama-3.1-8b-instruct | LLM | 42.86% | 86.67% | 80.00% | 0.00% | 7615.0 | 1.2 | 2.80% | 373.1 | 51138 | 28.543 |
| openrouter-granite-4.0-h-micro | openrouter | ibm-granite/granite-4.0-h-micro | LLM | 0.00% | 100.00% | 100.00% | 0.00% | 23.5 | 8.0 | 0.00% | 0.0 | 0 | 4.937 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 1301.7 | 8.4 | 5.56% | 1656.6 | 38815 | 71.286 |
| openrouter-qwen-2.5-7b-instruct | openrouter | qwen/qwen-2.5-7b-instruct | LLM | 28.57% | 86.67% | 100.00% | 0.00% | 2986.8 | 1.0 | 5.88% | 729.0 | 39191 | 45.184 |
| openrouter-llama-3.1-8b-instruct | openrouter | meta-llama/llama-3.1-8b-instruct | LLM | 42.86% | 86.67% | 80.00% | 0.00% | 7615.0 | 1.2 | 2.80% | 373.1 | 51138 | 28.545 |
| openrouter-granite-4.0-h-micro | openrouter | ibm-granite/granite-4.0-h-micro | LLM | 0.00% | 100.00% | 100.00% | 0.00% | 23.5 | 8.0 | 0.00% | 0.0 | 0 | 4.953 |

## Efficiency Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1208.6 | 1484.8 | 4.17% | 340.0 | 7397 |
| local-qwen3-1.7b-llm-ctx32768 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1275.3 | 2367.5 | 4.17% | 322.2 | 7397 |
| local-qwen3-1.7b-llm-ctx8192 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1282.2 | 2158.5 | 4.17% | 320.5 | 7397 |
| local-qwen3-1.7b-llm-ctx16384 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1299.2 | 2878.7 | 4.17% | 316.3 | 7397 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1430.2 | 1541.8 | 4.17% | 287.3 | 7397 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 1301.7 | 8.4 | 5.56% | 1656.6 | 38815 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 686.5 | 301.0 | 4.55% | 632.3 | 7813 |
| local-qwen3-1.7b-intent-ctx8192 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 728.7 | 301.0 | 4.55% | 595.7 | 7813 |
| local-qwen3-1.7b-intent-ctx16384 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 747.3 | 301.0 | 4.55% | 580.8 | 7813 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 775.2 | 301.0 | 4.55% | 559.9 | 7813 |
| local-qwen3-1.7b-intent-ctx32768 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 846.9 | 319.6 | 4.55% | 512.5 | 7813 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1640.8 | 301.0 | 6.25% | 242.8 | 7170 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1690.5 | 301.1 | 6.25% | 235.6 | 7170 |
| local-qwen3-8b-llm-ctx8192 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3302.2 | 4679.3 | 11.11% | 118.3 | 7033 |
| local-qwen3-8b-llm-ctx4096 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3368.5 | 4092.7 | 11.11% | 116.0 | 7033 |
| openrouter-llama-3.1-8b-instruct | openrouter | meta-llama/llama-3.1-8b-instruct | LLM | 42.86% | 86.67% | 80.00% | 0.00% | 7615.0 | 1.2 | 2.80% | 373.1 | 51138 |
| openrouter-qwen-2.5-7b-instruct | openrouter | qwen/qwen-2.5-7b-instruct | LLM | 28.57% | 86.67% | 100.00% | 0.00% | 2986.8 | 1.0 | 5.88% | 729.0 | 39191 |
| openrouter-granite-4.0-h-micro | openrouter | ibm-granite/granite-4.0-h-micro | LLM | 0.00% | 100.00% | 100.00% | 0.00% | 23.5 | 8.0 | 0.00% | 0.0 | 0 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 14 | 1278.8 | 686.5 | local-qwen3-1.7b-intent-ctx4096 |
| Remote | 4 | 2144.3 | 23.5 | openrouter-granite-4.0-h-micro |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1208.6 | 1484.8 | 4.17% | 340.0 | 7397 | 77.444 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 1301.7 | 8.4 | 5.56% | 1656.6 | 38815 | 71.269 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 686.5 | 301.0 | 4.55% | 632.3 | 7813 | 59.450 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 775.2 | 301.0 | 4.55% | 559.9 | 7813 | 59.273 |
| openrouter-qwen-2.5-7b-instruct | openrouter | qwen/qwen-2.5-7b-instruct | LLM | 28.57% | 86.67% | 100.00% | 0.00% | 2986.8 | 1.0 | 5.88% | 729.0 | 39191 | 45.182 |
| openrouter-llama-3.1-8b-instruct | openrouter | meta-llama/llama-3.1-8b-instruct | LLM | 42.86% | 86.67% | 80.00% | 0.00% | 7615.0 | 1.2 | 2.80% | 373.1 | 51138 | 28.543 |
| openrouter-granite-4.0-h-micro | openrouter | ibm-granite/granite-4.0-h-micro | LLM | 0.00% | 100.00% | 100.00% | 0.00% | 23.5 | 8.0 | 0.00% | 0.0 | 0 | 4.937 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf) @ctx8192 | 57.14% | 71.43% | +14.29% | 80.00% | 86.67% | +6.67% | 47.814 | 67.102 | +19.288 |
| local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf) @ctx4096 | 57.14% | 71.43% | +14.29% | 80.00% | 86.67% | +6.67% | 48.854 | 67.201 | +18.347 |
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx16384 | 85.71% | 71.43% | -14.28% | 93.33% | 86.67% | -6.66% | 74.475 | 59.328 | -15.147 |
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx32768 | 85.71% | 71.43% | -14.28% | 93.33% | 86.67% | -6.66% | 75.545 | 59.092 | -16.453 |
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx8192 | 85.71% | 71.43% | -14.28% | 93.33% | 86.67% | -6.66% | 75.950 | 59.366 | -16.584 |
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx4096 | 85.71% | 71.43% | -14.28% | 93.33% | 86.67% | -6.66% | 76.887 | 59.450 | -17.437 |
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx2048 | 85.71% | 71.43% | -14.28% | 93.33% | 86.67% | -6.66% | 77.444 | 59.273 | -18.171 |

## Context Window Coherence Sweep

- Near-peak ratio: 0.95
- Dropoff ratio: 0.90

| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) | 2048, 4096, 8192, 16384, 32768 | 73.000 @ 2048 | 68.359 | 2048 | none | 78.57% | 991.9 | 892.9 |
| local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf) | 4096, 8192 | 69.167 @ 4096 | 58.027 | 4096 | none | 64.29% | 2504.7 | 2196.9 |

## Recommendations

- Best overall quality: `local-qwen3-1.7b-llm-ctx2048` (qwen/qwen3-1.7b)
- Best low-memory option: `local-qwen3-1.7b-llm-ctx2048` (1484.8 MB peak)
- Best throughput option: `local-qwen3-1.7b-llm-ctx2048` (340.0 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512, score=71.286)
- Context recommendations (near-peak quality at lowest context):
  - `local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf)` -> `n_ctx=2048` (dropoff: not observed)
  - `local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf)` -> `n_ctx=4096` (dropoff: not observed)
- Routing gap summary: intent minus llm avg success delta = -6.12%
- Routing gap summary: intent minus llm avg score delta = -6.594
