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
    system_prompt: str | None = None
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
    avg_tool_latency_ms: float
    p95_tool_latency_ms: float
    tool_call_error_count: int
    tool_call_error_rate: float
    model_execution_error_count: int
    model_execution_error_rate: float
    first_turn_latency_ms: float
    tokens_per_second: float
    scenario_success_per_second: float
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


DEFAULT_RUBRIC: dict[str, Any] = {
    "version": "2026.1",
    "weights": {
        "task_success_rate": 0.35,
        "tool_selection_accuracy": 0.2,
        "argument_accuracy": 0.15,
        "recovery_success_rate": 0.1,
        "multistep_success_rate": 0.1,
        "robustness_success_rate": 0.05,
        "context_success_rate": 0.05,
    },
    "penalties": {
        "latency_ms_multiplier": 0.002,
        "memory_mb_multiplier": 0.002,
        "tool_error_rate_multiplier": 20.0,
        "model_error_rate_multiplier": 30.0,
    },
}


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _normalize_rubric(raw: Any) -> dict[str, Any]:
    normalized = {
        "version": str(DEFAULT_RUBRIC["version"]),
        "weights": dict(DEFAULT_RUBRIC["weights"]),
        "penalties": dict(DEFAULT_RUBRIC["penalties"]),
    }
    if not isinstance(raw, dict):
        return normalized
    if raw.get("version"):
        normalized["version"] = str(raw["version"]).strip() or normalized["version"]

    weights = raw.get("weights")
    if isinstance(weights, dict):
        for key, value in weights.items():
            if key not in normalized["weights"]:
                continue
            number = _coerce_float(value, normalized["weights"][key])
            if number >= 0.0:
                normalized["weights"][key] = number

    penalties = raw.get("penalties")
    if isinstance(penalties, dict):
        for key, value in penalties.items():
            if key not in normalized["penalties"]:
                continue
            number = _coerce_float(value, normalized["penalties"][key])
            if number >= 0.0:
                normalized["penalties"][key] = number

    return normalized


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


def _expand_profile_entry(entry: dict[str, Any]) -> list[BenchmarkProfile]:
    base = dict(entry)
    context_windows = base.pop("context_windows", None)
    n_ctx = base.pop("n_ctx", None)

    env = dict(base.get("env") or {})
    base["env"] = env
    if n_ctx is not None:
        env["TALKBOT_LOCAL_N_CTX"] = str(n_ctx)

    if not isinstance(context_windows, list) or not context_windows:
        return [BenchmarkProfile(**base)]

    profiles: list[BenchmarkProfile] = []
    for ctx in context_windows:
        try:
            ctx_int = int(ctx)
        except Exception:
            continue
        clone = dict(base)
        clone_env = dict(env)
        clone_env["TALKBOT_LOCAL_N_CTX"] = str(ctx_int)
        clone["env"] = clone_env
        base_name = str(clone.get("name") or "profile")
        clone["name"] = f"{base_name}-ctx{ctx_int}"
        profiles.append(BenchmarkProfile(**clone))
    if not profiles:
        raise ValueError(
            f"Profile '{base.get('name', 'unknown')}' has no valid context_windows values."
        )
    return profiles


def load_matrix_config(path: str | Path) -> dict[str, Any]:
    payload = _load_json(Path(path))
    raw_profiles: Any
    rubric_raw: Any = None
    matrix_version = "2026.1"
    if isinstance(payload, list):
        raw_profiles = payload
    elif isinstance(payload, dict):
        raw_profiles = payload.get("profiles") or payload.get("runs") or []
        benchmark_cfg = payload.get("benchmark")
        if isinstance(benchmark_cfg, dict):
            rubric_raw = benchmark_cfg.get("rubric")
            matrix_version = str(benchmark_cfg.get("schema_version") or matrix_version)
        if payload.get("rubric") and rubric_raw is None:
            rubric_raw = payload.get("rubric")
    else:
        raw_profiles = []

    if not isinstance(raw_profiles, list) or not raw_profiles:
        raise ValueError("Matrix must define a non-empty 'profiles' list.")

    profiles: list[BenchmarkProfile] = []
    for entry in raw_profiles:
        if not isinstance(entry, dict):
            raise ValueError("Each matrix profile entry must be an object.")
        profiles.extend(_expand_profile_entry(entry))

    return {
        "schema_version": matrix_version,
        "profiles": profiles,
        "rubric": _normalize_rubric(rubric_raw),
    }


def load_profiles_from_matrix(path: str | Path) -> list[BenchmarkProfile]:
    return list(load_matrix_config(path)["profiles"])


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
    rubric: dict[str, Any] | None = None,
    client_factory: Callable[[BenchmarkProfile], Any] | None = None,
) -> dict[str, Any]:
    """Run all profiles against all scenarios and return a report dictionary."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    factory = client_factory or _default_client_factory
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    rubric_config = _normalize_rubric(rubric)

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
                        system_parts: list[str] = []
                        if profile.system_prompt:
                            system_parts.append(str(profile.system_prompt).strip())
                        if scenario.get("system_prompt"):
                            system_parts.append(str(scenario["system_prompt"]).strip())
                        system_parts = [part for part in system_parts if part]
                        if system_parts:
                            messages.append(
                                {
                                    "role": "system",
                                    "content": "\n\n".join(system_parts),
                                }
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
                tool_traces=recorder.calls,
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
        "rubric": rubric_config,
        "runs": [_run_to_dict(run) for run in run_results],
    }
    return report


def _build_aggregate(
    *,
    scenario_results: list[ScenarioResult],
    tool_traces: list[ToolCallTrace],
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
    model_execution_error_count = 0
    first_turn_latencies: list[float] = []
    for turn in all_turns:
        p, c, t = _token_usage(turn.usage)
        prompt_tokens += p
        completion_tokens += c
        total_tokens += t
        max_history_messages = max(max_history_messages, turn.history_messages)
        max_history_chars = max(max_history_chars, turn.history_chars)
        if turn.index == 0:
            first_turn_latencies.append(turn.latency_ms)
        if any("Model execution error:" in assertion for assertion in turn.assertions):
            model_execution_error_count += 1

    tool_latencies = [trace.latency_ms for trace in tool_traces]
    if len(tool_latencies) >= 2:
        p95_tool_latency = statistics.quantiles(tool_latencies, n=20)[18]
    elif tool_latencies:
        p95_tool_latency = tool_latencies[0]
    else:
        p95_tool_latency = 0.0
    tool_call_error_count = sum(
        1
        for trace in tool_traces
        if trace.error or str(trace.result).strip().lower().startswith("error:")
    )

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
    total_turn_latency_s = sum(latencies) / 1000.0 if latencies else 0.0
    scenario_success_per_second = (
        round(passed_scenarios / total_turn_latency_s, 4)
        if total_turn_latency_s > 0
        else 0.0
    )
    tokens_per_second = (
        round(total_tokens / total_turn_latency_s, 3) if total_turn_latency_s > 0 else 0.0
    )
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
        avg_tool_latency_ms=(
            round(statistics.fmean(tool_latencies), 3) if tool_latencies else 0.0
        ),
        p95_tool_latency_ms=round(float(p95_tool_latency), 3),
        tool_call_error_count=tool_call_error_count,
        tool_call_error_rate=_percent(tool_call_error_count, max(1, len(tool_traces))),
        model_execution_error_count=model_execution_error_count,
        model_execution_error_rate=_percent(
            model_execution_error_count,
            max(1, len(all_turns)),
        ),
        first_turn_latency_ms=(
            round(statistics.fmean(first_turn_latencies), 3)
            if first_turn_latencies
            else 0.0
        ),
        tokens_per_second=tokens_per_second,
        scenario_success_per_second=scenario_success_per_second,
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


def _tag_metric(aggregate: dict[str, Any], tag: str) -> float:
    tags = aggregate.get("tag_success") or {}
    if isinstance(tags, dict):
        return _coerce_float(tags.get(tag), 0.0)
    return 0.0


def _rubric_metric(aggregate: dict[str, Any], metric: str) -> float:
    if metric in aggregate:
        return _coerce_float(aggregate.get(metric), 0.0)
    tag_map = {
        "recovery_success_rate": "recovery",
        "multistep_success_rate": "multistep",
        "robustness_success_rate": "robustness",
        "context_success_rate": "context",
    }
    if metric in tag_map:
        return _tag_metric(aggregate, tag_map[metric])
    return 0.0


def _rubric_score(aggregate: dict[str, Any], rubric: dict[str, Any]) -> float:
    weights = rubric.get("weights") if isinstance(rubric, dict) else {}
    penalties = rubric.get("penalties") if isinstance(rubric, dict) else {}
    if not isinstance(weights, dict):
        weights = {}
    if not isinstance(penalties, dict):
        penalties = {}

    weighted_total = 0.0
    weight_sum = 0.0
    for metric, raw_weight in weights.items():
        weight = _coerce_float(raw_weight, 0.0)
        if weight <= 0.0:
            continue
        value = _rubric_metric(aggregate, metric)
        weighted_total += value * weight
        weight_sum += weight

    quality_score = (weighted_total / weight_sum) * 100.0 if weight_sum > 0 else 0.0
    penalty = (
        _coerce_float(aggregate.get("avg_turn_latency_ms"), 0.0)
        * _coerce_float(penalties.get("latency_ms_multiplier"), 0.0)
        + _coerce_float(aggregate.get("memory_peak_mb"), 0.0)
        * _coerce_float(penalties.get("memory_mb_multiplier"), 0.0)
        + _coerce_float(aggregate.get("tool_call_error_rate"), 0.0)
        * _coerce_float(penalties.get("tool_error_rate_multiplier"), 0.0)
        + _coerce_float(aggregate.get("model_execution_error_rate"), 0.0)
        * _coerce_float(penalties.get("model_error_rate_multiplier"), 0.0)
    )
    return round(quality_score - penalty, 3)


def _dominates(
    left: dict[str, Any],
    right: dict[str, Any],
    rubric: dict[str, Any],
) -> bool:
    left_agg = left["aggregate"]
    right_agg = right["aggregate"]
    left_score = _rubric_score(left_agg, rubric)
    right_score = _rubric_score(right_agg, rubric)

    left_dims = (
        _coerce_float(left_agg.get("task_success_rate"), 0.0),
        _coerce_float(left_agg.get("tool_selection_accuracy"), 0.0),
        _coerce_float(left_agg.get("argument_accuracy"), 0.0),
        left_score,
        -_coerce_float(left_agg.get("avg_turn_latency_ms"), 0.0),
        -_coerce_float(left_agg.get("memory_peak_mb"), 0.0),
        -_coerce_float(left_agg.get("tool_call_error_rate"), 0.0),
    )
    right_dims = (
        _coerce_float(right_agg.get("task_success_rate"), 0.0),
        _coerce_float(right_agg.get("tool_selection_accuracy"), 0.0),
        _coerce_float(right_agg.get("argument_accuracy"), 0.0),
        right_score,
        -_coerce_float(right_agg.get("avg_turn_latency_ms"), 0.0),
        -_coerce_float(right_agg.get("memory_peak_mb"), 0.0),
        -_coerce_float(right_agg.get("tool_call_error_rate"), 0.0),
    )
    at_least_one_better = False
    for left_value, right_value in zip(left_dims, right_dims):
        if left_value < right_value:
            return False
        if left_value > right_value:
            at_least_one_better = True
    return at_least_one_better


def build_leaderboard_markdown(report: dict[str, Any]) -> str:
    """Render a markdown leaderboard from run results."""
    runs = [run for run in report.get("runs", []) if run.get("status") == "ok"]
    if not runs:
        return "# Benchmark Leaderboard\n\nNo successful runs."
    rubric = _normalize_rubric(report.get("rubric"))

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
        key=lambda run: _rubric_score(run["aggregate"], rubric),
        reverse=True,
    )
    efficiency_rank = sorted(
        runs,
        key=lambda run: (
            run["aggregate"]["task_success_rate"],
            run["aggregate"].get("tokens_per_second", 0.0),
            -run["aggregate"]["avg_turn_latency_ms"],
            -run["aggregate"]["memory_peak_mb"],
        ),
        reverse=True,
    )
    pareto = [
        run
        for run in runs
        if not any(_dominates(other, run, rubric) for other in runs if other is not run)
    ]
    pareto = sorted(
        pareto,
        key=lambda run: _rubric_score(run["aggregate"], rubric),
        reverse=True,
    )

    def row(run: dict[str, Any], include_score: bool = False) -> str:
        agg = run["aggregate"]
        score = _rubric_score(agg, rubric)
        recovery = _tag_metric(agg, "recovery")
        base = (
            f"| {run['profile']['name']} | {run['profile']['provider']} | "
            f"{run['profile']['model']} | {_coerce_float(agg.get('task_success_rate'), 0.0):.2%} | "
            f"{_coerce_float(agg.get('tool_selection_accuracy'), 0.0):.2%} | "
            f"{_coerce_float(agg.get('argument_accuracy'), 0.0):.2%} | "
            f"{recovery:.2%} | {_coerce_float(agg.get('avg_turn_latency_ms'), 0.0):.1f} | "
            f"{_coerce_float(agg.get('memory_peak_mb'), 0.0):.1f} | "
            f"{_coerce_float(agg.get('tool_call_error_rate'), 0.0):.2%} | "
            f"{_coerce_float(agg.get('tokens_per_second'), 0.0):.1f} | "
            f"{int(_coerce_float(agg.get('total_tokens'), 0.0))} |"
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
        f"- Rubric version: {rubric.get('version', '')}",
        "",
        "## Rubric",
        "",
        "| Metric | Weight |",
        "|---|---:|",
    ]
    lines.extend(
        f"| {metric} | {float(weight):.3f} |"
        for metric, weight in sorted((rubric.get("weights") or {}).items())
    )
    lines.extend(
        [
            "",
            "| Penalty | Multiplier |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {metric} | {float(weight):.3f} |"
        for metric, weight in sorted((rubric.get("penalties") or {}).items())
    )

    lines.extend(
        [
            "",
            "## Quality Rank",
            "",
            "| Run | Provider | Model | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run) for run in quality_rank)

    lines.extend(
        [
            "",
            "## Low-Memory Rank",
            "",
            "| Run | Provider | Model | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run) for run in low_mem_rank)

    lines.extend(
        [
            "",
            "## Balanced Rank",
            "",
            "| Run | Provider | Model | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run, include_score=True) for run in balanced_rank)

    lines.extend(
        [
            "",
            "## Efficiency Rank",
            "",
            "| Run | Provider | Model | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run) for run in efficiency_rank)

    lines.extend(
        [
            "",
            "## Pareto Frontier (Quality/Latency/Memory)",
            "",
            "| Run | Provider | Model | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run, include_score=True) for run in pareto)

    best_low_mem = low_mem_rank[0]
    best_quality = quality_rank[0]
    best_efficiency = efficiency_rank[0]
    lines.extend(
        [
            "",
            "## Recommendations",
            "",
            f"- Best overall quality: `{best_quality['profile']['name']}` "
            f"({best_quality['profile']['model']})",
            f"- Best low-memory option: `{best_low_mem['profile']['name']}` "
            f"({best_low_mem['aggregate']['memory_peak_mb']:.1f} MB peak)",
            f"- Best throughput option: `{best_efficiency['profile']['name']}` "
            f"({best_efficiency['aggregate']['tokens_per_second']:.1f} tokens/sec)",
        ]
    )
    return "\n".join(lines) + "\n"
