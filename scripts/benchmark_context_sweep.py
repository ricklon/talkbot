#!/usr/bin/env python3
"""Auto-generate and run context-window sweeps for benchmark profiles."""

from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path
from typing import Any

from talkbot.benchmark import BenchmarkProfile, load_scenarios, run_benchmark, write_outputs


def _load_matrix_profiles(path: str | Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {}, [dict(entry) for entry in payload if isinstance(entry, dict)]
    if not isinstance(payload, dict):
        raise ValueError("Matrix must be a JSON object or list.")

    benchmark_cfg = payload.get("benchmark")
    benchmark_cfg = dict(benchmark_cfg) if isinstance(benchmark_cfg, dict) else {}
    profiles = payload.get("profiles") or payload.get("runs") or []
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("Matrix must define a non-empty 'profiles' list.")
    return benchmark_cfg, [dict(entry) for entry in profiles if isinstance(entry, dict)]


def _detect_context_length(model_path: str) -> int:
    try:
        from llama_cpp import Llama  # type: ignore
    except Exception as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError(
            "llama_cpp is required for auto context sweep detection."
        ) from exc

    llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
    try:
        metadata = getattr(llm, "metadata", {}) or {}
        if isinstance(metadata, dict):
            for key in ("qwen3.context_length", "qwen2.context_length", "llama.context_length"):
                value = metadata.get(key)
                if value is None:
                    continue
                try:
                    parsed = int(value)
                    if parsed > 0:
                        return parsed
                except Exception:
                    continue
            for key, value in metadata.items():
                if not str(key).endswith(".context_length"):
                    continue
                try:
                    parsed = int(value)
                    if parsed > 0:
                        return parsed
                except Exception:
                    continue
    finally:
        del llm
        gc.collect()

    raise RuntimeError(f"Could not detect context length from GGUF metadata: {model_path}")


def _build_context_windows(
    train_ctx: int,
    *,
    include_yarn: bool,
    max_ctx_cap: int | None,
) -> list[int]:
    cap = max_ctx_cap if max_ctx_cap and max_ctx_cap > 0 else None
    base = [2048, 4096, 8192, 16384, 32768, train_ctx]
    contexts = sorted({c for c in base if c > 0 and c <= train_ctx})
    if include_yarn:
        contexts.extend([65536, 131072])
    contexts = sorted(set(contexts))
    if cap is not None:
        contexts = [c for c in contexts if c <= cap]
        if train_ctx <= cap and train_ctx not in contexts:
            contexts.append(train_ctx)
            contexts = sorted(set(contexts))
    return contexts


def _base_name(profile: dict[str, Any]) -> str:
    name = str(profile.get("name") or "profile").strip()
    if name:
        return name
    return "profile"


def _profile_for_ctx(profile: dict[str, Any], ctx: int) -> BenchmarkProfile:
    clone = dict(profile)
    clone.pop("context_windows", None)
    clone.pop("n_ctx", None)
    env = dict(clone.get("env") or {})
    env["TALKBOT_LOCAL_N_CTX"] = str(ctx)
    clone["env"] = env
    clone["name"] = f"{_base_name(profile)}-ctx{ctx}"
    return BenchmarkProfile(**clone)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", default="benchmarks/model_matrix.example.json")
    parser.add_argument("--scenarios", default="tests/conversations")
    parser.add_argument("--output", default="benchmark_results/context_auto")
    parser.add_argument("--include-yarn", action="store_true")
    parser.add_argument(
        "--max-ctx-cap",
        type=int,
        default=None,
        help="Optional hard cap for generated context windows.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop higher contexts for a model family after first failed run.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    benchmark_cfg, base_profiles = _load_matrix_profiles(args.matrix)
    scenarios = load_scenarios(args.scenarios)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    rubric = benchmark_cfg.get("rubric")
    context_analysis = benchmark_cfg.get("context_analysis")

    all_runs: list[dict[str, Any]] = []
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    for raw in base_profiles:
        provider = str(raw.get("provider") or "")
        model_path = str(raw.get("local_model_path") or "")
        if provider != "local" or not model_path:
            continue

        train_ctx = _detect_context_length(model_path)
        contexts = _build_context_windows(
            train_ctx,
            include_yarn=args.include_yarn,
            max_ctx_cap=args.max_ctx_cap,
        )
        if not contexts:
            continue

        for ctx in contexts:
            profile = _profile_for_ctx(raw, ctx)
            report = run_benchmark(
                profiles=[profile],
                scenarios=scenarios,
                output_dir=output_dir,
                rubric=rubric,
                context_analysis=context_analysis,
            )
            run = report["runs"][0]
            all_runs.append(run)
            if args.stop_on_error and run.get("status") != "ok":
                break

    final_report = {
        "started_at": started_at,
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "scenario_count": len(scenarios),
        "run_count": len(all_runs),
        "rubric": rubric,
        "context_analysis": context_analysis,
        "runs": all_runs,
    }
    paths = write_outputs(final_report, output_dir)
    print(f"Completed {final_report['run_count']} run(s) across {final_report['scenario_count']} scenario(s).")
    print(f"Results JSON: {paths['results']}")
    print(f"Leaderboard: {paths['leaderboard']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
