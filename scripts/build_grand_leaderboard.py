#!/usr/bin/env python3
"""Grand Leaderboard Builder

Scans all published LLM benchmark runs, finds the best result per model, and
produces a single ranked summary table — the "leaderboard of leaderboards".

Output: benchmarks/published/grand_leaderboard.md

Usage:
    uv run python scripts/build_grand_leaderboard.py
    uv run python scripts/build_grand_leaderboard.py --runs-dir benchmarks/published/runs
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return here.parent


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def _load_all_runs(runs_dir: Path) -> list[dict]:
    """Collect every model-run record from all results.json files under runs_dir."""
    all_runs: list[dict] = []
    for results_file in sorted(runs_dir.glob("*/results.json")):
        run_name = results_file.parent.name
        try:
            data = json.loads(results_file.read_text(encoding="utf-8"))
            scenario_count = data.get("scenario_count", 0)
            started_at = data.get("started_at", "")
            for run in data.get("runs", []):
                if not isinstance(run, dict):
                    continue
                profile = run.get("profile") or {}
                agg = run.get("aggregate") or {}
                # Skip error/empty runs
                if run.get("status") == "error" and not agg:
                    continue
                all_runs.append({
                    "run_name": run_name,
                    "started_at": started_at,
                    "scenario_count": scenario_count,
                    "model": profile.get("model", "unknown"),
                    "provider": profile.get("provider", "unknown"),
                    "success": agg.get("task_success_rate", 0.0),
                    "avg_ms": agg.get("avg_turn_latency_ms", 0.0),
                    "p95_ms": agg.get("p95_turn_latency_ms", 0.0),
                    "tool_sel": agg.get("tool_selection_accuracy", 0.0),
                    "arg_acc": agg.get("argument_accuracy", 0.0),
                    "tokens_per_s": agg.get("tokens_per_second", 0.0),
                    "scenario_passed": agg.get("scenario_passed", 0),
                    "scenario_total": agg.get("scenario_count", scenario_count),
                })
        except Exception as exc:
            print(f"  [warn] skip {run_name}: {exc}", file=sys.stderr)
    return all_runs


# ---------------------------------------------------------------------------
# Best-per-model selector
# ---------------------------------------------------------------------------

def _best_per_model(all_runs: list[dict]) -> list[dict]:
    """For each (model, provider) pair, keep the highest-success run.
    Ties broken by: higher scenario_count first, then lower avg_ms.
    """
    best: dict[tuple, dict] = {}
    for r in all_runs:
        key = (r["model"], r["provider"])
        if key not in best:
            best[key] = r
        else:
            prev = best[key]
            # Higher success wins
            if r["success"] > prev["success"]:
                best[key] = r
            elif r["success"] == prev["success"]:
                # More scenarios is more trustworthy
                if r["scenario_count"] > prev["scenario_count"]:
                    best[key] = r
                elif r["scenario_count"] == prev["scenario_count"] and r["avg_ms"] < prev["avg_ms"]:
                    best[key] = r
    return list(best.values())


# ---------------------------------------------------------------------------
# Leaderboard builder
# ---------------------------------------------------------------------------

PROVIDER_ORDER = ["local_server", "local", "openrouter", "unknown"]


def _provider_group(provider: str) -> str:
    if provider in ("local_server", "local"):
        return "Local / On-Device"
    if provider == "openrouter":
        return "Cloud (OpenRouter)"
    return "Other"


def build_grand_leaderboard(all_runs: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    best = _best_per_model(all_runs)
    # Sort: success DESC, avg_ms ASC
    best.sort(key=lambda r: (-r["success"], r["avg_ms"]))

    # Stats
    run_names = sorted({r["run_name"] for r in all_runs})
    unique_models = len(best)
    total_model_runs = len(all_runs)

    lines = [
        "# TalkBot Grand Leaderboard",
        "",
        f"- Generated: {now}",
        f"- Published runs scanned: {len(run_names)}",
        f"- Unique model × provider combos: {unique_models}",
        f"- Total model-run records: {total_model_runs}",
        "",
        "Best result per model across **all** published benchmark runs.",
        "Success% = fraction of scenarios where the model answered correctly.",
        "",
        "## All Models — Best Ever",
        "",
        "| # | Model | Provider | Success% | Avg ms | P95 ms | Tool Sel% | Scenarios | Best Run |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]

    for rank, r in enumerate(best, 1):
        run_date = r["started_at"][:10] if r["started_at"] else "?"
        lines.append(
            f"| {rank} "
            f"| {r['model']} "
            f"| {r['provider']} "
            f"| {r['success']:.1%} "
            f"| {r['avg_ms']:.0f} "
            f"| {r['p95_ms']:.0f} "
            f"| {r['tool_sel']:.1%} "
            f"| {r['scenario_count']} "
            f"| {r['run_name']} ({run_date}) "
            f"|"
        )

    # --- Provider group breakdowns ---
    lines += [
        "",
        "## By Provider",
        "",
    ]

    groups: dict[str, list[dict]] = {}
    for r in best:
        g = _provider_group(r["provider"])
        groups.setdefault(g, []).append(r)

    for group_name in ["Local / On-Device", "Cloud (OpenRouter)", "Other"]:
        members = groups.get(group_name)
        if not members:
            continue
        members.sort(key=lambda r: (-r["success"], r["avg_ms"]))
        lines += [
            f"### {group_name}",
            "",
            "| Model | Provider | Success% | Avg ms | Tool Sel% | Scenarios |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for r in members:
            lines.append(
                f"| {r['model']} "
                f"| {r['provider']} "
                f"| {r['success']:.1%} "
                f"| {r['avg_ms']:.0f} "
                f"| {r['tool_sel']:.1%} "
                f"| {r['scenario_count']} "
                f"|"
            )
        lines.append("")

    # --- Runs index ---
    lines += [
        "## Runs Index",
        "",
        "All published runs included in this leaderboard.",
        "",
        "| Run | Started | Models | Scenarios |",
        "|---|---|---:|---:|",
    ]
    run_meta: dict[str, dict] = {}
    for r in all_runs:
        rn = r["run_name"]
        if rn not in run_meta:
            run_meta[rn] = {"started": r["started_at"][:10] if r["started_at"] else "?",
                            "models": 0, "scenarios": r["scenario_count"]}
        run_meta[rn]["models"] += 1

    for run_name in sorted(run_meta):
        m = run_meta[run_name]
        lines.append(
            f"| {run_name} "
            f"| {m['started']} "
            f"| {m['models']} "
            f"| {m['scenarios']} "
            f"|"
        )

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs-dir", default="benchmarks/published/runs",
                        help="Directory containing run subdirectories "
                             "(default: benchmarks/published/runs)")
    parser.add_argument("--publish-dir", default="benchmarks/published",
                        help="Output directory (default: benchmarks/published)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = _repo_root()

    runs_dir = repo_root / args.runs_dir
    publish_dir = repo_root / args.publish_dir
    publish_dir.mkdir(parents=True, exist_ok=True)

    if not runs_dir.exists():
        print(f"Error: runs directory not found: {runs_dir}", file=sys.stderr)
        return 1

    all_runs = _load_all_runs(runs_dir)
    print(f"Loaded {len(all_runs)} model-run records from {runs_dir.name}/")

    if not all_runs:
        print("No runs found — nothing to publish.", file=sys.stderr)
        return 1

    md = build_grand_leaderboard(all_runs)
    out = publish_dir / "grand_leaderboard.md"
    out.write_text(md, encoding="utf-8")
    print(f"Written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
