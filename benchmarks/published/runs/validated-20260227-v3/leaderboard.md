# Benchmark Leaderboard

- Generated: 2026-02-27T11:51:34-0500
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
| openrouter | https://openrouter.ai/api/v1/models | 136.7 | 99.9 | 152.4 | 200 |
| ollama-local | http://localhost:11434/api/tags | 23.4 | 19.0 | 35.9 | 200 |
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
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 8852.4 | 2.5 | 0.00% | 129.6 | 28677 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 962.9 | 2.5 | 0.00% | 1988.6 | 47870 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3409.2 | 8.0 | 0.00% | 721.9 | 61531 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 528.8 | 301.0 | 0.00% | 747.8 | 9886 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 70.00% | 90.91% | 75.00% | 100.00% | 2560.4 | 8.0 | 0.00% | 950.1 | 60814 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 865.6 | 1540.6 | 0.00% | 452.6 | 9794 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 874.9 | 301.0 | 0.00% | 447.7 | 9792 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 999.2 | 1477.9 | 0.00% | 392.1 | 9794 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 1050.2 | 2.5 | 0.00% | 723.9 | 19006 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1603.9 | 3818.1 | 4.55% | 237.9 | 9538 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 1950.6 | 0.4 | 6.90% | 135.5 | 6607 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 8852.4 | 2.5 | 0.00% | 129.6 | 28677 |
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 962.9 | 2.5 | 0.00% | 1988.6 | 47870 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3409.2 | 8.0 | 0.00% | 721.9 | 61531 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 528.8 | 301.0 | 0.00% | 747.8 | 9886 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 70.00% | 90.91% | 75.00% | 100.00% | 2560.4 | 8.0 | 0.00% | 950.1 | 60814 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 874.9 | 301.0 | 0.00% | 447.7 | 9792 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 999.2 | 1477.9 | 0.00% | 392.1 | 9794 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 865.6 | 1540.6 | 0.00% | 452.6 | 9794 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 1050.2 | 2.5 | 0.00% | 723.9 | 19006 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1603.9 | 3818.1 | 4.55% | 237.9 | 9538 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 1950.6 | 0.4 | 6.90% | 135.5 | 6607 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 962.9 | 2.5 | 0.00% | 1988.6 | 47870 | 86.826 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 528.8 | 301.0 | 0.00% | 747.8 | 9886 | 80.279 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 1050.2 | 2.5 | 0.00% | 723.9 | 19006 | 77.417 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3409.2 | 8.0 | 0.00% | 721.9 | 61531 | 76.923 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 874.9 | 301.0 | 0.00% | 447.7 | 9792 | 75.179 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 865.6 | 1540.6 | 0.00% | 452.6 | 9794 | 72.719 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 999.2 | 1477.9 | 0.00% | 392.1 | 9794 | 72.577 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 70.00% | 90.91% | 75.00% | 100.00% | 2560.4 | 8.0 | 0.00% | 950.1 | 60814 | 70.462 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 1950.6 | 0.4 | 6.90% | 135.5 | 6607 | 57.672 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 8852.4 | 2.5 | 0.00% | 129.6 | 28677 | 56.540 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1603.9 | 3818.1 | 4.55% | 237.9 | 9538 | 54.700 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 962.9 | 2.5 | 0.00% | 1988.6 | 47870 | 86.831 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 1050.2 | 2.5 | 0.00% | 723.9 | 19006 | 77.422 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3409.2 | 8.0 | 0.00% | 721.9 | 61531 | 76.939 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 70.00% | 90.91% | 75.00% | 100.00% | 2560.4 | 8.0 | 0.00% | 950.1 | 60814 | 70.478 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 8852.4 | 2.5 | 0.00% | 129.6 | 28677 | 56.545 |

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 962.9 | 2.5 | 0.00% | 1988.6 | 47870 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 528.8 | 301.0 | 0.00% | 747.8 | 9886 |
| openrouter-claude-sonnet-4-6 | openrouter | anthropic/claude-sonnet-4-6 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 3409.2 | 8.0 | 0.00% | 721.9 | 61531 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 8852.4 | 2.5 | 0.00% | 129.6 | 28677 |
| openrouter-claude-haiku-4-5 | openrouter | anthropic/claude-haiku-4-5 | LLM | 0.0 | 70.00% | 90.91% | 75.00% | 100.00% | 2560.4 | 8.0 | 0.00% | 950.1 | 60814 |
| local-qwen3-1.7b-llm-ctx4096 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 865.6 | 1540.6 | 0.00% | 452.6 | 9794 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 874.9 | 301.0 | 0.00% | 447.7 | 9792 |
| local-qwen3-1.7b-llm-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.0 | 70.00% | 81.82% | 100.00% | 100.00% | 999.2 | 1477.9 | 0.00% | 392.1 | 9794 |
| openrouter-gemini-2.5-flash-lite | openrouter | google/gemini-2.5-flash-lite | LLM | 0.0 | 60.00% | 86.36% | 75.00% | 100.00% | 1050.2 | 2.5 | 0.00% | 723.9 | 19006 |
| local-qwen3-8b-intent-ctx4096 | local | qwen/qwen3-8b | INTENT | 0.0 | 60.00% | 77.27% | 100.00% | 100.00% | 1603.9 | 3818.1 | 4.55% | 237.9 | 9538 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 1950.6 | 0.4 | 6.90% | 135.5 | 6607 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 6 | 937.0 | 528.8 | local-qwen3-1.7b-intent-ctx2048 |
| Remote | 5 | 2560.4 | 962.9 | openrouter-ministral-3b-2512 |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-ministral-3b-2512 | openrouter | mistralai/ministral-3b-2512 | LLM | 0.0 | 80.00% | 95.45% | 100.00% | 100.00% | 962.9 | 2.5 | 0.00% | 1988.6 | 47870 | 86.826 |
| local-qwen3-1.7b-intent-ctx2048 | local | qwen/qwen3-1.7b | INTENT | 0.0 | 80.00% | 86.36% | 100.00% | 100.00% | 528.8 | 301.0 | 0.00% | 747.8 | 9886 | 80.279 |
| local-qwen3-1.7b-llm-t0.3-ctx2048 | local | qwen/qwen3-1.7b | LLM | 0.3 | 70.00% | 81.82% | 100.00% | 100.00% | 874.9 | 301.0 | 0.00% | 447.7 | 9792 | 75.179 |
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.3 | 50.00% | 77.27% | 100.00% | 100.00% | 1950.6 | 0.4 | 6.90% | 135.5 | 6607 | 57.672 |
| openrouter-gemini-2.5-pro | openrouter | google/gemini-2.5-pro | LLM | 0.0 | 80.00% | 100.00% | 75.00% | 0.00% | 8852.4 | 2.5 | 0.00% | 129.6 | 28677 | 56.540 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) @ctx2048 | 70.00% | 80.00% | +10.00% | 81.82% | 86.36% | +4.54% | 73.878 | 80.279 | +6.401 |

## Context Window Coherence Sweep

- Near-peak ratio: 0.95
- Dropoff ratio: 0.90

| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf) | 2048, 4096 | 79.000 @ 2048 | 76.012 | 2048 | none | 73.33% | 801.0 | 693.3 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local | 1 | local-qwen3-1.7b-intent-ctx2048 | qwen/qwen3-1.7b | 0.0 | 80.00% | 80.279 |
| local | 2 | local-qwen3-1.7b-llm-t0.3-ctx2048 | qwen/qwen3-1.7b | 0.3 | 70.00% | 75.179 |
| local | 3 | local-qwen3-1.7b-llm-ctx4096 | qwen/qwen3-1.7b | 0.0 | 70.00% | 72.719 |
| local_server | 1 | ollama-llama3.2-3b | llama3.2:3b | 0.3 | 50.00% | 57.672 |
| openrouter | 1 | openrouter-ministral-3b-2512 | mistralai/ministral-3b-2512 | 0.0 | 80.00% | 86.826 |
| openrouter | 2 | openrouter-gemini-2.5-flash-lite | google/gemini-2.5-flash-lite | 0.0 | 60.00% | 77.417 |
| openrouter | 3 | openrouter-claude-sonnet-4-6 | anthropic/claude-sonnet-4-6 | 0.0 | 80.00% | 76.923 |

## Recommendations

- Best overall quality: `openrouter-gemini-2.5-pro` (google/gemini-2.5-pro)
- Best low-memory option: `openrouter-gemini-2.5-pro` (2.5 MB peak)
- Best throughput option: `openrouter-ministral-3b-2512` (1988.6 tokens/sec)
- Best remote option (memory-agnostic): `openrouter-ministral-3b-2512` (mistralai/ministral-3b-2512, score=86.831)
- Context recommendations (near-peak quality at lowest context):
  - `local/qwen/qwen3-1.7b (qwen3-1.7b-q4_k_m.gguf)` -> `n_ctx=2048` (dropoff: not observed)
- Routing gap summary: intent minus llm avg success delta = +10.00%
- Routing gap summary: intent minus llm avg score delta = +6.401
