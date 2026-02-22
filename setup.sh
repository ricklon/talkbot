#!/usr/bin/env bash
set -euo pipefail

# Quick install/reinstall for the global talkbot and talkbot-gui tools
# with voice extras enabled.
UV_SKIP_WHEEL_FILENAME_CHECK=1 uv tool install --reinstall \
  --python /usr/bin/python3.12 . \
  --with faster-whisper \
  --with silero-vad \
  --with sounddevice \
  --with soundfile

echo "Installed talkbot and talkbot-gui with voice extras."
