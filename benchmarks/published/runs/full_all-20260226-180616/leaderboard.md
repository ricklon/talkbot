# Benchmark Leaderboard

- Generated: 2026-02-26T18:18:17-0500
- Runs: 16
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
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1582.4 | 1481.4 | 4.17% | 259.7 | 7397 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1606.3 | 1543.5 | 4.17% | 255.8 | 7397 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7350.9 | 2.5 | 5.56% | 310.0 | 41021 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 814.5 | 301.0 | 4.55% | 532.9 | 7813 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 894.9 | 301.0 | 4.55% | 485.1 | 7813 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1866.8 | 301.0 | 6.25% | 213.4 | 7170 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1998.7 | 301.0 | 6.25% | 199.3 | 7170 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 100.00% | 60.00% | 0.00% | 4549.5 | 2.5 | 5.88% | 200.6 | 16429 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 1848.0 | 2.5 | 5.88% | 559.7 | 18619 |
| local-qwen3-8b-llm-ctx4096 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3661.8 | 3686.1 | 11.11% | 106.7 | 7033 |
| local-qwen3-8b-llm-ctx8192 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3756.2 | 4976.5 | 11.11% | 104.0 | 7033 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 1540.6 | 2.5 | 0.00% | 539.0 | 14946 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 86.67% | 75.00% | 0.00% | 4288.0 | 2.5 | 0.00% | 655.1 | 50564 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 894.5 | 4.5 | 0.00% | 849.2 | 13672 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 66.67% | 100.00% | 0.00% | 2167.6 | 2.5 | 8.33% | 834.5 | 32560 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 851.7 | 2.5 | 0.00% | 888.1 | 13615 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1582.4 | 1481.4 | 4.17% | 259.7 | 7397 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1606.3 | 1543.5 | 4.17% | 255.8 | 7397 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7350.9 | 2.5 | 5.56% | 310.0 | 41021 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 894.9 | 301.0 | 4.55% | 485.1 | 7813 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 814.5 | 301.0 | 4.55% | 532.9 | 7813 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1866.8 | 301.0 | 6.25% | 213.4 | 7170 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1998.7 | 301.0 | 6.25% | 199.3 | 7170 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 1848.0 | 2.5 | 5.88% | 559.7 | 18619 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 100.00% | 60.00% | 0.00% | 4549.5 | 2.5 | 5.88% | 200.6 | 16429 |
| local-qwen3-8b-llm-ctx4096 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3661.8 | 3686.1 | 11.11% | 106.7 | 7033 |
| local-qwen3-8b-llm-ctx8192 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3756.2 | 4976.5 | 11.11% | 104.0 | 7033 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 86.67% | 75.00% | 0.00% | 4288.0 | 2.5 | 0.00% | 655.1 | 50564 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 1540.6 | 2.5 | 0.00% | 539.0 | 14946 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 894.5 | 4.5 | 0.00% | 849.2 | 13672 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 66.67% | 100.00% | 0.00% | 2167.6 | 2.5 | 8.33% | 834.5 | 32560 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 851.7 | 2.5 | 0.00% | 888.1 | 13615 |

## Balanced Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1582.4 | 1481.4 | 4.17% | 259.7 | 7397 | 76.703 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1606.3 | 1543.5 | 4.17% | 255.8 | 7397 | 76.531 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1866.8 | 301.0 | 6.25% | 213.4 | 7170 | 66.749 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1998.7 | 301.0 | 6.25% | 199.3 | 7170 | 66.485 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 814.5 | 301.0 | 4.55% | 532.9 | 7813 | 59.194 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 894.9 | 301.0 | 4.55% | 485.1 | 7813 | 59.033 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 894.5 | 4.5 | 0.00% | 849.2 | 13672 | 55.453 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7350.9 | 2.5 | 5.56% | 310.0 | 41021 | 54.182 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 100.00% | 60.00% | 0.00% | 4549.5 | 2.5 | 5.88% | 200.6 | 16429 | 53.719 |
| local-qwen3-8b-llm-ctx4096 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3661.8 | 3686.1 | 11.11% | 106.7 | 7033 | 49.081 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 1848.0 | 2.5 | 5.88% | 559.7 | 18619 | 48.788 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 1540.6 | 2.5 | 0.00% | 539.0 | 14946 | 46.831 |
| local-qwen3-8b-llm-ctx8192 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3756.2 | 4976.5 | 11.11% | 104.0 | 7033 | 46.311 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 86.67% | 75.00% | 0.00% | 4288.0 | 2.5 | 0.00% | 655.1 | 50564 | 40.004 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 66.67% | 100.00% | 0.00% | 2167.6 | 2.5 | 8.33% | 834.5 | 32560 | 32.328 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 851.7 | 2.5 | 0.00% | 888.1 | 13615 | 28.960 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 894.5 | 4.5 | 0.00% | 849.2 | 13672 | 55.462 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7350.9 | 2.5 | 5.56% | 310.0 | 41021 | 54.187 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 100.00% | 60.00% | 0.00% | 4549.5 | 2.5 | 5.88% | 200.6 | 16429 | 53.724 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 1848.0 | 2.5 | 5.88% | 559.7 | 18619 | 48.793 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 1540.6 | 2.5 | 0.00% | 539.0 | 14946 | 46.836 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 86.67% | 75.00% | 0.00% | 4288.0 | 2.5 | 0.00% | 655.1 | 50564 | 40.009 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 66.67% | 100.00% | 0.00% | 2167.6 | 2.5 | 8.33% | 834.5 | 32560 | 32.333 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 851.7 | 2.5 | 0.00% | 888.1 | 13615 | 28.965 |

## Efficiency Rank

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1582.4 | 1481.4 | 4.17% | 259.7 | 7397 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1606.3 | 1543.5 | 4.17% | 255.8 | 7397 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 814.5 | 301.0 | 4.55% | 532.9 | 7813 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 894.9 | 301.0 | 4.55% | 485.1 | 7813 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7350.9 | 2.5 | 5.56% | 310.0 | 41021 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1866.8 | 301.0 | 6.25% | 213.4 | 7170 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1998.7 | 301.0 | 6.25% | 199.3 | 7170 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 1848.0 | 2.5 | 5.88% | 559.7 | 18619 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 100.00% | 60.00% | 0.00% | 4549.5 | 2.5 | 5.88% | 200.6 | 16429 |
| local-qwen3-8b-llm-ctx4096 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3661.8 | 3686.1 | 11.11% | 106.7 | 7033 |
| local-qwen3-8b-llm-ctx8192 | local | qwen/qwen3-8b | LLM | 57.14% | 80.00% | 100.00% | 100.00% | 3756.2 | 4976.5 | 11.11% | 104.0 | 7033 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 894.5 | 4.5 | 0.00% | 849.2 | 13672 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 86.67% | 75.00% | 0.00% | 4288.0 | 2.5 | 0.00% | 655.1 | 50564 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 1540.6 | 2.5 | 0.00% | 539.0 | 14946 |
| openrouter-minimax-01 | openrouter | minimax/minimax-01 | LLM | 28.57% | 66.67% | 100.00% | 0.00% | 2167.6 | 2.5 | 8.33% | 834.5 | 32560 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 851.7 | 2.5 | 0.00% | 888.1 | 13615 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 8 | 1736.6 | 814.5 | local-qwen3-1.7b-intent-ctx4096 |
| Remote | 8 | 2007.8 | 851.7 | openrouter-gemini-2.0-flash-lite-001 |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 85.71% | 93.33% | 100.00% | 100.00% | 1582.4 | 1481.4 | 4.17% | 259.7 | 7397 | 76.703 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 71.43% | 86.67% | 100.00% | 100.00% | 1866.8 | 301.0 | 6.25% | 213.4 | 7170 | 66.749 |
| local-qwen3-1.7b-intent-ctx4096 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 814.5 | 301.0 | 4.55% | 532.9 | 7813 | 59.194 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 71.43% | 86.67% | 100.00% | 0.00% | 894.9 | 301.0 | 4.55% | 485.1 | 7813 | 59.033 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 42.86% | 80.00% | 75.00% | 0.00% | 894.5 | 4.5 | 0.00% | 849.2 | 13672 | 55.453 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 71.43% | 100.00% | 100.00% | 0.00% | 7350.9 | 2.5 | 5.56% | 310.0 | 41021 | 54.182 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 57.14% | 100.00% | 60.00% | 0.00% | 4549.5 | 2.5 | 5.88% | 200.6 | 16429 | 53.719 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 57.14% | 93.33% | 100.00% | 0.00% | 1848.0 | 2.5 | 5.88% | 559.7 | 18619 | 48.788 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 42.86% | 93.33% | 75.00% | 0.00% | 1540.6 | 2.5 | 0.00% | 539.0 | 14946 | 46.831 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | LLM | 42.86% | 86.67% | 75.00% | 0.00% | 4288.0 | 2.5 | 0.00% | 655.1 | 50564 | 40.004 |
| openrouter-gemini-2.0-flash-lite-001 | openrouter | google/gemini-2.0-flash-lite-001 | LLM | 14.29% | 53.33% | 100.00% | 0.00% | 851.7 | 2.5 | 0.00% | 888.1 | 13615 | 28.960 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf) @ctx8192 | 57.14% | 71.43% | +14.29% | 80.00% | 86.67% | +6.67% | 46.311 | 66.485 | +20.174 |
| local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf) @ctx4096 | 57.14% | 71.43% | +14.29% | 80.00% | 86.67% | +6.67% | 49.081 | 66.749 | +17.668 |
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx4096 | 85.71% | 71.43% | -14.28% | 93.33% | 86.67% | -6.66% | 76.531 | 59.194 | -17.337 |
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx2048 | 85.71% | 71.43% | -14.28% | 93.33% | 86.67% | -6.66% | 76.703 | 59.033 | -17.670 |

## Context Window Coherence Sweep

- Near-peak ratio: 0.95
- Dropoff ratio: 0.90

| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) | 2048, 4096 | 73.000 @ 2048 | 67.868 | 2048 | none | 78.57% | 1238.6 | 891.2 |
| local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf) | 4096, 8192 | 69.167 @ 4096 | 57.915 | 4096 | none | 64.29% | 2764.3 | 1993.6 |

## Recommendations

- Best overall quality: `local-qwen3-1.7b-llm-ctx2048` (qwen/qwen3-1.7b)
- Best low-memory option: `local-qwen3-1.7b-llm-ctx2048` (1481.4 MB peak)
- Best throughput option: `local-qwen3-1.7b-llm-ctx2048` (259.7 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-gemini-2.5-flash-lite` (google/gemini-2.5-flash-lite, score=55.462)
- Context recommendations (near-peak quality at lowest context):
  - `local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf)` -> `n_ctx=2048` (dropoff: not observed)
  - `local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf)` -> `n_ctx=4096` (dropoff: not observed)
- Routing gap summary: intent minus llm avg success delta = +0.01%
- Routing gap summary: intent minus llm avg score delta = +0.709
