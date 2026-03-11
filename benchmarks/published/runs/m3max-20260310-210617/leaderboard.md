# Benchmark Leaderboard

- Generated: 2026-03-10T21:09:09-0400
- Runs: 4
- Scenarios: 10
- Rubric version: 2026.m3max.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/Users/rianders/Documents/GitHub/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `UOES-0002.local` (Darwin 25.3.0, arm64, py 3.12.8, macos-native)
- Network: `wifi (Wi-Fi)`


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 137.7 | 125.2 | 193.8 | 200 |
| ollama-local | http://localhost:11434/api/tags | 18.2 | 17.6 | 21.3 | 200 |
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

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 786.6 | 0.4 | 0.00% | 21252.5 | 107.7 | 65531 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 80.00% | 90.91% | 66.67% | 100.00% | 872.3 | 0.4 | 0.00% | 20686.6 | 96.6 | 63319 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 40.00% | 59.09% | 50.00% | 0.00% | 2553.2 | 775.9 | 0.00% | 3486.7 | 39.6 | 29797 |
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 10.00% | 27.27% | 100.00% | 0.00% | 2605.2 | 775.9 | 0.00% | 3316.5 | 35.3 | 13210 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 786.6 | 0.4 | 0.00% | 21252.5 | 107.7 | 65531 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 80.00% | 90.91% | 66.67% | 100.00% | 872.3 | 0.4 | 0.00% | 20686.6 | 96.6 | 63319 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 40.00% | 59.09% | 50.00% | 0.00% | 2553.2 | 775.9 | 0.00% | 3486.7 | 39.6 | 29797 |
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 10.00% | 27.27% | 100.00% | 0.00% | 2605.2 | 775.9 | 0.00% | 3316.5 | 35.3 | 13210 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 786.6 | 0.4 | 0.00% | 21252.5 | 107.7 | 65531 | 85.684 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 80.00% | 90.91% | 66.67% | 100.00% | 872.3 | 0.4 | 0.00% | 20686.6 | 96.6 | 63319 | 81.105 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 40.00% | 59.09% | 50.00% | 0.00% | 2553.2 | 775.9 | 0.00% | 3486.7 | 39.6 | 29797 | 34.993 |
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 10.00% | 27.27% | 100.00% | 0.00% | 2605.2 | 775.9 | 0.00% | 3316.5 | 35.3 | 13210 | 20.525 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

No remote-provider runs found in this report.

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 786.6 | 0.4 | 0.00% | 21252.5 | 107.7 | 65531 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 80.00% | 90.91% | 66.67% | 100.00% | 872.3 | 0.4 | 0.00% | 20686.6 | 96.6 | 63319 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 40.00% | 59.09% | 50.00% | 0.00% | 2553.2 | 775.9 | 0.00% | 3486.7 | 39.6 | 29797 |
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 10.00% | 27.27% | 100.00% | 0.00% | 2605.2 | 775.9 | 0.00% | 3316.5 | 35.3 | 13210 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 4 | 1712.7 | 786.6 | qwen3.5-2b-q4km-llm |
| Remote | 0 | n/a | n/a | n/a |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 786.6 | 0.4 | 0.00% | 21252.5 | 107.7 | 65531 | 85.684 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 80.00% | 90.91% | 66.67% | 100.00% | 872.3 | 0.4 | 0.00% | 20686.6 | 96.6 | 63319 | 81.105 |
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 10.00% | 27.27% | 100.00% | 0.00% | 2605.2 | 775.9 | 0.00% | 3316.5 | 35.3 | 13210 | 20.525 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server/qwen/qwen3.5-0.8b (qwen3.5-0.8b-q8_0.gguf) @ctx0 | 10.00% | 40.00% | +30.00% | 27.27% | 59.09% | +31.82% | 20.525 | 34.993 | +14.468 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local_server | 1 | qwen3.5-2b-q4km-llm | qwen/qwen3.5-2b | 0.0 | 90.00% | 85.684 |
| local_server | 2 | qwen3.5-0.8b-q4km-llm | qwen/qwen3.5-0.8b | 0.0 | 80.00% | 81.105 |
| local_server | 3 | qwen3.5-0.8b-q8-intent | qwen/qwen3.5-0.8b | 0.0 | 40.00% | 34.993 |

## Recommendations

- Best overall quality: `qwen3.5-2b-q4km-llm` (qwen/qwen3.5-2b)
- Best low-memory option: `qwen3.5-2b-q4km-llm` (0.4 MB peak)
- Best throughput option: `qwen3.5-2b-q4km-llm` (107.7 gen tok/s)
- Routing gap summary: intent minus llm avg success delta = +30.00%
- Routing gap summary: intent minus llm avg score delta = +14.468

## TTS Friction

- `Avg Friction`: mean count of TTS-hostile tokens per turn (lower is better).
- `Clean Rate`: fraction of turns with zero friction (higher is better).

| Run | Avg Friction | Clean Rate |
|---|---:|---:|
| qwen3.5-2b-q4km-llm | 1.08 | 60.0% |
| qwen3.5-0.8b-q4km-llm | 1.60 | 56.0% |
| qwen3.5-0.8b-q8-intent | 1.80 | 52.0% |
| qwen3.5-0.8b-q8-llm | 1.52 | 56.0% |
