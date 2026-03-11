# Benchmark Leaderboard

- Generated: 2026-03-10T21:08:29-0400
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
| openrouter | https://openrouter.ai/api/v1/models | 150.9 | 136.4 | 206.5 | 200 |
| ollama-local | http://localhost:11434/api/tags | 22.4 | 21.5 | 44.4 | 200 |
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
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 657.9 | 775.9 | 0.00% | 40032.6 | 108.4 | 65531 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 660.6 | 775.9 | 0.00% | 40101.6 | 107.5 | 65531 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 30.00% | 54.55% | 50.00% | 0.00% | 2070.3 | 0.4 | 0.00% | 13001.9 | 39.3 | 32587 |
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 4.55% | 100.00% | 0.00% | 3524.1 | 0.4 | 0.00% | 2899.3 | 30.5 | 9047 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 657.9 | 775.9 | 0.00% | 40032.6 | 108.4 | 65531 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 660.6 | 775.9 | 0.00% | 40101.6 | 107.5 | 65531 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 30.00% | 54.55% | 50.00% | 0.00% | 2070.3 | 0.4 | 0.00% | 13001.9 | 39.3 | 32587 |
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 4.55% | 100.00% | 0.00% | 3524.1 | 0.4 | 0.00% | 2899.3 | 30.5 | 9047 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 657.9 | 775.9 | 0.00% | 40032.6 | 108.4 | 65531 | 84.390 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 660.6 | 775.9 | 0.00% | 40101.6 | 107.5 | 65531 | 84.385 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 30.00% | 54.55% | 50.00% | 0.00% | 2070.3 | 0.4 | 0.00% | 13001.9 | 39.3 | 32587 | 28.102 |
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 4.55% | 100.00% | 0.00% | 3524.1 | 0.4 | 0.00% | 2899.3 | 30.5 | 9047 | 8.861 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

No remote-provider runs found in this report.

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 657.9 | 775.9 | 0.00% | 40032.6 | 108.4 | 65531 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 660.6 | 775.9 | 0.00% | 40101.6 | 107.5 | 65531 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 30.00% | 54.55% | 50.00% | 0.00% | 2070.3 | 0.4 | 0.00% | 13001.9 | 39.3 | 32587 |
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 4.55% | 100.00% | 0.00% | 3524.1 | 0.4 | 0.00% | 2899.3 | 30.5 | 9047 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 4 | 1365.4 | 657.9 | qwen3.5-0.8b-q8-llm |
| Remote | 0 | n/a | n/a | n/a |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 90.00% | 95.45% | 66.67% | 100.00% | 657.9 | 775.9 | 0.00% | 40032.6 | 108.4 | 65531 | 84.390 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 30.00% | 54.55% | 50.00% | 0.00% | 2070.3 | 0.4 | 0.00% | 13001.9 | 39.3 | 32587 | 28.102 |
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 4.55% | 100.00% | 0.00% | 3524.1 | 0.4 | 0.00% | 2899.3 | 30.5 | 9047 | 8.861 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server/qwen/qwen3.5-0.8b (qwen3.5-0.8b-q8_0.gguf) @ctx0 | 90.00% | 90.00% | +0.00% | 95.45% | 95.45% | +0.00% | 84.390 | 84.385 | -0.005 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local_server | 1 | qwen3.5-0.8b-q8-llm | qwen/qwen3.5-0.8b | 0.0 | 90.00% | 84.390 |
| local_server | 2 | qwen3.5-0.8b-q8-intent | qwen/qwen3.5-0.8b | 0.0 | 90.00% | 84.385 |
| local_server | 3 | qwen3.5-0.8b-q4km-llm | qwen/qwen3.5-0.8b | 0.0 | 30.00% | 28.102 |

## Recommendations

- Best overall quality: `qwen3.5-0.8b-q8-llm` (qwen/qwen3.5-0.8b)
- Best low-memory option: `qwen3.5-0.8b-q8-llm` (775.9 MB peak)
- Best throughput option: `qwen3.5-0.8b-q8-llm` (108.4 gen tok/s)
- Routing gap summary: intent minus llm avg success delta = +0.00%
- Routing gap summary: intent minus llm avg score delta = -0.005

## TTS Friction

- `Avg Friction`: mean count of TTS-hostile tokens per turn (lower is better).
- `Clean Rate`: fraction of turns with zero friction (higher is better).

| Run | Avg Friction | Clean Rate |
|---|---:|---:|
| qwen3.5-0.8b-q8-llm | 1.08 | 60.0% |
| qwen3.5-0.8b-q8-intent | 1.08 | 60.0% |
| qwen3.5-0.8b-q4km-llm | 1.44 | 52.0% |
| qwen3.5-2b-q4km-llm | 2.40 | 48.0% |
