#!/usr/bin/env python3
"""Download Ministral-3B-Instruct-2512 GGUF and import it into Ollama.

Steps performed:
  1. Download Ministral-3-3B-Instruct-2512-Q4_K_M.gguf from HuggingFace
  2. Import the GGUF into Ollama as 'ministral-3b'
  3. Optionally install llama-cpp-python for the 'local' provider

Usage:
  uv run python scripts/setup_ministral.py
  uv run python scripts/setup_ministral.py --skip-ollama   # download only
  uv run python scripts/setup_ministral.py --skip-download # ollama import only
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

GGUF_URL = (
    "https://huggingface.co/lmstudio-community/Ministral-3-3B-Instruct-2512-GGUF"
    "/resolve/main/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"
)
GGUF_OUTPUT = "models/ministral-3b-2512-q4_k_m.gguf"
OLLAMA_MODEL_NAME = "ministral-3b"

MODELFILE_TEMPLATE = """\
FROM {gguf_path}
PARAMETER temperature 0.7
PARAMETER num_ctx 4096
"""


def download_gguf(url: str, output_path: str, force: bool) -> bool:
    output = Path(output_path)
    if output.exists() and not force:
        print(f"  Already exists: {output_path}")
        return True

    output.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = output.with_suffix(".part")

    print(f"  Downloading: {url}")
    print(f"  Destination: {output_path}")
    print("  This is ~2.1 GB — may take a few minutes...")

    req = urllib.request.Request(url)
    req.add_header("User-Agent", "TalkBot-Downloader/1.0")
    if hf_token := os.getenv("HF_TOKEN"):
        req.add_header("Authorization", f"Bearer {hf_token}")

    try:
        with urllib.request.urlopen(req) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk = 1024 * 1024  # 1 MB
            with open(tmp_file, "wb") as out_file:
                while True:
                    block = response.read(chunk)
                    if not block:
                        break
                    out_file.write(block)
                    downloaded += len(block)
                    if total:
                        pct = downloaded / total * 100
                        mb = downloaded / 1e6
                        print(f"\r  {pct:.1f}% ({mb:.0f} MB)", end="", flush=True)
            print()
        tmp_file.rename(output)
        print(f"  Saved: {output_path}")
        return True
    except Exception as e:
        print(f"\n  Error downloading: {e}", file=sys.stderr)
        if tmp_file.exists():
            tmp_file.unlink()
        return False


def ollama_import(gguf_path: str, model_name: str) -> bool:
    if not shutil.which("ollama"):
        print("  ERROR: 'ollama' not found in PATH.", file=sys.stderr)
        return False

    gguf_abs = str(Path(gguf_path).resolve())
    modelfile_content = MODELFILE_TEMPLATE.format(gguf_path=gguf_abs)

    with tempfile.NamedTemporaryFile(mode="w", suffix="Modelfile", delete=False) as f:
        f.write(modelfile_content)
        modelfile_path = f.name

    print(f"  Modelfile written to: {modelfile_path}")
    print(f"  Running: ollama create {model_name} -f {modelfile_path}")

    try:
        result = subprocess.run(
            ["ollama", "create", model_name, "-f", modelfile_path],
            capture_output=False,
        )
        if result.returncode != 0:
            print(f"  ERROR: ollama create exited with code {result.returncode}", file=sys.stderr)
            return False
        print(f"  Ollama model '{model_name}' created successfully.")
        return True
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return False
    finally:
        Path(modelfile_path).unlink(missing_ok=True)


def check_ollama_model(model_name: str) -> bool:
    """Return True if model is already registered in Ollama."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        return model_name in result.stdout
    except Exception:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up Ministral-3B for local and Ollama benchmarking.")
    parser.add_argument("--output", default=GGUF_OUTPUT, help=f"GGUF destination (default: {GGUF_OUTPUT})")
    parser.add_argument("--url", default=GGUF_URL, help="GGUF download URL")
    parser.add_argument("--ollama-name", default=OLLAMA_MODEL_NAME, help=f"Ollama model name (default: {OLLAMA_MODEL_NAME})")
    parser.add_argument("--skip-download", action="store_true", help="Skip GGUF download (use existing file)")
    parser.add_argument("--skip-ollama", action="store_true", help="Skip Ollama import")
    parser.add_argument("--force", action="store_true", help="Re-download even if file exists")
    args = parser.parse_args()

    ok = True

    # Step 1: Download
    print("\n[1/2] Download GGUF")
    if args.skip_download:
        print("  Skipped.")
    else:
        ok = download_gguf(args.url, args.output, args.force) and ok

    # Step 2: Import into Ollama
    print("\n[2/2] Import into Ollama")
    if args.skip_ollama:
        print("  Skipped.")
    elif not Path(args.output).exists():
        print(f"  Skipped — GGUF not found at {args.output}.", file=sys.stderr)
        ok = False
    elif check_ollama_model(args.ollama_name) and not args.force:
        print(f"  Model '{args.ollama_name}' already in Ollama. Use --force to reimport.")
    else:
        ok = ollama_import(args.output, args.ollama_name) and ok

    # Summary
    print("\n--- Summary ---")
    gguf_exists = Path(args.output).exists()
    ollama_ready = check_ollama_model(args.ollama_name)
    print(f"  GGUF file:        {'OK' if gguf_exists else 'MISSING'} ({args.output})")
    print(f"  Ollama model:     {'OK' if ollama_ready else 'NOT IMPORTED'} ({args.ollama_name})")
    print()

    if gguf_exists:
        print("  Ready for local provider:")
        print(f"    uv run talkbot --provider local --local-model-path {args.output} chat 'hello' --no-speak")
        print("    Or set TALKBOT_LOCAL_MODEL_PATH in .env (requires: uv sync --extra local)")

    if ollama_ready:
        print(f"\n  Ready for local_server (Ollama) provider:")
        print(f"    uv run talkbot --provider local_server --model {args.ollama_name} chat 'hello' --no-speak")

    print("\n  Run the cross-provider benchmark:")
    print("    uv run python scripts/benchmark_conversations.py \\")
    print("      --matrix benchmarks/model_matrix.ministral_cross_provider.json \\")
    print("      --run-name ministral-cross-provider")

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
