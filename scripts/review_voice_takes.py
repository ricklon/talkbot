#!/usr/bin/env python3
"""Review recorded voice takes: listen and keep or delete."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import sounddevice as sd
    import soundfile as sf
except Exception as exc:
    raise SystemExit("Missing deps. Run: uv sync --extra voice") from exc


def play(path: Path) -> None:
    data, sr = sf.read(str(path), dtype="float32")
    sd.play(data, sr)
    sd.wait()


def main() -> None:
    manifest_path = Path("benchmarks/voice_dataset/manifest.json")
    m = json.loads(manifest_path.read_text())
    entries = m["entries"]

    print("Commands: p=play, d=delete, k=keep, q=quit\n")
    for i, e in enumerate(entries, 1):
        print(f"{i:2}. {e['id']:40s} {e['duration_s']}s")

    to_delete: set[int] = set()

    while True:
        raw = input("\nEntry number (or q): ").strip().lower()
        if raw == "q":
            break
        try:
            n = int(raw)
            if not 1 <= n <= len(entries):
                print("Out of range.")
                continue
        except ValueError:
            print("Enter a number.")
            continue

        e = entries[n - 1]
        audio_path = Path(e["audio_path"])
        status = "[MARKED FOR DELETE]" if n in to_delete else ""
        print(f"\n{n}. {e['id']} ({e['duration_s']}s) {status}")
        print(f"   Text: {e['text']}")

        cmd = input("  p=play  d=delete  k=keep  (enter=skip): ").strip().lower()
        if cmd == "p":
            if audio_path.exists():
                print("  Playing...")
                play(audio_path)
            else:
                print(f"  File not found: {audio_path}")
            cmd = input("  d=delete  k=keep  (enter=skip): ").strip().lower()

        if cmd == "d":
            to_delete.add(n)
            print(f"  Marked for delete: {e['id']}")
        elif cmd == "k":
            to_delete.discard(n)
            print(f"  Keeping: {e['id']}")

    if not to_delete:
        print("\nNothing deleted.")
        return

    print(f"\nDeleting {len(to_delete)} entries:")
    new_entries = []
    for i, e in enumerate(entries, 1):
        if i in to_delete:
            p = Path(e["audio_path"])
            if p.exists():
                p.unlink()
            print(f"  deleted {e['id']}")
        else:
            new_entries.append(e)

    m["entries"] = new_entries
    manifest_path.write_text(json.dumps(m, indent=2))
    print(f"Manifest updated: {len(new_entries)} entries remain.")


if __name__ == "__main__":
    main()
