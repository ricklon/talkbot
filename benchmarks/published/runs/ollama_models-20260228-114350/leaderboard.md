# Benchmark Leaderboard

- Generated: 2026-02-28T11:49:43-0500
- Runs: 6
- Scenarios: 10
- Rubric version: 2026.full-suite.v1

## Scope

- Canonical latest leaderboard: `benchmark_results/leaderboard.md`
- Canonical latest JSON: `benchmark_results/results.json`
- Latest run snapshot path: `D:\Projects\GitHub\talkbot\benchmark_results\latest`
- Archived run folders: `benchmark_results/<run_name>/leaderboard.md`
- Runner: `win-dev` (Windows 11, AMD64, py 3.12.12)
- Network: `unknown`


## Endpoint Latency (TTFB)

- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.
- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.

| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |
|---|---|---:|---:|---:|---:|
| openrouter | https://openrouter.ai/api/v1/models | 131.8 | 91.4 | 167.1 | 200 |
| ollama-local | http://localhost:11434/api/tags | 5035.6 | 5026.0 | 5038.2 | 200 |
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
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 40.00% | 72.73% | 100.00% | 0.00% | 1243.9 | 0.4 | 4.00% | 276.9 | 8611 |
| ollama-mistral-nemo-12b | local_server | mistral-nemo:latest | LLM | 0.0 | 30.00% | 59.09% | 100.00% | 0.00% | 8053.1 | 0.4 | 5.56% | 241.3 | 48571 |
| ollama-phi4-mini | local_server | phi4-mini:latest | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 763.3 | 0.3 | 0.00% | 2656.6 | 50692 |
| ollama-gemma3-4b | local_server | gemma3:4b | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 765.0 | 0.3 | 0.00% | 213.1 | 4075 |
| ollama-deepseek-r1-1.5b | local_server | deepseek-r1:1.5b | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 2612.8 | 0.4 | 0.00% | 218.0 | 14238 |
| ollama-ministral-3b | local_server | ministral-3b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 39.5 | 0.4 | 0.00% | 0.0 | 0 |

## Low-Memory Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 40.00% | 72.73% | 100.00% | 0.00% | 1243.9 | 0.4 | 4.00% | 276.9 | 8611 |
| ollama-mistral-nemo-12b | local_server | mistral-nemo:latest | LLM | 0.0 | 30.00% | 59.09% | 100.00% | 0.00% | 8053.1 | 0.4 | 5.56% | 241.3 | 48571 |
| ollama-phi4-mini | local_server | phi4-mini:latest | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 763.3 | 0.3 | 0.00% | 2656.6 | 50692 |
| ollama-gemma3-4b | local_server | gemma3:4b | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 765.0 | 0.3 | 0.00% | 213.1 | 4075 |
| ollama-ministral-3b | local_server | ministral-3b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 39.5 | 0.4 | 0.00% | 0.0 | 0 |
| ollama-deepseek-r1-1.5b | local_server | deepseek-r1:1.5b | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 2612.8 | 0.4 | 0.00% | 218.0 | 14238 |

## Balanced Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 40.00% | 72.73% | 100.00% | 0.00% | 1243.9 | 0.4 | 4.00% | 276.9 | 8611 | 40.257 |
| ollama-mistral-nemo-12b | local_server | mistral-nemo:latest | LLM | 0.0 | 30.00% | 59.09% | 100.00% | 0.00% | 8053.1 | 0.4 | 5.56% | 241.3 | 48571 | 20.099 |
| ollama-phi4-mini | local_server | phi4-mini:latest | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 763.3 | 0.3 | 0.00% | 2656.6 | 50692 | 13.473 |
| ollama-gemma3-4b | local_server | gemma3:4b | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 765.0 | 0.3 | 0.00% | 213.1 | 4075 | 13.469 |
| ollama-deepseek-r1-1.5b | local_server | deepseek-r1:1.5b | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 2612.8 | 0.4 | 0.00% | 218.0 | 14238 | 9.774 |
| ollama-ministral-3b | local_server | ministral-3b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 39.5 | 0.4 | 0.00% | 0.0 | 0 | -30.080 |

## Remote Rank (No Memory Penalty)

- Purpose: compare hosted/API models without penalizing local process RSS.
- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.

No remote-provider runs found in this report.

## Efficiency Rank

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 40.00% | 72.73% | 100.00% | 0.00% | 1243.9 | 0.4 | 4.00% | 276.9 | 8611 |
| ollama-mistral-nemo-12b | local_server | mistral-nemo:latest | LLM | 0.0 | 30.00% | 59.09% | 100.00% | 0.00% | 8053.1 | 0.4 | 5.56% | 241.3 | 48571 |
| ollama-phi4-mini | local_server | phi4-mini:latest | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 763.3 | 0.3 | 0.00% | 2656.6 | 50692 |
| ollama-deepseek-r1-1.5b | local_server | deepseek-r1:1.5b | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 2612.8 | 0.4 | 0.00% | 218.0 | 14238 |
| ollama-gemma3-4b | local_server | gemma3:4b | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 765.0 | 0.3 | 0.00% | 213.1 | 4075 |
| ollama-ministral-3b | local_server | ministral-3b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 39.5 | 0.4 | 0.00% | 0.0 | 0 |

## Latency Snapshot (Local vs Remote)

- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.

| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |
|---|---:|---:|---:|---|
| Local | 6 | 1004.4 | 39.5 | ollama-ministral-3b |
| Remote | 0 | n/a | n/a | n/a |

## Pareto Frontier (Quality/Latency/Memory)

| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ollama-llama3.2-3b | local_server | llama3.2:3b | LLM | 0.0 | 40.00% | 72.73% | 100.00% | 0.00% | 1243.9 | 0.4 | 4.00% | 276.9 | 8611 | 40.257 |
| ollama-mistral-nemo-12b | local_server | mistral-nemo:latest | LLM | 0.0 | 30.00% | 59.09% | 100.00% | 0.00% | 8053.1 | 0.4 | 5.56% | 241.3 | 48571 | 20.099 |
| ollama-phi4-mini | local_server | phi4-mini:latest | LLM | 0.0 | 0.00% | 0.00% | 100.00% | 0.00% | 763.3 | 0.3 | 0.00% | 2656.6 | 50692 | 13.473 |
| ollama-ministral-3b | local_server | ministral-3b | LLM | 0.0 | 0.00% | 0.00% | 0.00% | 0.00% | 39.5 | 0.4 | 0.00% | 0.0 | 0 | -30.080 |

## Tool Routing A/B (Will vs Can)

- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)
- `Intent`: deterministic routing enabled (can the system force tool success?)

No matched LLM/Intent profile pairs found. Add profiles with the same model + context and `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` (LLM) and `1` (Intent).

## Top 3 Per Provider

| Provider | Rank | Run | Model | Temp | Success | Score |
|---|---:|---|---|---:|---:|---:|
| local_server | 1 | ollama-llama3.2-3b | llama3.2:3b | 0.0 | 40.00% | 40.257 |
| local_server | 2 | ollama-mistral-nemo-12b | mistral-nemo:latest | 0.0 | 30.00% | 20.099 |
| local_server | 3 | ollama-phi4-mini | phi4-mini:latest | 0.0 | 0.00% | 13.473 |

## Recommendations

- Best overall quality: `ollama-llama3.2-3b` (llama3.2:3b)
- Best low-memory option: `ollama-llama3.2-3b` (0.4 MB peak)
- Best throughput option: `ollama-llama3.2-3b` (276.9 tokens/sec)
