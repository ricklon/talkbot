# Benchmark Leaderboard

- Generated: 2026-02-27T13:25:37-0500
- Runs: 11
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
| openrouter | https://openrouter.ai/api/v1/models | 103.3 | 103.3 | 142.4 | 200 |
| ollama-local | http://localhost:11434/api/tags | 20.0 | 18.6 | 33.0 | 200 |
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
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 972.3 | 2.5 | 0.00% | 1174.5 | 28549 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3702.7 | 8.5 | 0.00% | 776.8 | 71902 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 10778.3 | 2.5 | 0.00% | 141.0 | 38003 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2019.8 | 8.0 | 0.00% | 1426.7 | 72042 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 509.0 | 301.0 | 0.00% | 794.6 | 10110 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 0.00% | 863.8 | 2.5 | 0.00% | 2660.2 | 57446 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 845.5 | 1540.7 | 0.00% | 463.4 | 9794 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 865.2 | 1478.3 | 0.00% | 452.8 | 9794 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 868.7 | 301.0 | 0.00% | 450.9 | 9792 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 1677.7 | 3788.2 | 4.55% | 234.9 | 9853 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 81.82% | 100.00% | 100.00% | 2243.9 | 0.4 | 0.00% | 119.5 | 6706 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 972.3 | 2.5 | 0.00% | 1174.5 | 28549 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3702.7 | 8.5 | 0.00% | 776.8 | 71902 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 10778.3 | 2.5 | 0.00% | 141.0 | 38003 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2019.8 | 8.0 | 0.00% | 1426.7 | 72042 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 509.0 | 301.0 | 0.00% | 794.6 | 10110 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 0.00% | 863.8 | 2.5 | 0.00% | 2660.2 | 57446 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 868.7 | 301.0 | 0.00% | 450.9 | 9792 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 865.2 | 1478.3 | 0.00% | 452.8 | 9794 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 845.5 | 1540.7 | 0.00% | 463.4 | 9794 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 1677.7 | 3788.2 | 4.55% | 234.9 | 9853 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 81.82% | 100.00% | 100.00% | 2243.9 | 0.4 | 0.00% | 119.5 | 6706 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 972.3 | 2.5 | 0.00% | 1174.5 | 28549 | 98.050 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3702.7 | 8.5 | 0.00% | 776.8 | 71902 | 89.078 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 509.0 | 301.0 | 0.00% | 794.6 | 10110 | 80.319 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2019.8 | 8.0 | 0.00% | 1426.7 | 72042 | 78.793 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 868.7 | 301.0 | 0.00% | 450.9 | 9792 | 75.192 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 865.2 | 1478.3 | 0.00% | 452.8 | 9794 | 72.844 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 845.5 | 1540.7 | 0.00% | 463.4 | 9794 | 72.759 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 0.00% | 863.8 | 2.5 | 0.00% | 2660.2 | 57446 | 71.857 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 10778.3 | 2.5 | 0.00% | 141.0 | 38003 | 63.105 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 81.82% | 100.00% | 100.00% | 2243.9 | 0.4 | 0.00% | 119.5 | 6706 | 62.708 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 1677.7 | 3788.2 | 4.55% | 234.9 | 9853 | 55.522 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 972.3 | 2.5 | 0.00% | 1174.5 | 28549 | 98.055 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3702.7 | 8.5 | 0.00% | 776.8 | 71902 | 89.095 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2019.8 | 8.0 | 0.00% | 1426.7 | 72042 | 78.809 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 0.00% | 863.8 | 2.5 | 0.00% | 2660.2 | 57446 | 71.862 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 10778.3 | 2.5 | 0.00% | 141.0 | 38003 | 63.110 |

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 972.3 | 2.5 | 0.00% | 1174.5 | 28549 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 90.00% | 100.00% | 100.00% | 100.00% | 3702.7 | 8.5 | 0.00% | 776.8 | 71902 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 80.00% | 90.91% | 100.00% | 100.00% | 2019.8 | 8.0 | 0.00% | 1426.7 | 72042 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 509.0 | 301.0 | 0.00% | 794.6 | 10110 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 100.00% | 100.00% | 10778.3 | 2.5 | 0.00% | 141.0 | 38003 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 0.00% | 863.8 | 2.5 | 0.00% | 2660.2 | 57446 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 845.5 | 1540.7 | 0.00% | 463.4 | 9794 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 865.2 | 1478.3 | 0.00% | 452.8 | 9794 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 868.7 | 301.0 | 0.00% | 450.9 | 9792 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 81.82% | 100.00% | 100.00% | 1677.7 | 3788.2 | 4.55% | 234.9 | 9853 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 81.82% | 100.00% | 100.00% | 2243.9 | 0.4 | 0.00% | 119.5 | 6706 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 6 | 867.0 | 509.0 | local-qwen3-1.7b-intent-ctx2048 |
| Remote | 5 | 2019.8 | 863.8 | openrouter-ministral-3b-2512 |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 972.3 | 2.5 | 0.00% | 1174.5 | 28549 | 98.050 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 509.0 | 301.0 | 0.00% | 794.6 | 10110 | 80.319 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 868.7 | 301.0 | 0.00% | 450.9 | 9792 | 75.192 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 70.00% | 95.45% | 100.00% | 0.00% | 863.8 | 2.5 | 0.00% | 2660.2 | 57446 | 71.857 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 81.82% | 100.00% | 100.00% | 2243.9 | 0.4 | 0.00% | 119.5 | 6706 | 62.708 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx2048 | 70.00% | 80.00% | +10.00% | 81.82% | 86.36% | +4.54% | 74.018 | 80.319 | +6.301 |

## Context Window Coherence Sweep

- Near-peak ratio: 0.95
- Dropoff ratio: 0.90

| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) | 2048, 4096 | 79.000 @ 2048 | 76.118 | 2048 | none | 73.33% | 747.6 | 693.4 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local | 1 | local-qwen3-1.7b-intent-ctx2048 | qwen/qwen3-1.7b | 0.0 | 80.00% | 80.319 |
| local | 2 | local-qwen3-1.7b-llm-t0.3-ctx2048 | qwen/qwen3-1.7b | 0.3 | 70.00% | 75.192 |
| local | 3 | local-qwen3-1.7b-llm-ctx2048 | qwen/qwen3-1.7b | 0.0 | 70.00% | 72.844 |
| local_server | 1 | ollama-llama3.2-3b | llama3.2:3b | 0.3 | 50.00% | 62.708 |
| openrouter | 1 | openrouter-gemini-2.5-flash-lite | google/gemini-2.5-flash-lite | 0.0 | 100.00% | 98.050 |
| openrouter | 2 | openrouter-claude-sonnet-4-6 | anthropic/claude-sonnet-4-6 | 0.0 | 90.00% | 89.078 |
| openrouter | 3 | openrouter-claude-haiku-4-5 | anthropic/claude-haiku-4-5 | 0.0 | 80.00% | 78.793 |

## Recommendations

- Best overall quality: `openrouter-gemini-2.5-flash-lite` (google/gemini-2.5-flash-lite)
- Best low-memory option: `openrouter-gemini-2.5-flash-lite` (2.5 MB peak)
- Best throughput option: `openrouter-gemini-2.5-flash-lite` (1174.5 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-gemini-2.5-flash-lite` (google/gemini-2.5-flash-lite, score=98.055)
- Context recommendations (near-peak quality at lowest context):
  - `local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf)` -> `n_ctx=2048` (dropoff: not observed)
- Routing gap summary: intent minus llm avg success delta = +10.00%
- Routing gap summary: intent minus llm avg score delta = +6.301
