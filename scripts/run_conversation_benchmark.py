#!/usr/bin/env python3
"""Multi-turn conversational end-to-end benchmark (STT → LLM+Tools → TTS)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import wave
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conversations",
        default="benchmarks/conversations",
        help="Directory with conversation JSON scripts (default: benchmarks/conversations)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path (default: benchmarks/conversation_results/<timestamp>__<model>.json)",
    )
    parser.add_argument("--provider", default="openrouter", help="LLM provider")
    parser.add_argument(
        "--model",
        default="mistralai/mistral-small-3.1-24b-instruct",
        help="LLM model ID",
    )
    parser.add_argument("--api-key", default=None, help="API key override")
    parser.add_argument("--stt-model", default="small.en", help="Whisper STT model")
    parser.add_argument(
        "--tts-backend",
        default=None,
        help="TTS backend: edge-tts, kittentts, pyttsx3 (default: auto)",
    )
    parser.add_argument("--tts-voice", default=None, help="TTS voice ID")
    parser.add_argument(
        "--no-tts", action="store_true", help="Skip TTS synthesis (no tts_ms timing)"
    )
    parser.add_argument("--no-tools", action="store_true", help="Disable tool use")
    parser.add_argument(
        "--only",
        default=None,
        help="Comma-separated conversation IDs to run (e.g. timer_flow,list_flow)",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fuzzy_match(response: str, expected: list[str]) -> bool:
    """Return True if ALL expected strings appear in response (case-insensitive)."""
    lower = response.lower()
    return all(e.lower() in lower for e in expected)


def _make_tracking_register(client, calls: list[str]) -> None:
    """Patch client.register_tool so every registered function appends its name to calls."""
    original_register = client.register_tool

    def tracking_register(name, func, description, parameters):
        def tracked(*args, **kwargs):
            calls.append(name)
            return func(*args, **kwargs)

        original_register(name=name, func=tracked, description=description, parameters=parameters)

    client.register_tool = tracking_register


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# STT — module-level Whisper cache (avoids reloading per call)
# ---------------------------------------------------------------------------

_whisper_cache: dict = {}


def _get_whisper(model_name: str):
    if model_name not in _whisper_cache:
        from faster_whisper import WhisperModel

        _whisper_cache[model_name] = WhisperModel(model_name, device="cpu", compute_type="int8")
    return _whisper_cache[model_name]


def _transcribe(path: str, model_name: str) -> tuple[str, int]:
    import numpy as np
    import soundfile as sf

    model = _get_whisper(model_name)
    audio, _ = sf.read(path, dtype="float32", always_2d=False)
    t0 = time.monotonic()
    segs, _ = model.transcribe(
        np.asarray(audio, dtype=np.float32), language="en", beam_size=1, vad_filter=False
    )
    text = " ".join(s.text.strip() for s in segs).strip()
    return text, int((time.monotonic() - t0) * 1000)


# ---------------------------------------------------------------------------
# TTS timing
# ---------------------------------------------------------------------------


def _audio_duration_ms(path: str, backend_name: str) -> int:
    try:
        if backend_name in ("kittentts", "pyttsx3"):
            with wave.open(path, "rb") as wf:
                return int(wf.getnframes() / wf.getframerate() * 1000)
        else:  # edge-tts → MP3
            import soundfile as sf

            return int(sf.info(path).duration * 1000)
    except Exception:
        return 0


def _synth_and_time(tts_manager, text: str) -> tuple[int, int]:
    """Synthesize text to a temp file and return (tts_ms, tts_audio_duration_ms)."""
    suffix = ".mp3" if tts_manager.backend_name == "edge-tts" else ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        tmp = f.name
    try:
        t0 = time.monotonic()
        tts_manager.save_to_file(text, tmp)
        tts_ms = int((time.monotonic() - t0) * 1000)
        dur_ms = _audio_duration_ms(tmp, tts_manager.backend_name)
        return tts_ms, dur_ms
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Conversation loading
# ---------------------------------------------------------------------------


def _load_conversations(conv_dir: str, only: list[str] | None) -> list[dict]:
    convs = []
    for p in sorted(Path(conv_dir).glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"  [skip] {p.name}: {exc}", file=sys.stderr)
            continue
        if only and data.get("id") not in only:
            continue
        convs.append(data)
    return convs


# ---------------------------------------------------------------------------
# Turn runner
# ---------------------------------------------------------------------------


def _run_turns(
    conv: dict,
    client,
    use_tools: bool,
    tts_manager,
    use_tts: bool,
    stt_model: str,
    turn_calls: list[str],
) -> dict:
    messages: list[dict] = []
    turn_results = []
    all_passed = True

    for turn_def in conv["turns"]:
        turn_num = turn_def["turn"]
        turn_calls.clear()

        # --- STT or text passthrough ---
        audio_path = turn_def.get("audio")
        if audio_path and Path(audio_path).exists():
            print(f"    STT from audio: {audio_path}")
            transcript, stt_ms = _transcribe(audio_path, stt_model)
            stt_source = "audio"
        else:
            transcript = turn_def["text"]
            stt_ms = 0
            stt_source = "text"

        print(f"    Turn {turn_num} | [{stt_source} {stt_ms}ms] {transcript!r}")

        messages.append({"role": "user", "content": transcript})

        # --- LLM ---
        t0 = time.monotonic()
        try:
            if use_tools:
                response = client.chat_with_tools(messages)
            else:
                raw = client.chat_completion(messages)
                choices = raw.get("choices") or []
                response = choices[0]["message"]["content"] if choices else ""
        except Exception as exc:
            print(f"    LLM error: {exc}", file=sys.stderr)
            response = ""
        llm_ms = int((time.monotonic() - t0) * 1000)
        print(f"    LLM {llm_ms}ms: {response[:100]!r}")
        if turn_calls:
            print(f"    Tools: {list(turn_calls)}")

        messages.append({"role": "assistant", "content": response})

        # --- TTS ---
        tts_ms = 0
        tts_audio_duration_ms = 0
        if use_tts and tts_manager and response:
            tts_ms, tts_audio_duration_ms = _synth_and_time(tts_manager, response)
            print(f"    TTS {tts_ms}ms (audio {tts_audio_duration_ms}ms)")

        round_trip_ms = stt_ms + llm_ms + tts_ms

        # --- Score ---
        expects = turn_def.get("expects", {})
        expected_contains = expects.get("answer_contains", [])
        expected_tools = expects.get("tool_calls", [])

        answer_ok = _fuzzy_match(response, expected_contains) if expected_contains else None
        if expected_tools:
            tool_ok = all(t in turn_calls for t in expected_tools)
        else:
            tool_ok = None

        if answer_ok is False or tool_ok is False:
            all_passed = False
        print(f"    answer_ok={answer_ok}  tool_ok={tool_ok}  round_trip={round_trip_ms}ms")

        turn_results.append({
            "turn": turn_num,
            "transcript": transcript,
            "stt_ms": stt_ms,
            "stt_source": stt_source,
            "llm_response": response,
            "llm_ms": llm_ms,
            "tts_ms": tts_ms,
            "tts_audio_duration_ms": tts_audio_duration_ms,
            "round_trip_ms": round_trip_ms,
            "tool_calls_made": list(turn_calls),
            "answer_ok": answer_ok,
            "tool_ok": tool_ok,
        })

    return {
        "id": conv["id"],
        "name": conv.get("name", conv["id"]),
        "all_turns_passed": all_passed,
        "turns": turn_results,
    }


# ---------------------------------------------------------------------------
# Per-conversation runner with tool state isolation
# ---------------------------------------------------------------------------


def run_conversation(
    conv: dict,
    client,
    use_tools: bool,
    tts_manager,
    use_tts: bool,
    stt_model: str,
    turn_calls: list[str],
    state_root: Path,
) -> dict:
    from talkbot.tools import reset_runtime_state

    conv_state_dir = state_root / conv["id"]
    conv_state_dir.mkdir(parents=True, exist_ok=True)

    old = os.environ.get("TALKBOT_DATA_DIR")
    os.environ["TALKBOT_DATA_DIR"] = str(conv_state_dir)
    try:
        reset_runtime_state(clear_persistent=True)
        return _run_turns(conv, client, use_tools, tts_manager, use_tts, stt_model, turn_calls)
    finally:
        if old is None:
            os.environ.pop("TALKBOT_DATA_DIR", None)
        else:
            os.environ["TALKBOT_DATA_DIR"] = old


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def _compute_summary(conv_results: list[dict]) -> dict:
    all_turns = [t for c in conv_results for t in c["turns"]]

    def avg(lst: list[int]) -> int:
        return int(sum(lst) / len(lst)) if lst else 0

    def p95(lst: list[int]) -> int:
        if not lst:
            return 0
        return sorted(lst)[max(0, int(len(lst) * 0.95) - 1)]

    round_trips = [t["round_trip_ms"] for t in all_turns]
    stt_times = [t["stt_ms"] for t in all_turns]
    llm_times = [t["llm_ms"] for t in all_turns]
    tts_times = [t["tts_ms"] for t in all_turns]

    turns_answer_ok = sum(1 for t in all_turns if t["answer_ok"] is True)
    turns_answer_total = sum(1 for t in all_turns if t["answer_ok"] is not None)
    turns_tool_ok = sum(1 for t in all_turns if t["tool_ok"] is True)
    turns_tool_total = sum(1 for t in all_turns if t["tool_ok"] is not None)
    convs_ok = sum(1 for c in conv_results if c["all_turns_passed"])

    coherence_denom = turns_answer_total + turns_tool_total
    coherence_score = (
        round((turns_answer_ok + turns_tool_ok) / coherence_denom, 4)
        if coherence_denom
        else 0.0
    )

    return {
        "total_conversations": len(conv_results),
        "total_turns": len(all_turns),
        "avg_round_trip_ms": avg(round_trips),
        "p95_round_trip_ms": p95(round_trips),
        "avg_stt_ms": avg(stt_times),
        "avg_llm_ms": avg(llm_times),
        "avg_tts_ms": avg(tts_times),
        "conversations_all_turns_ok": convs_ok,
        "turns_answer_ok": turns_answer_ok,
        "turns_answer_total": turns_answer_total,
        "turns_tool_ok": turns_tool_ok,
        "turns_tool_total": turns_tool_total,
        "coherence_score": coherence_score,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    only = [x.strip() for x in args.only.split(",")] if args.only else None
    conversations = _load_conversations(args.conversations, only)
    if not conversations:
        print(f"No conversation scripts found in {args.conversations}", file=sys.stderr)
        return 1
    print(f"Loaded {len(conversations)} conversation(s)")

    # TTS init (once, shared across all conversations)
    tts_manager = None
    use_tts = not args.no_tts
    if use_tts:
        from talkbot.tts import TTSManager

        try:
            tts_manager = TTSManager(voice_id=args.tts_voice, backend=args.tts_backend)
            print(f"TTS backend: {tts_manager.backend_name}")
        except Exception as exc:
            print(f"Warning: TTS init failed ({exc}), disabling TTS.", file=sys.stderr)
            use_tts = False

    # LLM client
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY", "")
    from talkbot.llm import create_llm_client, supports_tools
    from talkbot.tools import register_all_tools

    state_root = Path("benchmarks/conversation_results/.state")
    conv_results = []

    with create_llm_client(provider=args.provider, model=args.model, api_key=api_key) as client:
        use_tools = not args.no_tools and supports_tools(client)

        # Set up tool tracking once for the entire run; turn_calls is cleared per turn
        turn_calls: list[str] = []
        _make_tracking_register(client, turn_calls)
        register_all_tools(client)

        for conv in conversations:
            print(f"\n[{conv['id']}] {conv.get('name', '')}")
            result = run_conversation(
                conv=conv,
                client=client,
                use_tools=use_tools,
                tts_manager=tts_manager,
                use_tts=use_tts,
                stt_model=args.stt_model,
                turn_calls=turn_calls,
                state_root=state_root,
            )
            conv_results.append(result)

    # Summary
    summary = _compute_summary(conv_results)
    print(f"\n{'='*60}")
    print(f"Conversations: {summary['total_conversations']}  Turns: {summary['total_turns']}")
    print(
        f"  avg_round_trip_ms : {summary['avg_round_trip_ms']}  "
        f"p95: {summary['p95_round_trip_ms']}"
    )
    print(
        f"  avg_stt_ms={summary['avg_stt_ms']}  "
        f"avg_llm_ms={summary['avg_llm_ms']}  "
        f"avg_tts_ms={summary['avg_tts_ms']}"
    )
    print(
        f"  answer_ok: {summary['turns_answer_ok']}/{summary['turns_answer_total']}  "
        f"tool_ok: {summary['turns_tool_ok']}/{summary['turns_tool_total']}  "
        f"coherence: {summary['coherence_score']}"
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = args.model.replace("/", "_")
    out_path = (
        Path(args.output)
        if args.output
        else Path("benchmarks/conversation_results") / f"{ts}__{model_slug}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "schema_version": "2026.conv.v1",
                "model": args.model,
                "provider": args.provider,
                "stt_model": args.stt_model,
                "tts_backend": tts_manager.backend_name if tts_manager else None,
                "use_tts": use_tts,
                "ran_at": _now_iso(),
                "summary": summary,
                "conversations": conv_results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
