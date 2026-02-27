"""Conversation benchmark runner for tool-enabled TalkBot models.

This module executes scripted multi-turn conversations, validates expected
tool behavior, and produces leaderboard-friendly metrics.
"""

from __future__ import annotations

import json
import os
import platform
import re
import socket
import statistics
import subprocess
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

try:
    import psutil
except Exception:  # pragma: no cover - optional dependency
    psutil = None


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

DEFAULT_CONTEXT_ANALYSIS: dict[str, float] = {
    "near_peak_ratio": 0.95,
    "dropoff_ratio": 0.9,
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


def _normalize_context_analysis(raw: Any) -> dict[str, float]:
    normalized = dict(DEFAULT_CONTEXT_ANALYSIS)
    if not isinstance(raw, dict):
        return normalized
    near_peak = _coerce_float(raw.get("near_peak_ratio"), normalized["near_peak_ratio"])
    dropoff = _coerce_float(raw.get("dropoff_ratio"), normalized["dropoff_ratio"])
    if 0.0 < near_peak <= 1.0:
        normalized["near_peak_ratio"] = near_peak
    if 0.0 < dropoff <= 1.0:
        normalized["dropoff_ratio"] = dropoff
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
    context_analysis_raw: Any = None
    matrix_version = "2026.1"
    if isinstance(payload, list):
        raw_profiles = payload
    elif isinstance(payload, dict):
        raw_profiles = payload.get("profiles") or payload.get("runs") or []
        benchmark_cfg = payload.get("benchmark")
        if isinstance(benchmark_cfg, dict):
            rubric_raw = benchmark_cfg.get("rubric")
            context_analysis_raw = benchmark_cfg.get("context_analysis")
            matrix_version = str(benchmark_cfg.get("schema_version") or matrix_version)
        if payload.get("rubric") and rubric_raw is None:
            rubric_raw = payload.get("rubric")
        if payload.get("context_analysis") and context_analysis_raw is None:
            context_analysis_raw = payload.get("context_analysis")
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
        "context_analysis": _normalize_context_analysis(context_analysis_raw),
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


def _current_rss_mb() -> float:
    if psutil is None:
        return 0.0
    try:
        rss = float(psutil.Process().memory_info().rss)
    except Exception:
        return 0.0
    return round(rss / (1024.0 * 1024.0), 3)


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


def _detect_raspberry_pi_model() -> str:
    for path in ("/proc/device-tree/model", "/sys/firmware/devicetree/base/model"):
        try:
            text = Path(path).read_text(encoding="utf-8", errors="ignore").replace("\x00", "")
            text = text.strip()
            if text:
                return text
        except Exception:
            continue
    return ""


_DEFAULT_PROBE_ENDPOINTS: list[tuple[str, str]] = [
    ("openrouter", "https://openrouter.ai/api/v1/models"),
    ("ollama-local", "http://localhost:11434/api/tags"),
]


def _probe_endpoint(label: str, url: str, timeout: float = 5.0, samples: int = 3) -> dict[str, Any]:
    """Measure TTFB to *url* using *samples* requests, reporting the median.

    Uses httpx streaming so we record time-to-first-byte (headers received)
    without downloading the full response body. This isolates network + API
    gateway overhead from model inference time.
    """
    try:
        import httpx as _httpx

        timings: list[float] = []
        last_status: int | None = None
        for _ in range(samples):
            try:
                t0 = time.perf_counter()
                with _httpx.Client(timeout=timeout, follow_redirects=True) as client:
                    with client.stream("GET", url) as response:
                        ttfb_ms = (time.perf_counter() - t0) * 1000
                        last_status = response.status_code
                timings.append(ttfb_ms)
            except Exception:
                pass  # skip failed samples; report error below if none succeed

        if not timings:
            raise RuntimeError("all samples failed")

        return {
            "label": label,
            "url": url,
            "ttfb_ms_median": round(statistics.median(timings), 1),
            "ttfb_ms_min": round(min(timings), 1),
            "ttfb_ms_max": round(max(timings), 1),
            "samples": len(timings),
            "http_status": last_status,
            "error": None,
        }
    except Exception as exc:
        return {
            "label": label,
            "url": url,
            "ttfb_ms_median": None,
            "ttfb_ms_min": None,
            "ttfb_ms_max": None,
            "samples": 0,
            "http_status": None,
            "error": str(exc)[:120],
        }


def _detect_network_type() -> str:
    """Best-effort detection of the primary active network interface type.

    On macOS: uses ``networksetup -getinfo`` directly (no psutil needed) — checks
    each common service name for an active IP address.
    On Linux/other: uses psutil interface name heuristics (wlan*/eth* prefixes).
    Returns a short string like ``"wifi (Wi-Fi)"``, ``"ethernet (Ethernet)"``,
    or ``"unknown"`` on failure.
    """
    try:
        if platform.system() == "Darwin":
            # Check common macOS service names in priority order; first with a live
            # IP address wins.  networksetup -getinfo prints "IP address: <ip>" when
            # connected or "IP address: none" when not.
            for svc_name, kind in (
                ("Wi-Fi", "wifi"),
                ("Thunderbolt Ethernet", "ethernet"),
                ("USB 10/100/1000 LAN", "ethernet"),
                ("Ethernet", "ethernet"),
                ("Thunderbolt Bridge", "ethernet"),
            ):
                try:
                    out = subprocess.check_output(
                        ["networksetup", "-getinfo", svc_name],
                        stderr=subprocess.DEVNULL,
                        timeout=3,
                        text=True,
                    )
                    for line in out.splitlines():
                        if line.startswith("IP address:"):
                            ip = line.split(":", 1)[1].strip()
                            if ip and ip.lower() != "none":
                                return f"{kind} ({svc_name})"
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            return "unknown (macOS)"

        # Linux / other: use psutil interface name heuristics
        if psutil is None:
            return "unknown"
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        active = [
            iface
            for iface, st in stats.items()
            if st.isup
            and iface not in ("lo", "lo0")
            and any(
                a.family == socket.AF_INET and not a.address.startswith("127.")
                for a in addrs.get(iface, [])
            )
        ]
        wifi_prefixes = ("wlan", "wlp", "wl", "ath")
        eth_prefixes = ("eth", "eno", "enp", "em")
        for iface in active:
            low = iface.lower()
            if any(low.startswith(p) for p in wifi_prefixes):
                return f"wifi ({iface})"
            if any(low.startswith(p) for p in eth_prefixes):
                return f"ethernet ({iface})"
        return f"unknown ({', '.join(active[:2])})" if active else "none"
    except Exception:
        return "unknown"


def detect_runner_info(
    *,
    label: str | None = None,
    notes: str | None = None,
    network_type: str | None = None,
    probe_endpoints: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Collect host metadata for benchmark comparability across machines.

    *probe_endpoints* is a list of ``(label, url)`` pairs to TTFB-probe before
    the run. Defaults to :data:`_DEFAULT_PROBE_ENDPOINTS`. Pass ``[]`` to skip.
    """
    runner_label = str(label or os.getenv("TALKBOT_BENCHMARK_RUNNER") or "").strip()
    pi_model = _detect_raspberry_pi_model()
    is_pi = "raspberry pi" in pi_model.lower()
    logical_cpus = os.cpu_count()
    physical_cpus: int | None = None
    if psutil is not None:
        try:
            physical_cpus = psutil.cpu_count(logical=False)
        except Exception:
            physical_cpus = None

    endpoints_to_probe = probe_endpoints if probe_endpoints is not None else _DEFAULT_PROBE_ENDPOINTS
    print(f"[runner] probing {len(endpoints_to_probe)} endpoint(s) for TTFB latency...", flush=True)
    probes = [_probe_endpoint(lbl, url) for lbl, url in endpoints_to_probe]
    for p in probes:
        if p["error"]:
            print(f"  {p['label']}: unreachable — {p['error']}", flush=True)
        else:
            print(f"  {p['label']}: {p['ttfb_ms_median']} ms median TTFB (min {p['ttfb_ms_min']}, max {p['ttfb_ms_max']}, n={p['samples']})", flush=True)

    payload = {
        "label": runner_label or None,
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or None,
        "python_version": platform.python_version(),
        "cpu_count_logical": int(logical_cpus) if isinstance(logical_cpus, int) else None,
        "cpu_count_physical": int(physical_cpus) if isinstance(physical_cpus, int) else None,
        "is_raspberry_pi": is_pi,
        "raspberry_pi_model": pi_model or None,
        "network_type": str(network_type or "").strip() or _detect_network_type(),
        "endpoint_probes": probes,
        "notes": str(notes or "").strip() or None,
    }
    return _json_safe(payload)


def run_benchmark(
    *,
    profiles: list[BenchmarkProfile],
    scenarios: list[dict[str, Any]],
    output_dir: str | Path,
    rubric: dict[str, Any] | None = None,
    context_analysis: dict[str, Any] | None = None,
    client_factory: Callable[[BenchmarkProfile], Any] | None = None,
    runner_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run all profiles against all scenarios and return a report dictionary."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    factory = client_factory or _default_client_factory
    resolved_runner = _json_safe(runner_info) if runner_info else detect_runner_info()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    rubric_config = _normalize_rubric(rubric)
    context_analysis_config = _normalize_context_analysis(context_analysis)

    run_results: list[RunResult] = []
    for profile in profiles:
        run_started = time.perf_counter()
        cpu_started = time.process_time()
        rss_started = _current_rss_mb()
        rss_peak = rss_started
        rss_max_started = _process_rss_mb()
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
                    rss_peak = max(rss_peak, _current_rss_mb())
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
                            rss_peak = max(rss_peak, _current_rss_mb())

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
        rss_peak = max(rss_peak, _current_rss_mb())
        rss_max_ended = _process_rss_mb()
        run_duration = round(time.perf_counter() - run_started, 3)
        cpu_duration = round(time.process_time() - cpu_started, 3)

        aggregate: RunAggregate | None = None
        if status == "ok":
            aggregate = _build_aggregate(
                scenario_results=scenario_results,
                tool_traces=recorder.calls,
                cpu_time_s=cpu_duration,
                python_peak_mb=round(tracemalloc_peak / (1024.0 * 1024.0), 3),
                process_rss_delta_mb=max(
                    max(0.0, round(rss_peak - rss_started, 3)),
                    max(0.0, round(rss_max_ended - rss_max_started, 3)),
                ),
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
        "runner": resolved_runner,
        "scenario_count": len(scenarios),
        "run_count": len(run_results),
        "rubric": rubric_config,
        "context_analysis": context_analysis_config,
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
    tool_selection_accuracy = _percent(matched_tool_names, expected_tool_calls)
    argument_accuracy = _percent(matched_arg_checks, expected_arg_checks)
    # Avoid false-perfect metrics when execution errors prevent any tool assertions.
    if model_execution_error_count > 0 and expected_tool_calls <= 0:
        tool_selection_accuracy = 0.0
    if model_execution_error_count > 0 and expected_arg_checks <= 0:
        argument_accuracy = 0.0

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
        tool_selection_accuracy=tool_selection_accuracy,
        expected_arg_checks=expected_arg_checks,
        matched_arg_checks=matched_arg_checks,
        argument_accuracy=argument_accuracy,
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


def _rubric_quality_score(aggregate: dict[str, Any], rubric: dict[str, Any]) -> float:
    weights = rubric.get("weights") if isinstance(rubric, dict) else {}
    if not isinstance(weights, dict):
        weights = {}

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
    return round(quality_score, 3)


def _rubric_penalty(aggregate: dict[str, Any], rubric: dict[str, Any]) -> float:
    penalties = rubric.get("penalties") if isinstance(rubric, dict) else {}
    if not isinstance(penalties, dict):
        penalties = {}
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
    return round(penalty, 3)


def _rubric_score(aggregate: dict[str, Any], rubric: dict[str, Any]) -> float:
    return round(_rubric_quality_score(aggregate, rubric) - _rubric_penalty(aggregate, rubric), 3)


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


def _extract_context_window(profile: dict[str, Any]) -> int | None:
    env = profile.get("env")
    if isinstance(env, dict):
        value = env.get("TALKBOT_LOCAL_N_CTX")
        if value is not None:
            try:
                parsed = int(value)
                if parsed > 0:
                    return parsed
            except Exception:
                pass
    name = str(profile.get("name") or "")
    matches = re.findall(r"ctx(\d+)", name)
    if matches:
        try:
            return int(matches[-1])
        except Exception:
            return None
    return None


def _context_family_key(profile: dict[str, Any]) -> tuple[str, str, str]:
    provider = str(profile.get("provider") or "")
    model = str(profile.get("model") or "")
    local_path = str(profile.get("local_model_path") or "")
    model_variant = Path(local_path).name if local_path else ""
    return (provider, model, model_variant)


def _context_family_label(key: tuple[str, str, str]) -> str:
    provider, model, variant = key
    if variant:
        return f"{provider}/{model} ({variant})"
    return f"{provider}/{model}"


def _routing_mode(profile: dict[str, Any]) -> str:
    env = profile.get("env")
    if isinstance(env, dict):
        raw = str(env.get("TALKBOT_LOCAL_DIRECT_TOOL_ROUTING", "")).strip().lower()
        if raw in {"1", "true", "yes", "on"}:
            return "intent"
    return "llm"


def _ab_compare_key(profile: dict[str, Any]) -> tuple[str, str, str, int]:
    provider = str(profile.get("provider") or "")
    model = str(profile.get("model") or "")
    local_path = str(profile.get("local_model_path") or "")
    variant = Path(local_path).name if local_path else ""
    ctx = _extract_context_window(profile) or 0
    return (provider, model, variant, ctx)


def _ab_compare_label(key: tuple[str, str, str, int]) -> str:
    provider, model, variant, ctx = key
    base = f"{provider}/{model}"
    if variant:
        base = f"{base} ({variant})"
    return f"{base} @ctx{ctx}"


def _ab_comparison_rows(
    runs: list[dict[str, Any]],
    rubric: dict[str, Any],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, int], dict[str, list[dict[str, float]]]] = {}
    for run in runs:
        profile = run.get("profile") or {}
        aggregate = run.get("aggregate") or {}
        key = _ab_compare_key(profile)
        mode = _routing_mode(profile)
        grouped.setdefault(key, {}).setdefault(mode, []).append(
            {
                "task_success_rate": _coerce_float(aggregate.get("task_success_rate"), 0.0),
                "tool_selection_accuracy": _coerce_float(
                    aggregate.get("tool_selection_accuracy"), 0.0
                ),
                "argument_accuracy": _coerce_float(aggregate.get("argument_accuracy"), 0.0),
                "tool_call_error_rate": _coerce_float(
                    aggregate.get("tool_call_error_rate"), 0.0
                ),
                "avg_turn_latency_ms": _coerce_float(
                    aggregate.get("avg_turn_latency_ms"), 0.0
                ),
                "memory_peak_mb": _coerce_float(aggregate.get("memory_peak_mb"), 0.0),
                "score": _rubric_score(aggregate, rubric),
            }
        )

    def _avg(samples: list[dict[str, float]], metric: str) -> float:
        return statistics.fmean(sample[metric] for sample in samples) if samples else 0.0

    rows: list[dict[str, Any]] = []
    for key, modes in grouped.items():
        llm = modes.get("llm") or []
        intent = modes.get("intent") or []
        if not llm or not intent:
            continue
        rows.append(
            {
                "label": _ab_compare_label(key),
                "llm_success": _avg(llm, "task_success_rate"),
                "intent_success": _avg(intent, "task_success_rate"),
                "llm_tool": _avg(llm, "tool_selection_accuracy"),
                "intent_tool": _avg(intent, "tool_selection_accuracy"),
                "llm_score": _avg(llm, "score"),
                "intent_score": _avg(intent, "score"),
                "success_delta": _avg(intent, "task_success_rate")
                - _avg(llm, "task_success_rate"),
                "tool_delta": _avg(intent, "tool_selection_accuracy")
                - _avg(llm, "tool_selection_accuracy"),
                "score_delta": _avg(intent, "score") - _avg(llm, "score"),
            }
        )
    rows.sort(key=lambda row: (row["score_delta"], row["success_delta"]), reverse=True)
    return rows


def _context_sweep_summary(
    runs: list[dict[str, Any]],
    rubric: dict[str, Any],
    context_analysis: dict[str, float],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[int, list[dict[str, float]]]] = {}
    for run in runs:
        profile = run.get("profile") or {}
        aggregate = run.get("aggregate") or {}
        ctx = _extract_context_window(profile)
        if ctx is None:
            continue
        key = _context_family_key(profile)
        sample = {
            "coherence_score": _rubric_quality_score(aggregate, rubric),
            "balanced_score": _rubric_score(aggregate, rubric),
            "success": _coerce_float(aggregate.get("task_success_rate"), 0.0),
            "latency_ms": _coerce_float(aggregate.get("avg_turn_latency_ms"), 0.0),
            "memory_mb": _coerce_float(aggregate.get("memory_peak_mb"), 0.0),
        }
        grouped.setdefault(key, {}).setdefault(ctx, []).append(sample)

    near_peak_ratio = _coerce_float(
        context_analysis.get("near_peak_ratio"),
        DEFAULT_CONTEXT_ANALYSIS["near_peak_ratio"],
    )
    dropoff_ratio = _coerce_float(
        context_analysis.get("dropoff_ratio"),
        DEFAULT_CONTEXT_ANALYSIS["dropoff_ratio"],
    )

    rows: list[dict[str, Any]] = []
    for key, ctx_samples in grouped.items():
        if len(ctx_samples) < 2:
            continue
        points: list[dict[str, float]] = []
        for ctx in sorted(ctx_samples):
            samples = ctx_samples[ctx]
            points.append(
                {
                    "ctx": float(ctx),
                    "coherence_score": statistics.fmean(
                        s["coherence_score"] for s in samples
                    ),
                    "balanced_score": statistics.fmean(
                        s["balanced_score"] for s in samples
                    ),
                    "success": statistics.fmean(s["success"] for s in samples),
                    "latency_ms": statistics.fmean(s["latency_ms"] for s in samples),
                    "memory_mb": statistics.fmean(s["memory_mb"] for s in samples),
                }
            )

        peak = max(points, key=lambda point: point["coherence_score"])
        peak_coherence_score = peak["coherence_score"]
        near_peak_cutoff = peak_coherence_score * near_peak_ratio
        dropoff_cutoff = peak_coherence_score * dropoff_ratio

        optimal = next(
            (point for point in points if point["coherence_score"] >= near_peak_cutoff),
            peak,
        )
        dropoff = next(
            (
                point
                for point in points
                if point["ctx"] > peak["ctx"] and point["coherence_score"] < dropoff_cutoff
            ),
            None,
        )
        rows.append(
            {
                "family": _context_family_label(key),
                "contexts": ", ".join(str(int(point["ctx"])) for point in points),
                "peak_ctx": int(peak["ctx"]),
                "peak_coherence_score": round(float(peak_coherence_score), 3),
                "peak_balanced_score": round(float(peak["balanced_score"]), 3),
                "optimal_ctx": int(optimal["ctx"]),
                "dropoff_ctx": (int(dropoff["ctx"]) if dropoff else None),
                "peak_success": round(float(peak["success"]), 4),
                "peak_latency_ms": round(float(peak["latency_ms"]), 3),
                "peak_memory_mb": round(float(peak["memory_mb"]), 3),
            }
        )

    rows.sort(key=lambda row: row["family"])
    return rows


def top_n_per_provider(
    report: dict[str, Any],
    n: int = 3,
) -> dict[str, list[dict[str, Any]]]:
    """Group successful runs by provider and return top-N per group by balanced rubric score.

    Returns an ordered dict keyed by provider string (e.g. "local", "local_server",
    "openrouter"), each value being up to *n* run dicts sorted best-first.
    """
    rubric = _normalize_rubric(report.get("rubric"))
    groups: dict[str, list[dict[str, Any]]] = {}
    for run in report.get("runs", []):
        if run.get("status") != "ok":
            continue
        provider = str((run.get("profile") or {}).get("provider") or "").strip().lower() or "unknown"
        groups.setdefault(provider, []).append(run)
    return {
        provider: sorted(
            group,
            key=lambda r: _rubric_score(r["aggregate"], rubric),
            reverse=True,
        )[:n]
        for provider, group in sorted(groups.items())
    }


def build_leaderboard_markdown(report: dict[str, Any]) -> str:
    """Render a markdown leaderboard from run results."""
    runs = [run for run in report.get("runs", []) if run.get("status") == "ok"]
    if not runs:
        return "# Benchmark Leaderboard\n\nNo successful runs."
    rubric = _normalize_rubric(report.get("rubric"))
    context_analysis = _normalize_context_analysis(report.get("context_analysis"))
    meta = report.get("meta") if isinstance(report.get("meta"), dict) else {}
    runner = report.get("runner") if isinstance(report.get("runner"), dict) else {}
    runner_name = str(runner.get("label") or runner.get("hostname") or "").strip()
    runner_os = " ".join(
        part for part in [str(runner.get("os") or "").strip(), str(runner.get("os_release") or "").strip()] if part
    ).strip()
    runner_machine = str(runner.get("machine") or "").strip()
    runner_python = str(runner.get("python_version") or "").strip()
    runner_pi_model = str(runner.get("raspberry_pi_model") or "").strip()
    runner_network = str(runner.get("network_type") or "").strip()
    runner_notes = str(runner.get("notes") or "").strip()
    runner_probes: list[dict[str, Any]] = [
        p for p in (runner.get("endpoint_probes") or []) if isinstance(p, dict)
    ]
    main_output_root = str(meta.get("main_output_root") or "benchmark_results")
    latest_run = str(meta.get("latest_run") or "").strip()
    latest_run_text = latest_run if latest_run else "not provided"
    context_rows = _context_sweep_summary(runs, rubric, context_analysis)
    ab_rows = _ab_comparison_rows(runs, rubric)

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
    remote_runs = [
        run
        for run in runs
        if str((run.get("profile") or {}).get("provider") or "").strip().lower()
        not in {"local", "local_server"}
    ]
    remote_rubric = {
        "version": f"{rubric.get('version', '')}.remote",
        "weights": dict(rubric.get("weights") or {}),
        "penalties": dict(rubric.get("penalties") or {}),
    }
    remote_rubric["penalties"]["memory_mb_multiplier"] = 0.0
    remote_rank = sorted(
        remote_runs,
        key=lambda run: _rubric_score(run["aggregate"], remote_rubric),
        reverse=True,
    )
    local_runs = [
        run
        for run in runs
        if str((run.get("profile") or {}).get("provider") or "").strip().lower()
        in {"local", "local_server"}
    ]
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

    def row(
        run: dict[str, Any],
        include_score: bool = False,
        score_override: float | None = None,
    ) -> str:
        profile = run.get("profile") or {}
        agg = run["aggregate"]
        score = (
            float(score_override)
            if score_override is not None
            else _rubric_score(agg, rubric)
        )
        recovery = _tag_metric(agg, "recovery")
        routing = _routing_mode(profile).upper()
        base = (
            f"| {profile.get('name', '')} | {profile.get('provider', '')} | "
            f"{profile.get('model', '')} | {routing} | "
            f"{profile.get('temperature', 0.0):.1f} | "
            f"{_coerce_float(agg.get('task_success_rate'), 0.0):.2%} | "
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
            "## Scope",
            "",
            "- Canonical latest leaderboard: `benchmark_results/leaderboard.md`",
            f"- Canonical latest JSON: `{main_output_root}/results.json`",
            f"- Latest run snapshot path: `{latest_run_text}`",
            f"- Archived run folders: `{main_output_root}/<run_name>/leaderboard.md`",
            (
                f"- Runner: `{runner_name}` ({runner_os}, {runner_machine}, py {runner_python})"
                if runner_name and runner_os
                else "- Runner: not provided"
            ),
            "",
            "## Rubric",
            "",
        "| Metric | Weight |",
        "|---|---:|",
    ]
    if runner_pi_model:
        lines.insert(lines.index("## Rubric") - 1, f"- Raspberry Pi model: `{runner_pi_model}`")
    if runner_network:
        lines.insert(lines.index("## Rubric") - 1, f"- Network: `{runner_network}`")
    if runner_notes:
        lines.insert(lines.index("## Rubric") - 1, f"- Runner notes: {runner_notes}")
    if runner_probes:
        probe_lines = [
            "",
            "## Endpoint Latency (TTFB)",
            "",
            "- Measured before benchmarking: time-to-first-byte (headers received) over 3 samples.",
            "- Subtract median TTFB from a model's `Avg ms` to estimate server-side inference time.",
            "",
            "| Endpoint | URL | Median ms | Min ms | Max ms | HTTP |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for p in runner_probes:
            if p.get("error"):
                probe_lines.append(
                    f"| {p.get('label', '')} | {p.get('url', '')} | n/a | n/a | n/a | err: {p['error'][:60]} |"
                )
            else:
                probe_lines.append(
                    f"| {p.get('label', '')} | {p.get('url', '')} | "
                    f"{p.get('ttfb_ms_median', 0):.1f} | {p.get('ttfb_ms_min', 0):.1f} | "
                    f"{p.get('ttfb_ms_max', 0):.1f} | {p.get('http_status', '?')} |"
                )
        rubric_idx = lines.index("## Rubric")
        lines[rubric_idx:rubric_idx] = probe_lines
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
            "| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run) for run in quality_rank)

    lines.extend(
        [
            "",
            "## Low-Memory Rank",
            "",
            "| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run) for run in low_mem_rank)

    lines.extend(
        [
            "",
            "## Balanced Rank",
            "",
            "| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run, include_score=True) for run in balanced_rank)

    lines.extend(
        [
            "",
            "## Remote Rank (No Memory Penalty)",
            "",
            "- Purpose: compare hosted/API models without penalizing local process RSS.",
            "- Score keeps quality and latency/error penalties; `memory_mb_multiplier` is forced to `0.0`.",
            "",
        ]
    )
    if remote_rank:
        lines.extend(
            [
                "| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score (Remote) |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        lines.extend(
            row(
                run,
                include_score=True,
                score_override=_rubric_score(run["aggregate"], remote_rubric),
            )
            for run in remote_rank
        )
    else:
        lines.append("No remote-provider runs found in this report.")

    lines.extend(
        [
            "",
            "## Efficiency Rank",
            "",
            "| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run) for run in efficiency_rank)

    lines.extend(
        [
            "",
            "## Latency Snapshot (Local vs Remote)",
            "",
            "- Compares per-run `avg_turn_latency_ms` to show practical response-speed differences.",
            "",
            "| Group | Runs | Median Avg ms | Fastest Avg ms | Fastest Run |",
            "|---|---:|---:|---:|---|",
        ]
    )

    def _latency_group_row(group_name: str, group_runs: list[dict[str, Any]]) -> str:
        if not group_runs:
            return f"| {group_name} | 0 | n/a | n/a | n/a |"
        latencies = [
            _coerce_float((run.get("aggregate") or {}).get("avg_turn_latency_ms"), 0.0)
            for run in group_runs
        ]
        median_ms = statistics.median(latencies) if latencies else 0.0
        fastest = min(
            group_runs,
            key=lambda run: _coerce_float(
                (run.get("aggregate") or {}).get("avg_turn_latency_ms"),
                float("inf"),
            ),
        )
        fastest_ms = _coerce_float(
            (fastest.get("aggregate") or {}).get("avg_turn_latency_ms"),
            0.0,
        )
        fastest_name = str((fastest.get("profile") or {}).get("name") or "")
        return (
            f"| {group_name} | {len(group_runs)} | {median_ms:.1f} | "
            f"{fastest_ms:.1f} | {fastest_name} |"
        )

    lines.append(_latency_group_row("Local", local_runs))
    lines.append(_latency_group_row("Remote", remote_runs))

    lines.extend(
        [
            "",
            "## Pareto Frontier (Quality/Latency/Memory)",
            "",
            "| Run | Provider | Model | Routing | Temp | Success | Tool Sel | Arg Acc | Recovery | Avg ms | Mem MB | Tool Err | Tok/s | Tokens | Score |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(row(run, include_score=True) for run in pareto)

    lines.extend(
        [
            "",
            "## Tool Routing A/B (Will vs Can)",
            "",
            "- `LLM`: model-directed tool choice from prompt only (will it use tools correctly?)",
            "- `Intent`: deterministic routing enabled (can the system force tool success?)",
            "",
        ]
    )
    if ab_rows:
        lines.extend(
            [
                "| Model@Ctx | LLM Success | Intent Success | Delta | LLM Tool Sel | Intent Tool Sel | Delta | LLM Score | Intent Score | Delta |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        lines.extend(
            (
                f"| {row['label']} | "
                f"{row['llm_success']:.2%} | {row['intent_success']:.2%} | {row['success_delta']:+.2%} | "
                f"{row['llm_tool']:.2%} | {row['intent_tool']:.2%} | {row['tool_delta']:+.2%} | "
                f"{row['llm_score']:.3f} | {row['intent_score']:.3f} | {row['score_delta']:+.3f} |"
            )
            for row in ab_rows
        )
    else:
        lines.append(
            "No matched LLM/Intent profile pairs found. Add profiles with the same model + context and "
            "`TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=0` (LLM) and `1` (Intent)."
        )

    if context_rows:
        lines.extend(
            [
                "",
                "## Context Window Coherence Sweep",
                "",
                f"- Near-peak ratio: {context_analysis['near_peak_ratio']:.2f}",
                f"- Dropoff ratio: {context_analysis['dropoff_ratio']:.2f}",
                "",
                "| Model Family | Tested Contexts | Peak Coherence @Ctx | Peak Balanced | Optimal Ctx | Dropoff Ctx | Peak Success | Peak Avg ms | Peak Mem MB |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        lines.extend(
            (
                f"| {row['family']} | {row['contexts']} | "
                f"{row['peak_coherence_score']:.3f} @ {row['peak_ctx']} | "
                f"{row['peak_balanced_score']:.3f} | {row['optimal_ctx']} | "
                f"{(row['dropoff_ctx'] if row['dropoff_ctx'] is not None else 'none')} | "
                f"{row['peak_success']:.2%} | {row['peak_latency_ms']:.1f} | "
                f"{row['peak_memory_mb']:.1f} |"
            )
            for row in context_rows
        )

    top_per_provider = top_n_per_provider(report, n=3)
    lines.extend(["", "## Top 3 Per Provider", ""])
    if top_per_provider:
        lines.extend(
            [
                "| Provider | Rank | Run | Model | Temp | Success | Score |",
                "|---|---:|---|---|---:|---:|---:|",
            ]
        )
        for provider, provider_runs in top_per_provider.items():
            for rank, prun in enumerate(provider_runs, start=1):
                profile = prun.get("profile") or {}
                agg = prun["aggregate"]
                score = _rubric_score(agg, rubric)
                lines.append(
                    f"| {provider} | {rank} | {profile.get('name', '')} | "
                    f"{profile.get('model', '')} | "
                    f"{profile.get('temperature', 0.0):.1f} | "
                    f"{_coerce_float(agg.get('task_success_rate'), 0.0):.2%} | "
                    f"{score:.3f} |"
                )
    else:
        lines.append("No successful runs.")

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
    if remote_rank:
        best_remote = remote_rank[0]
        best_remote_score = _rubric_score(best_remote["aggregate"], remote_rubric)
        lines.extend(
            [
                f"- Best remote option (memory-agnostic): `{best_remote['profile']['name']}` "
                f"({best_remote['profile']['model']}, score={best_remote_score:.3f})",
            ]
        )
    if context_rows:
        lines.extend(
            [
                "- Context recommendations (near-peak quality at lowest context):",
            ]
        )
        lines.extend(
            f"  - `{row['family']}` -> `n_ctx={row['optimal_ctx']}` "
            f"(dropoff: {row['dropoff_ctx'] if row['dropoff_ctx'] is not None else 'not observed'})"
            for row in context_rows
        )
    if ab_rows:
        avg_success_gap = statistics.fmean(row["success_delta"] for row in ab_rows)
        avg_score_gap = statistics.fmean(row["score_delta"] for row in ab_rows)
        lines.extend(
            [
                f"- Routing gap summary: intent minus llm avg success delta = {avg_success_gap:+.2%}",
                f"- Routing gap summary: intent minus llm avg score delta = {avg_score_gap:+.3f}",
            ]
        )
    return "\n".join(lines) + "\n"
