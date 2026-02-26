"""Publish benchmark artifacts into a repo-tracked location."""

from __future__ import annotations

import json
import re
import shutil
import time
from pathlib import Path
from typing import Any


def _safe_segment(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-._")


def _run_name_from_report(report: dict[str, Any]) -> str:
    meta = report.get("meta") if isinstance(report.get("meta"), dict) else {}
    for key in ("run_name", "latest_run"):
        raw = str(meta.get(key) or "").strip()
        if not raw:
            continue
        candidate = _safe_segment(Path(raw).name)
        if key == "latest_run" and candidate.lower() == "latest":
            continue
        if candidate:
            return candidate

    finished_at = str(report.get("finished_at") or "").strip()
    if finished_at:
        candidate = _safe_segment(
            finished_at.replace(":", "")
            .replace("+", "_")
            .replace("T", "_")
        )
        if candidate:
            return candidate

    return f"run-{time.strftime('%Y%m%d-%H%M%S')}"


def _read_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_index(published_root: Path, latest_run: str) -> Path:
    runs_root = published_root / "runs"
    run_names = sorted(
        [entry.name for entry in runs_root.iterdir() if entry.is_dir()],
        reverse=True,
    )
    payload = {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "latest_run": latest_run,
        "runs": run_names,
    }
    index_path = published_root / "index.json"
    index_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return index_path


def publish_benchmark_results(
    *,
    source_root: str | Path = "benchmark_results",
    published_root: str | Path = "benchmarks/published",
    run_name: str | None = None,
) -> dict[str, str]:
    """Copy latest benchmark artifacts into published/latest and published/runs/<run>.

    Args:
        source_root: Directory containing `results.json` and `leaderboard.md`.
        published_root: Repo-tracked destination root.
        run_name: Optional explicit run folder name under `runs/`.
    """
    src = Path(source_root)
    results_src = src / "results.json"
    leaderboard_src = src / "leaderboard.md"
    if not results_src.exists():
        raise FileNotFoundError(f"Missing results file: {results_src}")
    if not leaderboard_src.exists():
        raise FileNotFoundError(f"Missing leaderboard file: {leaderboard_src}")

    report = _read_report(results_src)
    run_folder = _safe_segment(run_name or "")
    if not run_folder:
        run_folder = _run_name_from_report(report)
    if not run_folder:
        run_folder = f"run-{time.strftime('%Y%m%d-%H%M%S')}"

    pub = Path(published_root)
    latest_dir = pub / "latest"
    runs_dir = pub / "runs" / run_folder
    latest_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    latest_results = latest_dir / "results.json"
    latest_leaderboard = latest_dir / "leaderboard.md"
    run_results = runs_dir / "results.json"
    run_leaderboard = runs_dir / "leaderboard.md"

    shutil.copyfile(results_src, latest_results)
    shutil.copyfile(leaderboard_src, latest_leaderboard)
    shutil.copyfile(results_src, run_results)
    shutil.copyfile(leaderboard_src, run_leaderboard)

    (latest_dir / "run_name.txt").write_text(run_folder, encoding="utf-8")
    (latest_dir / "source_root.txt").write_text(str(src.resolve()), encoding="utf-8")
    index_path = _write_index(pub, run_folder)
    return {
        "published_root": str(pub),
        "latest_results": str(latest_results),
        "latest_leaderboard": str(latest_leaderboard),
        "run_results": str(run_results),
        "run_leaderboard": str(run_leaderboard),
        "index": str(index_path),
        "run_name": run_folder,
    }
