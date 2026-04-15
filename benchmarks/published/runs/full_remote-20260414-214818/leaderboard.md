# Benchmark Leaderboard

- Generated: 2026-04-14T21:55:41+0000
- Runs: 10
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/home/cc/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `coachable-robots-control` (Linux 5.15.0-174-generic, x86_64, py 3.12.13, linux-native)
- Network: `openrouter`
- Runner notes: Control node, gemma-4-26b added to matrix


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 155.4 | 144.8 | 192.3 | 200 |
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
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 804.4 | 3.6 | 0.00% | 0.0 | 0.0 | 59922 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2094.7 | 2.3 | 0.00% | 0.0 | 0.0 | 37322 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5564.3 | 2.3 | 0.00% | 0.0 | 0.0 | 34403 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 897.4 | 2.3 | 0.00% | 0.0 | 0.0 | 31504 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1384.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31601 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 0.00% | 1013.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31431 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 50.00% | 100.00% | 100.00% | 0.00% | 2394.1 | 2.3 | 0.00% | 0.0 | 0.0 | 81982 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 34.1 | 2.3 | 0.00% | 0.0 | 0.0 | 0 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 35.5 | 2.3 | 0.00% | 0.0 | 0.0 | 0 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 123.1 | 7.0 | 0.00% | 0.0 | 0.0 | 0 |

## Low-Memory Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2094.7 | 2.3 | 0.00% | 0.0 | 0.0 | 37322 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5564.3 | 2.3 | 0.00% | 0.0 | 0.0 | 34403 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 804.4 | 3.6 | 0.00% | 0.0 | 0.0 | 59922 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1384.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31601 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 897.4 | 2.3 | 0.00% | 0.0 | 0.0 | 31504 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 0.00% | 1013.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31431 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 50.00% | 100.00% | 100.00% | 0.00% | 2394.1 | 2.3 | 0.00% | 0.0 | 0.0 | 81982 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 35.5 | 2.3 | 0.00% | 0.0 | 0.0 | 0 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 34.1 | 2.3 | 0.00% | 0.0 | 0.0 | 0 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 123.1 | 7.0 | 0.00% | 0.0 | 0.0 | 0 |

## Balanced Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 804.4 | 3.6 | 0.00% | 0.0 | 0.0 | 59922 | 98.384 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2094.7 | 2.3 | 0.00% | 0.0 | 0.0 | 37322 | 95.806 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 897.4 | 2.3 | 0.00% | 0.0 | 0.0 | 31504 | 93.791 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1384.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31601 | 92.817 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5564.3 | 2.3 | 0.00% | 0.0 | 0.0 | 34403 | 88.867 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 0.00% | 1013.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31431 | 60.182 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 50.00% | 100.00% | 100.00% | 0.00% | 2394.1 | 2.3 | 0.00% | 0.0 | 0.0 | 81982 | 41.174 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 34.1 | 2.3 | 0.00% | 0.0 | 0.0 | 0 | -30.073 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 35.5 | 2.3 | 0.00% | 0.0 | 0.0 | 0 | -30.076 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 123.1 | 7.0 | 0.00% | 0.0 | 0.0 | 0 | -30.260 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score (Remote) |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 804.4 | 3.6 | 0.00% | 0.0 | 0.0 | 59922 | 98.391 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2094.7 | 2.3 | 0.00% | 0.0 | 0.0 | 37322 | 95.811 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 897.4 | 2.3 | 0.00% | 0.0 | 0.0 | 31504 | 93.795 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1384.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31601 | 92.821 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5564.3 | 2.3 | 0.00% | 0.0 | 0.0 | 34403 | 88.871 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 0.00% | 1013.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31431 | 60.187 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 50.00% | 100.00% | 100.00% | 0.00% | 2394.1 | 2.3 | 0.00% | 0.0 | 0.0 | 81982 | 41.179 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 34.1 | 2.3 | 0.00% | 0.0 | 0.0 | 0 | -30.068 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 35.5 | 2.3 | 0.00% | 0.0 | 0.0 | 0 | -30.071 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 123.1 | 7.0 | 0.00% | 0.0 | 0.0 | 0 | -30.246 |

## Efficiency Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 804.4 | 3.6 | 0.00% | 0.0 | 0.0 | 59922 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2094.7 | 2.3 | 0.00% | 0.0 | 0.0 | 37322 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 5564.3 | 2.3 | 0.00% | 0.0 | 0.0 | 34403 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 897.4 | 2.3 | 0.00% | 0.0 | 0.0 | 31504 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1384.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31601 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 0.00% | 1013.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31431 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 50.00% | 100.00% | 100.00% | 0.00% | 2394.1 | 2.3 | 0.00% | 0.0 | 0.0 | 81982 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 34.1 | 2.3 | 0.00% | 0.0 | 0.0 | 0 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 35.5 | 2.3 | 0.00% | 0.0 | 0.0 | 0 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 123.1 | 7.0 | 0.00% | 0.0 | 0.0 | 0 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 0 | n/a | n/a | n/a |
| Remote | 10 | 955.3 | 34.1 | openrouter-minimax-01 |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 804.4 | 3.6 | 0.00% | 0.0 | 0.0 | 59922 | 98.384 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2094.7 | 2.3 | 0.00% | 0.0 | 0.0 | 37322 | 95.806 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 897.4 | 2.3 | 0.00% | 0.0 | 0.0 | 31504 | 93.791 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1384.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31601 | 92.817 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 60.00% | 72.73% | 100.00% | 0.00% | 1013.1 | 2.3 | 0.00% | 0.0 | 0.0 | 31431 | 60.182 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 50.00% | 100.00% | 100.00% | 0.00% | 2394.1 | 2.3 | 0.00% | 0.0 | 0.0 | 81982 | 41.174 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 34.1 | 2.3 | 0.00% | 0.0 | 0.0 | 0 | -30.073 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 35.5 | 2.3 | 0.00% | 0.0 | 0.0 | 0 | -30.076 |

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
| openrouter | 1 | openrouter-ministral-3b-2512 | mistralai/ministral-3b-2512 | 0.0 | 100.00% | 98.384 |
| openrouter | 2 | openrouter-gpt-4o-mini | openai/gpt-4o-mini | 0.0 | 100.00% | 95.806 |
| openrouter | 3 | openrouter-gemini-2.5-flash-lite | google/gemini-2.5-flash-lite | 0.0 | 90.00% | 93.791 |

## Recommendations

- Best overall quality: `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512)
- Best low-memory option: `openrouter-gpt-4o-mini` (2.3 MB peak)
- Best throughput option: `openrouter-ministral-3b-2512` (0.0 gen tok/s)
- Best remote option (memory-agnostic): `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512, score=98.391)

## TTS Friction

- `Avg Friction`: mean count of TTS-hostile tokens per turn (lower is better).
- `Clean Rate`: fraction of turns with zero friction (higher is better).

| Run | Avg Friction | Clean Rate |
|---|---:|---:|
| openrouter-ministral-3b-2512 | 1.12 | 28.0% |
| openrouter-gpt-4o-mini | 0.32 | 80.0% |
| openrouter-gemini-2.5-pro | 0.16 | 84.0% |
| openrouter-gemini-2.5-flash-lite | 0.24 | 84.0% |
| openrouter-gemini-2.5-flash | 0.16 | 88.0% |
| openrouter-gemini-2.0-flash-lite-001 | 0.12 | 88.0% |
| openrouter-deepseek-chat | 0.28 | 84.0% |
| openrouter-minimax-01 | 0.00 | 100.0% |
| openrouter-gemma-4-26b | 0.00 | 100.0% |
| openrouter-claude-3.5-sonnet | 0.00 | 100.0% |

## LLM Judge Scores

- Scores are 1–5 (higher is better). Evaluated by the judge model on a sample of turns.
- `Correctness`: did the response correctly address the request?
- `Spoken Quality`: is the response phrased naturally for voice output?

| Run | Correctness | Spoken Quality | Judge Calls |
|---|---:|---:|---:|
| openrouter-ministral-3b-2512 | 4.08 | 3.68 | 25 |
| openrouter-gpt-4o-mini | 4.68 | 4.64 | 25 |
| openrouter-gemini-2.5-pro | 4.52 | 4.96 | 25 |
| openrouter-gemini-2.5-flash-lite | 4.52 | 4.84 | 25 |
| openrouter-gemini-2.5-flash | 4.84 | 4.96 | 25 |
| openrouter-gemini-2.0-flash-lite-001 | 4.20 | 5.00 | 20 |
| openrouter-deepseek-chat | 4.71 | 4.86 | 7 |
| openrouter-minimax-01 | n/a | n/a | 0 |
| openrouter-gemma-4-26b | n/a | n/a | 0 |
| openrouter-claude-3.5-sonnet | n/a | n/a | 0 |
