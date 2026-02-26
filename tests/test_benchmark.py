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


class FakeBenchClient:
    supports_tools = True
    provider_name = "fake"

    def __init__(self):
        self.tools = {}
        self.last_usage = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def clear_tools(self):
        self.tools.clear()

    def register_tool(self, name, func, description, parameters):
        del description, parameters
        self.tools[name] = func

    def chat_completion(self, messages, temperature=0.0, max_tokens=None):
        del messages, temperature, max_tokens
        return {"choices": [{"message": {"content": "ok"}}]}

    def chat_with_tools(self, messages, temperature=0.0, max_tokens=None):
        del temperature, max_tokens
        user_text = str(messages[-1]["content"])
        self.last_usage = {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        }
        lower = user_text.lower()
        if "set a timer for 10" in lower:
            return self.tools["set_timer"](seconds=10)
        if "set a timer for 0" in lower:
            return self.tools["set_timer"](seconds=0)
        if "retry that timer with 6" in lower:
            return self.tools["set_timer"](seconds=6)
        if "list timers" in lower:
            return self.tools["list_timers"]()
        if "cancel timer 1" in lower:
            return self.tools["cancel_timer"](timer_id="1")
        if "create a packing list" in lower:
            return self.tools["create_list"](list_name="packing")
        if "add socks and charger to the packing list" in lower:
            return self.tools["add_items_to_list"](
                items=["socks", "charger"],
                list_name="packing",
            )
        if "show me the packing list" in lower:
            return self.tools["get_list"](list_name="packing")
        if "create a grocery list" in lower:
            return self.tools["create_list"](list_name="grocery")
        if "add milk to the grocery list" in lower:
            return self.tools["add_to_list"](item="milk", list_name="grocery")
        if "what lists do you have" in lower:
            return self.tools["list_all_lists"]()
        if "remember that the launch codename is atlas" in lower:
            return self.tools["remember"](key="launch_codename", value="atlas")
        if "what launch codename did i ask you to remember" in lower:
            return self.tools["recall"](key="launch_codename")
        if "remember that my favorite color is blue" in lower:
            return self.tools["remember"](key="favorite_color", value="blue")
        if "what is my favorite color" in lower:
            return self.tools["recall"](key="favorite_color")
        return "Unhandled"


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
