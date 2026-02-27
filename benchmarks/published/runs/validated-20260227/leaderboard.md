# Benchmark Leaderboard

- Generated: 2026-02-27T10:35:42-0500
- Runs: 16
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/Users/rianders/Documents/GitHub/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `UOES-0002.local` (Darwin 25.3.0, arm64, py 3.12.8)
- Network: `unknown`

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

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 7073.4 | 2.5 | 0.00% | 319.9 | 56578 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 6262.2 | 2.5 | 0.00% | 173.0 | 27090 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 2603.5 | 2.5 | 0.00% | 397.4 | 25869 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 548.7 | 301.0 | 0.00% | 723.5 | 9925 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 905.6 | 301.0 | 0.00% | 433.4 | 9812 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 947.0 | 1479.8 | 0.00% | 414.5 | 9814 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 985.3 | 1545.5 | 0.00% | 402.9 | 9926 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1305.2 | 2.5 | 0.00% | 1465.0 | 47801 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 60.00% | 90.91% | 75.00% | 100.00% | 3304.2 | 2.5 | 0.00% | 238.1 | 19667 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 50.00% | 86.36% | 100.00% | 100.00% | 932.8 | 0.5 | 0.00% | 2037.5 | 47512 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 50.00% | 86.36% | 75.00% | 100.00% | 2501.0 | 2.5 | 0.00% | 404.4 | 25285 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2057.0 | 0.4 | 3.57% | 167.5 | 8613 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 1653.4 | 3814.6 | 4.76% | 232.1 | 9593 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 1655.6 | 4967.1 | 4.76% | 231.8 | 9595 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 30.00% | 77.27% | 100.00% | 0.00% | 1970.0 | 2.5 | 0.00% | 155.7 | 7670 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 10.00% | 31.82% | 100.00% | 0.00% | 5684.9 | 0.4 | 0.00% | 260.4 | 37003 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 7073.4 | 2.5 | 0.00% | 319.9 | 56578 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 2603.5 | 2.5 | 0.00% | 397.4 | 25869 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 6262.2 | 2.5 | 0.00% | 173.0 | 27090 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 905.6 | 301.0 | 0.00% | 433.4 | 9812 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 548.7 | 301.0 | 0.00% | 723.5 | 9925 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 947.0 | 1479.8 | 0.00% | 414.5 | 9814 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 985.3 | 1545.5 | 0.00% | 402.9 | 9926 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 60.00% | 90.91% | 75.00% | 100.00% | 3304.2 | 2.5 | 0.00% | 238.1 | 19667 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1305.2 | 2.5 | 0.00% | 1465.0 | 47801 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2057.0 | 0.4 | 3.57% | 167.5 | 8613 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 50.00% | 86.36% | 100.00% | 100.00% | 932.8 | 0.5 | 0.00% | 2037.5 | 47512 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 50.00% | 86.36% | 75.00% | 100.00% | 2501.0 | 2.5 | 0.00% | 404.4 | 25285 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 1653.4 | 3814.6 | 4.76% | 232.1 | 9593 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 1655.6 | 4967.1 | 4.76% | 231.8 | 9595 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 30.00% | 77.27% | 100.00% | 0.00% | 1970.0 | 2.5 | 0.00% | 155.7 | 7670 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 10.00% | 31.82% | 100.00% | 0.00% | 5684.9 | 0.4 | 0.00% | 260.4 | 37003 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 7073.4 | 2.5 | 0.00% | 319.9 | 56578 | 79.015 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 548.7 | 301.0 | 0.00% | 723.5 | 9925 | 75.832 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 2603.5 | 2.5 | 0.00% | 397.4 | 25869 | 75.211 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 905.6 | 301.0 | 0.00% | 433.4 | 9812 | 75.118 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 947.0 | 1479.8 | 0.00% | 414.5 | 9814 | 72.677 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 985.3 | 1545.5 | 0.00% | 402.9 | 9926 | 72.469 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1305.2 | 2.5 | 0.00% | 1465.0 | 47801 | 69.900 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 50.00% | 86.36% | 100.00% | 100.00% | 932.8 | 0.5 | 0.00% | 2037.5 | 47512 | 66.239 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 60.00% | 90.91% | 75.00% | 100.00% | 3304.2 | 2.5 | 0.00% | 238.1 | 19667 | 62.152 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 6262.2 | 2.5 | 0.00% | 173.0 | 27090 | 61.721 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 50.00% | 86.36% | 75.00% | 100.00% | 2501.0 | 2.5 | 0.00% | 404.4 | 25285 | 59.348 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2057.0 | 0.4 | 3.57% | 167.5 | 8613 | 58.125 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 1653.4 | 3814.6 | 4.76% | 232.1 | 9593 | 50.158 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 1655.6 | 4967.1 | 4.76% | 231.8 | 9595 | 47.848 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 30.00% | 77.27% | 100.00% | 0.00% | 1970.0 | 2.5 | 0.00% | 155.7 | 7670 | 37.009 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 10.00% | 31.82% | 100.00% | 0.00% | 5684.9 | 0.4 | 0.00% | 260.4 | 37003 | 13.493 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 7073.4 | 2.5 | 0.00% | 319.9 | 56578 | 79.020 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 2603.5 | 2.5 | 0.00% | 397.4 | 25869 | 75.216 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1305.2 | 2.5 | 0.00% | 1465.0 | 47801 | 69.905 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 50.00% | 86.36% | 100.00% | 100.00% | 932.8 | 0.5 | 0.00% | 2037.5 | 47512 | 66.239 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 60.00% | 90.91% | 75.00% | 100.00% | 3304.2 | 2.5 | 0.00% | 238.1 | 19667 | 62.157 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 6262.2 | 2.5 | 0.00% | 173.0 | 27090 | 61.726 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 50.00% | 86.36% | 75.00% | 100.00% | 2501.0 | 2.5 | 0.00% | 404.4 | 25285 | 59.353 |

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 7073.4 | 2.5 | 0.00% | 319.9 | 56578 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 2603.5 | 2.5 | 0.00% | 397.4 | 25869 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 6262.2 | 2.5 | 0.00% | 173.0 | 27090 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 548.7 | 301.0 | 0.00% | 723.5 | 9925 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 905.6 | 301.0 | 0.00% | 433.4 | 9812 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 947.0 | 1479.8 | 0.00% | 414.5 | 9814 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 985.3 | 1545.5 | 0.00% | 402.9 | 9926 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1305.2 | 2.5 | 0.00% | 1465.0 | 47801 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 60.00% | 90.91% | 75.00% | 100.00% | 3304.2 | 2.5 | 0.00% | 238.1 | 19667 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 50.00% | 86.36% | 100.00% | 100.00% | 932.8 | 0.5 | 0.00% | 2037.5 | 47512 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 50.00% | 86.36% | 75.00% | 100.00% | 2501.0 | 2.5 | 0.00% | 404.4 | 25285 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 1653.4 | 3814.6 | 4.76% | 232.1 | 9593 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 0.0 | 50.00% | 72.73% | 100.00% | 100.00% | 1655.6 | 4967.1 | 4.76% | 231.8 | 9595 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2057.0 | 0.4 | 3.57% | 167.5 | 8613 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 30.00% | 77.27% | 100.00% | 0.00% | 1970.0 | 2.5 | 0.00% | 155.7 | 7670 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 10.00% | 31.82% | 100.00% | 0.00% | 5684.9 | 0.4 | 0.00% | 260.4 | 37003 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 9 | 1653.4 | 548.7 | local-qwen3-1.7b-intent-ctx2048 |
| Remote | 7 | 2603.5 | 932.8 | openrouter-ministral-3b-2512-t0.3 |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 7073.4 | 2.5 | 0.00% | 319.9 | 56578 | 79.015 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 548.7 | 301.0 | 0.00% | 723.5 | 9925 | 75.832 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 2603.5 | 2.5 | 0.00% | 397.4 | 25869 | 75.211 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 905.6 | 301.0 | 0.00% | 433.4 | 9812 | 75.118 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 60.00% | 90.91% | 100.00% | 100.00% | 1305.2 | 2.5 | 0.00% | 1465.0 | 47801 | 69.900 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 50.00% | 86.36% | 100.00% | 100.00% | 932.8 | 0.5 | 0.00% | 2037.5 | 47512 | 66.239 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 60.00% | 90.91% | 75.00% | 100.00% | 3304.2 | 2.5 | 0.00% | 238.1 | 19667 | 62.152 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 6262.2 | 2.5 | 0.00% | 173.0 | 27090 | 61.721 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2057.0 | 0.4 | 3.57% | 167.5 | 8613 | 58.125 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 10.00% | 31.82% | 100.00% | 0.00% | 5684.9 | 0.4 | 0.00% | 260.4 | 37003 | 13.493 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx2048 | 70.00% | 70.00% | +0.00% | 81.82% | 81.82% | +0.00% | 73.898 | 75.832 | +1.934 |

## Context Window Coherence Sweep

- Near-peak ratio: 0.95
- Dropoff ratio: 0.90

| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) | 2048, 4096 | 77.531 @ 2048 | 74.542 | 2048 | none | 70.00% | 800.4 | 693.9 |
| local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf) | 4096, 8192 | 62.046 @ 4096 | 50.158 | 4096 | none | 50.00% | 1653.4 | 3814.6 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local | 1 | local-qwen3-1.7b-intent-ctx2048 | qwen/qwen3-1.7b | 0.0 | 70.00% | 75.832 |
| local | 2 | local-qwen3-1.7b-llm-t0.3-ctx2048 | qwen/qwen3-1.7b | 0.3 | 70.00% | 75.118 |
| local | 3 | local-qwen3-1.7b-llm-ctx2048 | qwen/qwen3-1.7b | 0.0 | 70.00% | 72.677 |
| local_server | 1 | ollama-llama3.2-3b-t0.3 | llama3.2:3b | 0.3 | 50.00% | 58.125 |
| local_server | 2 | ollama-llama3.2-3b | llama3.2:3b | 0.0 | 30.00% | 37.009 |
| local_server | 3 | ollama-mistral-nemo | mistral-nemo:latest | 0.0 | 10.00% | 13.493 |
| openrouter | 1 | openrouter-claude-3.5-sonnet | anthropic/claude-3.5-sonnet | 0.0 | 90.00% | 79.015 |
| openrouter | 2 | openrouter-gpt-4o-mini | openai/gpt-4o-mini | 0.0 | 80.00% | 75.211 |
| openrouter | 3 | openrouter-ministral-3b-2512 | mistralai/ministral-3b-2512 | 0.0 | 60.00% | 69.900 |

## Recommendations

- Best overall quality: `openrouter-claude-3.5-sonnet` (anthropic/claude-3.5-sonnet)
- Best low-memory option: `openrouter-claude-3.5-sonnet` (2.5 MB peak)
- Best throughput option: `openrouter-claude-3.5-sonnet` (319.9 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-claude-3.5-sonnet` (anthropic/claude-3.5-sonnet, score=79.020)
- Context recommendations (near-peak quality at lowest context):
  - `local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf)` -> `n_ctx=2048` (dropoff: not observed)
  - `local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf)` -> `n_ctx=4096` (dropoff: not observed)
- Routing gap summary: intent minus llm avg success delta = +0.00%
- Routing gap summary: intent minus llm avg score delta = +1.934
