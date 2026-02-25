#!/usr/bin/env python3
"""Run conversation-based tool benchmarks and generate a leaderboard."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from talkbot.benchmark import (
    BenchmarkProfile,
    load_profiles_from_matrix,
    load_scenarios,
    run_benchmark,
    write_outputs,
)


def _default_profile_from_args(args: argparse.Namespace) -> BenchmarkProfile:
    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
    profile_name = args.name or f"{args.provider}-{args.model}"
    env = {}
    if args.n_ctx is not None:
        env["TALKBOT_LOCAL_N_CTX"] = str(args.n_ctx)

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
    parser.add_argument("--repeats", type=int, default=1, help="Repeat each profile N times")

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
    scenarios = load_scenarios(args.scenarios)
    if args.matrix:
        profiles = load_profiles_from_matrix(args.matrix)
    else:
        profiles = [_default_profile_from_args(args)]

    profiles = _expand_repeats(profiles, max(1, args.repeats))
    report = run_benchmark(
        profiles=profiles,
        scenarios=scenarios,
        output_dir=Path(args.output),
    )
    paths = write_outputs(report, Path(args.output))

    print(f"Completed {report['run_count']} run(s) across {report['scenario_count']} scenario(s).")
    print(f"Results JSON: {paths['results']}")
    print(f"Leaderboard: {paths['leaderboard']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

