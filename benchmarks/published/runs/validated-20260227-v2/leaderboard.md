# Benchmark Leaderboard

- Generated: 2026-02-27T11:31:11-0500
- Runs: 16
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/Users/rianders/Documents/GitHub/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `UOES-0002.local` (Darwin 25.3.0, arm64, py 3.12.8)
- Network: `wifi (Wi-Fi)`


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 116.3 | 97.6 | 158.4 | 200 |
| ollama-local | http://localhost:11434/api/tags | 22.2 | 20.0 | 39.6 | 200 |
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
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 5264.2 | 2.5 | 0.00% | 428.9 | 56447 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1880.2 | 2.5 | 0.00% | 548.6 | 25786 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 100.00% | 7262.7 | 2.5 | 0.00% | 165.9 | 30128 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 784.7 | 2.5 | 0.00% | 2446.0 | 47983 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 513.5 | 301.0 | 0.00% | 770.1 | 9886 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 859.3 | 1543.6 | 0.00% | 455.9 | 9794 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 899.7 | 301.0 | 0.00% | 438.4 | 9860 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 925.5 | 1480.2 | 0.00% | 423.8 | 9806 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 60.00% | 86.36% | 100.00% | 100.00% | 722.9 | 0.4 | 0.00% | 2680.1 | 48434 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 919.1 | 2.5 | 0.00% | 827.2 | 19006 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1616.8 | 4930.0 | 4.55% | 236.0 | 9540 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1638.7 | 3786.6 | 4.55% | 232.8 | 9538 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 50.00% | 90.91% | 75.00% | 100.00% | 1216.4 | 2.5 | 0.00% | 625.8 | 19031 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2108.6 | 0.4 | 10.00% | 141.6 | 7466 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 40.00% | 68.18% | 50.00% | 100.00% | 7093.1 | 0.4 | 0.00% | 158.4 | 28081 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 30.00% | 77.27% | 100.00% | 0.00% | 1957.1 | 0.4 | 4.00% | 159.3 | 7795 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1880.2 | 2.5 | 0.00% | 548.6 | 25786 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 5264.2 | 2.5 | 0.00% | 428.9 | 56447 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 784.7 | 2.5 | 0.00% | 2446.0 | 47983 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 100.00% | 7262.7 | 2.5 | 0.00% | 165.9 | 30128 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 513.5 | 301.0 | 0.00% | 770.1 | 9886 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 899.7 | 301.0 | 0.00% | 438.4 | 9860 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 925.5 | 1480.2 | 0.00% | 423.8 | 9806 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 859.3 | 1543.6 | 0.00% | 455.9 | 9794 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 60.00% | 86.36% | 100.00% | 100.00% | 722.9 | 0.4 | 0.00% | 2680.1 | 48434 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 919.1 | 2.5 | 0.00% | 827.2 | 19006 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1638.7 | 3786.6 | 4.55% | 232.8 | 9538 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1616.8 | 4930.0 | 4.55% | 236.0 | 9540 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2108.6 | 0.4 | 10.00% | 141.6 | 7466 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 50.00% | 90.91% | 75.00% | 100.00% | 1216.4 | 2.5 | 0.00% | 625.8 | 19031 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 40.00% | 68.18% | 50.00% | 100.00% | 7093.1 | 0.4 | 0.00% | 158.4 | 28081 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 30.00% | 77.27% | 100.00% | 0.00% | 1957.1 | 0.4 | 4.00% | 159.3 | 7795 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 784.7 | 2.5 | 0.00% | 2446.0 | 47983 | 87.183 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1880.2 | 2.5 | 0.00% | 548.6 | 25786 | 83.492 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 5264.2 | 2.5 | 0.00% | 428.9 | 56447 | 82.634 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 513.5 | 301.0 | 0.00% | 770.1 | 9886 | 80.310 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 919.1 | 2.5 | 0.00% | 827.2 | 19006 | 77.679 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 899.7 | 301.0 | 0.00% | 438.4 | 9860 | 75.130 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 100.00% | 7262.7 | 2.5 | 0.00% | 165.9 | 30128 | 74.720 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 859.3 | 1543.6 | 0.00% | 455.9 | 9794 | 72.725 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 925.5 | 1480.2 | 0.00% | 423.8 | 9806 | 72.720 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 60.00% | 86.36% | 100.00% | 100.00% | 722.9 | 0.4 | 0.00% | 2680.1 | 48434 | 70.158 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 50.00% | 90.91% | 75.00% | 100.00% | 1216.4 | 2.5 | 0.00% | 625.8 | 19031 | 62.827 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2108.6 | 0.4 | 10.00% | 141.6 | 7466 | 56.736 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1638.7 | 3786.6 | 4.55% | 232.8 | 9538 | 54.694 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1616.8 | 4930.0 | 4.55% | 236.0 | 9540 | 52.450 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 30.00% | 77.27% | 100.00% | 0.00% | 1957.1 | 0.4 | 4.00% | 159.3 | 7795 | 36.239 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 40.00% | 68.18% | 50.00% | 100.00% | 7093.1 | 0.4 | 0.00% | 158.4 | 28081 | 35.949 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 784.7 | 2.5 | 0.00% | 2446.0 | 47983 | 87.188 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1880.2 | 2.5 | 0.00% | 548.6 | 25786 | 83.497 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 5264.2 | 2.5 | 0.00% | 428.9 | 56447 | 82.639 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 919.1 | 2.5 | 0.00% | 827.2 | 19006 | 77.684 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 100.00% | 7262.7 | 2.5 | 0.00% | 165.9 | 30128 | 74.725 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 60.00% | 86.36% | 100.00% | 100.00% | 722.9 | 0.4 | 0.00% | 2680.1 | 48434 | 70.159 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 50.00% | 90.91% | 75.00% | 100.00% | 1216.4 | 2.5 | 0.00% | 625.8 | 19031 | 62.832 |

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1880.2 | 2.5 | 0.00% | 548.6 | 25786 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 5264.2 | 2.5 | 0.00% | 428.9 | 56447 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 784.7 | 2.5 | 0.00% | 2446.0 | 47983 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 513.5 | 301.0 | 0.00% | 770.1 | 9886 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 100.00% | 7262.7 | 2.5 | 0.00% | 165.9 | 30128 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 859.3 | 1543.6 | 0.00% | 455.9 | 9794 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 899.7 | 301.0 | 0.00% | 438.4 | 9860 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 925.5 | 1480.2 | 0.00% | 423.8 | 9806 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 60.00% | 86.36% | 100.00% | 100.00% | 722.9 | 0.4 | 0.00% | 2680.1 | 48434 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 919.1 | 2.5 | 0.00% | 827.2 | 19006 |
| local-qwen3-8b-intent-ctx8192 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1616.8 | 4930.0 | 4.55% | 236.0 | 9540 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1638.7 | 3786.6 | 4.55% | 232.8 | 9538 |
| openrouter-gemini-2.5-flash | openrouter | google/gemini-2.5-flash | LLM | 0.0 | 50.00% | 90.91% | 75.00% | 100.00% | 1216.4 | 2.5 | 0.00% | 625.8 | 19031 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2108.6 | 0.4 | 10.00% | 141.6 | 7466 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 40.00% | 68.18% | 50.00% | 100.00% | 7093.1 | 0.4 | 0.00% | 158.4 | 28081 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 30.00% | 77.27% | 100.00% | 0.00% | 1957.1 | 0.4 | 4.00% | 159.3 | 7795 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 9 | 1616.8 | 513.5 | local-qwen3-1.7b-intent-ctx2048 |
| Remote | 7 | 1216.4 | 722.9 | openrouter-ministral-3b-2512-t0.3 |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 784.7 | 2.5 | 0.00% | 2446.0 | 47983 | 87.183 |
| openrouter-gpt-4o-mini | openrouter | openai/gpt-4o-mini | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 1880.2 | 2.5 | 0.00% | 548.6 | 25786 | 83.492 |
| openrouter-claude-3.5-sonnet | openrouter | anthropic/claude-3.5-sonnet | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 5264.2 | 2.5 | 0.00% | 428.9 | 56447 | 82.634 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 513.5 | 301.0 | 0.00% | 770.1 | 9886 | 80.310 |
| openrouter-ministral-3b-2512-t0.3 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.3 | 60.00% | 86.36% | 100.00% | 100.00% | 722.9 | 0.4 | 0.00% | 2680.1 | 48434 | 70.158 |
| ollama-llama3.2-3b-t0.3 | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 2108.6 | 0.4 | 10.00% | 141.6 | 7466 | 56.736 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 30.00% | 77.27% | 100.00% | 0.00% | 1957.1 | 0.4 | 4.00% | 159.3 | 7795 | 36.239 |
| ollama-mistral-nemo | local_server | mistral-nemo:latest | LLM | 0.0 | 40.00% | 68.18% | 50.00% | 100.00% | 7093.1 | 0.4 | 0.00% | 158.4 | 28081 | 35.949 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx2048 | 70.00% | 80.00% | +10.00% | 81.82% | 86.36% | +4.54% | 73.925 | 80.310 | +6.385 |

## Context Window Coherence Sweep

- Near-peak ratio: 0.95
- Dropoff ratio: 0.90

| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) | 2048, 4096 | 79.000 @ 2048 | 76.053 | 2048 | none | 73.33% | 779.6 | 694.0 |
| local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf) | 4096, 8192 | 66.454 @ 4096 | 54.694 | 4096 | none | 60.00% | 1638.7 | 3786.6 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local | 1 | local-qwen3-1.7b-intent-ctx2048 | qwen/qwen3-1.7b | 0.0 | 80.00% | 80.310 |
| local | 2 | local-qwen3-1.7b-llm-t0.3-ctx2048 | qwen/qwen3-1.7b | 0.3 | 70.00% | 75.130 |
| local | 3 | local-qwen3-1.7b-llm-ctx4096 | qwen/qwen3-1.7b | 0.0 | 70.00% | 72.725 |
| local_server | 1 | ollama-llama3.2-3b-t0.3 | llama3.2:3b | 0.3 | 50.00% | 56.736 |
| local_server | 2 | ollama-llama3.2-3b | llama3.2:3b | 0.0 | 30.00% | 36.239 |
| local_server | 3 | ollama-mistral-nemo | mistral-nemo:latest | 0.0 | 40.00% | 35.949 |
| openrouter | 1 | openrouter-ministral-3b-2512 | mistralai/ministral-3b-2512 | 0.0 | 80.00% | 87.183 |
| openrouter | 2 | openrouter-gpt-4o-mini | openai/gpt-4o-mini | 0.0 | 90.00% | 83.492 |
| openrouter | 3 | openrouter-claude-3.5-sonnet | anthropic/claude-3.5-sonnet | 0.0 | 90.00% | 82.634 |

## Recommendations

- Best overall quality: `openrouter-claude-3.5-sonnet` (anthropic/claude-3.5-sonnet)
- Best low-memory option: `openrouter-gpt-4o-mini` (2.5 MB peak)
- Best throughput option: `openrouter-gpt-4o-mini` (548.6 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512, score=87.188)
- Context recommendations (near-peak quality at lowest context):
  - `local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf)` -> `n_ctx=2048` (dropoff: not observed)
  - `local/qwen/qwen3-8b (qwen3-8b-q4_k_m.gguf)` -> `n_ctx=4096` (dropoff: not observed)
- Routing gap summary: intent minus llm avg success delta = +10.00%
- Routing gap summary: intent minus llm avg score delta = +6.385
