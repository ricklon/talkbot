#!/usr/bin/env python3
"""Run conversation-based tool benchmarks and generate a leaderboard."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from talkbot.benchmark import (
    BenchmarkProfile,
    detect_runner_info,
    load_matrix_config,
    load_scenarios,
    run_benchmark,
    top_n_per_provider,
    write_outputs,
)
from talkbot.benchmark_publish import publish_benchmark_results


def _safe_segment(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-._")


def _resolve_run_name(args: argparse.Namespace) -> str:
    explicit = _safe_segment(args.run_name or "")
    if explicit:
        return explicit

    output_name = _safe_segment(Path(args.output).name)
    if output_name and output_name.lower() != "latest":
        return output_name

    if args.matrix:
        matrix_name = _safe_segment(Path(args.matrix).stem)
        matrix_name = matrix_name.replace("model_matrix.", "").replace("model_matrix_", "")
        label = matrix_name or "matrix"
    else:
        provider = _safe_segment(args.provider)
        model = _safe_segment(args.model)
        label = f"{provider}-{model}".strip("-") or "single"

    return f"{label}-{time.strftime('%Y%m%d-%H%M%S')}"


def _default_profile_from_args(args: argparse.Namespace) -> BenchmarkProfile:
    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
    profile_name = args.name or f"{args.provider}-{args.model}"
    env = {}
    if args.n_ctx is not None:
        env["TALKBOT_LOCAL_N_CTX"] = str(args.n_ctx)

    system_prompt: str | None = None
    if args.system_prompt_file:
        system_prompt = Path(args.system_prompt_file).read_text(encoding="utf-8").strip()
    elif args.system_prompt:
        system_prompt = args.system_prompt.strip()

    return BenchmarkProfile(
        name=profile_name,
        provider=args.provider,
        model=args.model,
        api_key=api_key,
        local_model_path=args.local_model_path,
        llamacpp_bin=args.llamacpp_bin,
        local_server_url=args.local_server_url,
        local_server_api_key=args.local_server_api_key,
        enable_thinking=args.thinking,
        use_tools=not args.no_tools,
        system_prompt=system_prompt or None,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        env=env,
    )


def _expand_repeats(profiles: list[BenchmarkProfile], repeats: int) -> list[BenchmarkProfile]:
    if repeats <= 1:
        return profiles
    expanded: list[BenchmarkProfile] = []
    for profile in profiles:
        for idx in range(1, repeats + 1):
            clone = BenchmarkProfile(**json.loads(json.dumps(profile.__dict__)))
            clone.name = f"{profile.name}-r{idx}"
            expanded.append(clone)
    return expanded


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenarios",
        default="tests/conversations",
        help="Scenario JSON file or directory (default: tests/conversations)",
    )
    parser.add_argument(
        "--matrix",
        default=None,
        help="JSON matrix file with 'profiles' list. If omitted, single profile args are used.",
    )
    parser.add_argument(
        "--output",
        default="benchmark_results/latest",
        help="Output directory for results.json and leaderboard.md",
    )
    parser.add_argument(
        "--main-output-root",
        default="benchmark_results",
        help="Canonical root to mirror latest results.json/leaderboard.md for one-stop access",
    )
    parser.add_argument(
        "--no-update-main",
        action="store_true",
        help="Do not mirror outputs into <main-output-root>/results.json and leaderboard.md",
    )
    parser.add_argument(
        "--publish-root",
        default="benchmarks/published",
        help="Repo-tracked publish root for latest + run snapshots",
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Do not publish into <publish-root> after run completion",
    )
    parser.add_argument(
        "--no-update-latest",
        action="store_true",
        help="Archive run under runs/ without overwriting published/latest/",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional publish run name. Auto-generated when output ends with 'latest'.",
    )
    parser.add_argument("--repeats", type=int, default=1, help="Repeat each profile N times")
    parser.add_argument(
        "--runner-label",
        default=os.getenv("TALKBOT_BENCHMARK_RUNNER", ""),
        help="Optional machine label for cross-system comparison (e.g., linux-main, win-dev, pi5).",
    )
    parser.add_argument(
        "--runner-notes",
        default=None,
        help="Optional free-form notes stored in report metadata.",
    )

    parser.add_argument("--name", default=None, help="Run name for single-profile mode")
    parser.add_argument(
        "--provider",
        default=os.getenv("TALKBOT_LLM_PROVIDER", "local"),
        choices=["local", "local_server", "openrouter"],
        help="Provider for single-profile mode",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("TALKBOT_DEFAULT_MODEL", "qwen/qwen3-1.7b"),
        help="Model id/label for single-profile mode",
    )
    parser.add_argument("--api-key", default=None, help="OpenRouter API key override")
    parser.add_argument("--local-model-path", default=os.getenv("TALKBOT_LOCAL_MODEL_PATH"))
    parser.add_argument(
        "--llamacpp-bin",
        default=os.getenv("TALKBOT_LLAMACPP_BIN", "llama-cli"),
    )
    parser.add_argument(
        "--local-server-url",
        default=os.getenv("TALKBOT_LOCAL_SERVER_URL", "http://127.0.0.1:8000/v1"),
    )
    parser.add_argument(
        "--local-server-api-key",
        default=os.getenv("TALKBOT_LOCAL_SERVER_API_KEY"),
    )
    parser.add_argument("--thinking", action="store_true", help="Enable thinking mode")
    parser.add_argument("--no-tools", action="store_true", help="Disable tool mode")
    parser.add_argument(
        "--system-prompt",
        default=None,
        help="System prompt text to prepend to each scenario (single-profile mode)",
    )
    parser.add_argument(
        "--system-prompt-file",
        default=None,
        help="Path to a system prompt file to prepend to each scenario (single-profile mode)",
    )
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument(
        "--n-ctx",
        type=int,
        default=None,
        help="Set TALKBOT_LOCAL_N_CTX for local provider profiles",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    resolved_run_name = _resolve_run_name(args)
    runner_info = detect_runner_info(label=args.runner_label, notes=args.runner_notes)
    scenarios = load_scenarios(args.scenarios)
    rubric: dict | None = None
    context_analysis: dict | None = None
    if args.matrix:
        matrix_config = load_matrix_config(args.matrix)
        profiles = matrix_config["profiles"]
        rubric = matrix_config.get("rubric")
        context_analysis = matrix_config.get("context_analysis")
    else:
        profiles = [_default_profile_from_args(args)]

    profiles = _expand_repeats(profiles, max(1, args.repeats))
    report = run_benchmark(
        profiles=profiles,
        scenarios=scenarios,
        output_dir=Path(args.output),
        rubric=rubric,
        context_analysis=context_analysis,
        runner_info=runner_info,
    )
    report["meta"] = {
        "main_output_root": str(Path(args.main_output_root)),
        "latest_run": str(Path(args.output).resolve()),
        "run_name": resolved_run_name,
        "runner_label": runner_info.get("label"),
        "update_main": not args.no_update_main,
    }
    paths = write_outputs(report, Path(args.output))

    main_results = None
    main_leaderboard = None
    publish_paths = None
    if not args.no_update_main:
        main_root = Path(args.main_output_root)
        main_root.mkdir(parents=True, exist_ok=True)
        main_results = main_root / "results.json"
        main_leaderboard = main_root / "leaderboard.md"
        shutil.copyfile(paths["results"], main_results)
        shutil.copyfile(paths["leaderboard"], main_leaderboard)
        (main_root / "latest_run.txt").write_text(str(Path(args.output).resolve()), encoding="utf-8")

    if not args.no_publish:
        publish_source = Path(args.main_output_root if not args.no_update_main else args.output)
        publish_paths = publish_benchmark_results(
            source_root=publish_source,
            published_root=Path(args.publish_root),
            run_name=resolved_run_name,
            update_latest=not args.no_update_latest,
        )

    print(f"Completed {report['run_count']} run(s) across {report['scenario_count']} scenario(s).")
    print(f"Results JSON: {paths['results']}")
    print(f"Leaderboard: {paths['leaderboard']}")
    if main_results and main_leaderboard:
        print(f"Main Results JSON: {main_results}")
        print(f"Main Leaderboard: {main_leaderboard}")
    if publish_paths:
        print(f"Published Latest Leaderboard: {publish_paths['latest_leaderboard']}")
        print(f"Published Run Leaderboard: {publish_paths['run_leaderboard']}")
        print(f"Published Index: {publish_paths['index']}")

    _print_suggested_defaults(report)
    return 0


def _print_suggested_defaults(report: dict) -> None:
    """Print top-3 per provider and the env vars needed to adopt each as the default."""
    from talkbot.benchmark import _normalize_rubric, _rubric_score

    top = top_n_per_provider(report, n=3)
    if not top:
        return

    rubric = _normalize_rubric(report.get("rubric"))

    def _env_lines(provider: str, model: str) -> list[str]:
        if provider == "local_server":
            return [
                "  TALKBOT_LLM_PROVIDER=local_server",
                f"  TALKBOT_LOCAL_SERVER_MODEL={model}",
            ]
        return [
            f"  TALKBOT_LLM_PROVIDER={provider}",
            f"  TALKBOT_DEFAULT_MODEL={model}",
        ]

    print("\n" + "=" * 60)
    print("Suggested defaults (top 3 per provider by balanced score)")
    print("=" * 60)
    for provider, runs in top.items():
        print(f"\n  Provider: {provider}")
        print(f"  {'Rank':<5} {'Run':<40} {'Success':>8} {'Score':>7}")
        print(f"  {'-'*5} {'-'*40} {'-'*8} {'-'*7}")
        for rank, run in enumerate(runs, start=1):
            profile = run.get("profile") or {}
            agg = run["aggregate"]
            name = profile.get("name", "")
            success = agg.get("task_success_rate", 0.0)
            score = _rubric_score(agg, rubric)
            print(f"  {rank:<5} {name:<40} {success:>7.1%} {score:>7.3f}")

        best_model = (runs[0].get("profile") or {}).get("model", "")
        print(f"\n  To set {provider!r} as default (top model: {best_model}):")
        for line in _env_lines(provider, best_model):
            print(line)
        print("  Or append to .env:")
        for line in _env_lines(provider, best_model):
            print(f"    echo '{line.strip()}' >> .env")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
