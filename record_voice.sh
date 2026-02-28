#!/usr/bin/env bash
set -euo pipefail

SPEAKER="${1:-ricklon}"
DEVICE="${2:-3}"
TAKES="${3:-2}"

uv run -- python scripts/record_voice_benchmark.py \
  --prompts benchmarks/voice_prompts.template.json \
  --output-dir benchmarks/voice_dataset/raw \
  --manifest benchmarks/voice_dataset/manifest.json \
  --speaker-id "$SPEAKER" \
  --device "$DEVICE" \
  --takes "$TAKES"
