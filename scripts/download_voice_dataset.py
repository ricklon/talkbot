#!/usr/bin/env python3
"""Download voice benchmark dataset from a HuggingFace dataset repo.

Downloads WAV files and manifests into benchmarks/voice_dataset/.
Skips files that already exist locally unless --force is passed.

Usage:
    uv run python scripts/download_voice_dataset.py
    uv run python scripts/download_voice_dataset.py --repo ricklon/talkbot-voice-benchmark
    uv run python scripts/download_voice_dataset.py --force   # re-download all

Requirements:
    HF_TOKEN must be set in .env or the environment (needed for private repos).
    HF_DATASET_REPO may be set in .env to avoid passing --repo each time.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return here.parent


def _load_env(repo_root: Path) -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(repo_root / ".env")
    except ImportError:
        pass


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=None,
                        help="HuggingFace dataset repo (e.g. username/talkbot-voice-benchmark). "
                             "Falls back to HF_DATASET_REPO env var.")
    parser.add_argument("--voice-dir", default="benchmarks/voice_dataset",
                        help="Local destination directory (default: benchmarks/voice_dataset)")
    parser.add_argument("--force", action="store_true",
                        help="Re-download files even if they already exist locally")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = _repo_root()
    _load_env(repo_root)

    # --- Resolve repo name ---
    repo_id = args.repo or os.environ.get("HF_DATASET_REPO", "").strip()
    if not repo_id:
        print(
            "ERROR: No dataset repo specified.\n"
            "  Pass --repo username/dataset-name  OR\n"
            "  set HF_DATASET_REPO=username/dataset-name in .env",
            file=sys.stderr,
        )
        return 1

    # --- Resolve token ---
    token = os.environ.get("HF_TOKEN", "").strip() or None

    # --- Import HF hub ---
    try:
        from huggingface_hub import HfApi, hf_hub_download
    except ImportError:
        print("ERROR: huggingface_hub not installed. Run: uv add huggingface_hub", file=sys.stderr)
        return 1

    api = HfApi(token=token)

    # --- List repo files ---
    print(f"Fetching file list from {repo_id} ...")
    try:
        repo_files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
        repo_files = list(repo_files)
    except Exception as exc:
        print(f"ERROR: could not list repo files: {exc}", file=sys.stderr)
        if token is None:
            print("  (No HF_TOKEN found — required for private repos)", file=sys.stderr)
        return 1

    if not repo_files:
        print("No files found in the dataset repo.", file=sys.stderr)
        return 1

    # Filter to WAVs and manifests only (skip .gitattributes etc.)
    wanted = [
        f for f in repo_files
        if f.endswith(".wav") or f.endswith(".json")
    ]
    print(f"Found {len(wanted)} file(s) in repo (of {len(repo_files)} total)")

    voice_dir = repo_root / args.voice_dir
    raw_dir = voice_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # --- Download ---
    skipped = downloaded = errors = 0
    for repo_path in sorted(wanted):
        # Map repo path → local path
        if repo_path.startswith("raw/"):
            local_path = raw_dir / Path(repo_path).name
        else:
            local_path = voice_dir / repo_path

        if local_path.exists() and not args.force:
            skipped += 1
            continue

        try:
            tmp = hf_hub_download(
                repo_id=repo_id,
                filename=repo_path,
                repo_type="dataset",
                token=token,
            )
            # Copy from HF cache to our local path
            import shutil
            shutil.copy2(tmp, local_path)
            print(f"  [OK] {repo_path} → {local_path.relative_to(repo_root)}")
            downloaded += 1
        except Exception as exc:
            print(f"  [ERR] {repo_path}: {exc}", file=sys.stderr)
            errors += 1

    print(f"\nDownloaded: {downloaded}  Skipped (exist): {skipped}  Errors: {errors}")
    if skipped and not args.force:
        print("  (use --force to re-download existing files)")

    if errors:
        return 1

    wav_count = len(list(raw_dir.glob("*.wav")))
    print(f"\nVoice dataset ready: {raw_dir} ({wav_count} WAV files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
