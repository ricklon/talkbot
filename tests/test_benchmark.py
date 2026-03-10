import json
from pathlib import Path

from talkbot.benchmark import (
    BenchmarkProfile,
    ToolCallTrace,
    _evaluate_turn,
    build_leaderboard_markdown,
    load_matrix_config,
    load_scenarios,
    run_benchmark,
    write_outputs,
)
from conftest import FakeBenchClient


class ErrorBenchClient(FakeBenchClient):
    def chat_with_tools(self, messages, temperature=0.0, max_tokens=None):
        del messages, temperature, max_tokens
        self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        raise RuntimeError("simulated model execution failure")


def test_load_scenarios_from_directory():
    scenarios = load_scenarios("tests/conversations")
    ids = {scenario["id"] for scenario in scenarios}
    assert {
        "timer_basics",
        "list_basics",
        "memory_persistent_strict",
        "memory_context_flexible",
        "recovery_timer_retry",
        "list_multistep_packing",
        "memory_context_pressure",
    }.issubset(ids)


def test_run_benchmark_with_fake_client(tmp_path):
    scenarios = load_scenarios("tests/conversations")
    profiles = [
        BenchmarkProfile(
            name="fake-local",
            provider="local",
            model="fake/model",
            use_tools=True,
            max_tokens=128,
            temperature=0.0,
        )
    ]

    report = run_benchmark(
        profiles=profiles,
        scenarios=scenarios,
        output_dir=tmp_path,
        client_factory=lambda _profile: FakeBenchClient(),
    )
    assert isinstance(report.get("runner"), dict)
    assert report["runner"].get("os")
    assert report["runner"].get("python_version")
    assert report["run_count"] == 1
    run = report["runs"][0]
    assert run["status"] == "ok"
    assert run["aggregate"]["task_success_rate"] == 1.0
    assert run["aggregate"]["tool_selection_accuracy"] == 1.0
    assert run["aggregate"]["argument_accuracy"] == 1.0
    assert run["aggregate"]["total_tokens"] > 0
    assert run["aggregate"]["max_history_messages"] > 0
    assert run["aggregate"]["tokens_per_second"] > 0.0
    assert run["aggregate"]["tool_call_error_rate"] > 0.0
    assert run["aggregate"]["model_execution_error_rate"] == 0.0


def test_run_benchmark_model_execution_errors_do_not_score_tool_metrics_perfect(tmp_path):
    scenarios = [
        {
            "id": "error-only",
            "name": "Error Only",
            "description": "",
            "tags": [],
            "system_prompt": None,
            "reset_state": True,
            "turns": [{"user": "hello", "expect": {}}],
        }
    ]
    profiles = [
        BenchmarkProfile(
            name="fake-error",
            provider="local",
            model="fake/model",
            use_tools=True,
            max_tokens=32,
            temperature=0.0,
        )
    ]
    report = run_benchmark(
        profiles=profiles,
        scenarios=scenarios,
        output_dir=tmp_path,
        client_factory=lambda _profile: ErrorBenchClient(),
    )
    run = report["runs"][0]
    assert run["status"] == "ok"
    assert run["aggregate"]["model_execution_error_count"] == 1
    assert run["aggregate"]["expected_tool_calls"] == 0
    assert run["aggregate"]["expected_arg_checks"] == 0
    assert run["aggregate"]["tool_selection_accuracy"] == 0.0
    assert run["aggregate"]["argument_accuracy"] == 0.0


def test_write_outputs_and_leaderboard(tmp_path):
    report = {
        "started_at": "2026-01-01T00:00:00+0000",
        "finished_at": "2026-01-01T00:00:10+0000",
        "runner": {
            "label": "linux-main",
            "hostname": "bench-host",
            "os": "Linux",
            "os_release": "6.8.0",
            "machine": "x86_64",
            "python_version": "3.12.8",
            "raspberry_pi_model": None,
            "notes": "cpu-only",
        },
        "scenario_count": 2,
        "run_count": 2,
        "rubric": {
            "version": "test.v1",
            "weights": {"task_success_rate": 1.0},
            "penalties": {"latency_ms_multiplier": 0.0},
        },
        "context_analysis": {
            "near_peak_ratio": 0.95,
            "dropoff_ratio": 0.9,
        },
        "runs": [
            {
                "profile": {
                    "name": "demo-ctx2048",
                    "provider": "local",
                    "model": "fake/model",
                    "env": {"TALKBOT_LOCAL_N_CTX": "2048"},
                },
                "status": "ok",
                "aggregate": {
                    "task_success_rate": 1.0,
                    "tool_selection_accuracy": 1.0,
                    "argument_accuracy": 1.0,
                    "avg_turn_latency_ms": 25.0,
                    "memory_peak_mb": 12.0,
                    "tool_call_error_rate": 0.0,
                    "tokens_per_second": 4.0,
                    "total_tokens": 42,
                    "tag_success": {"recovery": 1.0},
                },
            },
            {
                "profile": {
                    "name": "demo-ctx4096",
                    "provider": "local",
                    "model": "fake/model",
                    "env": {"TALKBOT_LOCAL_N_CTX": "4096"},
                },
                "status": "ok",
                "aggregate": {
                    "task_success_rate": 0.85,
                    "tool_selection_accuracy": 0.85,
                    "argument_accuracy": 0.85,
                    "avg_turn_latency_ms": 35.0,
                    "memory_peak_mb": 24.0,
                    "tool_call_error_rate": 0.01,
                    "tokens_per_second": 3.5,
                    "total_tokens": 55,
                    "tag_success": {"recovery": 0.8},
                },
            }
        ],
    }
    md = build_leaderboard_markdown(report)
    assert "Tool Routing A/B (Will vs Can)" in md
    assert "## Scope" in md
    assert "Runner: `linux-main`" in md
    assert "Runner notes: cpu-only" in md
    assert "Quality Rank" in md
    assert "| Run | Provider | Model | Routing |" in md
    assert "Low-Memory Rank" in md
    assert "Balanced Rank" in md
    assert "Pareto Frontier" in md
    assert "Latency Snapshot (Local vs Remote)" in md
    assert "Rubric" in md
    assert "Context Window Coherence Sweep" in md
    assert "Optimal Ctx" in md

    paths = write_outputs(report, tmp_path)
    assert Path(paths["results"]).exists()
    assert Path(paths["leaderboard"]).exists()
    result_payload = json.loads(Path(paths["results"]).read_text())
    assert result_payload["run_count"] == 2


def test_load_matrix_config_expands_context_windows(tmp_path):
    matrix_path = tmp_path / "matrix.json"
    matrix_path.write_text(
        json.dumps(
            {
                "benchmark": {
                    "schema_version": "2026.1",
                    "rubric": {
                        "version": "custom",
                        "weights": {"task_success_rate": 0.7},
                    },
                    "context_analysis": {
                        "near_peak_ratio": 0.96,
                        "dropoff_ratio": 0.88,
                    },
                },
                "profiles": [
                    {
                        "name": "demo",
                        "provider": "local",
                        "model": "fake/model",
                        "context_windows": [2048, 4096],
                        "env": {"TALKBOT_LOCAL_DIRECT_TOOL_ROUTING": "0"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    matrix = load_matrix_config(matrix_path)
    names = [profile.name for profile in matrix["profiles"]]
    assert names == ["demo-ctx2048", "demo-ctx4096"]
    assert matrix["profiles"][0].env["TALKBOT_LOCAL_N_CTX"] == "2048"
    assert matrix["rubric"]["version"] == "custom"
    assert matrix["rubric"]["weights"]["task_success_rate"] == 0.7
    assert matrix["context_analysis"]["near_peak_ratio"] == 0.96
    assert matrix["context_analysis"]["dropoff_ratio"] == 0.88


def test_leaderboard_includes_ab_routing_section():
    report = {
        "started_at": "2026-01-01T00:00:00+0000",
        "finished_at": "2026-01-01T00:00:10+0000",
        "scenario_count": 1,
        "run_count": 2,
        "rubric": {
            "version": "test.v1",
            "weights": {"task_success_rate": 1.0},
            "penalties": {"latency_ms_multiplier": 0.0},
        },
        "runs": [
            {
                "profile": {
                    "name": "demo-llm-ctx2048",
                    "provider": "local",
                    "model": "fake/model",
                    "local_model_path": "models/fake.gguf",
                    "env": {
                        "TALKBOT_LOCAL_N_CTX": "2048",
                        "TALKBOT_LOCAL_DIRECT_TOOL_ROUTING": "0",
                    },
                },
                "status": "ok",
                "aggregate": {
                    "task_success_rate": 0.5,
                    "tool_selection_accuracy": 0.7,
                    "argument_accuracy": 0.9,
                    "avg_turn_latency_ms": 20.0,
                    "memory_peak_mb": 10.0,
                    "tool_call_error_rate": 0.1,
                    "model_execution_error_rate": 0.0,
                    "tokens_per_second": 3.0,
                    "total_tokens": 20,
                    "tag_success": {},
                },
            },
            {
                "profile": {
                    "name": "demo-intent-ctx2048",
                    "provider": "local",
                    "model": "fake/model",
                    "local_model_path": "models/fake.gguf",
                    "env": {
                        "TALKBOT_LOCAL_N_CTX": "2048",
                        "TALKBOT_LOCAL_DIRECT_TOOL_ROUTING": "1",
                    },
                },
                "status": "ok",
                "aggregate": {
                    "task_success_rate": 1.0,
                    "tool_selection_accuracy": 1.0,
                    "argument_accuracy": 1.0,
                    "avg_turn_latency_ms": 15.0,
                    "memory_peak_mb": 10.0,
                    "tool_call_error_rate": 0.0,
                    "model_execution_error_rate": 0.0,
                    "tokens_per_second": 3.5,
                    "total_tokens": 20,
                    "tag_success": {},
                },
            },
        ],
    }
    md = build_leaderboard_markdown(report)
    assert "Tool Routing A/B (Will vs Can)" in md
    assert "intent minus llm avg success delta" in md


def test_leaderboard_ab_section_without_pairs_shows_guidance():
    report = {
        "started_at": "2026-01-01T00:00:00+0000",
        "finished_at": "2026-01-01T00:00:10+0000",
        "scenario_count": 1,
        "run_count": 1,
        "rubric": {"version": "test.v1", "weights": {"task_success_rate": 1.0}},
        "runs": [
            {
                "profile": {
                    "name": "demo-llm",
                    "provider": "local",
                    "model": "fake/model",
                    "env": {"TALKBOT_LOCAL_DIRECT_TOOL_ROUTING": "0"},
                },
                "status": "ok",
                "aggregate": {
                    "task_success_rate": 0.5,
                    "tool_selection_accuracy": 0.5,
                    "argument_accuracy": 0.5,
                    "avg_turn_latency_ms": 10.0,
                    "memory_peak_mb": 10.0,
                    "tool_call_error_rate": 0.0,
                    "model_execution_error_rate": 0.0,
                    "tokens_per_second": 1.0,
                    "total_tokens": 10,
                    "tag_success": {},
                },
            }
        ],
    }
    md = build_leaderboard_markdown(report)
    assert "Tool Routing A/B (Will vs Can)" in md
    assert "No matched LLM/Intent profile pairs found" in md


def test_profile_system_prompt_is_prepended(tmp_path):
    scenarios = [
        {
            "id": "prompt-check",
            "name": "Prompt Check",
            "description": "",
            "tags": [],
            "system_prompt": None,
            "reset_state": True,
            "turns": [{"user": "What lists do you have?", "expect": {}}],
        }
    ]

    class PromptClient(FakeBenchClient):
        def chat_with_tools(self, messages, temperature=0.0, max_tokens=None):
            del temperature, max_tokens
            assert messages[0]["role"] == "system"
            assert "tool-use reliability" in messages[0]["content"]
            self.last_usage = {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
            return self.tools["list_all_lists"]()

    report = run_benchmark(
        profiles=[
            BenchmarkProfile(
                name="prompt",
                provider="local",
                model="fake/model",
                system_prompt="You are being evaluated for tool-use reliability.",
            )
        ],
        scenarios=scenarios,
        output_dir=tmp_path,
        client_factory=lambda _profile: PromptClient(),
    )
    assert report["runs"][0]["status"] == "ok"


def test_arg_alias_normalization_for_timer_and_cancel():
    turn = {
        "user": "Set and cancel",
        "expect": {
            "tool_calls": [
                {"name": "set_timer", "args_contains": {"seconds": 10}},
                {"name": "cancel_timer", "args_contains": {"timer_id": "1"}},
            ]
        },
    }
    tool_calls = [
        ToolCallTrace(
            scenario_id="s",
            turn_index=0,
            name="set_timer",
            args={"duration": 10},
            result="ok",
            error=None,
            latency_ms=1.0,
        ),
        ToolCallTrace(
            scenario_id="s",
            turn_index=0,
            name="cancel_timer",
            args={"id": 1},
            result="ok",
            error=None,
            latency_ms=1.0,
        ),
    ]
    passed, assertions, _, _, expected_arg_checks, matched_arg_checks = _evaluate_turn(
        turn=turn,
        response="ok",
        tool_calls=tool_calls,
        latency_ms=2.0,
    )
    assert passed is True
    assert assertions == []
    assert expected_arg_checks == 2
    assert matched_arg_checks == 2


def test_subset_match_treats_numeric_strings_as_equal():
    turn = {
        "user": "cancel timer",
        "expect": {
            "tool_calls": [
                {"name": "cancel_timer", "args_contains": {"timer_id": "1"}}
            ]
        },
    }
    tool_calls = [
        ToolCallTrace(
            scenario_id="s",
            turn_index=0,
            name="cancel_timer",
            args={"id": 1},
            result="ok",
            error=None,
            latency_ms=1.0,
        )
    ]
    passed, assertions, _, _, expected_arg_checks, matched_arg_checks = _evaluate_turn(
        turn=turn,
        response="ok",
        tool_calls=tool_calls,
        latency_ms=2.0,
    )
    assert passed is True
    assert assertions == []
    assert expected_arg_checks == 1
    assert matched_arg_checks == 1


# --- normalization tests for _evaluate_turn ---


def test_evaluate_turn_response_contains_strips_markdown():
    """Markdown in the response is normalized before contains check."""
    turn = {
        "user": "cancel the timer",
        "expect": {"response_contains": ["cancel timer"]},
    }
    # Response has underscore identifier — normalize_for_tts converts it
    passed, assertions, *_ = _evaluate_turn(
        turn=turn,
        response="I will cancel_timer for you.",
        tool_calls=[],
        latency_ms=1.0,
    )
    assert passed is True
    assert assertions == []


def test_evaluate_turn_response_regex_matches_normalized():
    """response_regex is matched against normalized text."""
    turn = {
        "user": "cancel the timer",
        "expect": {"response_regex": r"cancel timer"},
    }
    # Raw response uses underscore; normalization converts it so regex matches
    passed, assertions, *_ = _evaluate_turn(
        turn=turn,
        response="I will cancel_timer now.",
        tool_calls=[],
        latency_ms=1.0,
    )
    assert passed is True
    assert assertions == []


def test_evaluate_turn_response_spoken_contains():
    """response_spoken_contains matches against normalized text."""
    turn = {
        "user": "status",
        "expect": {"response_spoken_contains": ["timer 3"]},
    }
    passed, assertions, *_ = _evaluate_turn(
        turn=turn,
        response="Timer ID: 3 is active.",
        tool_calls=[],
        latency_ms=1.0,
    )
    assert passed is True
    assert assertions == []


def test_evaluate_turn_response_spoken_regex():
    """response_spoken_regex matches against normalized text."""
    turn = {
        "user": "status",
        "expect": {"response_spoken_regex": r"(?i)timer \d+"},
    }
    passed, assertions, *_ = _evaluate_turn(
        turn=turn,
        response="Timer ID: 5 is running.",
        tool_calls=[],
        latency_ms=1.0,
    )
    assert passed is True
    assert assertions == []


def test_evaluate_turn_normalization_report_field(tmp_path):
    """run_benchmark report includes normalization field."""
    from talkbot.benchmark import run_benchmark

    scenarios = [
        {
            "id": "s1",
            "name": "simple",
            "tags": [],
            "turns": [
                {"user": "hi", "expect": {"response_contains": ["ok"]}},
            ],
        }
    ]
    profile = BenchmarkProfile(name="test", provider="fake", model="fake")
    report = run_benchmark(
        profiles=[profile],
        scenarios=scenarios,
        output_dir=tmp_path,
        runner_info={"label": "test", "hostname": "localhost"},
        client_factory=lambda p: FakeBenchClient(),
    )
    assert report.get("normalization") == "v1"


# --- pass^k tests ---


def _simple_scenarios(user="hi", expect=None):
    return [
        {
            "id": "s1",
            "name": "simple",
            "tags": [],
            "turns": [{"user": user, "expect": expect or {"response_contains": ["ok"]}}],
        }
    ]


def test_pass_k_default_is_one(tmp_path):
    """Default run (k=1) sets pass_k=1 and pass_count 0 or 1."""
    # use_tools=False so chat_completion() is called, returning "ok"
    profile = BenchmarkProfile(name="test", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=_simple_scenarios(),
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
    )
    assert report["pass_k"] == 1
    scenario = report["runs"][0]["scenarios"][0]
    assert scenario["pass_k"] == 1
    assert scenario["pass_count"] in (0, 1)
    assert scenario["pass_rate"] in (0.0, 1.0)


def test_pass_k_three_all_pass(tmp_path):
    """k=3 with a scenario that always passes → pass_count=3, pass_rate=1.0."""
    profile = BenchmarkProfile(name="test", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=_simple_scenarios(),
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
        pass_k=3,
    )
    assert report["pass_k"] == 3
    scenario = report["runs"][0]["scenarios"][0]
    assert scenario["pass_k"] == 3
    assert scenario["pass_count"] == 3
    assert scenario["pass_rate"] == 1.0
    assert scenario["reliability_band"] == "high"
    assert scenario["passed"] is True


def test_pass_k_three_all_fail(tmp_path):
    """k=3 with a scenario that always fails → pass_count=0, reliability_band=low."""
    profile = BenchmarkProfile(name="test", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=_simple_scenarios(expect={"response_contains": ["NEVER_IN_RESPONSE"]}),
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
        pass_k=3,
    )
    scenario = report["runs"][0]["scenarios"][0]
    assert scenario["pass_count"] == 0
    assert scenario["pass_rate"] == 0.0
    assert scenario["reliability_band"] == "low"
    assert scenario["passed"] is False


def test_pass_k_report_metadata(tmp_path):
    """Report includes pass_k and pass_k_temperature when k > 1."""
    profile = BenchmarkProfile(name="test", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=_simple_scenarios(),
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
        pass_k=3,
        pass_k_temperature=0.5,
    )
    assert report["pass_k"] == 3
    assert report["pass_k_temperature"] == 0.5


def test_pass_k_one_no_temperature_in_report(tmp_path):
    """pass_k_temperature is None in report when k=1."""
    profile = BenchmarkProfile(name="test", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=_simple_scenarios(),
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
    )
    assert report["pass_k_temperature"] is None


def test_high_variability_tag_uses_k5(tmp_path):
    """Scenarios tagged 'high_variability' always use k=5 regardless of --pass-k."""
    profile = BenchmarkProfile(name="test", provider="fake", model="fake", use_tools=False)
    scenarios = [
        {
            "id": "s1",
            "name": "recovery",
            "tags": ["high_variability"],
            "turns": [{"user": "hi", "expect": {"response_contains": ["ok"]}}],
        }
    ]
    report = run_benchmark(
        profiles=[profile],
        scenarios=scenarios,
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
        pass_k=1,  # global default is 1, but tag should override to 5
    )
    scenario = report["runs"][0]["scenarios"][0]
    assert scenario["pass_k"] == 5
    assert scenario["pass_count"] == 5


def test_reliability_band_values(tmp_path):
    """reliability_band is 'high' for pass_rate>=0.80, 'medium' >=0.40, 'low' below."""
    from talkbot.benchmark import _reliability_band
    assert _reliability_band(1.0) == "high"
    assert _reliability_band(0.80) == "high"
    assert _reliability_band(0.79) == "medium"
    assert _reliability_band(0.40) == "medium"
    assert _reliability_band(0.39) == "low"
    assert _reliability_band(0.0) == "low"
