#!/usr/bin/env python3
"""STT Benchmark Runner

Runs audio clips from a voice dataset manifest through faster-whisper,
measures WER and latency per config, and publishes a leaderboard.

Each invocation benchmarks ONE STT config (model × compute_type × device).
Results accumulate in --output-dir; --publish regenerates the leaderboard
from all accumulated result files.

Usage examples:
    # CPU baseline (always works)
    uv run python scripts/benchmark_stt.py --model small.en --compute-type int8 --device cpu

    # GPU (requires CUDA in environment)
    uv run python scripts/benchmark_stt.py --model small.en --compute-type float16 --device cuda

    # Both manifests
    uv run python scripts/benchmark_stt.py \\
        --manifest benchmarks/voice_dataset/manifest.json \\
        --manifest benchmarks/voice_dataset/pipeline_manifest.json

    # Regenerate leaderboard only (no new run)
    uv run python scripts/benchmark_stt.py --publish-only
"""

from __future__ import annotations

import argparse
import json
import platform
import socket
import statistics
import string
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Text normalisation + WER
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def _wer(reference: str, hypothesis: str) -> float:
    """Word Error Rate = edit_distance(ref_words, hyp_words) / len(ref_words).

    Uses Wagner-Fischer DP. Can exceed 1.0 when hypothesis is longer than reference.
    Returns 0.0 when both are empty; 1.0 when reference is empty but hypothesis is not.
    """
    ref = _normalize(reference).split()
    hyp = _normalize(hypothesis).split()
    if not ref:
        return 0.0 if not hyp else 1.0
    n, m = len(ref), len(hyp)
    # Single-row rolling DP
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i] + [0] * m
        for j in range(1, m + 1):
            if ref[i - 1] == hyp[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j - 1], prev[j], curr[j - 1])
        prev = curr
    return round(prev[m] / n, 4)


def _best_wer(hypothesis: str, text: str, expected_variants: list[str]) -> float:
    """Return the minimum WER across all candidate references."""
    candidates = [v for v in expected_variants if v] or [text]
    return min(_wer(ref, hypothesis) for ref in candidates)


def _reference_label(text: str, expected_variants: list[str]) -> str:
    """Human-readable reference string for display."""
    if expected_variants:
        return expected_variants[0]
    return text


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

def _load_manifest(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "entries" in data:
        return data["entries"]
    raise ValueError(f"Unrecognised manifest format in {path}")


# ---------------------------------------------------------------------------
# Core benchmark
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    """Walk up from this script to find the repo root (contains pyproject.toml)."""
    here = Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return here.parent


def run_stt_benchmark(
    manifest_paths: list[Path],
    stt_model: str,
    compute_type: str,
    device: str,
    beam_size: int,
    wer_pass_threshold: float,
    repo_root: Path,
) -> dict:
    """Load the model once, transcribe all entries, return a result dict."""
    try:
        import numpy as np
        import soundfile as sf
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit(
            f"Missing voice dependencies: {exc}\n"
            "Install with: uv sync --extra voice"
        ) from exc

    print(f"[stt-bench] Loading model={stt_model!r} compute={compute_type!r} device={device!r}")
    t0 = time.perf_counter()
    model = WhisperModel(stt_model, device=device, compute_type=compute_type)
    model_load_ms = round((time.perf_counter() - t0) * 1000, 1)
    print(f"[stt-bench] Model loaded in {model_load_ms:.0f} ms")

    all_entries: list[dict] = []
    for mp in manifest_paths:
        for entry in _load_manifest(mp):
            entry["_manifest"] = str(mp)
            all_entries.append(entry)

    entry_results: list[dict] = []

    for entry in all_entries:
        entry_id = entry.get("id", "unknown")
        audio_rel = entry.get("audio_path", "")
        audio_path = repo_root / audio_rel
        if not audio_path.exists():
            print(f"  [SKIP] {entry_id} — audio not found: {audio_path}")
            continue

        text = entry.get("text", "")
        variants = entry.get("expected_variants") or []
        duration_s = float(entry.get("duration_s", 0.0))
        category = entry.get("category", "unknown")

        try:
            audio, _sr = sf.read(str(audio_path), dtype="float32", always_2d=False)
            audio_np = np.asarray(audio, dtype=np.float32)

            t_start = time.perf_counter()
            segments, _ = model.transcribe(
                audio_np,
                language="en",
                beam_size=beam_size,
                vad_filter=False,
            )
            hypothesis = " ".join(
                seg.text.strip() for seg in segments if seg.text.strip()
            ).strip()
            latency_ms = round((time.perf_counter() - t_start) * 1000, 1)

            wer = _best_wer(hypothesis, text, variants)
            rtf = round((latency_ms / 1000) / duration_s, 3) if duration_s > 0 else 0.0
            passed = wer <= wer_pass_threshold
            ref_label = _reference_label(text, variants)

            entry_results.append({
                "id": entry_id,
                "prompt_id": entry.get("prompt_id", entry_id),
                "category": category,
                "manifest": entry.get("_manifest", ""),
                "audio_path": audio_rel,
                "duration_s": duration_s,
                "reference": ref_label,
                "hypothesis": hypothesis,
                "wer": wer,
                "latency_ms": latency_ms,
                "rtf": rtf,
                "passed": passed,
            })
            status = "OK  " if passed else "FAIL"
            print(
                f"  [{status}] {entry_id:<40s} "
                f"WER={wer:.0%}  {latency_ms:>6.0f}ms  RTF={rtf:.2f}x"
            )
            if wer > 0:
                print(f"          ref: {ref_label!r}")
                print(f"          hyp: {hypothesis!r}")

        except Exception as exc:
            print(f"  [ERR ] {entry_id}: {exc}")

    # Aggregate
    wers = [r["wer"] for r in entry_results]
    latencies = [r["latency_ms"] for r in entry_results]
    rtfs = [r["rtf"] for r in entry_results]
    pass_count = sum(1 for r in entry_results if r["passed"])

    def _p95(values: list[float]) -> float:
        if len(values) >= 2:
            return round(statistics.quantiles(values, n=20)[18], 1)
        return round(values[0], 1) if values else 0.0

    # Per-category breakdown
    categories: dict[str, list[dict]] = {}
    for r in entry_results:
        categories.setdefault(r["category"], []).append(r)

    by_category = {}
    for cat, rows in sorted(categories.items()):
        cat_wers = [r["wer"] for r in rows]
        cat_lats = [r["latency_ms"] for r in rows]
        cat_pass = sum(1 for r in rows if r["passed"])
        by_category[cat] = {
            "count": len(rows),
            "pass_count": cat_pass,
            "pass_rate": round(cat_pass / len(rows), 4) if rows else 0.0,
            "avg_wer": round(statistics.fmean(cat_wers), 4) if cat_wers else 1.0,
            "avg_latency_ms": round(statistics.fmean(cat_lats), 1) if cat_lats else 0.0,
        }

    return {
        "schema_version": "2026.stt.v1",
        "stt_model": stt_model,
        "compute_type": compute_type,
        "device": device,
        "beam_size": beam_size,
        "wer_pass_threshold": wer_pass_threshold,
        "manifests": [str(p) for p in manifest_paths],
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "runner": {
            "hostname": socket.gethostname(),
            "os": f"{platform.system()} {platform.release()}",
            "arch": platform.machine(),
            "python": platform.python_version(),
        },
        "summary": {
            "entry_count": len(entry_results),
            "pass_count": pass_count,
            "pass_rate": round(pass_count / len(entry_results), 4) if entry_results else 0.0,
            "avg_wer": round(statistics.fmean(wers), 4) if wers else 1.0,
            "median_wer": round(statistics.median(wers), 4) if wers else 1.0,
            "avg_latency_ms": round(statistics.fmean(latencies), 1) if latencies else 0.0,
            "p95_latency_ms": _p95(latencies),
            "avg_rtf": round(statistics.fmean(rtfs), 3) if rtfs else 0.0,
            "model_load_ms": model_load_ms,
        },
        "by_category": by_category,
        "entries": entry_results,
    }


# ---------------------------------------------------------------------------
# Leaderboard generation
# ---------------------------------------------------------------------------

def _config_label(result: dict) -> str:
    return f"{result['stt_model']} / {result['compute_type']} / {result['device']}"


def generate_leaderboard(result_files: list[Path]) -> str:
    """Read all result JSONs and produce a ranked leaderboard markdown.

    When multiple runs exist for the same (model, compute_type, device),
    only the most recent run is kept.
    """
    # Load all, then deduplicate: most recent run per config key wins
    all_configs: list[dict] = []
    for path in sorted(result_files):
        try:
            all_configs.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            print(f"  [warn] could not read {path}: {exc}", file=sys.stderr)

    seen: dict[tuple, dict] = {}
    for c in sorted(all_configs, key=lambda x: x.get("ran_at", "")):
        key = (c.get("stt_model", ""), c.get("compute_type", ""), c.get("device", ""))
        seen[key] = c
    configs = list(seen.values())

    if not configs:
        return "# STT Benchmark Leaderboard\n\n_No results found._\n"

    # Sort by avg_wer ascending (lower is better), then avg_latency_ms
    configs.sort(key=lambda c: (
        c["summary"]["avg_wer"],
        c["summary"]["avg_latency_ms"],
    ))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# STT Benchmark Leaderboard",
        "",
        f"- Generated: {now}",
        f"- Configs: {len(configs)}",
        f"- WER pass threshold: {configs[0].get('wer_pass_threshold', 0.1):.0%}",
        "",
        "## Overall Rank",
        "",
        "Sorted by average WER (lower = better). RTF = realtime factor "
        "(synthesis time / audio duration; < 1.0 means faster than realtime).",
        "",
        "| Config | Entries | Pass% | Avg WER | Median WER | Avg ms | P95 ms | Avg RTF | Load ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for c in configs:
        s = c["summary"]
        lines.append(
            f"| {_config_label(c)} "
            f"| {s['entry_count']} "
            f"| {s['pass_rate']:.1%} "
            f"| {s['avg_wer']:.1%} "
            f"| {s['median_wer']:.1%} "
            f"| {s['avg_latency_ms']:.0f} "
            f"| {s['p95_latency_ms']:.0f} "
            f"| {s['avg_rtf']:.2f}x "
            f"| {s['model_load_ms']:.0f} "
            f"|"
        )

    # Category breakdown for the best config
    best = configs[0]
    if best.get("by_category"):
        lines += [
            "",
            f"## Category Breakdown — {_config_label(best)}",
            "",
            "| Category | Count | Pass% | Avg WER | Avg ms |",
            "|---|---:|---:|---:|---:|",
        ]
        for cat, stats in best["by_category"].items():
            lines.append(
                f"| {cat} "
                f"| {stats['count']} "
                f"| {stats['pass_rate']:.1%} "
                f"| {stats['avg_wer']:.1%} "
                f"| {stats['avg_latency_ms']:.0f} "
                f"|"
            )

    # Entry detail for the best config
    entries = best.get("entries", [])
    if entries:
        lines += [
            "",
            f"## Entry Detail — {_config_label(best)}",
            "",
            "Rows sorted by WER descending (worst first).",
            "",
            "| ID | Category | Dur s | WER | ms | RTF | Reference | Hypothesis |",
            "|---|---|---:|---:|---:|---:|---|---|",
        ]
        for e in sorted(entries, key=lambda x: x["wer"], reverse=True):
            ref = e["reference"][:60].replace("|", "\\|")
            hyp = e["hypothesis"][:60].replace("|", "\\|")
            lines.append(
                f"| {e['id']} "
                f"| {e['category']} "
                f"| {e['duration_s']:.1f} "
                f"| {e['wer']:.0%} "
                f"| {e['latency_ms']:.0f} "
                f"| {e['rtf']:.2f}x "
                f"| {ref} "
                f"| {hyp} "
                f"|"
            )

    # Pipeline timing context
    lines += [
        "",
        "## Pipeline Timing Context",
        "",
        "These STT latencies are one stage of the full voice pipeline:",
        "",
        "```",
        "TTFA = VAD_ms + STT_ms + LLM_ms + TTS_ms",
        "         ~0ms   ^^^here   see LLM leaderboard",
        "```",
        "",
        "Subtract `avg_latency_ms` above from the LLM benchmark's `Avg ms` to see "
        "how much of end-to-end latency comes from STT vs inference.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--manifest",
        dest="manifests",
        action="append",
        default=None,
        metavar="PATH",
        help=(
            "Voice dataset manifest JSON (repeatable). "
            "Defaults to both manifest.json and pipeline_manifest.json."
        ),
    )
    parser.add_argument(
        "--model",
        default="small.en",
        help="faster-whisper model name (default: small.en)",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        choices=["int8", "int8_float16", "float16", "float32"],
        help="faster-whisper compute type (default: int8)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda", "auto"],
        help="Inference device (default: cpu)",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=1,
        help="Beam size for decoding (default: 1 — fastest)",
    )
    parser.add_argument(
        "--wer-threshold",
        type=float,
        default=0.10,
        metavar="RATE",
        help="WER pass threshold 0–1 (default: 0.10 = 10%%)",
    )
    parser.add_argument(
        "--output-dir",
        default="benchmarks/stt_results",
        metavar="DIR",
        help="Directory to accumulate result JSON files (default: benchmarks/stt_results)",
    )
    parser.add_argument(
        "--publish-dir",
        default="benchmarks/published",
        metavar="DIR",
        help="Published leaderboard directory (default: benchmarks/published)",
    )
    parser.add_argument(
        "--publish-only",
        action="store_true",
        help="Regenerate the leaderboard from existing results without a new run",
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Save result JSON but do not regenerate the leaderboard",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = _repo_root()

    # Resolve manifests
    default_manifests = [
        repo_root / "benchmarks/voice_dataset/manifest.json",
        repo_root / "benchmarks/voice_dataset/pipeline_manifest.json",
    ]
    if args.manifests:
        manifest_paths = [Path(p) for p in args.manifests]
    else:
        manifest_paths = [p for p in default_manifests if p.exists()]

    missing = [p for p in manifest_paths if not p.exists()]
    if missing:
        print(f"ERROR: manifest not found: {missing}", file=sys.stderr)
        return 1

    output_dir = repo_root / args.output_dir
    publish_dir = repo_root / args.publish_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    publish_dir.mkdir(parents=True, exist_ok=True)

    # --- Run ---
    if not args.publish_only:
        print(f"\n{'='*60}")
        print(f"STT Benchmark: {args.model} / {args.compute_type} / {args.device}")
        print(f"Manifests:     {[str(p) for p in manifest_paths]}")
        print(f"{'='*60}\n")

        result = run_stt_benchmark(
            manifest_paths=manifest_paths,
            stt_model=args.model,
            compute_type=args.compute_type,
            device=args.device,
            beam_size=args.beam_size,
            wer_pass_threshold=args.wer_threshold,
            repo_root=repo_root,
        )

        s = result["summary"]
        print(f"\n{'='*60}")
        print(f"Results: {s['entry_count']} entries")
        print(f"  Pass rate:       {s['pass_rate']:.1%}  ({s['pass_count']}/{s['entry_count']})")
        print(f"  Avg WER:         {s['avg_wer']:.1%}")
        print(f"  Median WER:      {s['median_wer']:.1%}")
        print(f"  Avg latency:     {s['avg_latency_ms']:.0f} ms")
        print(f"  P95 latency:     {s['p95_latency_ms']:.0f} ms")
        print(f"  Avg RTF:         {s['avg_rtf']:.2f}x (< 1 = faster than realtime)")
        print(f"{'='*60}\n")

        # Save result JSON
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_model = args.model.replace("/", "_").replace(":", "-")
        result_filename = f"{ts}__{safe_model}__{args.compute_type}__{args.device}.json"
        result_path = output_dir / result_filename
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Saved: {result_path}")

    # --- Publish leaderboard ---
    if not args.no_publish:
        result_files = sorted(output_dir.glob("*.json"))
        if not result_files:
            print("No result files found to publish.", file=sys.stderr)
            return 0

        leaderboard_md = generate_leaderboard(result_files)
        leaderboard_path = publish_dir / "stt_leaderboard.md"
        leaderboard_path.write_text(leaderboard_md, encoding="utf-8")
        print(f"Leaderboard: {leaderboard_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
