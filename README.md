# TalkBot

A talking AI assistant with local-first LLM + TTS defaults, plus optional OpenRouter for remote models. TTS supports edge-tts (online), KittenTTS (local neural), and pyttsx3.

## Features

- 🤖 **AI Chat**: Local llama.cpp provider by default, with OpenRouter optional
- 🧠 **Agent Personality**: Set a system prompt once via `TALKBOT_AGENT_PROMPT` env var or the GUI Prompt tab — all commands pick it up automatically
- 🛠️ **17 Built-in Tools**: Calculator, timers (with cancel), web search, shopping lists, memory/preferences, dice, and more
- ⏰ **Cancellable Timers**: Set, list, and cancel named timers that fire spoken alerts through TTS
- 📋 **Persistent Lists & Memory**: Shopping lists and user preferences survive across sessions (`~/.talkbot/`)
- 🔊 **Text-to-Speech**: KittenTTS (local neural, default), Edge TTS (322 voices), or pyttsx3
- 🖥️ **Modern GUI**: Dark-themed tkinter interface with Prompt tab for live agent editing
- ⏹️ **Stop Button**: Instantly stop AI responses and speech
- 💻 **CLI Interface**: Command-line interface with Click
- ⚙️ **Configurable**: Voice, rate, volume, model, and agent prompt settings

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
TALKBOT_DEFAULT_USE_TOOLS=1
# Optional when llama-cpp-python is installed.
# Required only if using external llama.cpp CLI binary:
# TALKBOT_LLAMACPP_BIN=/full/path/to/llama-cli
TALKBOT_ENABLE_THINKING=0
TALKBOT_DEFAULT_MODEL=qwen/qwen3-1.7b
TALKBOT_DEFAULT_TTS_BACKEND=kittentts

# Agent personality prompt (optional) — applied to all CLI commands and
# pre-populated in the GUI Prompt tab on launch.
# TALKBOT_AGENT_PROMPT="You are a brief voice assistant. Always prefer tool calls over knowledge answers. Confirm actions in past tense."
```

Optional remote provider:
```bash
TALKBOT_LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_api_key_here
```

Optional local server provider (OpenAI-compatible API):
```bash
TALKBOT_LLM_PROVIDER=local_server
TALKBOT_LOCAL_SERVER_URL=http://127.0.0.1:8000/v1
TALKBOT_LOCAL_SERVER_MODEL=models/default.gguf
# TALKBOT_LOCAL_SERVER_API_KEY=optional
```

Get OpenRouter keys at [OpenRouter](https://openrouter.ai/keys).

The application automatically loads environment variables from `.env` using python-dotenv, so you don't need to manually export them.

### Default Runtime Behavior

- Default LLM provider is `local`.
- Default TTS backend is `kittentts`.
- Default model label is `qwen/qwen3-1.7b`.
- Default thinking mode is OFF (`TALKBOT_ENABLE_THINKING=0`) for faster conversational turns.
- Default tools toggle is ON in GUI (`TALKBOT_DEFAULT_USE_TOOLS=1`).
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

- **Agent personality prompt**: `TALKBOT_AGENT_PROMPT` env var applies a system prompt to all CLI commands (`chat`, `say`, `tool`, `voice-chat`). Pass `--system/-s` per-command to override. GUI Prompt tab pre-populates from the env var on launch.
- **17 built-in tools**: added timers, web search, lists, and memory (see [Available Tools](#available-tools) below).
- **Cancellable timers**: `set_timer` returns a timer ID; `cancel_timer` and `list_timers` manage active timers. Timer alerts fire through TTS (spoken) rather than stdout-only.
- **Persistent lists & memory**: `~/.talkbot/lists.json` and `~/.talkbot/memory.json` survive across sessions.
- **`talkbot say`** now accepts `--system/-s` (previously missing).
- Added CLI backend selection to all TTS commands and `talkbot doctor-tts` diagnostics.

## Usage

### Provider Feature Matrix

| Provider | Runs Where | Tool Calling | Setup Complexity | Recommended For |
|---|---|---|---|---|
| `local` | In-process (`llama-cpp-python` or `llama-cli`) | Limited (no standard server tool loop) | Low | Fastest local CPU path |
| `local_server` | OpenAI-compatible local server (`llama-server` / `llama_cpp.server`) | Yes (standard tools flow; includes compatibility fallback for `<tool_call>` text) | Medium | Best local option for tool-calling workflows |
| `openrouter` | Remote API | Yes | Low | Easiest cloud setup / strongest tool reliability |

Quick guidance:

- Use `local` for lowest overhead local inference.
- Use `local_server` if you want local + more standard tool-calling behavior.
- Use `openrouter` when you want managed reliability and broader model access.

### LLM Provider Selection

```bash
# Local (default)
talkbot --provider local --local-model-path /models/model.gguf chat "Hello"

# Local server (llama-server / llama_cpp.server)
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model models/default.gguf chat "Hello"

# OpenRouter
talkbot --provider openrouter --api-key "$OPENROUTER_API_KEY" --model openai/gpt-4o-mini chat "Hello"

# Toggle thinking mode (default is --no-thinking)
talkbot --thinking chat "Think deeply"
talkbot --no-thinking chat "Respond quickly"
```

In GUI:
- `Provider` dropdown chooses `local`, `local_server`, or `openrouter`.
- `Local GGUF` field sets the local model path when provider is `local`.
- `Llama Bin` field overrides the local llama.cpp executable path when using CLI mode.
- `Use Tools` checkbox controls tool calling per request (unchecked means no tool loop).
- `Thinking` checkbox controls deliberate thinking mode.

### Local Server Provider

`local_server` uses an OpenAI-compatible local endpoint and keeps OpenRouter support unchanged.

Example launch (python server wrapper):

```bash
uv run --with uvicorn --with fastapi --with sse-starlette --with starlette-context --with pydantic-settings \
  python -m llama_cpp.server --model models/default.gguf --n_ctx 8192 --host 127.0.0.1 --port 8000
```

Then run TalkBot:

```bash
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model models/default.gguf chat --tools "What is 2+2?"
```

Quick verification checks:

```bash
# 1) plain response
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model models/default.gguf chat --no-speak "Reply with OK"

# 2) tools on
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model models/default.gguf chat --tools --no-speak "What is 2+2? Use calculator tool."

# 3) tools off
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model models/default.gguf chat --no-tools --no-speak "What is 2+2? Do not use tools."
```

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

### HF/Torch Comparison Target

For Hugging Face Transformers comparisons, use:

- `Qwen/Qwen3-1.7B`

The older `Qwen/Qwen3-1.7B-Instruct` identifier may no longer be valid on HF.

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

# With tools and agent personality
talkbot say --tools
talkbot say --tools --system "You are a brief voice assistant. Confirm actions in past tense."

# Or set TALKBOT_AGENT_PROMPT in .env / env and omit --system
export TALKBOT_AGENT_PROMPT="You are a brief voice assistant."
talkbot say --tools
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

```bash
# Utility
talkbot tool "What time is it?"
talkbot tool "What is 15% of 240?"
talkbot tool "Roll a 20-sided die"
talkbot tool "Flip a coin"
talkbot tool "Pick a random number between 1 and 100"

# Timers
talkbot tool "Set a 5 minute pasta timer"
talkbot tool "What timers are running?"
talkbot tool "Cancel timer 1"

# Web search (DuckDuckGo instant answers)
talkbot tool "How many feet in a mile?"
talkbot tool "What is the speed of light?"

# Shopping / named lists
talkbot tool "Add milk to my shopping list"
talkbot tool "What's on my shopping list?"
talkbot tool "Remove milk from my shopping list"
talkbot tool "Clear my shopping list"

# Memory / user preferences
talkbot tool "Remember that my name is Rick"
talkbot tool "Remember my preferred music service is Spotify"
talkbot tool "What do you remember about me?"
talkbot tool "What is my name?"
```

### Available Tools

| Tool | Category | Description |
|---|---|---|
| `get_current_time` | Utility | Current date and time |
| `get_current_date` | Utility | Current date |
| `calculator` | Utility | Safe math: `+`, `-`, `*`, `/`, `sqrt`, `sin`, `log`, `pi`, … |
| `roll_dice` | Utility | Roll N dice with D sides |
| `flip_coin` | Utility | Heads or tails |
| `random_number` | Utility | Random integer in a range |
| `set_timer` | Timer | Named countdown — returns a timer ID; fires a spoken TTS alert |
| `cancel_timer` | Timer | Cancel an active timer by ID |
| `list_timers` | Timer | Show all running timers with remaining time |
| `web_search` | Search | DuckDuckGo instant answers (facts, definitions, conversions) |
| `add_to_list` | Lists | Add an item to a named list (default: `shopping`) |
| `get_list` | Lists | Read all items from a named list |
| `remove_from_list` | Lists | Remove an item from a named list (case-insensitive) |
| `clear_list` | Lists | Empty a named list |
| `remember` | Memory | Store a key-value preference that persists across sessions |
| `recall` | Memory | Look up a stored preference by key |
| `recall_all` | Memory | Dump all stored preferences |

Lists are stored in `~/.talkbot/lists.json`; memory in `~/.talkbot/memory.json`.

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
- 🧰 **Use Tools toggle** - Enable all 17 built-in tools for chat and voice
- 📝 **Prompt tab** - Edit the agent system prompt live; pre-populated from `TALKBOT_AGENT_PROMPT` on launch

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
