#!/usr/bin/env python3
"""Record spoken benchmark prompts into a reproducible dataset manifest."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


try:
    import numpy as np
    import sounddevice as sd
    import soundfile as sf
except Exception as exc:  # pragma: no cover - runtime dependency
    raise SystemExit(
        "Missing recording dependencies. Install with: uv sync --extra voice"
    ) from exc


@dataclass
class PromptItem:
    prompt_id: str
    text: str
    category: str
    notes: str
    expected_variants: list[str]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prompts",
        default="benchmarks/voice_prompts.template.json",
        help="Path to prompt JSON file",
    )
    parser.add_argument(
        "--output-dir",
        default="benchmarks/voice_dataset/raw",
        help="Directory for recorded WAV files",
    )
    parser.add_argument(
        "--manifest",
        default="benchmarks/voice_dataset/manifest.json",
        help="Path to output manifest JSON file",
    )
    parser.add_argument(
        "--speaker-id",
        required=True,
        help="Speaker identifier (e.g., speaker_a)",
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="Optional session id (default: UTC timestamp)",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Recording sample rate (default: 16000)",
    )
    parser.add_argument(
        "--channels",
        type=int,
        default=1,
        help="Audio channel count (default: 1)",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Input device name or index (optional)",
    )
    parser.add_argument(
        "--takes",
        type=int,
        default=1,
        help="Number of takes per prompt (default: 1)",
    )
    parser.add_argument(
        "--min-seconds",
        type=float,
        default=0.5,
        help="Minimum accepted recording duration (default: 0.5)",
    )
    parser.add_argument(
        "--max-seconds",
        type=float,
        default=20.0,
        help="Hard stop per take in seconds (default: 20.0)",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Print available audio devices and exit",
    )
    parser.add_argument(
        "--only",
        default=None,
        help="Comma-separated prompt IDs to record (e.g. date_iso,time_24h). "
             "Removes existing manifest entries for those prompts before recording.",
    )
    return parser.parse_args(argv)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_id(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value.strip())
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned or "prompt"


def _load_prompts(path: Path) -> list[PromptItem]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Prompt file must be a JSON list.")
    prompts: list[PromptItem] = []
    for index, raw in enumerate(payload, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Prompt index {index} must be an object.")
        prompt_id = _safe_id(str(raw.get("id") or f"prompt_{index}"))
        text = str(raw.get("text") or "").strip()
        if not text:
            raise ValueError(f"Prompt '{prompt_id}' missing text.")
        category = str(raw.get("category") or "general").strip() or "general"
        notes = str(raw.get("notes") or "").strip()
        variants = raw.get("expected_variants") or []
        if not isinstance(variants, list):
            variants = []
        expected_variants = [str(v).strip() for v in variants if str(v).strip()]
        prompts.append(
            PromptItem(
                prompt_id=prompt_id,
                text=text,
                category=category,
                notes=notes,
                expected_variants=expected_variants,
            )
        )
    if not prompts:
        raise ValueError("Prompt file is empty.")
    return prompts


def _choose_input_device(device_arg: str | None) -> int | str | None:
    if not device_arg:
        return None
    try:
        return int(device_arg)
    except ValueError:
        return device_arg


def _record_take(
    *,
    sample_rate: int,
    channels: int,
    device: int | str | None,
    max_seconds: float,
) -> np.ndarray:
    chunks: list[np.ndarray] = []
    started = time.monotonic()

    def _callback(indata, frames, callback_time, status):
        del frames, callback_time
        if status:
            print(f"[warn] {status}", file=sys.stderr)
        chunks.append(np.copy(indata))
        if time.monotonic() - started >= max_seconds:
            raise sd.CallbackStop()

    with sd.InputStream(
        samplerate=sample_rate,
        channels=channels,
        dtype="float32",
        callback=_callback,
        device=device,
    ):
        input("Recording... press ENTER to stop early.\n")

    if not chunks:
        return np.empty((0, channels), dtype=np.float32)
    return np.concatenate(chunks, axis=0)


def _load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "2026.voice.v1", "entries": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {"schema_version": "2026.voice.v1", "entries": []}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        payload["entries"] = []
    return payload


def _save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if args.list_devices:
        print(sd.query_devices())
        return 0

    prompts_path = Path(args.prompts)
    output_dir = Path(args.output_dir)
    manifest_path = Path(args.manifest)
    prompts = _load_prompts(prompts_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest(manifest_path)

    # Filter prompts if --only specified, and purge old entries from manifest
    only_ids: set[str] | None = None
    if args.only:
        only_ids = {_safe_id(s.strip()) for s in args.only.split(",") if s.strip()}
        prompts = [p for p in prompts if p.prompt_id in only_ids]
        if not prompts:
            print(f"No prompts matched --only ids: {only_ids}", file=sys.stderr)
            return 1
        # Remove existing manifest entries for these prompts
        before = len(manifest.get("entries", []))
        kept = []
        for e in manifest.get("entries", []):
            if e.get("prompt_id") in only_ids:
                p = Path(e.get("audio_path", ""))
                if p.exists():
                    p.unlink()
            else:
                kept.append(e)
        manifest["entries"] = kept
        purged = before - len(kept)
        if purged:
            print(f"Purged {purged} existing entries for: {', '.join(sorted(only_ids))}")

    session_id = args.session_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    device = _choose_input_device(args.device)
    takes = max(1, int(args.takes))

    print(f"Loaded {len(prompts)} prompts from {prompts_path}")
    print(f"Speaker: {args.speaker_id}")
    print(f"Session: {session_id}")
    print(f"Output WAV dir: {output_dir}")
    print(f"Manifest: {manifest_path}")
    print("")
    print("Commands: [ENTER]=record, s=skip, q=quit")

    recorded = 0
    skipped = 0
    for idx, prompt in enumerate(prompts, start=1):
        for take in range(1, takes + 1):
            print("")
            print(f"[{idx}/{len(prompts)}] {prompt.prompt_id} (category={prompt.category}) take {take}/{takes}")
            print(f"Prompt: {prompt.text}")
            if prompt.notes:
                print(f"Notes: {prompt.notes}")
            choice = input("Action: ").strip().lower()
            if choice == "q":
                print("Stopping early.")
                _save_manifest(manifest_path, manifest)
                print(f"Saved manifest with {len(manifest.get('entries', []))} entries.")
                return 0
            if choice == "s":
                skipped += 1
                continue

            input("Press ENTER to start recording.")
            audio = _record_take(
                sample_rate=args.sample_rate,
                channels=args.channels,
                device=device,
                max_seconds=float(args.max_seconds),
            )
            duration = float(audio.shape[0]) / float(args.sample_rate) if audio.size else 0.0
            if duration < float(args.min_seconds):
                print(
                    f"[skip] too short ({duration:.2f}s < {args.min_seconds:.2f}s). "
                    "Retry this take."
                )
                continue

            filename = (
                f"{session_id}__{args.speaker_id}__{prompt.prompt_id}__take{take:02d}.wav"
            )
            wav_path = output_dir / filename
            sf.write(wav_path, audio, samplerate=args.sample_rate, subtype="PCM_16")

            entry = {
                "id": f"{prompt.prompt_id}__take{take:02d}",
                "prompt_id": prompt.prompt_id,
                "text": prompt.text,
                "category": prompt.category,
                "notes": prompt.notes,
                "expected_variants": prompt.expected_variants,
                "speaker_id": args.speaker_id,
                "session_id": session_id,
                "audio_path": str(wav_path.as_posix()),
                "sample_rate_hz": int(args.sample_rate),
                "channels": int(args.channels),
                "duration_s": round(duration, 3),
                "recorded_at": _now_iso(),
            }
            manifest.setdefault("entries", []).append(entry)
            _save_manifest(manifest_path, manifest)
            recorded += 1
            print(f"[ok] saved {wav_path} ({duration:.2f}s)")

    print("")
    print(
        f"Done. Recorded {recorded} takes, skipped {skipped}. "
        f"Manifest entries: {len(manifest.get('entries', []))}."
    )
    print(f"Manifest saved to: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

