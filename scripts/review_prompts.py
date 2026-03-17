#!/usr/bin/env python3
"""Review prompt presets and optionally benchmark them."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from talkbot.benchmark import BenchmarkProfile, load_scenarios, run_benchmark, write_outputs
from talkbot.prompting import DEFAULT_PROMPT_CATALOG, PromptPreset, load_prompt_catalog, review_prompt_preset


load_dotenv()


DEFAULT_LOCAL_SERVER_MODEL = "qwen3.5-0.8b-q8_0"


def _default_provider() -> str:
    return os.getenv("TALKBOT_LLM_PROVIDER", "local_server")


def _default_model(provider: str) -> str:
    if provider == "local_server":
        configured = (os.getenv("TALKBOT_LOCAL_SERVER_MODEL") or "").strip()
        return configured or DEFAULT_LOCAL_SERVER_MODEL
    configured = (os.getenv("TALKBOT_DEFAULT_MODEL") or "").strip()
    if configured:
        return configured
    if provider == "openrouter":
        return "mistralai/ministral-3b-2512"
    return "qwen/qwen3-1.7b"


def parse_args(argv: list[str]) -> argparse.Namespace:
    provider = _default_provider()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default=str(DEFAULT_PROMPT_CATALOG), help="Prompt catalog JSON path")
    parser.add_argument("--preset", action="append", default=None, help="Prompt preset name to review")
    parser.add_argument(
        "--scenarios",
        default="tests/conversations",
        help="Scenario JSON file or directory used for prompt review",
    )
    parser.add_argument(
        "--output",
        default="benchmark_results/prompts/latest",
        help="Benchmark output directory when --run-benchmark is used",
    )
    parser.add_argument("--run-benchmark", action="store_true", help="Run the prompt presets against review scenarios")
    parser.add_argument("--provider", default=provider, choices=["local", "local_server", "openrouter"])
    parser.add_argument("--model", default=_default_model(provider))
    parser.add_argument("--api-key", default=os.getenv("OPENROUTER_API_KEY", ""))
    parser.add_argument("--local-model-path", default=os.getenv("TALKBOT_LOCAL_MODEL_PATH", ""))
    parser.add_argument("--llamacpp-bin", default=os.getenv("TALKBOT_LLAMACPP_BIN", "llama-cli"))
    parser.add_argument(
        "--local-server-url",
        default=os.getenv("TALKBOT_LOCAL_SERVER_URL", "http://127.0.0.1:8000/v1"),
    )
    parser.add_argument("--local-server-api-key", default=os.getenv("TALKBOT_LOCAL_SERVER_API_KEY", ""))
    parser.add_argument("--max-tokens", type=int, default=int(os.getenv("TALKBOT_MAX_TOKENS", "512") or "512"))
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--no-tools", action="store_true", help="Disable tool registration in the benchmark")
    return parser.parse_args(argv)


def _select_presets(all_presets: list[PromptPreset], names: list[str] | None) -> list[PromptPreset]:
    if not names:
        return all_presets
    wanted = {name.strip().lower() for name in names if name.strip()}
    selected = [preset for preset in all_presets if preset.name.lower() in wanted]
    missing = sorted(wanted - {preset.name.lower() for preset in selected})
    if missing:
        raise KeyError(f"Unknown prompt preset(s): {', '.join(missing)}")
    return selected


def _filter_review_scenarios(all_scenarios: list[dict], presets: list[PromptPreset]) -> list[dict]:
    scenario_ids = {scenario["id"] for scenario in all_scenarios}
    wanted = {scenario_id for preset in presets for scenario_id in preset.scenarios}
    if not wanted:
        return all_scenarios
    missing = sorted(wanted - scenario_ids)
    if missing:
        raise ValueError(f"Unknown scenario id(s) in prompt catalog: {', '.join(missing)}")
    return [scenario for scenario in all_scenarios if scenario["id"] in wanted]


def _print_review(presets: list[PromptPreset], scenario_ids: set[str]) -> int:
    error_count = 0
    warning_count = 0
    for preset in presets:
        findings = review_prompt_preset(preset, available_scenarios=scenario_ids)
        errors = [finding for finding in findings if finding.severity == "error"]
        warnings = [finding for finding in findings if finding.severity == "warning"]
        error_count += len(errors)
        warning_count += len(warnings)

        rel_path = preset.path
        try:
            rel_path = preset.path.relative_to(Path.cwd())
        except ValueError:
            pass

        print(f"[{preset.name}] {rel_path}")
        print(f"Summary: {preset.summary or '(missing summary)'}")
        print(f"Goals: {', '.join(preset.goals) if preset.goals else '(none)'}")
        print(f"Scenarios: {', '.join(preset.scenarios) if preset.scenarios else '(none)'}")
        if preset.review_notes:
            print(f"Notes: {preset.review_notes}")
        if not findings:
            print("Review: OK")
        else:
            for finding in findings:
                print(f"{finding.severity.upper()}: {finding.code} - {finding.message}")
        print()

    print(f"Summary: {len(presets)} preset(s), {error_count} error(s), {warning_count} warning(s)")
    return 1 if error_count else 0


def _build_profiles(args: argparse.Namespace, presets: list[PromptPreset]) -> list[BenchmarkProfile]:
    profiles: list[BenchmarkProfile] = []
    for preset in presets:
        profiles.append(
            BenchmarkProfile(
                name=f"prompt-{preset.name}",
                provider=args.provider,
                model=args.model,
                api_key=args.api_key or None,
                local_model_path=args.local_model_path or None,
                llamacpp_bin=args.llamacpp_bin or None,
                local_server_url=args.local_server_url or None,
                local_server_api_key=args.local_server_api_key or None,
                use_tools=not args.no_tools,
                system_prompt=preset.load_text() or None,
                prompt_preset=preset.name,
                prompt_source=f"preset:{preset.name}",
                max_tokens=args.max_tokens,
                temperature=args.temperature,
            )
        )
    return profiles


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    presets = _select_presets(load_prompt_catalog(args.catalog), args.preset)
    scenarios = load_scenarios(args.scenarios)
    scenario_ids = {scenario["id"] for scenario in scenarios}

    review_exit = _print_review(presets, scenario_ids)
    if review_exit or not args.run_benchmark:
        return review_exit

    review_scenarios = _filter_review_scenarios(scenarios, presets)
    report = run_benchmark(
        profiles=_build_profiles(args, presets),
        scenarios=review_scenarios,
        output_dir=args.output,
    )
    paths = write_outputs(report, args.output)
    print(f"Benchmark results: {paths['results']}")
    print(f"Benchmark leaderboard: {paths['leaderboard']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
