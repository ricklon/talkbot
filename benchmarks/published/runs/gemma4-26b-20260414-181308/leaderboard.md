# Benchmark Leaderboard

- Generated: 2026-04-14T18:14:18+0000
- Runs: 1
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/app/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `arm-01` (Linux 6.12.61-v8, aarch64, py 3.12.13, linux-native)
- Network: `unknown`
- Runner notes: CHI@Edge Pi CM4, OpenRouter, gemma-4-26b-a4b-it test

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

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemma-4-26b-it | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2743.2 | 9.9 | 0.00% | 0.0 | 0.0 | 50059 |

## Low-Memory Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemma-4-26b-it | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2743.2 | 9.9 | 0.00% | 0.0 | 0.0 | 50059 |

## Balanced Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemma-4-26b-it | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2743.2 | 9.9 | 0.00% | 0.0 | 0.0 | 50059 | 94.494 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score (Remote) |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemma-4-26b-it | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2743.2 | 9.9 | 0.00% | 0.0 | 0.0 | 50059 | 94.514 |

## Efficiency Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemma-4-26b-it | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2743.2 | 9.9 | 0.00% | 0.0 | 0.0 | 50059 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 0 | n/a | n/a | n/a |
| Remote | 1 | 2743.2 | 2743.2 | openrouter-gemma-4-26b-it |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemma-4-26b-it | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2743.2 | 9.9 | 0.00% | 0.0 | 0.0 | 50059 | 94.494 |

## Prompt Impact

- Compares runs that share provider, model, context, routing mode, and temperature.
- Use this to isolate prompt effects from model/runtime effects.

No matched prompt comparison groups found. Run the same model/runtime slice with two or more prompt presets.

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

No matched LLM/Intent profile pairs found. Add profiles with the same model + context and `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` (LLM) and `1` (Intent).

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| openrouter | 1 | openrouter-gemma-4-26b-it | google/gemma-4-26b-a4b-it | 0.0 | 100.00% | 94.494 |

## Recommendations

- Best overall quality: `openrouter-gemma-4-26b-it` (google/gemma-4-26b-a4b-it)
- Best low-memory option: `openrouter-gemma-4-26b-it` (9.9 MB peak)
- Best throughput option: `openrouter-gemma-4-26b-it` (0.0 gen tok/s)
- Best remote option (memory-agnostic): `openrouter-gemma-4-26b-it` (google/gemma-4-26b-a4b-it, score=94.514)

## TTS Friction

- `Avg Friction`: mean count of TTS-hostile tokens per turn (lower is better).
- `Clean Rate`: fraction of turns with zero friction (higher is better).

| Run | Avg Friction | Clean Rate |
|---|---:|---:|
| openrouter-gemma-4-26b-it | 0.48 | 68.0% |
