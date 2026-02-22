# TalkBot

A talking AI assistant with local-first LLM + TTS defaults, plus optional OpenRouter for remote models. TTS supports edge-tts (online), KittenTTS (local neural), and pyttsx3.

## Features

- 🤖 **AI Chat**: Local llama.cpp provider by default, with OpenRouter optional
- 🛠️ **Tool Calling**: AI can use built-in tools (calculator, time, dice rolling, etc.)
- 🔊 **Text-to-Speech**: Microsoft Edge TTS (322 voices!) with pyttsx3 offline fallback
- 🖥️ **Modern GUI**: Beautiful dark-themed tkinter interface with rounded buttons
- ⏹️ **Stop Button**: Instantly stop AI responses and speech
- 💻 **CLI Interface**: Command-line interface with Click
- ⚙️ **Configurable**: Voice, rate, volume, and model settings

## Quick Start

```bash
# 1) Install as a tool
cd talkbot
UV_SKIP_WHEEL_FILENAME_CHECK=1 uv tool install --python /usr/bin/python3.12 . --with llama-cpp-python --with faster-whisper --with silero-vad --with sounddevice --with soundfile

# (optional) same install via helper script
./setup.sh
# or install + fetch default local model in one go
./setup.sh --download-model

# 2) Configure defaults
cp .env.example .env
# put your GGUF at ./models/default.gguf (or override TALKBOT_LOCAL_MODEL_PATH)

# If TALKBOT_LOCAL_MODEL_PATH is not set, TalkBot auto-uses ./models/default.gguf when present.

# 3) Run a quick CLI check
talkbot doctor-tts
talkbot doctor-voice
talkbot chat --no-speak "Hello"
talkbot voice-chat --backend kittentts

# 4) Run GUI
talkbot-gui
```

## Installation

### Prerequisites (Linux)

tkinter is required for the GUI and must be installed as a system package:

```bash
sudo apt install python3-tk        # Debian/Ubuntu
sudo dnf install python3-tkinter   # Fedora/RHEL
```

### Install as a global tool (recommended)

Makes `talkbot` and `talkbot-gui` available anywhere in your shell:

```bash
cd talkbot
UV_SKIP_WHEEL_FILENAME_CHECK=1 uv tool install --python /usr/bin/python3.12 . --with llama-cpp-python --with faster-whisper --with silero-vad --with sounddevice --with soundfile
```

To refresh an existing install:

```bash
cd talkbot
UV_SKIP_WHEEL_FILENAME_CHECK=1 uv tool install --reinstall --python /usr/bin/python3.12 . --with llama-cpp-python --with faster-whisper --with silero-vad --with sounddevice --with soundfile
```

Or use:

```bash
./setup.sh
./setup.sh --download-model
```

> **Note:** `--python /usr/bin/python3.12` tells uv to use the system Python, which has tkinter. uv's own bundled Python builds omit it.
>
> `UV_SKIP_WHEEL_FILENAME_CHECK=1` works around a version mismatch in the kittentts wheel packaging. Add `export UV_SKIP_WHEEL_FILENAME_CHECK=1` to your `~/.bashrc` to avoid typing it each time.

### Install as a Python package

Install into your active Python environment:

```bash
UV_SKIP_WHEEL_FILENAME_CHECK=1 uv pip install .
```

Editable install (for local development while importing `talkbot`):

```bash
UV_SKIP_WHEEL_FILENAME_CHECK=1 uv pip install -e .
```

### Install for development

```bash
uv sync
```

### Local LLM Prerequisites (required for `provider=local`)

TalkBot local mode needs one of these:

1. `llama-cpp-python` in the active environment (no external binary needed), or
2. a system `llama.cpp` executable (`llama-cli` or `llama`) on `PATH`.

Recommended (Python backend):

```bash
uv add llama-cpp-python
```

If you prefer external llama.cpp CLI:

```bash
# build/install llama.cpp first, then point TalkBot to it
export TALKBOT_LLAMACPP_BIN=/full/path/to/llama-cli
```

### Install voice pipeline extras (VAD + STT + audio I/O)

```bash
uv sync --extra voice
```

### Download a default local GGUF

```bash
./scripts/download-model.sh
```

Default source is the official Qwen GGUF file:
- `Qwen/Qwen3-1.7B-GGUF` (`Qwen3-1.7B-Q8_0.gguf`)

Override URL or output path:

```bash
./scripts/download-model.sh --output models/default.gguf --url "https://..."
```

## Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Configure `.env` for local-first (recommended):
```bash
TALKBOT_LLM_PROVIDER=local
TALKBOT_LOCAL_MODEL_PATH=./models/default.gguf
TALKBOT_LOCAL_N_CTX=2048
# Optional when llama-cpp-python is installed.
# Required only if using external llama.cpp CLI binary:
# TALKBOT_LLAMACPP_BIN=/full/path/to/llama-cli
TALKBOT_ENABLE_THINKING=0
TALKBOT_DEFAULT_MODEL=qwen/qwen3-1.7b
TALKBOT_DEFAULT_TTS_BACKEND=kittentts
```

Optional remote provider:
```bash
TALKBOT_LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_api_key_here
```

Get OpenRouter keys at [OpenRouter](https://openrouter.ai/keys).

The application automatically loads environment variables from `.env` using python-dotenv, so you don't need to manually export them.

### Default Runtime Behavior

- Default LLM provider is `local`.
- Default TTS backend is `kittentts`.
- Default model label is `qwen/qwen3-1.7b`.
- Default thinking mode is OFF (`TALKBOT_ENABLE_THINKING=0`) for faster conversational turns.
- Override with:

```bash
TALKBOT_LLM_PROVIDER=local
TALKBOT_LOCAL_MODEL_PATH=./models/default.gguf
TALKBOT_LOCAL_N_CTX=2048
TALKBOT_DEFAULT_TTS_BACKEND=edge-tts
TALKBOT_DEFAULT_MODEL=qwen/qwen3-1.7b
```

`TALKBOT_LOCAL_N_CTX` controls local llama context size (for example `8192`).

## Recent Changes

- Added CLI backend selection to all TTS commands:
  - `talkbot chat --backend ...`
  - `talkbot tool --backend ...`
  - `talkbot say --backend ...`
  - `talkbot save --backend ...`
  - `talkbot voices --backend ...`
- Added `talkbot doctor-tts` to run per-backend diagnostics.
- Added optional integration tests that exercise real backend behavior.

## Usage

### LLM Provider Selection

```bash
# Local (default)
talkbot --provider local --local-model-path /models/model.gguf chat "Hello"

# OpenRouter
talkbot --provider openrouter --api-key "$OPENROUTER_API_KEY" --model openai/gpt-4o-mini chat "Hello"

# Toggle thinking mode (default is --no-thinking)
talkbot --thinking chat "Think deeply"
talkbot --no-thinking chat "Respond quickly"
```

In GUI:
- `Provider` dropdown chooses `local` or `openrouter`.
- `Local GGUF` field sets the local model path when provider is `local`.
- `Llama Bin` field overrides the local llama.cpp executable path when using CLI mode.
- `Thinking` checkbox controls deliberate thinking mode.

### Troubleshooting: `llama.cpp binary not found ... TALKBOT_LLAMACPP_BIN`

This means local mode cannot find `llama-cpp-python` and cannot find a `llama.cpp` binary.

Use one of these fixes:

```bash
# Fix A (recommended): install python backend
uv add llama-cpp-python
```

```bash
# Fix B: install llama.cpp CLI and configure env
which llama-cli || which llama
echo 'TALKBOT_LLAMACPP_BIN=/full/path/to/llama-cli' >> .env
```

Then restart:

```bash
talkbot-gui
# or
uv run python -m talkbot.gui
```

### Memory Sizing Guide (local mode)

Measured on a Linux host with `30 GiB` RAM, model `./models/default.gguf` (~`1.8 GiB`), CPU inference, and `kittentts`:

- CLI local chat, `TALKBOT_LOCAL_N_CTX=2048`: peak RSS ~`2.56 GiB`
- CLI local chat, `TALKBOT_LOCAL_N_CTX=8192`: peak RSS ~`3.22 GiB`
- Full stack in one process (GUI + STT + TTS + local LLM at 8k): peak RSS ~`3.76 GiB`

Takeaways:

- `8192` context is safe on a `32 GiB` class machine with substantial headroom.
- On this setup, moving from `2k` to `8k` costs about `+0.66 GiB`.
- Rough slope for this model was about `~112 MB` per additional `+1k` context tokens.

Use this as an estimate, not an absolute guarantee. Actual memory depends on:

- model size/quantization
- STT model choice (for example `small.en` vs larger Whisper models)
- selected TTS backend
- concurrent apps and desktop load

To right-size on your own system:

```bash
# Example: compare 2k vs 8k for CLI local mode
/usr/bin/time -v env TALKBOT_LOCAL_N_CTX=2048 uv run talkbot --provider local chat --no-speak "ping"
/usr/bin/time -v env TALKBOT_LOCAL_N_CTX=8192 uv run talkbot --provider local chat --no-speak "ping"
```

Check `Maximum resident set size` from `/usr/bin/time -v` and keep swap usage near zero during normal runs.

### CLI Commands

#### Single Message
```bash
# Basic chat
talkbot chat "Hello, how are you?"

# With explicit provider/model
talkbot --provider local --local-model-path /models/qwen3-1.7b-instruct-q4_k_m.gguf chat "Local run"
talkbot --provider openrouter --api-key "$OPENROUTER_API_KEY" --model openai/gpt-4o-mini chat "Remote run"

# With specific model
talkbot --model anthropic/claude-3-haiku chat "What's the weather?"

# Without speaking
talkbot chat --no-speak "Just text please"

# Force a TTS backend
talkbot chat --backend pyttsx3 "Use offline system TTS"

# With custom voice settings
talkbot chat --rate 200 --volume 0.8 "Hello world"

# Enable built-in tools in chat mode
talkbot chat --tools "What's 15 percent of 240?"
```

#### Interactive Mode
```bash
talkbot say
talkbot say --backend kittentts
```

#### Local Voice Chat (Half-Duplex, VAD-Gated)
```bash
# Start local voice loop (Ctrl+C to stop)
talkbot voice-chat

# Choose TTS backend and tune VAD
talkbot voice-chat --backend pyttsx3 --vad-threshold 0.30 --energy-threshold 0.003 --vad-min-silence-ms 1200

# Enable tools while in voice loop
talkbot voice-chat --tools

# Select devices by index
talkbot voice-chat --device-in 2 --device-out 3
```

#### List Available Voices
```bash
talkbot voices
talkbot voices --backend edge-tts
```

#### Diagnose TTS Backends
```bash
# Fast health check (init + voice listing)
talkbot doctor-tts

# Check specific backend
talkbot doctor-tts --backend kittentts

# Deep check with real synthesis to temp files
talkbot doctor-tts --synthesize
```

#### Diagnose Voice Pipeline
```bash
# Check mic/speaker devices + silero-vad + faster-whisper model load
talkbot doctor-voice

# Test a specific STT model load
talkbot doctor-voice --stt-model small.en
```

#### Test Transcription Only (No LLM/TTS)
```bash
# Mic one-shot test: speak once, then pause
talkbot test-stt

# Transcribe an existing file
talkbot test-stt --file sample.wav

# Simulated test: play a prompt phrase, then listen/transcribe once
talkbot test-stt --simulate --prompt-text "What time is it?"
```

#### Save Text to Audio File
```bash
talkbot save "Hello, this is a test" output.wav
talkbot save --backend pyttsx3 "Hello, this is offline speech" output.wav
```

#### Chat with Tools
The AI can use built-in tools for calculations, time, and random generation:
```bash
# Get current time
talkbot tool "What time is it?"

# Calculate math
talkbot tool "What is 15% of 240?"

# Roll dice
talkbot tool "Roll a 20-sided die"

# Force a backend for tool responses with speech
talkbot tool --backend kittentts "Roll a 20-sided die"

# Flip a coin
talkbot tool "Flip a coin"

# Generate random number
talkbot tool "Pick a random number between 1 and 100"
```

**Available Tools:**
- `calculator` - Safe math calculations
- `get_current_time` - Get current date/time
- `get_current_date` - Get current date
- `roll_dice` - Roll dice with customizable sides
- `flip_coin` - Flip a coin
- `random_number` - Generate random numbers

## TTS Backends

The application automatically selects the best available TTS backend:

### 1. Microsoft Edge TTS (Default) ★
- **322 high-quality voices** in 100+ languages
- Neural voices sound very natural
- Requires internet connection
- Fast synthesis

**Example voices:**
- `en-US-AriaNeural` - English (US) Female
- `en-GB-SoniaNeural` - English (UK) Female  
- `en-US-GuyNeural` - English (US) Male
- `es-ES-ElviraNeural` - Spanish Female
- `ja-JP-NanamiNeural` - Japanese Female

### 2. KittenTTS (Local Neural TTS) ★
- **8 neural voices** (model-defined IDs, shown in `talkbot voices --backend kittentts`)
- Runs fully offline — no internet required after model download
- Lightweight models (15–80MB), CPU-optimized
- Requires Python 3.12+

**Models** (auto-downloaded on first use):
- `KittenML/kitten-tts-nano` (15M params, 56MB) — default
- `KittenML/kitten-tts-nano-int8` (15M params, 25MB) — smallest
- `KittenML/kitten-tts-micro` (40M params, 41MB)
- `KittenML/kitten-tts-mini` (80M params, 80MB) — highest quality

### 3. pyttsx3 (Offline Fallback)
- Works offline
- Uses system TTS (eSpeak on Linux)
- Lower quality but always available

### GUI Mode

The GUI features a modern dark theme with:
- 🎨 Beautiful dark color scheme
- 🔘 Rounded buttons with hover effects
- ⏹️ Stop button to interrupt AI responses
- 🎚️ Real-time sliders for rate and volume
- 💬 Styled chat history with user/AI colors
- 🔄 **Backend switcher** - Toggle between online/offline TTS modes
- 🧰 **Use Tools toggle** - Enable calculator/time/dice/random tools for chat and voice
- 📝 **Prompt tab** - Edit system prompt live for text and voice conversations

**Backend Selection:**
The GUI includes a dropdown to switch between TTS backends:
- 🌐 **Edge-TTS** (Online) - 322 voices, requires internet
- 🐱 **KittenTTS** (Local) - Neural voices, fully offline, CPU-optimized
- 💻 **pyttsx3** (Offline) - System voices, always available

```bash
talkbot-gui
```

### Python API

```python
from talkbot import OpenRouterClient, TTSManager

# Chat with AI
with OpenRouterClient(api_key="your-key") as client:
    response = client.simple_chat("Hello!")
    print(response)

# Text-to-speech
tts = TTSManager(rate=150, volume=1.0)
tts.speak("Hello, world!")

# List available voices
tts.list_voices()
```

## Available Models

Any model available on OpenRouter can be used. See [OpenRouter Models](https://openrouter.ai/models) for the full list.

## Project Structure

```
talkbot/
├── src/talkbot/
│   ├── __init__.py        # Package initialization
│   ├── openrouter.py      # OpenRouter API client with tool support
│   ├── tools.py          # Built-in tools (calculator, time, dice, etc.)
│   ├── tts.py            # Text-to-speech manager
│   ├── cli.py            # Click CLI interface
│   └── gui.py            # Modern themed tkinter GUI
├── pyproject.toml        # Project configuration
├── .env.example          # Environment template
└── README.md            # This file
```

## Dependencies

- `click>=8.0` - CLI framework
- `edge-tts>=6.1` - Microsoft Edge TTS (online)
- `httpx>=0.24` - HTTP client
- `kittentts` - Local neural TTS (KittenTTS 0.8)
- `pygame>=2.5` - Audio playback
- `pyttsx3>=2.90` - System TTS (offline fallback)
- `python-dotenv>=1.0` - Environment variable management

**Optional voice extras (`uv sync --extra voice`):**
- `sounddevice` - Microphone capture and playback streams
- `silero-vad` - Voice activity detection (pause/speech gating)
- `faster-whisper` - CPU-optimized STT (int8)
- `soundfile` - Audio file decode for voice playback path

## License

MIT License
