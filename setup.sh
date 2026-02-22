#!/usr/bin/env bash
set -euo pipefail

# Quick install/reinstall for the global talkbot and talkbot-gui tools
# with voice extras enabled.
download_model=0
if [[ $# -gt 0 ]]; then
  case "${1:-}" in
    --download-model)
      download_model=1
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./setup.sh [--download-model]

Options:
  --download-model   Install tool + voice deps, then download default GGUF
  -h, --help         Show this help
EOF
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Run ./setup.sh --help" >&2
      exit 1
      ;;
  esac
fi

UV_SKIP_WHEEL_FILENAME_CHECK=1 uv tool install --reinstall \
  --python /usr/bin/python3.12 . \
  --with llama-cpp-python \
  --with faster-whisper \
  --with silero-vad \
  --with sounddevice \
  --with soundfile

echo "Installed talkbot and talkbot-gui with voice extras."
if [[ "$download_model" == "1" ]]; then
  ./scripts/download-model.sh
else
  echo "Place your GGUF at ./models/default.gguf (or set TALKBOT_LOCAL_MODEL_PATH)."
  echo "Optional: run ./setup.sh --download-model"
fi
