# Benchmark Leaderboard

- Generated: 2026-03-10T21:44:31-0400
- Runs: 4
- Scenarios: 5
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
| openrouter | https://openrouter.ai/api/v1/models | 203.0 | 174.6 | 209.7 | 200 |
| ollama-local | http://localhost:11434/api/tags | 22.6 | 21.4 | 43.1 | 200 |
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
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 61.36% | 100.00% | 0.00% | 899.0 | 0.8 | 0.00% | 19799.3 | 103.4 | 268975 |
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 59.09% | 100.00% | 0.00% | 889.2 | 0.8 | 1.16% | 21829.7 | 103.5 | 279418 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 0.00% | 57.95% | 100.00% | 0.00% | 879.4 | 775.9 | 0.00% | 20741.5 | 102.2 | 283067 |
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 55.68% | 100.00% | 0.00% | 854.2 | 775.9 | 0.00% | 20331.1 | 104.1 | 272574 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 59.09% | 100.00% | 0.00% | 889.2 | 0.8 | 1.16% | 21829.7 | 103.5 | 279418 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 61.36% | 100.00% | 0.00% | 899.0 | 0.8 | 0.00% | 19799.3 | 103.4 | 268975 |
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 55.68% | 100.00% | 0.00% | 854.2 | 775.9 | 0.00% | 20331.1 | 104.1 | 272574 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 0.00% | 57.95% | 100.00% | 0.00% | 879.4 | 775.9 | 0.00% | 20741.5 | 102.2 | 283067 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 61.36% | 100.00% | 0.00% | 899.0 | 0.8 | 0.00% | 19799.3 | 103.4 | 268975 | 25.472 |
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 59.09% | 100.00% | 0.00% | 889.2 | 0.8 | 1.16% | 21829.7 | 103.5 | 279418 | 24.806 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 0.00% | 57.95% | 100.00% | 0.00% | 879.4 | 775.9 | 0.00% | 20741.5 | 102.2 | 283067 | 23.279 |
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 55.68% | 100.00% | 0.00% | 854.2 | 775.9 | 0.00% | 20331.1 | 104.1 | 272574 | 22.876 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

No remote-provider runs found in this report.

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 55.68% | 100.00% | 0.00% | 854.2 | 775.9 | 0.00% | 20331.1 | 104.1 | 272574 |
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 59.09% | 100.00% | 0.00% | 889.2 | 0.8 | 1.16% | 21829.7 | 103.5 | 279418 |
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 61.36% | 100.00% | 0.00% | 899.0 | 0.8 | 0.00% | 19799.3 | 103.4 | 268975 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 0.00% | 57.95% | 100.00% | 0.00% | 879.4 | 775.9 | 0.00% | 20741.5 | 102.2 | 283067 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 4 | 884.3 | 854.2 | qwen3.5-0.8b-q8-llm |
| Remote | 0 | n/a | n/a | n/a |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.5-0.8b-q4km-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 61.36% | 100.00% | 0.00% | 899.0 | 0.8 | 0.00% | 19799.3 | 103.4 | 268975 | 25.472 |
| qwen3.5-2b-q4km-llm | local_server | qwen/qwen3.5-2b | LLM | 0.0 | 0.00% | 59.09% | 100.00% | 0.00% | 889.2 | 0.8 | 1.16% | 21829.7 | 103.5 | 279418 | 24.806 |
| qwen3.5-0.8b-q8-intent | local_server | qwen/qwen3.5-0.8b | INTENT | 0.0 | 0.00% | 57.95% | 100.00% | 0.00% | 879.4 | 775.9 | 0.00% | 20741.5 | 102.2 | 283067 | 23.279 |
| qwen3.5-0.8b-q8-llm | local_server | qwen/qwen3.5-0.8b | LLM | 0.0 | 0.00% | 55.68% | 100.00% | 0.00% | 854.2 | 775.9 | 0.00% | 20331.1 | 104.1 | 272574 | 22.876 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local_server/qwen/qwen3.5-0.8b (qwen3.5-0.8b-q8_0.gguf) @ctx0 | 0.00% | 0.00% | +0.00% | 55.68% | 57.95% | +2.27% | 22.876 | 23.279 | +0.403 |

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local_server | 1 | qwen3.5-0.8b-q4km-llm | qwen/qwen3.5-0.8b | 0.0 | 0.00% | 25.472 |
| local_server | 2 | qwen3.5-2b-q4km-llm | qwen/qwen3.5-2b | 0.0 | 0.00% | 24.806 |
| local_server | 3 | qwen3.5-0.8b-q8-intent | qwen/qwen3.5-0.8b | 0.0 | 0.00% | 23.279 |

## Recommendations

- Best overall quality: `qwen3.5-0.8b-q4km-llm` (qwen/qwen3.5-0.8b)
- Best low-memory option: `qwen3.5-2b-q4km-llm` (0.8 MB peak)
- Best throughput option: `qwen3.5-0.8b-q8-llm` (104.1 gen tok/s)
- Routing gap summary: intent minus llm avg success delta = +0.00%
- Routing gap summary: intent minus llm avg score delta = +0.403

## TTS Friction

- `Avg Friction`: mean count of TTS-hostile tokens per turn (lower is better).
- `Clean Rate`: fraction of turns with zero friction (higher is better).

| Run | Avg Friction | Clean Rate |
|---|---:|---:|
| qwen3.5-0.8b-q4km-llm | 3.46 | 59.0% |
| qwen3.5-2b-q4km-llm | 3.40 | 59.0% |
| qwen3.5-0.8b-q8-intent | 3.81 | 61.1% |
| qwen3.5-0.8b-q8-llm | 3.31 | 51.6% |

## Reliability Bands (pass^k)

- Bands: **high** ≥80 %, **medium** 50–79 %, **low** 20–49 %, **very-low** <20 %.

| Run | High | Medium | Low | Very-Low | Avg Pass Rate |
|---|---:|---:|---:|---:|---:|
| qwen3.5-0.8b-q4km-llm | 0 | 0 | 5 | 0 | 0.0% |
| qwen3.5-2b-q4km-llm | 0 | 0 | 5 | 0 | 0.0% |
| qwen3.5-0.8b-q8-intent | 0 | 0 | 5 | 0 | 0.0% |
| qwen3.5-0.8b-q8-llm | 0 | 0 | 5 | 0 | 0.0% |

## Endurance

- `Endurance Scen`: number of endurance-tagged scenarios run.
- `Latency Growth`: average ms/turn slope across endurance scenarios (positive = slowing down).

| Run | Endurance Scen | Latency Growth (ms/turn) |
|---|---:|---:|
| qwen3.5-0.8b-q4km-llm | 5 | -11.1 |
| qwen3.5-2b-q4km-llm | 5 | +9.4 |
| qwen3.5-0.8b-q8-intent | 5 | -2.4 |
| qwen3.5-0.8b-q8-llm | 5 | -5.9 |
