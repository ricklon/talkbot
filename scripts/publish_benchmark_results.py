#!/usr/bin/env python3
"""Publish benchmark artifacts into benchmarks/published/."""

from __future__ import annotations

import argparse
import sys

from talkbot.benchmark_publish import publish_benchmark_results


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        default="benchmark_results",
        help="Directory containing latest results.json and leaderboard.md",
    )
    parser.add_argument(
        "--published-root",
        default="benchmarks/published",
        help="Repo path to publish latest + runs snapshots",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional explicit run name under published/runs/<run-name>",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    paths = publish_benchmark_results(
        source_root=args.source_root,
        published_root=args.published_root,
        run_name=args.run_name,
    )
    print(f"Published root: {paths['published_root']}")
    print(f"Latest leaderboard: {paths['latest_leaderboard']}")
    print(f"Run leaderboard: {paths['run_leaderboard']}")
    print(f"Index: {paths['index']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

