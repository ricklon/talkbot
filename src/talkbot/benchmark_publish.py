"""Publish benchmark artifacts into a repo-tracked location."""

from __future__ import annotations

import json
import os
import re
import shutil
import time
from pathlib import Path
from typing import Any


def check_regressions(
    results_path: str | Path,
    baselines_path: str | Path = "benchmarks/baselines.json",
) -> list[dict[str, Any]]:
    """Return list of regressions: profile+metric combos that fell below baseline floor.

    Each regression dict contains:
        profile, metric, baseline, actual, delta, source_run
    """
    baselines_path = Path(baselines_path)
    if not baselines_path.exists():
        return []

    baselines = json.loads(baselines_path.read_text(encoding="utf-8"))
    profile_floors: dict[str, dict[str, float]] = {
        name: entry.get("metrics", {})
        for name, entry in baselines.get("profiles", {}).items()
    }
    profile_source: dict[str, str] = {
        name: entry.get("source_run", "")
        for name, entry in baselines.get("profiles", {}).items()
    }

    report = json.loads(Path(results_path).read_text(encoding="utf-8"))
    regressions: list[dict[str, Any]] = []
    for run in report.get("runs", []):
        profile_name = run.get("profile", {}).get("name", "")
        if profile_name not in profile_floors:
            continue
        floors = profile_floors[profile_name]
        agg = run.get("aggregate", {})
        for metric, floor in floors.items():
            actual = agg.get(metric)
            if actual is None:
                continue
            if actual < floor:
                regressions.append(
                    {
                        "profile": profile_name,
                        "metric": metric,
                        "baseline": floor,
                        "actual": actual,
                        "delta": round(actual - floor, 4),
                        "source_run": profile_source.get(profile_name, ""),
                    }
                )

    if regressions:
        print("\n[benchmark] WARNING: Regression(s) detected below baseline floor:")
        for r in regressions:
            print(
                f"  {r['profile']} | {r['metric']}: "
                f"actual={r['actual']:.3f} < floor={r['baseline']:.3f} "
                f"(delta={r['delta']:+.4f})"
            )
        print()

    return regressions


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


def _read_index_latest_run(published_root: Path) -> str:
    index_path = published_root / "index.json"
    if index_path.exists():
        try:
            return str(json.loads(index_path.read_text(encoding="utf-8")).get("latest_run", ""))
        except Exception:
            pass
    return ""


def publish_benchmark_results(
    *,
    source_root: str | Path = "benchmark_results",
    published_root: str | Path = "benchmarks/published",
    run_name: str | None = None,
    update_latest: bool = True,
) -> dict[str, Any]:
    """Copy benchmark artifacts into published/runs/<run> and optionally published/latest.

    Args:
        source_root: Directory containing `results.json` and `leaderboard.md`.
        published_root: Repo-tracked destination root.
        run_name: Optional explicit run folder name under `runs/`.
        update_latest: When False, skip updating `latest/` and preserve the existing
            `latest_run` value in `index.json`. The run still appears in `runs[]`.
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
    runs_dir.mkdir(parents=True, exist_ok=True)

    run_results = runs_dir / "results.json"
    run_leaderboard = runs_dir / "leaderboard.md"
    if results_src.resolve() != run_results.resolve():
        shutil.copyfile(results_src, run_results)
    if leaderboard_src.resolve() != run_leaderboard.resolve():
        shutil.copyfile(leaderboard_src, run_leaderboard)

    if update_latest:
        latest_dir.mkdir(parents=True, exist_ok=True)
        latest_results = latest_dir / "results.json"
        latest_leaderboard = latest_dir / "leaderboard.md"
        shutil.copyfile(results_src, latest_results)
        shutil.copyfile(leaderboard_src, latest_leaderboard)
        (latest_dir / "run_name.txt").write_text(run_folder, encoding="utf-8")
        try:
            rel = Path(os.path.relpath(src.resolve(), latest_dir.resolve()))
        except ValueError:
            rel = src.resolve()
        (latest_dir / "source_root.txt").write_text(str(rel), encoding="utf-8")
        index_latest = run_folder
    else:
        index_latest = _read_index_latest_run(pub) or run_folder

    index_path = _write_index(pub, index_latest)

    regressions = check_regressions(results_src)

    return {
        "published_root": str(pub),
        "latest_results": str(latest_dir / "results.json"),
        "latest_leaderboard": str(latest_dir / "leaderboard.md"),
        "run_results": str(run_results),
        "run_leaderboard": str(run_leaderboard),
        "index": str(index_path),
        "run_name": run_folder,
        "regressions": regressions,
    }
