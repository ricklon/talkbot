#!/usr/bin/env python3
"""Download a default local GGUF model for TalkBot."""

import argparse
import os
import shutil
import sys
import urllib.request
from pathlib import Path

DEFAULT_URL = "https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q4_K_M.gguf"
DEFAULT_OUTPUT = "models/qwen3-1.7b-q4_k_m.gguf"

def download_model(url: str, output_path: str, force: bool) -> None:
    output = Path(output_path)
    if output.exists() and not force:
        print(f"Model already exists at {output_path}")
        print("Use --force to overwrite.")
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = output.with_suffix(".part")
    
    print("Downloading GGUF model...")
    print(f"URL: {url}")
    print(f"OUT: {output_path}")

    req = urllib.request.Request(url)
    # Be conversational with servers like huggingface
    req.add_header('User-Agent', 'TalkBot-Downloader/1.0')
    if hf_token := os.getenv("HF_TOKEN"):
        req.add_header("Authorization", f"Bearer {hf_token}")

    try:
        with urllib.request.urlopen(req) as response:
            with open(tmp_file, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        
        tmp_file.rename(output)
        print(f"Model saved to {output}")
        print(f"Set TALKBOT_LOCAL_MODEL_PATH={output} (or keep .env.example default).")
    
    except Exception as e:
        print(f"Error downloading: {e}", file=sys.stderr)
        if tmp_file.exists():
            tmp_file.unlink()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download a default local GGUF model for TalkBot.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Destination file path (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"Direct GGUF URL (default: {DEFAULT_URL})")
    parser.add_argument("--force", action="store_true", help="Overwrite existing destination file")
    
    args = parser.parse_args()
    download_model(args.url, args.output, args.force)

if __name__ == "__main__":
    main()
