#!/usr/bin/env python3
"""Upload voice benchmark dataset to a HuggingFace dataset repo.

Creates the repo if it doesn't exist (private by default).
Uploads WAV files from benchmarks/voice_dataset/raw/ plus the two manifest JSONs.

Usage:
    uv run python scripts/upload_voice_dataset.py
    uv run python scripts/upload_voice_dataset.py --repo ricklon/talkbot-voice-benchmark
    uv run python scripts/upload_voice_dataset.py --public    # make repo public
    uv run python scripts/upload_voice_dataset.py --dry-run   # list files, no upload

Requirements:
    HF_TOKEN must be set in .env or the environment.
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
    """Load .env if python-dotenv is available."""
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
                        help="Voice dataset directory (default: benchmarks/voice_dataset)")
    parser.add_argument("--public", action="store_true",
                        help="Make the dataset repo public (default: private)")
    parser.add_argument("--dry-run", action="store_true",
                        help="List files that would be uploaded without uploading")
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
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        print("ERROR: HF_TOKEN not set in .env or environment.", file=sys.stderr)
        return 1

    # --- Collect files ---
    voice_dir = repo_root / args.voice_dir
    raw_dir = voice_dir / "raw"

    files_to_upload: list[tuple[Path, str]] = []  # (local_path, repo_path)

    # Manifests
    for name in ("manifest.json", "pipeline_manifest.json"):
        p = voice_dir / name
        if p.exists():
            files_to_upload.append((p, name))
        else:
            print(f"  [warn] manifest not found, skipping: {p}", file=sys.stderr)

    # WAV files
    if raw_dir.exists():
        wavs = sorted(raw_dir.glob("*.wav"))
        for wav in wavs:
            files_to_upload.append((wav, f"raw/{wav.name}"))
    else:
        print(f"  [warn] raw/ directory not found: {raw_dir}", file=sys.stderr)

    if not files_to_upload:
        print("ERROR: No files found to upload.", file=sys.stderr)
        return 1

    total_bytes = sum(p.stat().st_size for p, _ in files_to_upload)
    print(f"Dataset repo : {repo_id}")
    print(f"Visibility   : {'public' if args.public else 'private'}")
    print(f"Files        : {len(files_to_upload)} ({total_bytes / 1024:.1f} KB)")
    for local, repo_path in files_to_upload:
        size_kb = local.stat().st_size / 1024
        print(f"  {repo_path:<55} {size_kb:6.1f} KB")

    if args.dry_run:
        print("\n[dry-run] No files uploaded.")
        return 0

    # --- Upload ---
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("ERROR: huggingface_hub not installed. Run: uv add huggingface_hub", file=sys.stderr)
        return 1

    api = HfApi(token=token)

    # Create repo if needed
    print(f"\nCreating/verifying repo: {repo_id} ...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            private=not args.public,
            exist_ok=True,
        )
    except Exception as exc:
        print(f"ERROR creating repo: {exc}", file=sys.stderr)
        return 1

    # Upload files
    print("Uploading files ...")
    errors = 0
    for local, repo_path in files_to_upload:
        try:
            api.upload_file(
                path_or_fileobj=str(local),
                path_in_repo=repo_path,
                repo_id=repo_id,
                repo_type="dataset",
            )
            print(f"  [OK] {repo_path}")
        except Exception as exc:
            print(f"  [ERR] {repo_path}: {exc}", file=sys.stderr)
            errors += 1

    if errors:
        print(f"\n{errors} file(s) failed to upload.", file=sys.stderr)
        return 1

    print(f"\nDone. View at: https://huggingface.co/datasets/{repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
