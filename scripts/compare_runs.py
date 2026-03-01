#!/usr/bin/env python3
"""
Compare benchmark results across machines/runners.

Usage:
    uv run python scripts/compare_runs.py
    uv run python scripts/compare_runs.py --provider local_server --min-machines 2
    uv run python scripts/compare_runs.py --runs benchmarks/published/runs/ --output benchmarks/published/comparison.md
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_runs(runs_dir: Path) -> list[dict]:
    """Load all results.json files from run subfolders, skipping 'latest/'."""
    reports = []
    for results_file in sorted(runs_dir.glob("*/results.json")):
        if results_file.parent.name == "latest":
            continue
        try:
            data = json.loads(results_file.read_text(encoding="utf-8"))
            data["_run_name"] = results_file.parent.name
            reports.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: skipping {results_file}: {e}", file=sys.stderr)
    return reports


def runner_label(runner: dict) -> str:
    """Return runner label, falling back to hostname."""
    label = (runner or {}).get("label") or ""
    if label:
        return label
    return (runner or {}).get("hostname") or "unknown"


def model_key(profile: dict) -> tuple[str, str]:
    """Return (model, provider) grouping key."""
    return (profile["model"], profile["provider"])


def build_comparison(
    reports: list[dict], provider_filter: str | None = None
) -> tuple[dict, list[str]]:
    """
    Build {(model, provider): {machine_label: metrics}} from all reports.

    If the same machine+model appears in multiple runs, keep the most recent
    by started_at. Only include runs with status == "ok".
    """
    # Track best (most recent) entry per (model, provider, machine)
    best: dict[tuple, dict] = {}

    for report in reports:
        machine = runner_label(report.get("runner", {}))
        report_started = report.get("started_at", "")

        for run in report.get("runs", []):
            if run.get("status") != "ok":
                continue
            profile = run.get("profile", {})
            if provider_filter and profile.get("provider") != provider_filter:
                continue

            key = model_key(profile)
            cell_key = (*key, machine)
            agg = run.get("aggregate", {})

            entry = {
                "success_rate": agg.get("task_success_rate", 0.0),
                "avg_latency_ms": agg.get("avg_turn_latency_ms", 0.0),
                "memory_peak_mb": agg.get("memory_peak_mb", 0.0),
                "tokens_per_second": agg.get("tokens_per_second", 0.0),
                "profile_name": profile.get("name", ""),
                "started_at": run.get("started_at") or report_started,
            }

            existing = best.get(cell_key)
            if existing is None or entry["started_at"] > existing["started_at"]:
                best[cell_key] = entry

    # Reorganise into comparison dict
    comparison: dict[tuple, dict[str, dict]] = {}
    for (model, provider, machine), metrics in best.items():
        key = (model, provider)
        comparison.setdefault(key, {})[machine] = metrics

    all_machines = sorted({m for (_, _, m) in best})
    return comparison, all_machines


def _cell(metrics: dict | None) -> str:
    if metrics is None:
        return "—"
    sr = metrics["success_rate"]
    lat = metrics["avg_latency_ms"]
    mem_mb = metrics["memory_peak_mb"]
    mem_gb = mem_mb / 1024 if mem_mb else 0.0
    mem_str = f"{mem_gb:.1f}GB" if mem_mb else "—"
    return f"{sr:.0%} · {lat:.0f}ms · {mem_str}"


def generate_markdown(
    comparison: dict,
    machines: list[str],
    min_machines: int = 1,
) -> str:
    """Render a markdown comparison table."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Filter rows
    rows = [
        (key, machine_map)
        for key, machine_map in comparison.items()
        if len(machine_map) >= min_machines
    ]

    # Sort: models on most machines first, then by best success rate descending
    def sort_key(item):
        _, mm = item
        best_sr = max(m["success_rate"] for m in mm.values())
        return (-len(mm), -best_sr)

    rows.sort(key=sort_key)

    # Build table
    col_sep = " | "
    header_cols = ["Model", "Provider"] + machines
    header = "| " + col_sep.join(header_cols) + " |"
    divider = "| " + col_sep.join("---" for _ in header_cols) + " |"

    table_lines = [header, divider]
    for (model, provider), machine_map in rows:
        cells = [f"`{model}`", provider] + [
            _cell(machine_map.get(m)) for m in machines
        ]
        table_lines.append("| " + col_sep.join(cells) + " |")

    table = "\n".join(table_lines)

    lines = [
        "# Benchmark Cross-Machine Comparison",
        "",
        f"_Generated {now} · {len(machines)} machine(s) · {len(rows)} model(s)_",
        "",
        "Columns: `Success% · Avg Latency · Peak Memory`",
        "",
        table,
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare benchmark runs across machines")
    parser.add_argument(
        "--runs",
        type=Path,
        default=Path("benchmarks/published/runs"),
        help="Directory of run subfolders [benchmarks/published/runs]",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmarks/published/comparison.md"),
        help="Output markdown path [benchmarks/published/comparison.md]",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="Filter to one provider (e.g. local_server)",
    )
    parser.add_argument(
        "--min-machines",
        type=int,
        default=1,
        metavar="N",
        help="Only include rows with results on N+ machines [1]",
    )
    args = parser.parse_args()

    if not args.runs.is_dir():
        print(f"Error: runs directory not found: {args.runs}", file=sys.stderr)
        sys.exit(1)

    reports = load_runs(args.runs)
    if not reports:
        print("No run results found.", file=sys.stderr)
        sys.exit(1)

    comparison, machines = build_comparison(reports, provider_filter=args.provider)

    if not machines:
        print("No matching runs found (check --provider filter).", file=sys.stderr)
        sys.exit(1)

    md = generate_markdown(comparison, machines, min_machines=args.min_machines)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(md, encoding="utf-8")
    print(f"Written: {args.output}  ({len(comparison)} models, {len(machines)} machines)")


if __name__ == "__main__":
    main()
