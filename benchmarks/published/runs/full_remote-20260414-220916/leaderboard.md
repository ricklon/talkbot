# Benchmark Leaderboard

- Generated: 2026-04-14T22:20:55+0000
- Runs: 8
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/home/cc/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `coachable-robots-control` (Linux 5.15.0-174-generic, x86_64, py 3.12.13, linux-native)
- Network: `openrouter`
- Runner notes: Control node, clean matrix: gemini-2.0 and minimax removed, gemma-4-26b and claude-sonnet-4.5 added


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 114.4 | 103.7 | 192.3 | 200 |
| ollama-local | http://127.0.0.1:11434/api/tags | n/a | n/a | n/a | err: all samples failed |
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
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 895.1 | 3.6 | 0.00% | 0.0 | 0.0 | 59966 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2093.8 | 2.3 | 0.00% | 0.0 | 0.0 | 50079 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2186.4 | 2.3 | 0.00% | 0.0 | 0.0 | 37334 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4454.7 | 2.3 | 0.00% | 0.0 | 0.0 | 82679 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5850.0 | 2.3 | 0.00% | 0.0 | 0.0 | 34300 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1355.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31609 |
| openrouter-claude-sonnet-4-5 | openrouter | anthropic/claude-sonnet-4.5 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 4685.9 | 2.3 | 0.00% | 0.0 | 0.0 | 74855 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 1025.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31596 |

## Low-Memory Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2093.8 | 2.3 | 0.00% | 0.0 | 0.0 | 50079 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2186.4 | 2.3 | 0.00% | 0.0 | 0.0 | 37334 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4454.7 | 2.3 | 0.00% | 0.0 | 0.0 | 82679 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5850.0 | 2.3 | 0.00% | 0.0 | 0.0 | 34300 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 895.1 | 3.6 | 0.00% | 0.0 | 0.0 | 59966 |
| openrouter-claude-sonnet-4-5 | openrouter | anthropic/claude-sonnet-4.5 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 4685.9 | 2.3 | 0.00% | 0.0 | 0.0 | 74855 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1355.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31609 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 1025.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31596 |

## Balanced Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 895.1 | 3.6 | 0.00% | 0.0 | 0.0 | 59966 | 98.203 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2093.8 | 2.3 | 0.00% | 0.0 | 0.0 | 50079 | 95.808 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2186.4 | 2.3 | 0.00% | 0.0 | 0.0 | 37334 | 95.623 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1355.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31609 | 92.875 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4454.7 | 2.3 | 0.00% | 0.0 | 0.0 | 82679 | 91.086 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 1025.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31596 | 89.127 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5850.0 | 2.3 | 0.00% | 0.0 | 0.0 | 34300 | 88.295 |
| openrouter-claude-sonnet-4-5 | openrouter | anthropic/claude-sonnet-4.5 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 4685.9 | 2.3 | 0.00% | 0.0 | 0.0 | 74855 | 82.881 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score (Remote) |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 895.1 | 3.6 | 0.00% | 0.0 | 0.0 | 59966 | 98.210 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2093.8 | 2.3 | 0.00% | 0.0 | 0.0 | 50079 | 95.812 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2186.4 | 2.3 | 0.00% | 0.0 | 0.0 | 37334 | 95.627 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1355.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31609 | 92.880 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4454.7 | 2.3 | 0.00% | 0.0 | 0.0 | 82679 | 91.091 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 1025.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31596 | 89.132 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5850.0 | 2.3 | 0.00% | 0.0 | 0.0 | 34300 | 88.300 |
| openrouter-claude-sonnet-4-5 | openrouter | anthropic/claude-sonnet-4.5 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 4685.9 | 2.3 | 0.00% | 0.0 | 0.0 | 74855 | 82.885 |

## Efficiency Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 895.1 | 3.6 | 0.00% | 0.0 | 0.0 | 59966 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2093.8 | 2.3 | 0.00% | 0.0 | 0.0 | 50079 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2186.4 | 2.3 | 0.00% | 0.0 | 0.0 | 37334 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4454.7 | 2.3 | 0.00% | 0.0 | 0.0 | 82679 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5850.0 | 2.3 | 0.00% | 0.0 | 0.0 | 34300 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1355.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31609 |
| openrouter-claude-sonnet-4-5 | openrouter | anthropic/claude-sonnet-4.5 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 4685.9 | 2.3 | 0.00% | 0.0 | 0.0 | 74855 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 1025.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31596 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 0 | n/a | n/a | n/a |
| Remote | 8 | 2140.1 | 895.1 | openrouter-ministral-3b-2512 |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 895.1 | 3.6 | 0.00% | 0.0 | 0.0 | 59966 | 98.203 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2093.8 | 2.3 | 0.00% | 0.0 | 0.0 | 50079 | 95.808 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1355.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31609 | 92.875 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 1025.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31596 | 89.127 |

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
| openrouter | 1 | openrouter-ministral-3b-2512 | mistralai/ministral-3b-2512 | 0.0 | 100.00% | 98.203 |
| openrouter | 2 | openrouter-gemma-4-26b | google/gemma-4-26b-a4b-it | 0.0 | 100.00% | 95.808 |
| openrouter | 3 | openrouter-gpt-4o-mini | openai/gpt-4o-mini | 0.0 | 100.00% | 95.623 |

## Recommendations

- Best overall quality: `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512)
- Best low-memory option: `openrouter-gemma-4-26b` (2.3 MB peak)
- Best throughput option: `openrouter-ministral-3b-2512` (0.0 gen tok/s)
- Best remote option (memory-agnostic): `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512, score=98.210)

## TTS Friction

- `Avg Friction`: mean count of TTS-hostile tokens per turn (lower is better).
- `Clean Rate`: fraction of turns with zero friction (higher is better).

| Run | Avg Friction | Clean Rate |
|---|---:|---:|
| openrouter-ministral-3b-2512 | 1.04 | 36.0% |
| openrouter-gemma-4-26b | 0.36 | 76.0% |
| openrouter-gpt-4o-mini | 0.32 | 80.0% |
| openrouter-deepseek-chat | 0.68 | 68.0% |
| openrouter-gemini-2.5-pro | 0.20 | 84.0% |
| openrouter-gemini-2.5-flash | 0.16 | 88.0% |
| openrouter-claude-sonnet-4-5 | 0.72 | 68.0% |
| openrouter-gemini-2.5-flash-lite | 0.28 | 80.0% |

## LLM Judge Scores

- Scores are 1–5 (higher is better). Evaluated by the judge model on a sample of turns.
- `Correctness`: did the response correctly address the request?
- `Spoken Quality`: is the response phrased naturally for voice output?

| Run | Correctness | Spoken Quality | Judge Calls |
|---|---:|---:|---:|
| openrouter-ministral-3b-2512 | 4.24 | 3.68 | 25 |
| openrouter-gemma-4-26b | 4.80 | 4.64 | 25 |
| openrouter-gpt-4o-mini | 4.68 | 4.64 | 25 |
| openrouter-deepseek-chat | 4.56 | 4.52 | 25 |
| openrouter-gemini-2.5-pro | 4.48 | 5.00 | 25 |
| openrouter-gemini-2.5-flash | 4.72 | 4.96 | 25 |
| openrouter-claude-sonnet-4-5 | 4.64 | 4.00 | 25 |
| openrouter-gemini-2.5-flash-lite | 4.44 | 4.68 | 25 |
