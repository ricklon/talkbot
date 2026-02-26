import json
from pathlib import Path

from talkbot.benchmark_publish import publish_benchmark_results


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
