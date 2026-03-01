#!/usr/bin/env python3
"""Pipeline TTFA Leaderboard Builder

Reads accumulated STT and TTS result JSONs, reads LLM benchmark data from
the published LLM leaderboard, and composes end-to-end TTFA estimates.

Output: benchmarks/published/pipeline_leaderboard.md

Usage:
    uv run python scripts/build_pipeline_leaderboard.py
    uv run python scripts/build_pipeline_leaderboard.py --llm-results benchmark_results/results.json
"""

from __future__ import annotations

import argparse
import json
import statistics
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
# Loaders
# ---------------------------------------------------------------------------

def _load_stt_results(stt_dir: Path) -> list[dict]:
    results = []
    for path in sorted(stt_dir.glob("*.json")):
        try:
            results.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            print(f"  [warn] STT: could not read {path}: {exc}", file=sys.stderr)
    return results


def _load_tts_results(tts_dir: Path) -> list[dict]:
    results = []
    for path in sorted(tts_dir.glob("*.json")):
        try:
            results.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            print(f"  [warn] TTS: could not read {path}: {exc}", file=sys.stderr)
    return results


def _load_llm_runs(llm_results_path: Path) -> list[dict]:
    """Load LLM benchmark run aggregates from results.json."""
    if not llm_results_path.exists():
        return []
    try:
        data = json.loads(llm_results_path.read_text(encoding="utf-8"))
        return data.get("runs", [])
    except Exception as exc:
        print(f"  [warn] LLM: could not read {llm_results_path}: {exc}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Best-per-config selectors
# ---------------------------------------------------------------------------

def _best_stt_configs(stt_results: list[dict]) -> list[dict]:
    """For each (model, compute_type, device) combo keep the most recent run."""
    seen: dict[tuple, dict] = {}
    for r in sorted(stt_results, key=lambda x: x.get("ran_at", "")):
        key = (r.get("stt_model", ""), r.get("compute_type", ""), r.get("device", ""))
        seen[key] = r
    return list(seen.values())


def _best_tts_configs(tts_results: list[dict]) -> list[dict]:
    """For each (backend, voice) combo keep the most recent run."""
    seen: dict[tuple, dict] = {}
    for r in sorted(tts_results, key=lambda x: x.get("ran_at", "")):
        key = (r.get("backend", ""), r.get("voice", ""))
        seen[key] = r
    return list(seen.values())


def _best_llm_runs(llm_runs: list[dict]) -> list[dict]:
    """For each model keep the highest-scoring run."""
    seen: dict[str, dict] = {}
    for run in llm_runs:
        profile = run.get("profile") or {}
        model = profile.get("model", "unknown")
        agg = run.get("aggregate") or {}
        score = agg.get("task_success_rate", 0.0)
        if model not in seen or score > (seen[model].get("aggregate") or {}).get("task_success_rate", 0.0):
            seen[model] = run
    return list(seen.values())


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------

def _stt_label(r: dict) -> str:
    return f"{r['stt_model']}/{r['compute_type']}/{r['device']}"


def _tts_label(r: dict) -> str:
    return f"{r['backend']}/{r['voice']}"


def _llm_label(run: dict) -> str:
    profile = run.get("profile") or {}
    return profile.get("model", "unknown")


def build_pipeline_leaderboard(
    stt_results: list[dict],
    tts_results: list[dict],
    llm_runs: list[dict],
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    stt_configs = sorted(_best_stt_configs(stt_results),
                         key=lambda r: r["summary"]["avg_latency_ms"])
    tts_configs = sorted(_best_tts_configs(tts_results),
                         key=lambda r: r["summary"]["avg_synthesis_ms"])
    llm_best = sorted(_best_llm_runs(llm_runs),
                      key=lambda r: -(r.get("aggregate") or {}).get("task_success_rate", 0.0))

    lines = [
        "# TalkBot End-to-End Pipeline Leaderboard",
        "",
        f"- Generated: {now}",
        f"- STT configs: {len(stt_configs)}",
        f"- TTS configs: {len(tts_configs)}",
        f"- LLM models: {len(llm_best)}",
        "",
        "```",
        "TTFA = STT_ms + LLM_ms + TTS_ms",
        "       (transcribe) (infer+tools) (synthesise)",
        "```",
        "",
        "TTFA = time from end-of-speech to first audio byte.",
        "All values are averages over benchmark runs on this machine.",
        "",
    ]

    # --- Stage summary ---
    lines += [
        "## Stage Latencies",
        "",
        "### STT",
        "",
        "| Config | Pass% | Avg ms | P95 ms | Avg RTF |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in stt_configs:
        s = r["summary"]
        lines.append(
            f"| {_stt_label(r)} "
            f"| {s['pass_rate']:.1%} "
            f"| {s['avg_latency_ms']:.0f} "
            f"| {s['p95_latency_ms']:.0f} "
            f"| {s['avg_rtf']:.2f}x "
            f"|"
        )

    lines += [
        "",
        "### LLM",
        "",
        "| Model | Provider | Success% | Avg ms | Tool Sel% |",
        "|---|---|---:|---:|---:|",
    ]
    for run in llm_best:
        profile = run.get("profile") or {}
        agg = run.get("aggregate") or {}
        lines.append(
            f"| {profile.get('model', '?')} "
            f"| {profile.get('provider', '?')} "
            f"| {agg.get('task_success_rate', 0.0):.1%} "
            f"| {agg.get('avg_turn_latency_ms', 0.0):.0f} "
            f"| {agg.get('tool_selection_accuracy', 0.0):.1%} "
            f"|"
        )

    lines += [
        "",
        "### TTS",
        "",
        "| Config | Avg Synth ms | P95 Synth ms | Avg Audio ms | Avg RTF |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in tts_configs:
        s = r["summary"]
        lines.append(
            f"| {_tts_label(r)} "
            f"| {s['avg_synthesis_ms']:.0f} "
            f"| {s['p95_synthesis_ms']:.0f} "
            f"| {s['avg_audio_duration_ms']:.0f} "
            f"| {s['avg_rtf']:.2f}x "
            f"|"
        )

    # --- TTFA composition table ---
    if not (stt_configs and tts_configs and llm_best):
        lines += [
            "",
            "## TTFA Estimates",
            "",
            "_Not enough data — need at least one result from each stage._",
        ]
    else:
        lines += [
            "",
            "## TTFA Estimates (Composed)",
            "",
            "Each row is one possible STT × LLM × TTS configuration.",
            "Sorted by TTFA ascending (fastest first).",
            "",
            "| STT | LLM | TTS | STT ms | LLM ms | TTS ms | **TTFA ms** | LLM Success% |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]

        rows = []
        for stt in stt_configs:
            stt_ms = stt["summary"]["avg_latency_ms"]
            for llm in llm_best:
                agg = llm.get("aggregate") or {}
                llm_ms = agg.get("avg_turn_latency_ms", 0.0)
                llm_success = agg.get("task_success_rate", 0.0)
                profile = llm.get("profile") or {}
                for tts in tts_configs:
                    tts_ms = tts["summary"]["avg_synthesis_ms"]
                    ttfa = stt_ms + llm_ms + tts_ms
                    rows.append({
                        "stt": _stt_label(stt),
                        "llm": profile.get("model", "?"),
                        "tts": _tts_label(tts),
                        "stt_ms": stt_ms,
                        "llm_ms": llm_ms,
                        "tts_ms": tts_ms,
                        "ttfa_ms": ttfa,
                        "llm_success": llm_success,
                    })

        rows.sort(key=lambda r: r["ttfa_ms"])
        for row in rows:
            lines.append(
                f"| {row['stt']} "
                f"| {row['llm']} "
                f"| {row['tts']} "
                f"| {row['stt_ms']:.0f} "
                f"| {row['llm_ms']:.0f} "
                f"| {row['tts_ms']:.0f} "
                f"| **{row['ttfa_ms']:.0f}** "
                f"| {row['llm_success']:.1%} "
                f"|"
            )

        # Highlight the best balanced config
        # "Best" = highest LLM success% among configs with TTFA <= 1.5× minimum TTFA
        min_ttfa = rows[0]["ttfa_ms"]
        affordable = [r for r in rows if r["ttfa_ms"] <= min_ttfa * 1.5]
        best_balanced = max(affordable, key=lambda r: r["llm_success"])

        lines += [
            "",
            "## Recommended Configs",
            "",
            f"**Fastest:** {rows[0]['stt']} + {rows[0]['llm']} + {rows[0]['tts']}  ",
            f"→ TTFA ~{rows[0]['ttfa_ms']:.0f} ms | LLM success {rows[0]['llm_success']:.1%}",
            "",
            f"**Best balanced** (highest success within 1.5× min TTFA):  ",
            f"{best_balanced['stt']} + {best_balanced['llm']} + {best_balanced['tts']}  ",
            f"→ TTFA ~{best_balanced['ttfa_ms']:.0f} ms | LLM success {best_balanced['llm_success']:.1%}",
            "",
        ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stt-dir", default="benchmarks/stt_results",
                        help="STT results directory (default: benchmarks/stt_results)")
    parser.add_argument("--tts-dir", default="benchmarks/tts_results",
                        help="TTS results directory (default: benchmarks/tts_results)")
    parser.add_argument("--llm-results", default="benchmark_results/results.json",
                        help="LLM results.json path (default: benchmark_results/results.json)")
    parser.add_argument("--publish-dir", default="benchmarks/published",
                        help="Output directory (default: benchmarks/published)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = _repo_root()

    stt_dir = repo_root / args.stt_dir
    tts_dir = repo_root / args.tts_dir
    llm_path = repo_root / args.llm_results
    publish_dir = repo_root / args.publish_dir
    publish_dir.mkdir(parents=True, exist_ok=True)

    stt_results = _load_stt_results(stt_dir)
    tts_results = _load_tts_results(tts_dir)
    llm_runs = _load_llm_runs(llm_path)

    print(f"Loaded: {len(stt_results)} STT runs, {len(tts_results)} TTS runs, {len(llm_runs)} LLM runs")

    md = build_pipeline_leaderboard(stt_results, tts_results, llm_runs)
    out = publish_dir / "pipeline_leaderboard.md"
    out.write_text(md, encoding="utf-8")
    print(f"Written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
