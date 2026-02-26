# Benchmark Decision Strategy

Last updated: February 26, 2026

Use this guide with `benchmark_results/leaderboard.md` to choose between local and remote models.

## Core Goal

- Keep evaluations apples-to-apples for tool use.
- Prefer native OpenAI-style tool calling (`tools` + `tool_choice`) for comparison runs.
- Use intent routing only as a control ceiling, not as primary capability scoring.

## Key Metrics

- `task_success_rate`: end-to-end scenario success.
- `tool_selection_accuracy`: did it choose the correct tool.
- `argument_accuracy`: did it call tools with valid arguments.
- `avg_turn_latency_ms`: perceived responsiveness.
- `tool_call_error_rate`: tool execution reliability.
- `model_execution_error_rate`: provider/model transport failures.

Latency is a primary decision metric:
- Lower `avg_turn_latency_ms` improves UX immediately.
- Compare `Local` vs `Remote` with the leaderboard section:
  - `Latency Snapshot (Local vs Remote)`.

## Local vs Remote Decision Rules

1. Choose `Local` when:
- You need privacy/offline behavior.
- You can afford local RAM/CPU usage.
- You want stable, deterministic behavior without provider routing drift.

2. Choose `Remote` when:
- You want to avoid local memory pressure.
- You need easy model switching.
- You can tolerate provider/network variability.

3. For remote ranking:
- Use the leaderboard’s `Remote Rank (No Memory Penalty)`.
- Do not compare local memory numbers against remote process RSS.

## Standard Tool-Calling Policy

To force native tool-calling compatibility in OpenRouter benchmarks:

```bash
export TALKBOT_OPENROUTER_TOOL_TRANSPORT=native
export TALKBOT_OPENROUTER_TOOL_PREFLIGHT=1
```

This fails fast for models/routes that do not advertise native `tools` + `tool_choice`.

## Practical Workflow

1. Run matrix benchmark.
2. Check `Quality Rank` and `Remote Rank (No Memory Penalty)`.
3. Check `Latency Snapshot (Local vs Remote)`.
4. Validate failure modes in per-scenario assertions.
5. Pick one primary local and one primary remote model.
6. Re-run after prompt/tool updates and compare deltas.
