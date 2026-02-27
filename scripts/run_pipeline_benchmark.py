#!/usr/bin/env python3
"""Run the full STT → LLM → score pipeline benchmark against recorded audio."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prompts",
        default="benchmarks/pipeline_prompts.json",
        help="Pipeline prompt definitions",
    )
    parser.add_argument(
        "--manifest",
        default="benchmarks/voice_dataset/pipeline_manifest.json",
        help="Recorded audio manifest",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Results JSON output path (default: benchmarks/pipeline_results/<timestamp>.json)",
    )
    parser.add_argument(
        "--provider",
        default="openrouter",
        help="LLM provider (default: openrouter)",
    )
    parser.add_argument(
        "--model",
        default="mistralai/mistral-small-3.1-24b-instruct",
        help="LLM model ID",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (default: OPENROUTER_API_KEY env var)",
    )
    parser.add_argument(
        "--stt-model",
        default="small.en",
        help="Whisper STT model (default: small.en)",
    )
    parser.add_argument(
        "--take",
        type=int,
        default=1,
        help="Which take to use per prompt (default: 1)",
    )
    parser.add_argument(
        "--no-tools",
        action="store_true",
        help="Disable tool use",
    )
    return parser.parse_args(argv)


def _fuzzy_match(response: str, expected: list[str]) -> bool:
    """Return True if ALL expected strings appear in the response (case-insensitive)."""
    lower = response.lower()
    return all(e.lower() in lower for e in expected)


def _make_tracking_register(client, calls: list[str]) -> None:
    """Wrap registered tool functions to record which tools are called."""
    original_register = client.register_tool

    def tracking_register(name, func, description, parameters):
        def tracked(*args, **kwargs):
            calls.append(name)
            return func(*args, **kwargs)
        original_register(name=name, func=tracked, description=description, parameters=parameters)

    client.register_tool = tracking_register


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    # Load prompts indexed by id
    prompts_path = Path(args.prompts)
    prompts_raw = json.loads(prompts_path.read_text(encoding="utf-8"))
    prompts = {p["id"]: p for p in prompts_raw}

    # Load manifest
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("entries", [])

    # Filter to requested take
    take_suffix = f"__take{args.take:02d}"
    entries = [e for e in entries if e["id"].endswith(take_suffix)]

    if not entries:
        print(f"No entries found for take {args.take}.", file=sys.stderr)
        return 1

    # Set up STT
    print(f"Loading STT model: {args.stt_model}")
    from talkbot.voice import transcribe_audio_file

    # Set up LLM
    import os
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY", "")
    from talkbot.llm import create_llm_client, supports_tools
    from talkbot.tools import register_all_tools

    results = []

    with create_llm_client(
        provider=args.provider,
        model=args.model,
        api_key=api_key,
    ) as client:
        use_tools = not args.no_tools and supports_tools(client)

        for entry in entries:
            prompt_id = entry["prompt_id"]
            prompt = prompts.get(prompt_id)
            if not prompt:
                print(f"  [skip] no prompt definition for {prompt_id}")
                continue

            audio_path = entry["audio_path"]
            print(f"\n[{prompt_id}]")
            print(f"  Audio: {audio_path}")

            # STT
            t0 = time.monotonic()
            try:
                transcript = transcribe_audio_file(
                    audio_path,
                    stt_model=args.stt_model,
                )
            except Exception as exc:
                print(f"  STT error: {exc}")
                transcript = ""
            stt_ms = int((time.monotonic() - t0) * 1000)
            print(f"  STT ({stt_ms}ms): {transcript!r}")

            # LLM
            tool_calls_made: list[str] = []
            if use_tools:
                _make_tracking_register(client, tool_calls_made)
                register_all_tools(client)

            messages = [{"role": "user", "content": transcript}]
            t0 = time.monotonic()
            try:
                if use_tools:
                    response = client.chat_with_tools(messages)
                else:
                    raw = client.chat_completion(messages)
                    choices = raw.get("choices") or []
                    response = choices[0]["message"]["content"] if choices else ""
            except Exception as exc:
                print(f"  LLM error: {exc}")
                response = ""
            llm_ms = int((time.monotonic() - t0) * 1000)
            print(f"  LLM ({llm_ms}ms): {response[:120]!r}")
            if tool_calls_made:
                print(f"  Tools called: {tool_calls_made}")

            # Score
            expected_contains = prompt.get("expected_answer_contains") or []
            answer_ok = _fuzzy_match(response, expected_contains) if expected_contains else None

            requires_tool = prompt.get("requires_tool")
            if requires_tool:
                tool_ok = requires_tool in tool_calls_made
            else:
                tool_ok = None

            print(f"  answer_ok={answer_ok}  tool_ok={tool_ok}")

            results.append({
                "prompt_id": prompt_id,
                "category": prompt.get("category"),
                "take": args.take,
                "audio_path": audio_path,
                "expected_question": prompt.get("text"),
                "stt_transcript": transcript,
                "stt_ms": stt_ms,
                "llm_response": response,
                "llm_ms": llm_ms,
                "tool_calls_made": tool_calls_made,
                "requires_tool": requires_tool,
                "expected_answer_contains": expected_contains,
                "answer_ok": answer_ok,
                "tool_ok": tool_ok,
                "scored_at": _now_iso(),
            })

    # Summary
    answered = [r for r in results if r["answer_ok"] is True]
    tool_results = [r for r in results if r["tool_ok"] is not None]
    tool_ok_count = sum(1 for r in tool_results if r["tool_ok"])

    print(f"\n{'='*50}")
    print(f"Results: {len(results)} prompts")
    print(f"  Answer OK:  {len(answered)}/{len(results)}")
    if tool_results:
        print(f"  Tool OK:    {tool_ok_count}/{len(tool_results)}")

    # Save
    out_path = Path(args.output) if args.output else (
        Path("benchmarks/pipeline_results") /
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}__{args.model.replace('/', '_')}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "model": args.model,
        "provider": args.provider,
        "stt_model": args.stt_model,
        "take": args.take,
        "use_tools": use_tools,
        "ran_at": _now_iso(),
        "summary": {
            "total": len(results),
            "answer_ok": len(answered),
            "tool_ok": tool_ok_count,
            "tool_total": len(tool_results),
        },
        "results": results,
    }, indent=2), encoding="utf-8")
    print(f"  Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
