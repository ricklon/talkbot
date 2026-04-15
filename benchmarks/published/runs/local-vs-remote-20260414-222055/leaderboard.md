# Benchmark Leaderboard

- Generated: 2026-04-14T22:38:49+0000
- Runs: 5
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `/home/cc/talkbot/benchmark_results/latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `coachable-robots-control` (Linux 5.15.0-174-generic, x86_64, py 3.12.13, linux-native)
- Network: `mixed`
- Runner notes: Local: qwen3.5-0.8b Q8 CPU llama-server vs Remote: OpenRouter (ministral-3b, gemma-4-26b, gemini-3.1-flash-lite, deepseek-chat)


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 103.9 | 103.3 | 147.1 | 200 |
| ollama-local | http://127.0.0.1:11434/api/tags | n/a | n/a | n/a | err: all samples failed |
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
| openrouter-gemini-3.1-flash-lite | openrouter | google/gemini-3.1-flash-lite-preview | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 1935.2 | 2.3 | 0.00% | 0.0 | 0.0 | 50491 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2164.6 | 2.3 | 0.00% | 0.0 | 0.0 | 50038 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4370.6 | 2.3 | 0.00% | 0.0 | 0.0 | 82416 |
| local-qwen35-0.8b-q8 | local_server | qwen3.5-0.8b-q8_0 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 30841.0 | 775.9 | 7.41% | 289.5 | 12.5 | 55457 |
| openrouter-ministral-3b | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 785.2 | 2.3 | 0.00% | 0.0 | 0.0 | 60281 |

## Low-Memory Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-3.1-flash-lite | openrouter | google/gemini-3.1-flash-lite-preview | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 1935.2 | 2.3 | 0.00% | 0.0 | 0.0 | 50491 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2164.6 | 2.3 | 0.00% | 0.0 | 0.0 | 50038 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4370.6 | 2.3 | 0.00% | 0.0 | 0.0 | 82416 |
| local-qwen35-0.8b-q8 | local_server | qwen3.5-0.8b-q8_0 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 30841.0 | 775.9 | 7.41% | 289.5 | 12.5 | 55457 |
| openrouter-ministral-3b | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 785.2 | 2.3 | 0.00% | 0.0 | 0.0 | 60281 |

## Balanced Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-3.1-flash-lite | openrouter | google/gemini-3.1-flash-lite-preview | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 1935.2 | 2.3 | 0.00% | 0.0 | 0.0 | 50491 | 96.125 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2164.6 | 2.3 | 0.00% | 0.0 | 0.0 | 50038 | 95.666 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4370.6 | 2.3 | 0.00% | 0.0 | 0.0 | 82416 | 91.254 |
| openrouter-ministral-3b | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 785.2 | 2.3 | 0.00% | 0.0 | 0.0 | 60281 | 90.682 |
| local-qwen35-0.8b-q8 | local_server | qwen3.5-0.8b-q8_0 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 30841.0 | 775.9 | 7.41% | 289.5 | 12.5 | 55457 | 35.284 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score (Remote) |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-3.1-flash-lite | openrouter | google/gemini-3.1-flash-lite-preview | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 1935.2 | 2.3 | 0.00% | 0.0 | 0.0 | 50491 | 96.130 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2164.6 | 2.3 | 0.00% | 0.0 | 0.0 | 50038 | 95.671 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4370.6 | 2.3 | 0.00% | 0.0 | 0.0 | 82416 | 91.259 |
| openrouter-ministral-3b | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 785.2 | 2.3 | 0.00% | 0.0 | 0.0 | 60281 | 90.686 |

## Efficiency Rank

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-qwen35-0.8b-q8 | local_server | qwen3.5-0.8b-q8_0 | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 30841.0 | 775.9 | 7.41% | 289.5 | 12.5 | 55457 |
| openrouter-gemini-3.1-flash-lite | openrouter | google/gemini-3.1-flash-lite-preview | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 1935.2 | 2.3 | 0.00% | 0.0 | 0.0 | 50491 |
| openrouter-gemma-4-26b | openrouter | google/gemma-4-26b-a4b-it | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 2164.6 | 2.3 | 0.00% | 0.0 | 0.0 | 50038 |
| openrouter-deepseek-chat | openrouter | deepseek/deepseek-chat | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 4370.6 | 2.3 | 0.00% | 0.0 | 0.0 | 82416 |
| openrouter-ministral-3b | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 785.2 | 2.3 | 0.00% | 0.0 | 0.0 | 60281 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 1 | 30841.0 | 30841.0 | local-qwen35-0.8b-q8 |
| Remote | 4 | 2049.9 | 785.2 | openrouter-ministral-3b |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Prompt | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Pfill/s | Gen/s | Tokens | Score |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| openrouter-gemini-3.1-flash-lite | openrouter | google/gemini-3.1-flash-lite-preview | default | LLM | 0.0 | 100.00% | 100.00% | 100.00% | 100.00% | 1935.2 | 2.3 | 0.00% | 0.0 | 0.0 | 50491 | 96.125 |
| openrouter-ministral-3b | openrouter | mistralai/ministral-3b-2512 | default | LLM | 0.0 | 90.00% | 95.45% | 100.00% | 100.00% | 785.2 | 2.3 | 0.00% | 0.0 | 0.0 | 60281 | 90.682 |

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
| local_server | 1 | local-qwen35-0.8b-q8 | qwen3.5-0.8b-q8_0 | 0.0 | 100.00% | 35.284 |
| openrouter | 1 | openrouter-gemini-3.1-flash-lite | google/gemini-3.1-flash-lite-preview | 0.0 | 100.00% | 96.125 |
| openrouter | 2 | openrouter-gemma-4-26b | google/gemma-4-26b-a4b-it | 0.0 | 100.00% | 95.666 |
| openrouter | 3 | openrouter-deepseek-chat | deepseek/deepseek-chat | 0.0 | 100.00% | 91.254 |

## Recommendations

- Best overall quality: `openrouter-gemini-3.1-flash-lite` (google/gemini-3.1-flash-lite-preview)
- Best low-memory option: `openrouter-gemini-3.1-flash-lite` (2.3 MB peak)
- Best throughput option: `local-qwen35-0.8b-q8` (12.5 gen tok/s)
- Best remote option (memory-agnostic): `openrouter-gemini-3.1-flash-lite` (google/gemini-3.1-flash-lite-preview, score=96.130)

## TTS Friction

- `Avg Friction`: mean count of TTS-hostile tokens per turn (lower is better).
- `Clean Rate`: fraction of turns with zero friction (higher is better).

| Run | Avg Friction | Clean Rate |
|---|---:|---:|
| openrouter-gemini-3.1-flash-lite | 0.36 | 76.0% |
| openrouter-gemma-4-26b | 0.44 | 72.0% |
| openrouter-deepseek-chat | 0.32 | 80.0% |
| local-qwen35-0.8b-q8 | 0.48 | 80.0% |
| openrouter-ministral-3b | 1.92 | 32.0% |

## LLM Judge Scores

- Scores are 1–5 (higher is better). Evaluated by the judge model on a sample of turns.
- `Correctness`: did the response correctly address the request?
- `Spoken Quality`: is the response phrased naturally for voice output?

| Run | Correctness | Spoken Quality | Judge Calls |
|---|---:|---:|---:|
| openrouter-gemini-3.1-flash-lite | 4.92 | 4.76 | 25 |
| openrouter-gemma-4-26b | 4.88 | 4.64 | 25 |
| openrouter-deepseek-chat | 4.52 | 4.68 | 25 |
| local-qwen35-0.8b-q8 | 4.04 | 4.24 | 25 |
| openrouter-ministral-3b | 4.20 | 3.68 | 25 |
