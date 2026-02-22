#!/usr/bin/env bash
set -euo pipefail

DEFAULT_URL="https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q8_0.gguf"
DEFAULT_OUTPUT="models/default.gguf"

url="$DEFAULT_URL"
output="$DEFAULT_OUTPUT"
force="0"

usage() {
  cat <<'EOF'
Download a default local GGUF model for TalkBot.

Usage:
  ./scripts/download-model.sh [--output PATH] [--url URL] [--force]

Options:
  --output PATH   Destination file path (default: models/default.gguf)
  --url URL       Direct GGUF URL (default: official Qwen3-1.7B Q8_0)
  --force         Overwrite existing destination file
  -h, --help      Show help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      output="${2:-}"
      shift 2
      ;;
    --url)
      url="${2:-}"
      shift 2
      ;;
    --force)
      force="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$output" || -z "$url" ]]; then
  echo "Error: output and url must be non-empty." >&2
  exit 1
fi

mkdir -p "$(dirname "$output")"

if [[ -s "$output" && "$force" != "1" ]]; then
  echo "Model already exists at $output"
  echo "Use --force to overwrite."
  exit 0
fi

tmp_file="${output}.part"
rm -f "$tmp_file"

echo "Downloading GGUF model..."
echo "URL: $url"
echo "OUT: $output"

if command -v curl >/dev/null 2>&1; then
  curl_args=(
    -L
    --fail
    --retry 5
    --retry-delay 2
    --connect-timeout 30
    -o "$tmp_file"
    "$url"
  )
  if [[ -n "${HF_TOKEN:-}" ]]; then
    curl_args=(-H "Authorization: Bearer ${HF_TOKEN}" "${curl_args[@]}")
  fi
  curl "${curl_args[@]}"
elif command -v wget >/dev/null 2>&1; then
  if [[ -n "${HF_TOKEN:-}" ]]; then
    wget --header="Authorization: Bearer ${HF_TOKEN}" -O "$tmp_file" "$url"
  else
    wget -O "$tmp_file" "$url"
  fi
else
  echo "Error: neither curl nor wget is installed." >&2
  exit 1
fi

mv "$tmp_file" "$output"
echo "Model saved to $output"
echo "Set TALKBOT_LOCAL_MODEL_PATH=$output (or keep .env.example default)."

