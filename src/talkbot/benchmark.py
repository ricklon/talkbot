"""Conversation benchmark runner for tool-enabled TalkBot models.

This module executes scripted multi-turn conversations, validates expected
tool behavior, and produces leaderboard-friendly metrics.
"""

from __future__ import annotations

import json
import os
import re
import statistics
import sys
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from talkbot.llm import create_llm_client, supports_tools
from talkbot.tools import TOOL_DEFINITIONS, TOOLS, reset_runtime_state

try:
    import resource
except Exception:  # pragma: no cover - platform-dependent
    resource = None


@dataclass
class BenchmarkProfile:
    """Single model/runtime configuration to benchmark."""

    name: str
    provider: str
    model: str
    api_key: str | None = None
    local_model_path: str | None = None
    llamacpp_bin: str | None = None
    local_server_url: str | None = None
    local_server_api_key: str | None = None
    enable_thinking: bool = False
    use_tools: bool = True
    max_tokens: int = 512
    temperature: float = 0.0
    env: dict[str, str] = field(default_factory=dict)


@dataclass
class ToolCallTrace:
    scenario_id: str
    turn_index: int
    name: str
    args: dict[str, Any]
    result: str
    error: str | None
    latency_ms: float


@dataclass
class TurnResult:
    index: int
    user: str
    response: str
    passed: bool
    assertions: list[str]
    latency_ms: float
    tool_calls: list[dict[str, Any]]
    usage: dict[str, Any]
    history_messages: int
    history_chars: int


@dataclass
class ScenarioResult:
    id: str
    name: str
    tags: list[str]
    passed: bool
    turns: list[TurnResult]
    turn_count: int
    passed_turns: int
    expected_tool_calls: int
    matched_tool_names: int
    expected_arg_checks: int
    matched_arg_checks: int
    actual_tool_calls: int


@dataclass
class RunAggregate:
    scenario_count: int
    scenario_passed: int
    task_success_rate: float
    total_turns: int
    avg_turn_latency_ms: float
    p95_turn_latency_ms: float
    avg_turns_to_success: float
    expected_tool_calls: int
    matched_tool_names: int
    tool_selection_accuracy: float
    expected_arg_checks: int
    matched_arg_checks: int
    argument_accuracy: float
    actual_tool_calls: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    max_history_messages: int
    max_history_chars: int
    cpu_time_s: float
    python_peak_mb: float
    process_rss_delta_mb: float
    memory_peak_mb: float
    tag_success: dict[str, float]


@dataclass
class RunResult:
    profile: BenchmarkProfile
    status: str
    error: str | None
    started_at: str
    duration_s: float
    aggregate: RunAggregate | None
    scenarios: list[ScenarioResult]
    tool_traces: list[ToolCallTrace]


class ToolRecorder:
    """Wraps registered tools and records tool call traces."""

    def __init__(self) -> None:
        self.active_scenario_id = ""
        self.active_turn_index = -1
        self.calls: list[ToolCallTrace] = []

    def wrap(self, name: str, func: Callable[..., Any]) -> Callable[..., Any]:
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            started = time.perf_counter()
            error: str | None = None
            result_text = ""
            named_args: dict[str, Any]
            if kwargs:
                named_args = dict(kwargs)
            elif args:
                named_args = {"_args": list(args)}
            else:
                named_args = {}
            try:
                result = func(*args, **kwargs)
                result_text = str(result)
                return result
            except Exception as exc:
                error = str(exc)
                result_text = f"Error: {exc}"
                raise
            finally:
                latency_ms = (time.perf_counter() - started) * 1000.0
                self.calls.append(
                    ToolCallTrace(
                        scenario_id=self.active_scenario_id,
                        turn_index=self.active_turn_index,
                        name=name,
                        args=_json_safe(named_args),
                        result=result_text,
                        error=error,
                        latency_ms=round(latency_ms, 3),
                    )
                )

        return _wrapped


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    return str(value)


def _response_content(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        message = choices[0].get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if content is None:
                return ""
            return content if isinstance(content, str) else str(content)
    error = response.get("error")
    if error:
        return f"Error: {error}"
    return ""


def _token_usage(usage: dict[str, Any]) -> tuple[int, int, int]:
    prompt = _to_int(usage.get("prompt_tokens") or usage.get("input_tokens"))
    completion = _to_int(usage.get("completion_tokens") or usage.get("output_tokens"))
    total = _to_int(usage.get("total_tokens")) or (prompt + completion)
    return prompt, completion, total


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _subset_match(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        for key, expected_value in expected.items():
            if key not in actual:
                return False
            if not _subset_match(actual[key], expected_value):
                return False
        return True
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) < len(expected):
            return False
        return all(_subset_match(a, e) for a, e in zip(actual, expected))
    if actual == expected:
        return True

    # Treat numeric strings and numbers as equivalent for benchmark assertions.
    if isinstance(actual, (int, float, str)) and isinstance(expected, (int, float, str)):
        try:
            return float(actual) == float(expected)
        except Exception:
            return str(actual) == str(expected)

    return False


def _percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 1.0
    return round(float(numerator) / float(denominator), 4)


_TOOL_ARG_ALIASES: dict[str, dict[str, str]] = {
    "set_timer": {
        "duration": "seconds",
        "time": "seconds",
        "secs": "seconds",
        "sec": "seconds",
    },
    "set_reminder": {
        "duration": "seconds",
        "time": "seconds",
    },
    "cancel_timer": {
        "id": "timer_id",
        "timer": "timer_id",
        "timerid": "timer_id",
    },
}


def _normalize_tool_args(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    mapping = _TOOL_ARG_ALIASES.get(tool_name, {})
    if not mapping:
        return dict(args)
    normalized = dict(args)
    for alias, canonical in mapping.items():
        if alias in normalized and canonical not in normalized:
            normalized[canonical] = normalized[alias]
    return normalized


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_scenarios(path: str | Path) -> list[dict[str, Any]]:
    """Load scenario JSON file(s) from a file path or directory."""
    base = Path(path)
    files: list[Path]
    if base.is_file():
        files = [base]
    else:
        files = sorted(base.glob("*.json"))
    scenarios: list[dict[str, Any]] = []
    for file in files:
        payload = _load_json(file)
        scenario = _normalize_scenario(payload, file)
        scenarios.append(scenario)
    if not scenarios:
        raise ValueError(f"No scenario JSON files found at '{base}'.")
    return scenarios


def _normalize_scenario(payload: dict[str, Any], source: Path) -> dict[str, Any]:
    sid = str(payload.get("id") or source.stem).strip()
    name = str(payload.get("name") or sid).strip()
    turns = payload.get("turns")
    if not isinstance(turns, list) or not turns:
        raise ValueError(f"Scenario '{sid}' has no turns.")
    normalized_turns = []
    for index, turn in enumerate(turns):
        if not isinstance(turn, dict):
            raise ValueError(f"Scenario '{sid}' turn {index} must be an object.")
        user = str(turn.get("user", "")).strip()
        if not user:
            raise ValueError(f"Scenario '{sid}' turn {index} missing 'user'.")
        expect = turn.get("expect") or {}
        if not isinstance(expect, dict):
            raise ValueError(f"Scenario '{sid}' turn {index} expect must be an object.")
        normalized_turns.append({"user": user, "expect": expect})
    tags = payload.get("tags") or []
    return {
        "id": sid,
        "name": name,
        "description": str(payload.get("description") or "").strip(),
        "tags": [str(tag) for tag in tags] if isinstance(tags, list) else [],
        "system_prompt": str(payload.get("system_prompt") or "").strip() or None,
        "reset_state": bool(payload.get("reset_state", True)),
        "turns": normalized_turns,
    }


def load_profiles_from_matrix(path: str | Path) -> list[BenchmarkProfile]:
    payload = _load_json(Path(path))
    raw_profiles: Any
    if isinstance(payload, list):
        raw_profiles = payload
    else:
        raw_profiles = payload.get("profiles") or payload.get("runs") or []
    if not isinstance(raw_profiles, list) or not raw_profiles:
        raise ValueError("Matrix must define a non-empty 'profiles' list.")
    profiles = [BenchmarkProfile(**dict(entry)) for entry in raw_profiles]
    return profiles


@contextmanager
def _patched_env(overrides: dict[str, str]):
    previous: dict[str, str | None] = {}
    for key, value in overrides.items():
        previous[key] = os.environ.get(key)
        os.environ[key] = str(value)
    try:
        yield
    finally:
        for key, old in previous.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old


def _process_rss_mb() -> float:
    if resource is None:
        return 0.0
    usage = resource.getrusage(resource.RUSAGE_SELF)
    raw = float(usage.ru_maxrss)
    if sys.platform == "darwin":
        return round(raw / (1024.0 * 1024.0), 3)
    return round(raw / 1024.0, 3)


def _register_traced_tools(client: Any, recorder: ToolRecorder) -> None:
    if hasattr(client, "clear_tools"):
        try:
            client.clear_tools()
        except Exception:
            pass
    for name, func in TOOLS.items():
        definition = TOOL_DEFINITIONS.get(name)
        if not definition:
            continue
        client.register_tool(
            name=name,
            func=recorder.wrap(name, func),
            description=definition["description"],
            parameters=definition["parameters"],
        )


def _evaluate_turn(
    turn: dict[str, Any],
    response: str,
    tool_calls: list[ToolCallTrace],
    latency_ms: float,
) -> tuple[bool, list[str], int, int, int, int]:
    expect = turn.get("expect") or {}
    assertions: list[str] = []
    expected_tool_names = 0
    matched_tool_names = 0
    expected_arg_checks = 0
    matched_arg_checks = 0

    contains = expect.get("response_contains") or []
    if isinstance(contains, list):
        for part in contains:
            part_text = str(part)
            if part_text not in response:
                assertions.append(f"Missing response text: {part_text!r}")

    regex = expect.get("response_regex")
    if regex:
        if re.search(str(regex), response) is None:
            assertions.append(f"Response does not match regex: {regex!r}")

    if expect.get("no_tool_calls") and tool_calls:
        assertions.append("Expected no tool calls, but at least one was executed.")

    expected_calls = expect.get("tool_calls") or []
    if isinstance(expected_calls, list):
        unmatched = list(tool_calls)
        for entry in expected_calls:
            if not isinstance(entry, dict):
                continue
            expected_tool_names += 1
            names: list[str]
            if "name_any" in entry and isinstance(entry["name_any"], list):
                names = [str(name) for name in entry["name_any"]]
            else:
                names = [str(entry.get("name", "")).strip()]
            names = [name for name in names if name]
            if not names:
                assertions.append("Expected tool call missing name/name_any.")
                continue
            match_index = next(
                (
                    idx
                    for idx, call in enumerate(unmatched)
                    if call.name in names
                ),
                -1,
            )
            if match_index < 0:
                assertions.append(f"Missing expected tool call: {names}")
                continue
            matched_tool_names += 1
            matched_call = unmatched.pop(match_index)

            args_contains = entry.get("args_contains")
            if isinstance(args_contains, dict):
                expected_arg_checks += 1
                normalized_args = _normalize_tool_args(
                    matched_call.name,
                    matched_call.args,
                )
                if _subset_match(normalized_args, args_contains):
                    matched_arg_checks += 1
                else:
                    assertions.append(
                        f"Tool args mismatch for {matched_call.name}: "
                        f"expected subset {args_contains}, got {matched_call.args}"
                    )

    min_tool_calls = expect.get("min_tool_calls")
    if min_tool_calls is not None and len(tool_calls) < _to_int(min_tool_calls):
        assertions.append(
            f"Expected at least {min_tool_calls} tool call(s), got {len(tool_calls)}."
        )
    max_tool_calls = expect.get("max_tool_calls")
    if max_tool_calls is not None and len(tool_calls) > _to_int(max_tool_calls):
        assertions.append(
            f"Expected at most {max_tool_calls} tool call(s), got {len(tool_calls)}."
        )

    max_latency_ms = expect.get("max_latency_ms")
    if max_latency_ms is not None and latency_ms > float(max_latency_ms):
        assertions.append(
            f"Turn latency {latency_ms:.1f}ms exceeded max {float(max_latency_ms):.1f}ms."
        )

    return (
        not assertions,
        assertions,
        expected_tool_names,
        matched_tool_names,
        expected_arg_checks,
        matched_arg_checks,
    )


def _default_client_factory(profile: BenchmarkProfile):
    return create_llm_client(
        provider=profile.provider,
        model=profile.model,
        api_key=profile.api_key,
        local_model_path=profile.local_model_path,
        llamacpp_bin=profile.llamacpp_bin,
        local_server_url=profile.local_server_url,
        local_server_api_key=profile.local_server_api_key,
        enable_thinking=profile.enable_thinking,
    )


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    return cleaned.strip("-") or "run"


def run_benchmark(
    *,
    profiles: list[BenchmarkProfile],
    scenarios: list[dict[str, Any]],
    output_dir: str | Path,
    client_factory: Callable[[BenchmarkProfile], Any] | None = None,
) -> dict[str, Any]:
    """Run all profiles against all scenarios and return a report dictionary."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    factory = client_factory or _default_client_factory
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    run_results: list[RunResult] = []
    for profile in profiles:
        run_started = time.perf_counter()
        cpu_started = time.process_time()
        rss_started = _process_rss_mb()
        tracemalloc.start()

        recorder = ToolRecorder()
        scenario_results: list[ScenarioResult] = []
        run_error: str | None = None
        status = "ok"

        run_state_dir = out_dir / "_state" / _safe_name(profile.name)
        env_overrides = dict(profile.env)
        env_overrides.setdefault("TALKBOT_DATA_DIR", str(run_state_dir))

        with _patched_env(env_overrides):
            try:
                with factory(profile) as client:
                    if profile.use_tools and supports_tools(client):
                        _register_traced_tools(client, recorder)
                    elif profile.use_tools:
                        raise RuntimeError("Client does not support tool registration.")

                    for scenario in scenarios:
                        if scenario.get("reset_state", True):
                            reset_runtime_state(clear_persistent=True)
                        messages: list[dict[str, str]] = []
                        if scenario.get("system_prompt"):
                            messages.append(
                                {"role": "system", "content": scenario["system_prompt"]}
                            )

                        turns: list[TurnResult] = []
                        expected_tool_calls = 0
                        matched_tool_names = 0
                        expected_arg_checks = 0
                        matched_arg_checks = 0
                        actual_tool_calls = 0

                        for turn_idx, turn in enumerate(scenario["turns"]):
                            recorder.active_scenario_id = scenario["id"]
                            recorder.active_turn_index = turn_idx
                            start_call_index = len(recorder.calls)

                            user_text = turn["user"]
                            messages.append({"role": "user", "content": user_text})
                            turn_started = time.perf_counter()
                            assertions: list[str] = []
                            response_text = ""
                            try:
                                if profile.use_tools:
                                    response_text = str(
                                        client.chat_with_tools(
                                            messages,
                                            temperature=profile.temperature,
                                            max_tokens=profile.max_tokens,
                                        )
                                        or ""
                                    ).strip()
                                else:
                                    response = client.chat_completion(
                                        messages,
                                        temperature=profile.temperature,
                                        max_tokens=profile.max_tokens,
                                    )
                                    response_text = _response_content(response).strip()
                            except Exception as exc:
                                assertions.append(f"Model execution error: {exc}")

                            latency_ms = round(
                                (time.perf_counter() - turn_started) * 1000.0, 3
                            )
                            turn_calls = recorder.calls[start_call_index:]
                            usage = dict(getattr(client, "last_usage", {}) or {})
                            if not assertions:
                                (
                                    passed,
                                    extra_assertions,
                                    exp_names,
                                    got_names,
                                    exp_args,
                                    got_args,
                                ) = _evaluate_turn(
                                    turn=turn,
                                    response=response_text,
                                    tool_calls=turn_calls,
                                    latency_ms=latency_ms,
                                )
                                assertions.extend(extra_assertions)
                            else:
                                passed = False
                                exp_names = 0
                                got_names = 0
                                exp_args = 0
                                got_args = 0

                            expected_tool_calls += exp_names
                            matched_tool_names += got_names
                            expected_arg_checks += exp_args
                            matched_arg_checks += got_args
                            actual_tool_calls += len(turn_calls)

                            if response_text:
                                messages.append(
                                    {"role": "assistant", "content": response_text}
                                )
                            history_chars = sum(
                                len(str(message.get("content", "")))
                                for message in messages
                            )
                            turns.append(
                                TurnResult(
                                    index=turn_idx,
                                    user=user_text,
                                    response=response_text,
                                    passed=passed and not assertions,
                                    assertions=assertions,
                                    latency_ms=latency_ms,
                                    tool_calls=[asdict(call) for call in turn_calls],
                                    usage=usage,
                                    history_messages=len(messages),
                                    history_chars=history_chars,
                                )
                            )

                        scenario_results.append(
                            ScenarioResult(
                                id=scenario["id"],
                                name=scenario["name"],
                                tags=list(scenario.get("tags") or []),
                                passed=all(turn.passed for turn in turns),
                                turns=turns,
                                turn_count=len(turns),
                                passed_turns=sum(1 for turn in turns if turn.passed),
                                expected_tool_calls=expected_tool_calls,
                                matched_tool_names=matched_tool_names,
                                expected_arg_checks=expected_arg_checks,
                                matched_arg_checks=matched_arg_checks,
                                actual_tool_calls=actual_tool_calls,
                            )
                        )
            except Exception as exc:
                status = "error"
                run_error = str(exc)

        _, tracemalloc_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        rss_ended = _process_rss_mb()
        run_duration = round(time.perf_counter() - run_started, 3)
        cpu_duration = round(time.process_time() - cpu_started, 3)

        aggregate: RunAggregate | None = None
        if status == "ok":
            aggregate = _build_aggregate(
                scenario_results=scenario_results,
                cpu_time_s=cpu_duration,
                python_peak_mb=round(tracemalloc_peak / (1024.0 * 1024.0), 3),
                process_rss_delta_mb=max(0.0, round(rss_ended - rss_started, 3)),
            )

        run_results.append(
            RunResult(
                profile=profile,
                status=status,
                error=run_error,
                started_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                duration_s=run_duration,
                aggregate=aggregate,
                scenarios=scenario_results,
                tool_traces=list(recorder.calls),
            )
        )

    report = {
        "started_at": started_at,
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "scenario_count": len(scenarios),
        "run_count": len(run_results),
        "runs": [_run_to_dict(run) for run in run_results],
    }
    return report


def _build_aggregate(
    *,
    scenario_results: list[ScenarioResult],
    cpu_time_s: float,
    python_peak_mb: float,
    process_rss_delta_mb: float,
) -> RunAggregate:
    all_turns = [turn for scenario in scenario_results for turn in scenario.turns]
    latencies = [turn.latency_ms for turn in all_turns]
    p95_latency = (
        statistics.quantiles(latencies, n=20)[18]
        if len(latencies) >= 2
        else (latencies[0] if latencies else 0.0)
    )

    scenario_count = len(scenario_results)
    passed_scenarios = sum(1 for scenario in scenario_results if scenario.passed)
    turns_to_success = [scenario.turn_count for scenario in scenario_results if scenario.passed]
    expected_tool_calls = sum(s.expected_tool_calls for s in scenario_results)
    matched_tool_names = sum(s.matched_tool_names for s in scenario_results)
    expected_arg_checks = sum(s.expected_arg_checks for s in scenario_results)
    matched_arg_checks = sum(s.matched_arg_checks for s in scenario_results)
    actual_tool_calls = sum(s.actual_tool_calls for s in scenario_results)

    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    max_history_messages = 0
    max_history_chars = 0
    for turn in all_turns:
        p, c, t = _token_usage(turn.usage)
        prompt_tokens += p
        completion_tokens += c
        total_tokens += t
        max_history_messages = max(max_history_messages, turn.history_messages)
        max_history_chars = max(max_history_chars, turn.history_chars)

    tag_totals: dict[str, int] = {}
    tag_passed: dict[str, int] = {}
    for scenario in scenario_results:
        for tag in scenario.tags:
            tag_totals[tag] = tag_totals.get(tag, 0) + 1
            if scenario.passed:
                tag_passed[tag] = tag_passed.get(tag, 0) + 1
    tag_success = {
        tag: _percent(tag_passed.get(tag, 0), total)
        for tag, total in sorted(tag_totals.items())
    }

    memory_peak_mb = round(max(python_peak_mb, process_rss_delta_mb), 3)
    return RunAggregate(
        scenario_count=scenario_count,
        scenario_passed=passed_scenarios,
        task_success_rate=_percent(passed_scenarios, scenario_count),
        total_turns=len(all_turns),
        avg_turn_latency_ms=round(statistics.fmean(latencies), 3) if latencies else 0.0,
        p95_turn_latency_ms=round(float(p95_latency), 3),
        avg_turns_to_success=(
            round(statistics.fmean(turns_to_success), 3) if turns_to_success else 0.0
        ),
        expected_tool_calls=expected_tool_calls,
        matched_tool_names=matched_tool_names,
        tool_selection_accuracy=_percent(matched_tool_names, expected_tool_calls),
        expected_arg_checks=expected_arg_checks,
        matched_arg_checks=matched_arg_checks,
        argument_accuracy=_percent(matched_arg_checks, expected_arg_checks),
        actual_tool_calls=actual_tool_calls,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        max_history_messages=max_history_messages,
        max_history_chars=max_history_chars,
        cpu_time_s=cpu_time_s,
        python_peak_mb=python_peak_mb,
        process_rss_delta_mb=process_rss_delta_mb,
        memory_peak_mb=memory_peak_mb,
        tag_success=tag_success,
    )


def _run_to_dict(run: RunResult) -> dict[str, Any]:
    return {
        "profile": asdict(run.profile),
        "status": run.status,
        "error": run.error,
        "started_at": run.started_at,
        "duration_s": run.duration_s,
        "aggregate": asdict(run.aggregate) if run.aggregate else None,
        "scenarios": [asdict(scenario) for scenario in run.scenarios],
        "tool_traces": [asdict(trace) for trace in run.tool_traces],
    }


def write_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    """Write JSON results and markdown leaderboard."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results_path = out / "results.json"
    leaderboard_path = out / "leaderboard.md"
    results_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    leaderboard_path.write_text(build_leaderboard_markdown(report), encoding="utf-8")
    return {"results": str(results_path), "leaderboard": str(leaderboard_path)}


def _balanced_score(aggregate: dict[str, Any]) -> float:
    success = float(aggregate.get("task_success_rate", 0.0))
    tool = float(aggregate.get("tool_selection_accuracy", 0.0))
    args = float(aggregate.get("argument_accuracy", 0.0))
    latency = float(aggregate.get("avg_turn_latency_ms", 0.0))
    memory = float(aggregate.get("memory_peak_mb", 0.0))
    return round(
        (success * 60.0) + (tool * 25.0) + (args * 15.0)
        - min(25.0, latency / 1000.0)
        - min(25.0, memory / 512.0),
        3,
    )


def build_leaderboard_markdown(report: dict[str, Any]) -> str:
    """Render a markdown leaderboard from run results."""
    runs = [run for run in report.get("runs", []) if run.get("status") == "ok"]
    if not runs:
        return "# Benchmark Leaderboard\n\nNo successful runs."

    quality_rank = sorted(
        runs,
        key=lambda run: (
            run["aggregate"]["task_success_rate"],
            run["aggregate"]["tool_selection_accuracy"],
            run["aggregate"]["argument_accuracy"],
            -run["aggregate"]["avg_turn_latency_ms"],
        ),
        reverse=True,
    )
    low_mem_rank = sorted(
        runs,
        key=lambda run: (
            run["aggregate"]["task_success_rate"],
            -run["aggregate"]["memory_peak_mb"],
            -run["aggregate"]["avg_turn_latency_ms"],
        ),
        reverse=True,
    )
    balanced_rank = sorted(
        runs,
        key=lambda run: _balanced_score(run["aggregate"]),
        reverse=True,
    )

    def row(run: dict[str, Any], include_score: bool = False) -> str:
        agg = run["aggregate"]
        score = _balanced_score(agg)
        base = (
            f"| {run['profile']['name']} | {run['profile']['provider']} | "
            f"{run['profile']['model']} | {agg['task_success_rate']:.2%} | "
            f"{agg['tool_selection_accuracy']:.2%} | {agg['argument_accuracy']:.2%} | "
            f"{agg['avg_turn_latency_ms']:.1f} | {agg['memory_peak_mb']:.1f} | "
            f"{agg['total_tokens']} |"
        )
        if include_score:
            base = base + f" {score:.3f} |"
        return base

    lines = [
        "# Benchmark Leaderboard",
        "",
        f"- Generated: {report.get('finished_at', '')}",
        f"- Runs: {report.get('run_count', 0)}",
        f"- Scenarios: {report.get('scenario_count', 0)}",
        "",
        "## Quality Rank",
        "",
        "| Run | Provider | Model | Success | Tool Sel | Arg Acc | Avg ms | Mem MB | Tokens |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    lines.extend(row(run) for run in quality_rank)

    lines.extend(
        [
            "",
            "## Low-Memory Rank",
            "",
            "| Run | Provider | Model | Success | Tool Sel | Arg Acc | Avg ms | Mem MB | Tokens |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run) for run in low_mem_rank)

    lines.extend(
        [
            "",
            "## Balanced Rank",
            "",
            "| Run | Provider | Model | Success | Tool Sel | Arg Acc | Avg ms | Mem MB | Tokens | Score |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run, include_score=True) for run in balanced_rank)

    best_low_mem = low_mem_rank[0]
    best_quality = quality_rank[0]
    lines.extend(
        [
            "",
            "## Recommendations",
            "",
            f"- Best overall quality: `{best_quality['profile']['name']}` "
            f"({best_quality['profile']['model']})",
            f"- Best low-memory option: `{best_low_mem['profile']['name']}` "
            f"({best_low_mem['aggregate']['memory_peak_mb']:.1f} MB peak)",
        ]
    )
    return "\n".join(lines) + "\n"
