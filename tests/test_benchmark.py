import json
from pathlib import Path

from talkbot.benchmark import (
    BenchmarkProfile,
    ToolCallTrace,
    _evaluate_turn,
    build_leaderboard_markdown,
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
        if "list timers" in lower:
            return self.tools["list_timers"]()
        if "cancel timer 1" in lower:
            return self.tools["cancel_timer"](timer_id="1")
        if "create a grocery list" in lower:
            return self.tools["create_list"](list_name="grocery")
        if "add milk to the grocery list" in lower:
            return self.tools["add_to_list"](item="milk", list_name="grocery")
        if "what lists do you have" in lower:
            return self.tools["list_all_lists"]()
        if "remember that my favorite color is blue" in lower:
            return self.tools["remember"](key="favorite_color", value="blue")
        if "what is my favorite color" in lower:
            return self.tools["recall"](key="favorite_color")
        return "Unhandled"


def test_load_scenarios_from_directory():
    scenarios = load_scenarios("tests/conversations")
    ids = {scenario["id"] for scenario in scenarios}
    assert {"timer_basics", "list_basics", "memory_basics"}.issubset(ids)


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
    assert report["run_count"] == 1
    run = report["runs"][0]
    assert run["status"] == "ok"
    assert run["aggregate"]["task_success_rate"] == 1.0
    assert run["aggregate"]["tool_selection_accuracy"] == 1.0
    assert run["aggregate"]["argument_accuracy"] == 1.0
    assert run["aggregate"]["total_tokens"] > 0
    assert run["aggregate"]["max_history_messages"] > 0


def test_write_outputs_and_leaderboard(tmp_path):
    report = {
        "started_at": "2026-01-01T00:00:00+0000",
        "finished_at": "2026-01-01T00:00:10+0000",
        "scenario_count": 1,
        "run_count": 1,
        "runs": [
            {
                "profile": {
                    "name": "demo",
                    "provider": "local",
                    "model": "fake/model",
                },
                "status": "ok",
                "aggregate": {
                    "task_success_rate": 1.0,
                    "tool_selection_accuracy": 1.0,
                    "argument_accuracy": 1.0,
                    "avg_turn_latency_ms": 25.0,
                    "memory_peak_mb": 12.0,
                    "total_tokens": 42,
                },
            }
        ],
    }
    md = build_leaderboard_markdown(report)
    assert "Quality Rank" in md
    assert "Low-Memory Rank" in md
    assert "Balanced Rank" in md

    paths = write_outputs(report, tmp_path)
    assert Path(paths["results"]).exists()
    assert Path(paths["leaderboard"]).exists()
    result_payload = json.loads(Path(paths["results"]).read_text())
    assert result_payload["run_count"] == 1


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
