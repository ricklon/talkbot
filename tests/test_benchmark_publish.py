import json
from pathlib import Path

from talkbot.benchmark_publish import check_regressions, publish_benchmark_results


def _write_source(
    root: Path,
    *,
    latest_run: str | None = None,
    run_name: str | None = None,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    report = {
        "started_at": "2026-02-26T13:00:00-0500",
        "finished_at": "2026-02-26T13:15:01-0500",
        "run_count": 1,
        "scenario_count": 1,
        "runs": [],
    }
    if latest_run or run_name:
        meta: dict[str, str] = {}
        if latest_run:
            meta["latest_run"] = latest_run
        if run_name:
            meta["run_name"] = run_name
        report["meta"] = meta
    (root / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (root / "leaderboard.md").write_text("# Benchmark Leaderboard\n", encoding="utf-8")


def test_publish_benchmark_results_with_explicit_run_name(tmp_path):
    source = tmp_path / "source"
    published = tmp_path / "published"
    _write_source(source, latest_run="/tmp/run/ignored")

    paths = publish_benchmark_results(
        source_root=source,
        published_root=published,
        run_name="my-run",
    )

    assert paths["run_name"] == "my-run"
    assert (published / "latest" / "leaderboard.md").exists()
    assert (published / "latest" / "results.json").exists()
    assert (published / "runs" / "my-run" / "leaderboard.md").exists()
    assert (published / "runs" / "my-run" / "results.json").exists()
    assert (published / "latest" / "run_name.txt").read_text(encoding="utf-8") == "my-run"

    index_payload = json.loads((published / "index.json").read_text(encoding="utf-8"))
    assert index_payload["latest_run"] == "my-run"
    assert "my-run" in index_payload["runs"]


def test_publish_benchmark_results_uses_report_latest_run_name(tmp_path):
    source = tmp_path / "source"
    published = tmp_path / "published"
    _write_source(source, latest_run="/Users/me/project/benchmark_results/main_ab")

    paths = publish_benchmark_results(
        source_root=source,
        published_root=published,
    )

    assert paths["run_name"] == "main_ab"
    assert (published / "runs" / "main_ab" / "leaderboard.md").exists()
    assert (published / "runs" / "main_ab" / "results.json").exists()


def test_publish_benchmark_results_prefers_report_run_name(tmp_path):
    source = tmp_path / "source"
    published = tmp_path / "published"
    _write_source(
        source,
        latest_run="/Users/me/project/benchmark_results/latest",
        run_name="openrouter-full-remote",
    )

    paths = publish_benchmark_results(
        source_root=source,
        published_root=published,
    )

    assert paths["run_name"] == "openrouter-full-remote"
    assert (published / "runs" / "openrouter-full-remote" / "leaderboard.md").exists()
    assert (published / "runs" / "openrouter-full-remote" / "results.json").exists()


def test_publish_benchmark_results_ignores_latest_literal_run_name(tmp_path):
    source = tmp_path / "source"
    published = tmp_path / "published"
    _write_source(source, latest_run="/Users/me/project/benchmark_results/latest")

    paths = publish_benchmark_results(
        source_root=source,
        published_root=published,
    )

    assert paths["run_name"] != "latest"


def test_no_update_latest_preserves_latest_dir(tmp_path):
    """--no-update-latest: latest/ not overwritten, run still in index."""
    # Publish a first run to establish latest/
    source1 = tmp_path / "source1"
    published = tmp_path / "published"
    _write_source(source1, run_name="first-run")
    publish_benchmark_results(source_root=source1, published_root=published, run_name="first-run")

    original_leaderboard = (published / "latest" / "leaderboard.md").read_text()
    original_run_name = (published / "latest" / "run_name.txt").read_text()

    # Publish a second run with update_latest=False
    source2 = tmp_path / "source2"
    source2.mkdir()
    (source2 / "results.json").write_text(
        json.dumps({"run_count": 1, "scenario_count": 1, "runs": [], "meta": {"run_name": "second-run"}}),
        encoding="utf-8",
    )
    (source2 / "leaderboard.md").write_text("# Second Run\n", encoding="utf-8")
    paths = publish_benchmark_results(
        source_root=source2, published_root=published, run_name="second-run", update_latest=False
    )

    # latest/ content unchanged
    assert (published / "latest" / "leaderboard.md").read_text() == original_leaderboard
    assert (published / "latest" / "run_name.txt").read_text() == original_run_name

    # second run still archived under runs/
    assert (published / "runs" / "second-run" / "leaderboard.md").exists()

    # index still shows first-run as latest_run, but second-run appears in runs[]
    index = json.loads((published / "index.json").read_text())
    assert index["latest_run"] == "first-run"
    assert "second-run" in index["runs"]
    assert "first-run" in index["runs"]


def _write_results_with_metrics(path: Path, profile_name: str, metrics: dict) -> None:
    """Write a minimal results.json with one run entry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "run_count": 1,
        "scenario_count": 1,
        "runs": [
            {
                "profile": {"name": profile_name},
                "aggregate": metrics,
            }
        ],
    }
    path.write_text(json.dumps(report), encoding="utf-8")


def _write_baselines(path: Path, profiles: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"version": "1", "profiles": profiles}),
        encoding="utf-8",
    )


def test_check_regressions_detects_drop(tmp_path):
    results = tmp_path / "results.json"
    baselines = tmp_path / "baselines.json"
    _write_results_with_metrics(results, "my-profile", {"task_success_rate": 0.30, "tool_selection_accuracy": 0.95})
    _write_baselines(
        baselines,
        {
            "my-profile": {
                "source_run": "test-run",
                "metrics": {"task_success_rate": 0.57, "tool_selection_accuracy": 0.85},
            }
        },
    )

    regressions = check_regressions(results, baselines)

    assert len(regressions) == 1
    assert regressions[0]["profile"] == "my-profile"
    assert regressions[0]["metric"] == "task_success_rate"
    assert regressions[0]["actual"] == 0.30
    assert regressions[0]["baseline"] == 0.57


def test_check_regressions_no_false_positives(tmp_path):
    results = tmp_path / "results.json"
    baselines = tmp_path / "baselines.json"
    _write_results_with_metrics(results, "my-profile", {"task_success_rate": 0.57, "tool_selection_accuracy": 0.90})
    _write_baselines(
        baselines,
        {
            "my-profile": {
                "source_run": "test-run",
                "metrics": {"task_success_rate": 0.57, "tool_selection_accuracy": 0.85},
            }
        },
    )

    regressions = check_regressions(results, baselines)

    assert regressions == []


def test_check_regressions_ignores_unknown_profiles(tmp_path):
    results = tmp_path / "results.json"
    baselines = tmp_path / "baselines.json"
    _write_results_with_metrics(results, "unknown-profile", {"task_success_rate": 0.10})
    _write_baselines(
        baselines,
        {
            "known-profile": {
                "source_run": "test-run",
                "metrics": {"task_success_rate": 0.57},
            }
        },
    )

    regressions = check_regressions(results, baselines)

    assert regressions == []
