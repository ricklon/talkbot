import json
from pathlib import Path

import pytest

from talkbot.benchmark import (
    BenchmarkProfile,
    TTS_VOICE_DIRECTIVE,
    ToolCallTrace,
    _evaluate_turn,
    _tts_directive_ab_rows,
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


# --- TTS friction scoring tests ---


def test_turn_result_has_tts_friction_fields(tmp_path):
    """Every TurnResult has tts_friction_score and tts_friction_detail."""
    profile = BenchmarkProfile(name="test", provider="fake", model="fake", use_tools=False)
    scenarios = [
        {
            "id": "s1",
            "name": "clean",
            "tags": [],
            "turns": [{"user": "hi", "expect": {}}],
        }
    ]
    report = run_benchmark(
        profiles=[profile],
        scenarios=scenarios,
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
    )
    turn = report["runs"][0]["scenarios"][0]["turns"][0]
    assert "tts_friction_score" in turn
    assert "tts_friction_detail" in turn
    assert isinstance(turn["tts_friction_score"], int)
    assert isinstance(turn["tts_friction_detail"], dict)


def test_aggregate_has_friction_fields(tmp_path):
    """RunAggregate includes avg_tts_friction_score and tts_friction_zero_rate."""
    profile = BenchmarkProfile(name="test", provider="fake", model="fake", use_tools=False)
    scenarios = [
        {
            "id": "s1",
            "name": "clean",
            "tags": [],
            "turns": [{"user": "hi", "expect": {}}],
        }
    ]
    report = run_benchmark(
        profiles=[profile],
        scenarios=scenarios,
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
    )
    agg = report["runs"][0]["aggregate"]
    assert "avg_tts_friction_score" in agg
    assert "tts_friction_zero_rate" in agg
    # FakeBenchClient returns "ok" — no markdown, so friction should be 0
    assert agg["avg_tts_friction_score"] == 0.0
    assert agg["tts_friction_zero_rate"] == 1.0  # _percent returns 0-1 fraction


# --- PR 4: endurance tests ---


def _endurance_scenario(turns=5):
    """Short endurance scenario for testing; last turn is a recall check."""
    turn_list = [
        {"user": "hi", "expect": {"response_contains": ["ok"]}}
        for _ in range(turns - 1)
    ]
    turn_list.append({
        "user": "hi",
        "recall_turn": True,
        "expect": {"response_contains": ["ok"]},
    })
    return [{
        "id": "endurance_test",
        "name": "Endurance Test",
        "tags": ["endurance"],
        "type": "endurance",
        "reset_state": True,
        "turns": turn_list,
    }]


def test_turn_result_has_failure_mode_field(tmp_path):
    """Every TurnResult has a failure_mode field defaulting to 'none'."""
    profile = BenchmarkProfile(name="t", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=_endurance_scenario(turns=3),
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
    )
    turns = report["runs"][0]["scenarios"][0]["turns"]
    for turn in turns:
        assert "failure_mode" in turn
        assert turn["failure_mode"] in ("none", "repetition", "refusal")


def test_turn_result_has_recall_turn_field(tmp_path):
    """recall_turn is True on turns where scenario marks recall_turn: true."""
    profile = BenchmarkProfile(name="t", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=_endurance_scenario(turns=3),
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
    )
    turns = report["runs"][0]["scenarios"][0]["turns"]
    assert turns[-1]["recall_turn"] is True
    assert turns[0]["recall_turn"] is False


def test_scenario_result_has_latency_growth_rate(tmp_path):
    """latency_growth_rate is computed for scenarios with >=3 turns."""
    profile = BenchmarkProfile(name="t", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=_endurance_scenario(turns=4),
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
    )
    scenario = report["runs"][0]["scenarios"][0]
    assert "latency_growth_rate" in scenario
    assert isinstance(scenario["latency_growth_rate"], float)


def test_scenario_result_latency_growth_rate_none_for_short(tmp_path):
    """latency_growth_rate is None for scenarios with <3 turns."""
    profile = BenchmarkProfile(name="t", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=[{
            "id": "s1", "name": "short", "tags": [], "reset_state": True,
            "turns": [{"user": "hi", "expect": {}}],
        }],
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
    )
    scenario = report["runs"][0]["scenarios"][0]
    assert scenario["latency_growth_rate"] is None


def test_aggregate_has_endurance_fields(tmp_path):
    """RunAggregate includes endurance_scenario_count and failure_mode_counts."""
    profile = BenchmarkProfile(name="t", provider="fake", model="fake", use_tools=False)
    report = run_benchmark(
        profiles=[profile],
        scenarios=_endurance_scenario(turns=4),
        output_dir=tmp_path,
        runner_info={"label": "t", "hostname": "h"},
        client_factory=lambda p: FakeBenchClient(),
    )
    agg = report["runs"][0]["aggregate"]
    assert "endurance_scenario_count" in agg
    assert agg["endurance_scenario_count"] == 1
    assert "failure_mode_counts" in agg
    assert isinstance(agg["failure_mode_counts"], dict)


def test_endurance_scenarios_load_from_disk():
    """The three endurance scenario JSON files are valid and loadable."""
    from talkbot.benchmark import load_scenarios
    import pathlib
    endurance_dir = pathlib.Path("tests/conversations/endurance")
    for fname in [
        "endurance_timer_sequence.json",
        "endurance_list_management.json",
        "endurance_memory_recall.json",
    ]:
        scenarios = load_scenarios(str(endurance_dir / fname))
        assert len(scenarios) == 1
        scenario = scenarios[0]
        assert "endurance" in scenario["tags"]
        assert len(scenario["turns"]) >= 10
        # At least one recall turn should be marked
        recall_turns = [t for t in scenario["turns"] if t.get("recall_turn")]
        assert len(recall_turns) >= 1


def test_detect_failure_mode_refusal():
    from talkbot.benchmark import _detect_failure_mode
    assert _detect_failure_mode("I cannot help with that.", None) == "refusal"
    assert _detect_failure_mode("I'm unable to do that.", None) == "refusal"
    assert _detect_failure_mode("Sorry, I can't assist.", None) == "refusal"


def test_detect_failure_mode_repetition():
    from talkbot.benchmark import _detect_failure_mode
    prior = "The timer is set for five minutes and counting down."
    same = "The timer is set for five minutes and counting down."
    assert _detect_failure_mode(same, prior) == "repetition"


def test_detect_failure_mode_none():
    from talkbot.benchmark import _detect_failure_mode
    assert _detect_failure_mode("Sure, I set a timer for 5 minutes.", None) == "none"
    assert _detect_failure_mode(
        "Sure, I set a timer.",
        "Your list now has three items: passport, charger, and hat.",
    ) == "none"


def test_linear_slope_positive():
    from talkbot.benchmark import _linear_slope
    # Steadily increasing latencies
    latencies = [100.0, 200.0, 300.0, 400.0, 500.0]
    slope = _linear_slope(latencies)
    assert slope > 0


def test_linear_slope_flat():
    from talkbot.benchmark import _linear_slope
    latencies = [100.0, 100.0, 100.0, 100.0]
    assert _linear_slope(latencies) == 0.0


def test_linear_slope_short_returns_zero():
    from talkbot.benchmark import _linear_slope
    assert _linear_slope([100.0]) == 0.0
    assert _linear_slope([100.0, 200.0]) == 0.0


# --- TTS directive A/B tests ---

def _make_run(name, provider, model, tts_directive, friction, clean_rate, success_rate, spoken=None):
    """Build a minimal run dict for _tts_directive_ab_rows tests."""
    agg = {
        "task_success_rate": success_rate,
        "tool_selection_accuracy": success_rate,
        "argument_accuracy": success_rate,
        "recovery_success_rate": success_rate,
        "avg_turn_latency_ms": 500.0,
        "memory_peak_mb": 200.0,
        "tool_call_error_rate": 0.0,
        "avg_prefill_tok_s": 0.0,
        "avg_gen_tok_s": 0.0,
        "total_tokens": 0,
        "avg_tts_friction_score": friction,
        "tts_friction_zero_rate": clean_rate,
        "avg_judge_spoken_quality": spoken,
        "avg_judge_correctness": None,
        "judge_calls": 0,
        "endurance_scenario_count": 0,
    }
    return {
        "status": "ok",
        "profile": {
            "name": name,
            "provider": provider,
            "model": model,
            "tts_directive": tts_directive,
            "temperature": 0.0,
        },
        "aggregate": agg,
        "scenarios": [],
    }


def test_tts_directive_ab_rows_produces_row_for_matched_pair():
    runs = [
        _make_run("qwen-baseline", "local_server", "qwen3.5", False, friction=4.0, clean_rate=0.2, success_rate=0.9),
        _make_run("qwen-tts",      "local_server", "qwen3.5", True,  friction=1.0, clean_rate=0.7, success_rate=0.88),
    ]
    rows = _tts_directive_ab_rows(runs)
    assert len(rows) == 1
    row = rows[0]
    assert row["friction_delta"] == pytest.approx(-3.0)
    assert row["clean_delta"] == pytest.approx(0.5)
    assert row["success_delta"] == pytest.approx(-0.02)


def test_tts_directive_ab_rows_no_row_without_pair():
    # Only a baseline — no tts counterpart
    runs = [
        _make_run("qwen-baseline", "local_server", "qwen3.5", False, 4.0, 0.2, 0.9),
    ]
    rows = _tts_directive_ab_rows(runs)
    assert rows == []


def test_tts_directive_ab_rows_sorted_by_friction_improvement():
    runs = [
        _make_run("a-baseline", "local_server", "model-a", False, 5.0, 0.1, 0.9),
        _make_run("a-tts",      "local_server", "model-a", True,  1.0, 0.8, 0.88),
        _make_run("b-baseline", "openrouter",   "model-b", False, 3.0, 0.3, 0.95),
        _make_run("b-tts",      "openrouter",   "model-b", True,  2.5, 0.4, 0.94),
    ]
    rows = _tts_directive_ab_rows(runs)
    assert len(rows) == 2
    # Most improvement (most negative delta) first
    assert rows[0]["friction_delta"] <= rows[1]["friction_delta"]


def test_tts_directive_constant_is_non_empty():
    assert len(TTS_VOICE_DIRECTIVE) > 20
    assert "markdown" in TTS_VOICE_DIRECTIVE.lower()


def test_tts_directive_ab_leaderboard_section_rendered(tmp_path):
    runs = [
        _make_run("q-baseline", "local_server", "qwen3.5", False, 4.0, 0.2, 0.9),
        _make_run("q-tts",      "local_server", "qwen3.5", True,  1.0, 0.7, 0.88),
    ]
    report = {
        "finished_at": "2026-01-01T00:00:00Z",
        "run_count": 2,
        "scenario_count": 3,
        "runs": runs,
        "meta": {},
        "runner": {},
    }
    md = build_leaderboard_markdown(report)
    assert "## TTS Directive A/B" in md
    assert "Friction" in md
    assert "-3.00" in md  # friction_delta
