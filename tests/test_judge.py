"""Tests for the LLM judge module.

All tests use dry_run=True so no real API calls are made.
"""

from talkbot.judge import (
    DEFAULT_JUDGE_MODEL,
    JudgeConfig,
    JudgeResult,
    LLMJudge,
    estimate_judge_cost,
)


# --- JudgeConfig defaults ---


def test_judge_config_defaults():
    config = JudgeConfig()
    assert config.model == DEFAULT_JUDGE_MODEL
    assert config.max_calls == 500
    assert config.dry_run is False
    assert config.api_key is None


# --- dry-run evaluation ---


def test_dry_run_clean_text_scores_high():
    config = JudgeConfig(dry_run=True)
    with LLMJudge(config) as judge:
        result = judge.evaluate_turn(
            user="Set a timer for 5 minutes",
            response="Sure, I have set a timer for 5 minutes.",
            history=[],
            tags=["timer"],
        )
    assert result.has_error is False
    assert result.spoken_quality == 5.0
    assert result.correctness == 3.0  # neutral in dry-run
    assert result.tokens_used == 0
    assert "[dry-run]" in result.reasoning


def test_dry_run_markdown_response_scores_lower():
    config = JudgeConfig(dry_run=True)
    with LLMJudge(config) as judge:
        result = judge.evaluate_turn(
            user="What can you do?",
            response="I can help with:\n- **Timers**\n- `Lists`\n## Memory",
            history=[],
            tags=["default"],
        )
    assert result.spoken_quality < 5.0


def test_dry_run_underscore_identifier_reduces_score():
    config = JudgeConfig(dry_run=True)
    with LLMJudge(config) as judge:
        result = judge.evaluate_turn(
            user="Cancel my timer",
            response="I will call cancel_timer to cancel your timer.",
            history=[],
            tags=["timer"],
        )
    assert result.spoken_quality < 5.0


def test_dry_run_uses_tag_rubric():
    config = JudgeConfig(dry_run=True)
    with LLMJudge(config) as judge:
        result = judge.evaluate_turn(
            user="What is on my shopping list?",
            response="Your shopping list has: milk, eggs.",
            history=[],
            tags=["list"],
        )
    # list rubric has 3 items
    assert len(result.checklist) == 3


def test_dry_run_unknown_tag_uses_default_rubric():
    config = JudgeConfig(dry_run=True)
    with LLMJudge(config) as judge:
        result = judge.evaluate_turn(
            user="Hello",
            response="Hello! How can I help?",
            history=[],
            tags=["unknown_tag_xyz"],
        )
    # default rubric has 3 items
    assert len(result.checklist) == 3


def test_dry_run_empty_tags_uses_default_rubric():
    config = JudgeConfig(dry_run=True)
    with LLMJudge(config) as judge:
        result = judge.evaluate_turn(
            user="Hello",
            response="Hi there!",
            history=[],
            tags=[],
        )
    assert len(result.checklist) == 3


# --- call limit ---


def test_call_limit_returns_error_result():
    config = JudgeConfig(dry_run=True, max_calls=2)
    with LLMJudge(config) as judge:
        judge.evaluate_turn(user="a", response="b", history=[], tags=[])
        judge.evaluate_turn(user="a", response="b", history=[], tags=[])
        # Third call exceeds limit
        result = judge.evaluate_turn(user="a", response="b", history=[], tags=[])
    assert result.has_error is True
    assert result.error == "call_limit_reached"
    assert result.correctness == 0.0
    assert result.spoken_quality == 0.0


def test_calls_remaining_decrements():
    config = JudgeConfig(dry_run=True, max_calls=5)
    with LLMJudge(config) as judge:
        assert judge.calls_remaining == 5
        judge.evaluate_turn(user="a", response="b", history=[], tags=[])
        assert judge.calls_remaining == 4
        assert judge.calls_made == 1


# --- JudgeResult properties ---


def test_judge_result_avg_score():
    result = JudgeResult(
        correctness=4.0,
        spoken_quality=2.0,
        checklist={},
        reasoning="test",
    )
    assert result.avg_score == 3.0


def test_judge_result_avg_score_zero_on_error():
    result = JudgeResult(
        correctness=0.0,
        spoken_quality=0.0,
        checklist={},
        reasoning="",
        error="something went wrong",
    )
    assert result.avg_score == 0.0
    assert result.has_error is True


# --- estimate_judge_cost ---


def test_estimate_judge_cost_known_model():
    est = estimate_judge_cost(
        scenario_count=50,
        avg_turns=3.0,
        model="google/gemini-2.5-flash-lite",
    )
    assert est["judge_calls"] == 150
    assert est["input_tokens"] == 150 * 700
    assert est["estimated_cost_usd"] > 0.0
    assert est["model"] == "google/gemini-2.5-flash-lite"


def test_estimate_judge_cost_free_model():
    est = estimate_judge_cost(
        scenario_count=50,
        avg_turns=3.0,
        model="meta-llama/llama-3.3-70b-instruct:free",
    )
    assert est["estimated_cost_usd"] == 0.0


def test_estimate_judge_cost_unknown_model_uses_default_rate():
    est = estimate_judge_cost(
        scenario_count=10,
        avg_turns=2.0,
        model="some/unknown-model",
    )
    # Falls back to (0.10, 0.40) — should produce a small positive cost
    assert est["estimated_cost_usd"] > 0.0


# --- benchmark integration: judge results land in TurnResult ---


def test_benchmark_run_with_dry_run_judge(tmp_path):
    """Judge results are attached to TurnResult when judge is passed to run_benchmark."""
    from talkbot.benchmark import BenchmarkProfile, TurnResult, run_benchmark
    from conftest import FakeBenchClient

    scenarios = [
        {
            "id": "s1",
            "name": "timer set",
            "tags": ["timer"],
            "turns": [
                {
                    "user": "Set a timer for 10 seconds",
                    "expect": {"tool_calls": [{"name": "set_timer"}]},
                }
            ],
        }
    ]
    profile = BenchmarkProfile(name="test", provider="fake", model="fake", use_tools=True)
    judge_config = JudgeConfig(dry_run=True)
    judge = LLMJudge(judge_config)

    report = run_benchmark(
        profiles=[profile],
        scenarios=scenarios,
        output_dir=tmp_path,
        runner_info={"label": "test", "hostname": "localhost"},
        client_factory=lambda p: FakeBenchClient(),
        judge=judge,
    )
    judge.close()

    # Report has judge metadata
    assert report["judge_model"] == DEFAULT_JUDGE_MODEL
    assert report["judge_dry_run"] is True

    # TurnResult has judge scores
    turn = report["runs"][0]["scenarios"][0]["turns"][0]
    assert turn["judge_correctness"] is not None
    assert turn["judge_spoken_quality"] is not None
    assert turn["judge_reasoning"] is not None
    assert turn["judge_error"] is None


def test_benchmark_run_without_judge_has_null_judge_fields(tmp_path):
    """When no judge is passed, judge fields are None in TurnResult."""
    from talkbot.benchmark import BenchmarkProfile, run_benchmark
    from conftest import FakeBenchClient

    scenarios = [
        {
            "id": "s1",
            "name": "simple",
            "tags": [],
            "turns": [{"user": "hi", "expect": {"response_contains": ["ok"]}}],
        }
    ]
    profile = BenchmarkProfile(name="test", provider="fake", model="fake")
    report = run_benchmark(
        profiles=[profile],
        scenarios=scenarios,
        output_dir=tmp_path,
        runner_info={"label": "test", "hostname": "localhost"},
        client_factory=lambda p: FakeBenchClient(),
        judge=None,
    )

    assert report["judge_model"] is None
    turn = report["runs"][0]["scenarios"][0]["turns"][0]
    assert turn["judge_correctness"] is None
    assert turn["judge_spoken_quality"] is None


def test_benchmark_aggregate_includes_judge_averages(tmp_path):
    """RunAggregate has avg_judge_correctness and avg_judge_spoken_quality."""
    from talkbot.benchmark import BenchmarkProfile, run_benchmark
    from conftest import FakeBenchClient

    scenarios = [
        {
            "id": "s1",
            "name": "timer",
            "tags": ["timer"],
            "turns": [
                {"user": "Set a timer for 10 seconds", "expect": {}},
                {"user": "Cancel the timer", "expect": {}},
            ],
        }
    ]
    profile = BenchmarkProfile(name="test", provider="fake", model="fake")
    judge = LLMJudge(JudgeConfig(dry_run=True))

    report = run_benchmark(
        profiles=[profile],
        scenarios=scenarios,
        output_dir=tmp_path,
        runner_info={"label": "test", "hostname": "localhost"},
        client_factory=lambda p: FakeBenchClient(),
        judge=judge,
    )
    judge.close()

    agg = report["runs"][0]["aggregate"]
    assert agg["avg_judge_correctness"] is not None
    assert agg["avg_judge_spoken_quality"] is not None
    assert agg["judge_calls"] == 2
