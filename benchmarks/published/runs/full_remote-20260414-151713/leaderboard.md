# Benchmark Leaderboard

- Generated: 2026-04-14T15:26:18+0000
- Runs: 9
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/app/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `arm-01` (Linux 6.12.61-v8, aarch64, py 3.12.13, linux-native)
- Network: `unknown`
- Runner notes: CHI@Edge Pi CM4, OpenRouter inference, arm-talk-20260414b

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
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2174.2 | 2.3 | 0.00% | 0.0 | 0.0 | 37349 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4959.0 | 2.3 | 0.00% | 0.0 | 0.0 | 82922 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 6210.5 | 2.3 | 0.00% | 0.0 | 0.0 | 35082 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1032.9 | 9.9 | 0.00% | 0.0 | 0.0 | 59974 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 2111.2 | 2.3 | 0.00% | 0.0 | 0.0 | 32168 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 973.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31598 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 3036.2 | 2.3 | 30.77% | 0.0 | 0.0 | 58777 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 50.00% | 68.18% | 100.00% | 0.00% | 943.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31436 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 259.2 | 7.0 | 0.00% | 0.0 | 0.0 | 0 |

## Low-Memory Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4959.0 | 2.3 | 0.00% | 0.0 | 0.0 | 82922 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2174.2 | 2.3 | 0.00% | 0.0 | 0.0 | 37349 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 6210.5 | 2.3 | 0.00% | 0.0 | 0.0 | 35082 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 2111.2 | 2.3 | 0.00% | 0.0 | 0.0 | 32168 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1032.9 | 9.9 | 0.00% | 0.0 | 0.0 | 59974 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 973.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31598 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 3036.2 | 2.3 | 30.77% | 0.0 | 0.0 | 58777 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 50.00% | 68.18% | 100.00% | 0.00% | 943.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31436 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 259.2 | 7.0 | 0.00% | 0.0 | 0.0 | 0 |

## Balanced Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2174.2 | 2.3 | 0.00% | 0.0 | 0.0 | 37349 | 95.647 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 2111.2 | 2.3 | 0.00% | 0.0 | 0.0 | 32168 | 91.363 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1032.9 | 9.9 | 0.00% | 0.0 | 0.0 | 59974 | 90.171 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4959.0 | 2.3 | 0.00% | 0.0 | 0.0 | 82922 | 90.077 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 973.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31598 | 89.231 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 6210.5 | 2.3 | 0.00% | 0.0 | 0.0 | 35082 | 87.575 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 3036.2 | 2.3 | 30.77% | 0.0 | 0.0 | 58777 | 59.541 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 50.00% | 68.18% | 100.00% | 0.00% | 943.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31436 | 52.578 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 259.2 | 7.0 | 0.00% | 0.0 | 0.0 | 0 | -30.532 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score (Remote) |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2174.2 | 2.3 | 0.00% | 0.0 | 0.0 | 37349 | 95.652 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 2111.2 | 2.3 | 0.00% | 0.0 | 0.0 | 32168 | 91.368 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1032.9 | 9.9 | 0.00% | 0.0 | 0.0 | 59974 | 90.191 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4959.0 | 2.3 | 0.00% | 0.0 | 0.0 | 82922 | 90.082 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 973.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31598 | 89.236 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 6210.5 | 2.3 | 0.00% | 0.0 | 0.0 | 35082 | 87.579 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 3036.2 | 2.3 | 30.77% | 0.0 | 0.0 | 58777 | 59.546 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 50.00% | 68.18% | 100.00% | 0.00% | 943.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31436 | 52.582 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 259.2 | 7.0 | 0.00% | 0.0 | 0.0 | 0 | -30.518 |

## Efficiency Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2174.2 | 2.3 | 0.00% | 0.0 | 0.0 | 37349 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4959.0 | 2.3 | 0.00% | 0.0 | 0.0 | 82922 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 6210.5 | 2.3 | 0.00% | 0.0 | 0.0 | 35082 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1032.9 | 9.9 | 0.00% | 0.0 | 0.0 | 59974 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 2111.2 | 2.3 | 0.00% | 0.0 | 0.0 | 32168 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 973.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31598 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 3036.2 | 2.3 | 30.77% | 0.0 | 0.0 | 58777 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 50.00% | 68.18% | 100.00% | 0.00% | 943.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31436 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 259.2 | 7.0 | 0.00% | 0.0 | 0.0 | 0 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 0 | n/a | n/a | n/a |
| Remote | 9 | 2111.2 | 259.2 | openrouter-claude-3.5-sonnet |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2174.2 | 2.3 | 0.00% | 0.0 | 0.0 | 37349 | 95.647 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 2111.2 | 2.3 | 0.00% | 0.0 | 0.0 | 32168 | 91.363 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1032.9 | 9.9 | 0.00% | 0.0 | 0.0 | 59974 | 90.171 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4959.0 | 2.3 | 0.00% | 0.0 | 0.0 | 82922 | 90.077 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | default | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 973.0 | 2.3 | 0.00% | 0.0 | 0.0 | 31598 | 89.231 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | default | LLM | 0.0 | 70.00% | 86.36% | 100.00% | 0.00% | 3036.2 | 2.3 | 30.77% | 0.0 | 0.0 | 58777 | 59.541 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | default | LLM | 0.0 | 50.00% | 68.18% | 100.00% | 0.00% | 943.3 | 2.3 | 0.00% | 0.0 | 0.0 | 31436 | 52.578 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | default | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 259.2 | 7.0 | 0.00% | 0.0 | 0.0 | 0 | -30.532 |

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
| openrouter | 1 | openrouter-gpt-4o-mini | openai/gpt-4o-mini | 0.0 | 100.00% | 95.647 |
| openrouter | 2 | openrouter-gemini-2.5-flash | google/gemini-2.5-flash | 0.0 | 90.00% | 91.363 |
| openrouter | 3 | openrouter-ministral-3b-2512 | mistralai/ministral-3b-2512 | 0.0 | 90.00% | 90.171 |

## Recommendations

- Best overall quality: `openrouter-gpt-4o-mini` (openai/gpt-4o-mini)
- Best low-memory option: `openrouter-deepseek-chat` (2.3 MB peak)
- Best throughput option: `openrouter-gpt-4o-mini` (0.0 gen tok/s)
- Best remote option (memory-agnostic): `openrouter-gpt-4o-mini` (openai/gpt-4o-mini, score=95.652)

## TTS Friction

- `Avg Friction`: mean count of TTS-hostile tokens per turn (lower is better).
- `Clean Rate`: fraction of turns with zero friction (higher is better).

| Run | Avg Friction | Clean Rate |
|---|---:|---:|
| openrouter-gpt-4o-mini | 0.36 | 80.0% |
| openrouter-deepseek-chat | 0.96 | 68.0% |
| openrouter-gemini-2.5-pro | 0.32 | 76.0% |
| openrouter-ministral-3b-2512 | 1.20 | 32.0% |
| openrouter-gemini-2.5-flash | 0.16 | 88.0% |
| openrouter-gemini-2.5-flash-lite | 0.28 | 80.0% |
| openrouter-minimax-01 | 1.00 | 68.0% |
| openrouter-gemini-2.0-flash-lite-001 | 0.08 | 92.0% |
| openrouter-claude-3.5-sonnet | 0.00 | 100.0% |
