# TalkBot

A talking AI assistant that uses OpenRouter for AI responses and edge-tts (Microsoft Azure) for high-quality text-to-speech, with KittenTTS (local neural) and pyttsx3 as offline alternatives.

## Features

- 🤖 **AI Chat**: Powered by OpenRouter (supports OpenAI, Anthropic, Google, Meta, and more)
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
UV_SKIP_WHEEL_FILENAME_CHECK=1 uv tool install --python /usr/bin/python3.12 . --with faster-whisper --with silero-vad --with sounddevice --with soundfile

# 2) Configure API key
cp .env.example .env
# edit .env and set OPENROUTER_API_KEY=...

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
UV_SKIP_WHEEL_FILENAME_CHECK=1 uv tool install --python /usr/bin/python3.12 . --with faster-whisper --with silero-vad --with sounddevice --with soundfile
```

To refresh an existing install:

```bash
cd talkbot
UV_SKIP_WHEEL_FILENAME_CHECK=1 uv tool install --reinstall --python /usr/bin/python3.12 . --with faster-whisper --with silero-vad --with sounddevice --with soundfile
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

### Install voice pipeline extras (VAD + STT + audio I/O)

```bash
uv sync --extra voice
```

## Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Add your OpenRouter API key to `.env`:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

Get your API key from [OpenRouter](https://openrouter.ai/keys)

The application automatically loads environment variables from `.env` using python-dotenv, so you don't need to manually export them.

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

### CLI Commands

#### Single Message
```bash
# Basic chat
talkbot chat "Hello, how are you?"

# With specific model
talkbot --model anthropic/claude-3-haiku chat "What's the weather?"

# Without speaking
talkbot chat --no-speak "Just text please"

# Force a TTS backend
talkbot chat --backend pyttsx3 "Use offline system TTS"

# With custom voice settings
talkbot chat --rate 200 --volume 0.8 "Hello world"
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
