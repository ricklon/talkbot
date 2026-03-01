#!/usr/bin/env python3
"""TTS Benchmark Runner

Synthesises a set of prompts through each TTS backend/voice config,
measures synthesis latency and realtime factor, and publishes a leaderboard.

Each invocation benchmarks ONE config (backend × voice × rate).
Results accumulate in --output-dir; leaderboard is regenerated after each run.

Usage examples:
    # KittenTTS default voice
    uv run python scripts/benchmark_tts.py --backend kittentts --voice Bella

    # All KittenTTS voices
    for voice in Bella Jasper Luna Bruno Rosie Hugo Kiki Leo; do
        uv run python scripts/benchmark_tts.py --backend kittentts --voice $voice
    done

    # edge-tts (requires internet)
    uv run python scripts/benchmark_tts.py --backend edge-tts --voice en-US-AriaNeural

    # Regenerate leaderboard only
    uv run python scripts/benchmark_tts.py --publish-only
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import statistics
import sys
import tempfile
import time
import wave
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Audio duration helper
# ---------------------------------------------------------------------------

def _wav_duration_ms(path: str) -> float:
    """Return WAV file duration in milliseconds. Returns 0.0 on error."""
    try:
        with wave.open(path, "rb") as wf:
            return wf.getnframes() / wf.getframerate() * 1000.0
    except Exception:
        return 0.0


def _mp3_duration_ms(path: str) -> float:
    """Return MP3 duration in milliseconds via soundfile. Returns 0.0 on error."""
    try:
        import soundfile as sf
        return sf.info(path).duration * 1000.0
    except Exception:
        return 0.0


def _audio_duration_ms(path: str, backend_name: str) -> float:
    if backend_name == "edge-tts":
        return _mp3_duration_ms(path)
    return _wav_duration_ms(path)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

# These are the expected *TTS output* texts from the pipeline prompts —
# representative short answers a voice assistant would speak aloud.
# Sourced from pipeline_prompts.json expected_tts_spoken_form.
DEFAULT_PROMPTS = [
    # Tool outputs — numeric/time formatting challenges
    {"id": "time_spoken",         "category": "tool_time",       "text": "The current time is three forty five PM."},
    {"id": "date_spoken",         "category": "tool_date",       "text": "Today is February twenty seventh twenty twenty six."},
    {"id": "math_result",         "category": "tool_calculator", "text": "One hundred and forty four divided by twelve equals twelve."},
    {"id": "percent_result",      "category": "tool_calculator", "text": "Fifteen percent of two hundred is thirty."},
    {"id": "duration_spoken",     "category": "tool_time",       "text": "There are four hours and twelve minutes until midnight."},
    # LLM knowledge answers
    {"id": "year_apollo",         "category": "llm_history",     "text": "The Apollo eleven moon landing happened in nineteen sixty nine."},
    {"id": "year_ww2",            "category": "llm_history",     "text": "World War Two ended in nineteen forty five."},
    {"id": "formula_water",       "category": "llm_science",     "text": "The chemical formula for water is H two O."},
    {"id": "speed_of_light",      "category": "llm_science",     "text": "The speed of light is approximately two hundred ninety nine million seven hundred ninety two thousand four hundred fifty eight metres per second."},
    {"id": "seconds_in_hour",     "category": "llm_conversion",  "text": "There are three thousand six hundred seconds in an hour."},
    {"id": "dna_acronym",         "category": "llm_science",     "text": "DNA stands for deoxyribonucleic acid."},
    {"id": "pi_decimal",          "category": "llm_math",        "text": "Pi to two decimal places is three point one four."},
    # Edge cases for TTS naturalness
    {"id": "short_ack",           "category": "ux",              "text": "Got it."},
    {"id": "long_sentence",       "category": "ux",              "text": "I've added milk and eggs to your groceries list. Is there anything else you'd like to add?"},
    {"id": "tool_error",          "category": "ux",              "text": "Sorry, I couldn't complete that request. Please try again."},
]


def _load_prompts(path: Path | None) -> list[dict]:
    if path is None:
        return DEFAULT_PROMPTS
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "prompts" in data:
        return data["prompts"]
    raise ValueError(f"Unrecognised prompts format in {path}")


# ---------------------------------------------------------------------------
# Core benchmark
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return here.parent


def run_tts_benchmark(
    backend: str,
    voice: str | None,
    rate: int,
    prompts: list[dict],
) -> dict:
    """Initialise TTS once, synthesise all prompts, return result dict."""
    from talkbot.tts import TTSManager

    print(f"[tts-bench] Initialising backend={backend!r} voice={voice!r} rate={rate}")
    t0 = time.perf_counter()
    tts = TTSManager(backend=backend, rate=rate)
    if voice:
        tts.set_voice(voice)
    init_ms = round((time.perf_counter() - t0) * 1000, 1)
    active_backend = tts.backend_name
    active_voice = voice or "(default)"
    print(f"[tts-bench] Ready: backend={active_backend!r} voice={active_voice!r} in {init_ms:.0f} ms")

    suffix = ".mp3" if active_backend == "edge-tts" else ".wav"

    entry_results: list[dict] = []

    for prompt in prompts:
        prompt_id = prompt.get("id", "unknown")
        text = prompt.get("text", "")
        category = prompt.get("category", "unknown")
        word_count = len(text.split())

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            tmp_path = f.name

        try:
            t_start = time.perf_counter()
            tts.save_to_file(text, tmp_path)
            synthesis_ms = round((time.perf_counter() - t_start) * 1000, 1)

            audio_duration_ms = round(_audio_duration_ms(tmp_path, active_backend), 1)
            rtf = round(synthesis_ms / audio_duration_ms, 3) if audio_duration_ms > 0 else 0.0
            words_per_sec = round(word_count / (synthesis_ms / 1000), 1) if synthesis_ms > 0 else 0.0

            entry_results.append({
                "id": prompt_id,
                "category": category,
                "text": text,
                "word_count": word_count,
                "synthesis_ms": synthesis_ms,
                "audio_duration_ms": audio_duration_ms,
                "rtf": rtf,
                "words_per_sec": words_per_sec,
            })
            print(
                f"  [OK] {prompt_id:<30s} "
                f"{synthesis_ms:>6.0f}ms synth  "
                f"{audio_duration_ms:>6.0f}ms audio  "
                f"RTF={rtf:.2f}x  "
                f"{words_per_sec:.1f} w/s"
            )
        except Exception as exc:
            print(f"  [ERR] {prompt_id}: {exc}")
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    # Aggregate
    synth_ms_list = [r["synthesis_ms"] for r in entry_results]
    audio_dur_list = [r["audio_duration_ms"] for r in entry_results]
    rtf_list = [r["rtf"] for r in entry_results if r["rtf"] > 0]

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
        cat_synth = [r["synthesis_ms"] for r in rows]
        cat_rtf = [r["rtf"] for r in rows if r["rtf"] > 0]
        by_category[cat] = {
            "count": len(rows),
            "avg_synthesis_ms": round(statistics.fmean(cat_synth), 1) if cat_synth else 0.0,
            "avg_rtf": round(statistics.fmean(cat_rtf), 3) if cat_rtf else 0.0,
        }

    return {
        "schema_version": "2026.tts.v1",
        "backend": active_backend,
        "voice": active_voice,
        "rate": rate,
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "runner": {
            "hostname": socket.gethostname(),
            "os": f"{platform.system()} {platform.release()}",
            "arch": platform.machine(),
            "python": platform.python_version(),
        },
        "summary": {
            "prompt_count": len(entry_results),
            "avg_synthesis_ms": round(statistics.fmean(synth_ms_list), 1) if synth_ms_list else 0.0,
            "p95_synthesis_ms": _p95(synth_ms_list),
            "avg_audio_duration_ms": round(statistics.fmean(audio_dur_list), 1) if audio_dur_list else 0.0,
            "avg_rtf": round(statistics.fmean(rtf_list), 3) if rtf_list else 0.0,
            "init_ms": init_ms,
        },
        "by_category": by_category,
        "entries": entry_results,
    }


# ---------------------------------------------------------------------------
# Leaderboard generation
# ---------------------------------------------------------------------------

def _config_label(result: dict) -> str:
    return f"{result['backend']} / {result['voice']} / rate={result['rate']}"


def generate_leaderboard(result_files: list[Path]) -> str:
    configs: list[dict] = []
    for path in sorted(result_files):
        try:
            configs.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            print(f"  [warn] could not read {path}: {exc}", file=sys.stderr)

    if not configs:
        return "# TTS Benchmark Leaderboard\n\n_No results found._\n"

    # Sort by avg_synthesis_ms ascending (faster = better)
    configs.sort(key=lambda c: c["summary"]["avg_synthesis_ms"])

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# TTS Benchmark Leaderboard",
        "",
        f"- Generated: {now}",
        f"- Configs: {len(configs)}",
        "",
        "RTF = synthesis time / audio duration. < 1.0 means faster than realtime.",
        "Avg synthesis ms is the time from `save_to_file()` call to file written — "
        "this is the TTS contribution to TTFA.",
        "",
        "## Overall Rank",
        "",
        "| Config | Prompts | Avg Synth ms | P95 Synth ms | Avg Audio ms | Avg RTF | Init ms |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for c in configs:
        s = c["summary"]
        lines.append(
            f"| {_config_label(c)} "
            f"| {s['prompt_count']} "
            f"| {s['avg_synthesis_ms']:.0f} "
            f"| {s['p95_synthesis_ms']:.0f} "
            f"| {s['avg_audio_duration_ms']:.0f} "
            f"| {s['avg_rtf']:.2f}x "
            f"| {s['init_ms']:.0f} "
            f"|"
        )

    # Category breakdown for fastest config
    best = configs[0]
    if best.get("by_category"):
        lines += [
            "",
            f"## Category Breakdown — {_config_label(best)}",
            "",
            "| Category | Count | Avg Synth ms | Avg RTF |",
            "|---|---:|---:|---:|",
        ]
        for cat, stats in best["by_category"].items():
            lines.append(
                f"| {cat} "
                f"| {stats['count']} "
                f"| {stats['avg_synthesis_ms']:.0f} "
                f"| {stats['avg_rtf']:.2f}x "
                f"|"
            )

    # Entry detail for fastest config
    entries = best.get("entries", [])
    if entries:
        lines += [
            "",
            f"## Entry Detail — {_config_label(best)}",
            "",
            "| ID | Category | Words | Synth ms | Audio ms | RTF |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for e in sorted(entries, key=lambda x: x["synthesis_ms"], reverse=True):
            lines.append(
                f"| {e['id']} "
                f"| {e['category']} "
                f"| {e['word_count']} "
                f"| {e['synthesis_ms']:.0f} "
                f"| {e['audio_duration_ms']:.0f} "
                f"| {e['rtf']:.2f}x "
                f"|"
            )

    # Pipeline context
    lines += [
        "",
        "## Pipeline Timing Context",
        "",
        "TTS synthesis latency is one stage of the full voice pipeline:",
        "",
        "```",
        "TTFA = VAD_ms + STT_ms + LLM_ms + TTS_ms",
        "                                   ^^^here",
        "```",
        "",
        "Add `avg_synthesis_ms` above to the STT and LLM leaderboard latencies "
        "to estimate total TTFA for a given config.",
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
        "--backend",
        choices=["kittentts", "edge-tts", "pyttsx3"],
        default="kittentts",
        help="TTS backend to benchmark (default: kittentts)",
    )
    parser.add_argument(
        "--voice",
        default=None,
        help="Voice ID (default: backend default)",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=175,
        help="Speech rate in words-per-minute equivalent (default: 175)",
    )
    parser.add_argument(
        "--prompts",
        default=None,
        metavar="PATH",
        help="JSON file with prompt list (default: built-in set of 15 prompts)",
    )
    parser.add_argument(
        "--output-dir",
        default="benchmarks/tts_results",
        metavar="DIR",
        help="Directory to accumulate result JSON files (default: benchmarks/tts_results)",
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
        help="Regenerate leaderboard from existing results without a new run",
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Save result JSON but do not regenerate the leaderboard",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    args = parse_args(argv)
    repo_root = _repo_root()

    output_dir = repo_root / args.output_dir
    publish_dir = repo_root / args.publish_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    publish_dir.mkdir(parents=True, exist_ok=True)

    prompts_path = Path(args.prompts) if args.prompts else None
    prompts = _load_prompts(prompts_path)

    if not args.publish_only:
        print(f"\n{'='*60}")
        print(f"TTS Benchmark: {args.backend} / {args.voice or '(default)'} / rate={args.rate}")
        print(f"Prompts: {len(prompts)}")
        print(f"{'='*60}\n")

        result = run_tts_benchmark(
            backend=args.backend,
            voice=args.voice,
            rate=args.rate,
            prompts=prompts,
        )

        s = result["summary"]
        print(f"\n{'='*60}")
        print(f"Results: {s['prompt_count']} prompts")
        print(f"  Avg synthesis:   {s['avg_synthesis_ms']:.0f} ms")
        print(f"  P95 synthesis:   {s['p95_synthesis_ms']:.0f} ms")
        print(f"  Avg audio dur:   {s['avg_audio_duration_ms']:.0f} ms")
        print(f"  Avg RTF:         {s['avg_rtf']:.2f}x  (< 1 = faster than realtime)")
        print(f"{'='*60}\n")

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_backend = args.backend.replace("-", "_")
        safe_voice = (args.voice or "default").replace(" ", "_").replace("/", "_")
        filename = f"{ts}__{safe_backend}__{safe_voice}__rate{args.rate}.json"
        result_path = output_dir / filename
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Saved: {result_path}")

    if not args.no_publish:
        result_files = sorted(output_dir.glob("*.json"))
        if not result_files:
            print("No result files found to publish.", file=sys.stderr)
            return 0

        leaderboard_md = generate_leaderboard(result_files)
        leaderboard_path = publish_dir / "tts_leaderboard.md"
        leaderboard_path.write_text(leaderboard_md, encoding="utf-8")
        print(f"Leaderboard: {leaderboard_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
