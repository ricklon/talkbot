# Benchmark Leaderboard

- Generated: 2026-02-26T17:58:37-0500
- Runs: 8
- Scenarios: 7
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/Users/rianders/Documents/GitHub/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `UOES-0002.local` (Darwin 25.3.0, arm64, py 3.12.8)

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
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7393.0 | 2.5 | 5.56% | 308.2 | 41012 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 2527.7 | 2.5 | 5.88% | 409.2 | 18620 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 93.33% | 75.00% | 0.00% | 5327.9 | 2.5 | 0.00% | 233.3 | 22375 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 93.33% | 80.00% | 0.00% | 4381.0 | 2.5 | 6.25% | 642.9 | 50702 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 2820.4 | 2.5 | 0.00% | 294.2 | 14936 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 831.1 | 12.8 | 0.00% | 914.0 | 13672 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 60.00% | 100.00% | 0.00% | 1946.4 | 2.5 | 9.09% | 923.2 | 32344 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 962.4 | 2.5 | 0.00% | 786.6 | 13627 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7393.0 | 2.5 | 5.56% | 308.2 | 41012 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 2527.7 | 2.5 | 5.88% | 409.2 | 18620 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 93.33% | 75.00% | 0.00% | 5327.9 | 2.5 | 0.00% | 233.3 | 22375 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 93.33% | 80.00% | 0.00% | 4381.0 | 2.5 | 6.25% | 642.9 | 50702 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 2820.4 | 2.5 | 0.00% | 294.2 | 14936 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 831.1 | 12.8 | 0.00% | 914.0 | 13672 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 60.00% | 100.00% | 0.00% | 1946.4 | 2.5 | 9.09% | 923.2 | 32344 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 962.4 | 2.5 | 0.00% | 786.6 | 13627 |

## Balanced Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 831.1 | 12.8 | 0.00% | 914.0 | 13672 | 55.563 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 93.33% | 75.00% | 0.00% | 5327.9 | 2.5 | 0.00% | 233.3 | 22375 | 54.254 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7393.0 | 2.5 | 5.56% | 308.2 | 41012 | 54.098 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 2527.7 | 2.5 | 5.88% | 409.2 | 18620 | 47.429 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 2820.4 | 2.5 | 0.00% | 294.2 | 14936 | 44.271 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 93.33% | 80.00% | 0.00% | 4381.0 | 2.5 | 6.25% | 642.9 | 50702 | 35.650 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 60.00% | 100.00% | 0.00% | 1946.4 | 2.5 | 9.09% | 923.2 | 32344 | 31.283 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 962.4 | 2.5 | 0.00% | 786.6 | 13627 | 28.738 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 831.1 | 12.8 | 0.00% | 914.0 | 13672 | 55.589 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 93.33% | 75.00% | 0.00% | 5327.9 | 2.5 | 0.00% | 233.3 | 22375 | 54.259 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7393.0 | 2.5 | 5.56% | 308.2 | 41012 | 54.103 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 2527.7 | 2.5 | 5.88% | 409.2 | 18620 | 47.434 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 2820.4 | 2.5 | 0.00% | 294.2 | 14936 | 44.276 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 93.33% | 80.00% | 0.00% | 4381.0 | 2.5 | 6.25% | 642.9 | 50702 | 35.655 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 60.00% | 100.00% | 0.00% | 1946.4 | 2.5 | 9.09% | 923.2 | 32344 | 31.288 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 962.4 | 2.5 | 0.00% | 786.6 | 13627 | 28.743 |

## Efficiency Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7393.0 | 2.5 | 5.56% | 308.2 | 41012 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 2527.7 | 2.5 | 5.88% | 409.2 | 18620 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 93.33% | 75.00% | 0.00% | 5327.9 | 2.5 | 0.00% | 233.3 | 22375 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 831.1 | 12.8 | 0.00% | 914.0 | 13672 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 93.33% | 80.00% | 0.00% | 4381.0 | 2.5 | 6.25% | 642.9 | 50702 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 2820.4 | 2.5 | 0.00% | 294.2 | 14936 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 60.00% | 100.00% | 0.00% | 1946.4 | 2.5 | 9.09% | 923.2 | 32344 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 962.4 | 2.5 | 0.00% | 786.6 | 13627 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 0 | n/a | n/a | n/a |
| Remote | 8 | 2674.1 | 831.1 | openrouter-gemini-2.5-flash-lite |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 831.1 | 12.8 | 0.00% | 914.0 | 13672 | 55.563 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 93.33% | 75.00% | 0.00% | 5327.9 | 2.5 | 0.00% | 233.3 | 22375 | 54.254 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7393.0 | 2.5 | 5.56% | 308.2 | 41012 | 54.098 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 2527.7 | 2.5 | 5.88% | 409.2 | 18620 | 47.429 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 2820.4 | 2.5 | 0.00% | 294.2 | 14936 | 44.271 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 60.00% | 100.00% | 0.00% | 1946.4 | 2.5 | 9.09% | 923.2 | 32344 | 31.283 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 962.4 | 2.5 | 0.00% | 786.6 | 13627 | 28.738 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

No matched LLM/Intent profile pairs found. Add profiles with the same model + context and `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` (LLM) and `1` (Intent).

## Recommendations

- Best overall quality: `openrouter-claude-3.5-sonnet` (anthropic/claude-3.5-sonnet)
- Best low-memory option: `openrouter-claude-3.5-sonnet` (2.5 MB peak)
- Best throughput option: `openrouter-claude-3.5-sonnet` (308.2 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-gemini-2.5-flash-lite` (google/gemini-2.5-flash-lite, score=55.589)
