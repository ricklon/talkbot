# TalkBot

A talking AI assistant with local-first LLM + TTS defaults, plus optional OpenRouter for remote models. TTS supports edge-tts (online), KittenTTS (local neural), and pyttsx3.

## Features

- 🤖 **AI Chat**: Local llama-server provider by default, with OpenRouter optional
- 🧠 **Agent Personality**: Set a system prompt once via `TALKBOT_AGENT_PROMPT` env var or the GUI Prompt tab — all commands pick it up automatically
- 🛠️ **19 Built-in Tools**: Calculator, timers, reminders, web search, shopping lists, memory/preferences, dice, and more
- ⏰ **Timers & Reminders**: `set_timer` for simple countdowns; `set_reminder` for custom spoken messages — cancellable, with live GUI display
- 📋 **Persistent Lists & Memory**: Named lists and user preferences survive across sessions (`~/.talkbot/`)
- 🔊 **Text-to-Speech**: KittenTTS (local neural, default), Edge TTS (322 voices), or pyttsx3
- 🖥️ **Modern GUI**: Dark-themed tkinter interface with Conversation, Timers, Lists, and Prompt tabs
- ⏹️ **Stop Button**: Instantly stop AI responses and speech
- 💻 **CLI Interface**: Command-line interface with Click
- ⚙️ **Configurable**: Voice, rate, volume, model, and agent prompt settings

## Quick Start

### Windows
```bat
REM 1) Run setup (installs talkbot + voice extras into %LOCALAPPDATA%\talkbot\.venv)
setup.bat

REM 2) Download default model
scripts\download-model.bat

REM 3) Copy and edit config
copy .env.example .env

REM 4) Start llama-server (keep this window open)
run-server.bat

REM 5) Start the GUI (new window)
run-gui.bat
```

### Linux / macOS
```bash
# 1) Install
./setup.sh --download-model

# 2) Configure
cp .env.example .env

# 3) Start server + GUI
llama-server -m models/qwen3-1.7b-q4_k_m.gguf --jinja -c 8192 -n 256 --temp 0.7 --port 8000 &
talkbot-gui
```

## Platform Compatibility

| Component | Windows 11 | Linux / macOS | Notes |
|---|---|---|---|
| **local_server** (default LLM) | ✅ | ✅ | Pre-built `llama-server.exe` provided for Windows; `run-server.bat` included |
| **local** (in-process LLM) | ⚠️ | ✅ | Requires MSVC build tools on Windows to compile `llama-cpp-python`; use `local_server` instead |
| **openrouter** (cloud LLM) | ✅ | ✅ | No platform concerns |
| **kittentts** (default TTS) | ✅ | ✅ | fd-suppression during init silently skipped on Windows — cosmetic only, TTS works fully |
| **edge-tts** (online TTS) | ✅ | ✅ | asyncio + pygame, no issues |
| **pyttsx3** (offline TTS) | ✅ | ✅ | Uses Windows SAPI5 on Windows, eSpeak on Linux |
| **faster-whisper** (STT) | ✅ | ✅ | Pre-built PyPI wheels; CPU int8 inference |
| **silero-vad** (VAD) | ✅ | ✅ | Pre-built PyPI wheels |
| **sounddevice / soundfile** | ✅ | ✅ | PortAudio; well-tested on Windows |
| **GUI (tkinter)** | ✅ | ✅ | tkinter bundled with Python on Windows; system package on Linux |
| **setup.bat / run-*.bat** | ✅ | N/A | Windows-only; Linux/macOS uses setup.sh |
| **setup.sh / download-model.sh** | N/A | ✅ | Linux/macOS only; Windows uses .bat equivalents |

> **Dependency note (2026-02-24):** TalkBot now uses `kittentts` from PyPI, so `UV_SKIP_WHEEL_FILENAME_CHECK` is no longer required.

## Installation

### Prerequisites (Linux)

tkinter is required for the GUI and must be installed as a system package:

```bash
sudo apt install python3-tk        # Debian/Ubuntu
sudo dnf install python3-tkinter   # Fedora/RHEL
```

KittenTTS also needs eSpeak NG:

```bash
sudo apt install espeak-ng espeak-ng-data   # Debian/Ubuntu
sudo dnf install espeak-ng                  # Fedora/RHEL
```

### Prerequisites (macOS)

KittenTTS needs eSpeak NG:

```bash
brew install espeak-ng
```

### Prerequisites (Windows)

The recommended Windows setup uses the pre-built `llama-server.exe` binary (no MSVC required):

1. Download a pre-built llama.cpp release from https://github.com/ggerganov/llama.cpp/releases
2. Extract and place `llama-server.exe` (and its `.dll` files) in `tools/llama-cpp/`
3. Use `run-server.bat` (included) to start the server before launching the GUI
4. Use `run-gui.bat` (included) to launch the GUI — sets required env vars automatically

> **Note:** The `.venv` is placed in `%LOCALAPPDATA%\talkbot\.venv` (outside OneDrive) to avoid file-locking issues.
>
> **KittenTTS note:** install eSpeak NG and ensure `espeak-ng.exe` (or `espeak.exe`) is on your `PATH`.

If you want the `llama-cpp-python` backend instead of a server:

```bat
uv sync --extra local
```

### Install as a global tool (recommended)

Makes `talkbot` and `talkbot-gui` available anywhere in your shell:

```bash
cd talkbot
uv tool install --python /usr/bin/python3.12 . --with llama-cpp-python --with faster-whisper --with silero-vad --with sounddevice --with soundfile
```

To refresh an existing install:

```bash
cd talkbot
uv tool install --reinstall --python /usr/bin/python3.12 . --with llama-cpp-python --with faster-whisper --with silero-vad --with sounddevice --with soundfile
```

Or use:

```bash
./setup.sh
./setup.sh --download-model
```

> **Note:** `--python /usr/bin/python3.12` tells uv to use the system Python, which has tkinter. uv's own bundled Python builds omit it.

### Install as a Python package

Install into your active Python environment:

```bash
uv pip install .
```

Editable install (for local development while importing `talkbot`):

```bash
uv pip install -e .
```

### Install for development

```bash
uv sync
```

#### Troubleshooting: stale lockfile/cache after the KittenTTS fix

If your local checkout or cache still reflects the old direct-wheel setup, you may still see lock/resolve failures mentioning `kittentts` wheel filename/version mismatch.

From a fresh checkout of main, run:

```bash
uv sync --refresh
```

If you still see the old error, clear local cache and retry:

```bash
uv cache clean
uv sync
```

### Local LLM Prerequisites

**Recommended: `local_server` provider (llama-server)**

The default provider is `local_server`, which requires llama-server to be running before TalkBot starts. This enables proper tool calling, conversation memory, and correct Qwen3 chat templates via `--jinja`.

Start the server (Windows):
```bat
run-server.bat
```

Start the server (Linux/macOS — example):
```bash
llama-server -m models/qwen3-1.7b-q4_k_m.gguf --jinja -c 8192 -n 512 --temp 0.6 --top-p 0.95 --min-p 0.0 --port 8000
```

**Alternative: `local` provider (llama-cpp-python or llama-cli)**

If you prefer in-process inference without a server:

```bash
uv add llama-cpp-python
# or point to an external llama-cli binary:
echo 'TALKBOT_LLAMACPP_BIN=/full/path/to/llama-cli' >> .env
```

Note: the `local` provider does not support the standard tools loop. Use `local_server` for tool calling.

### Install voice pipeline extras (VAD + STT + audio I/O)

```bash
uv sync --extra voice
```

### Download a default local GGUF

```bash
./scripts/download-model.sh        # Linux/macOS
scripts\download-model.bat         # Windows
```

Default model: `Qwen/Qwen3-1.7B-GGUF` → `Qwen3-1.7B-Q4_K_M.gguf`, saved as `models/qwen3-1.7b-q4_k_m.gguf`

Override URL or output path:

```bash
./scripts/download-model.sh --output models/my-model.gguf --url "https://..."
```

## Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Configure `.env` for local-first (recommended):
```bash
TALKBOT_LLM_PROVIDER=local_server
TALKBOT_LOCAL_SERVER_URL=http://127.0.0.1:8000/v1
TALKBOT_LOCAL_SERVER_MODEL=models/qwen3-1.7b-q4_k_m.gguf
TALKBOT_LOCAL_MODEL_PATH=./models/qwen3-1.7b-q4_k_m.gguf
TALKBOT_LOCAL_N_CTX=8192
TALKBOT_MAX_TOKENS=512
TALKBOT_DEFAULT_USE_TOOLS=1
TALKBOT_ENABLE_THINKING=0
TALKBOT_DEFAULT_MODEL=qwen3-1.7b-q4_k_m
TALKBOT_DEFAULT_TTS_BACKEND=kittentts

# Agent personality (optional) — applied to all CLI commands and GUI Prompt tab
# TALKBOT_AGENT_PROMPT="You are a voice-first assistant with access to tools. Be extremely brief."
# Keep TALKBOT_AGENT_PROMPT single-line in .env.
# For multiline markdown prompts, store them in a file (for example: prompts/agent.md)
# and pass with --system "$(cat prompts/agent.md)".
```

Optional remote provider:
```bash
TALKBOT_LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_api_key_here
```

Get OpenRouter keys at [OpenRouter](https://openrouter.ai/keys).

The application automatically loads environment variables from `.env` using python-dotenv, so you don't need to manually export them.

### Default Runtime Behavior

- Default LLM provider is `local_server`.
- Default TTS backend is `kittentts`.
- Default model is `qwen3-1.7b-q4_k_m`.
- Default context window is `8192` tokens.
- Default thinking mode is OFF (`TALKBOT_ENABLE_THINKING=0`) for faster conversational turns.
- Default tools toggle is ON in GUI (`TALKBOT_DEFAULT_USE_TOOLS=1`).

`TALKBOT_LOCAL_N_CTX` controls local llama context size. 8192 is recommended for tool calling with conversation history.
`TALKBOT_MAX_TOKENS` sets the default generation cap used by the GUI `Max Tokens` field.
`TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=1` enables deterministic local intent routing for a few common voice/tool intents (off by default).

## Recent Changes

- **`add_items_to_list`**: add multiple items in one call — "add lettuce, tomato, and onion to the grocery list".
- **`create_list`**: explicit empty-list creation prevents the model from hallucinating items.
- **Calculator percentage support**: `15% of 84` now correctly returns `12.6` (was treated as modulo).
- **Timer dedup**: prevents the same timer from firing multiple times if the model repeats a tool call.
- **Python-style tool call fallback**: model output like `set_timer(seconds=10, label="pasta")` is now parsed and executed rather than displayed as raw text.
- **Timestamps on conversation messages**: every chat entry shows `[HH:MM:SS]`.
- **Token counter**: toolbar shows prompt/completion token counts after each response.
- **GUI max tokens control**: Configuration panel now includes `Max Tokens` (default from `TALKBOT_MAX_TOKENS`, clamped 32-8192).
- **Timer alerts in GUI**: timer alerts appear in the conversation panel instead of being spoken (prevents mic echo loop during voice chat).
- **`</think>` tag stripping**: lone closing think tags no longer leak into displayed responses.
- **Date/time injection**: `LocalServerClient` now injects current date and time into the system prompt so day-of-week and time queries work without a tool call.
- **`local` provider tools**: in-process local mode now supports tool calling with text-call parsing and `<think>`-safe output cleaning.
- **19 built-in tools**: added `set_reminder` (custom spoken message on fire), `list_all_lists` (show all named lists at once).
- **Lists tab**: GUI now has a live Lists tab showing all named lists and their contents (updates every 2s).
- **`local_server` is now the default provider**: enables proper tool calling, KV cache, and Qwen3 chat templates via `--jinja`.
- **Agent personality prompt**: `TALKBOT_AGENT_PROMPT` env var applies a system prompt to all CLI commands and pre-populates the GUI Prompt tab.
- **Timers tab**: live countdown display in GUI (updates every second).
- **Cancellable timers**: `set_timer` returns a timer ID; `cancel_timer` and `list_timers` manage active timers.
- **Persistent lists & memory**: `~/.talkbot/lists.json` and `~/.talkbot/memory.json` survive across sessions.

## Usage

### Provider Feature Matrix

| Provider | Runs Where | Tool Calling | Setup Complexity | Recommended For |
|---|---|---|---|---|
| `local_server` | OpenAI-compatible local server (`llama-server` / `llama_cpp.server`) | Yes (standard tools flow; includes `<tool_call>` text fallback) | Medium | **Default — best local option for tool-calling** |
| `local` | In-process (`llama-cpp-python` or `llama-cli`) | Yes (text-call tool parsing + local execution) | Low | Fastest local CPU path without server |
| `openrouter` | Remote API | Yes | Low | Easiest cloud setup / strongest tool reliability |

Quick guidance:

- Use `local_server` (default) for local inference with tool calling.
- Use `local` for lowest overhead local inference (tools supported via text-call parsing).
- Use `openrouter` when you want managed reliability and broader model access.

### LLM Provider Selection

```bash
# Local server (default)
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model models/qwen3-1.7b-q4_k_m.gguf chat "Hello"

# Local in-process
talkbot --provider local --local-model-path ./models/qwen3-1.7b-q4_k_m.gguf chat "Hello"

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

`local_server` uses an OpenAI-compatible local endpoint. Start the server before launching TalkBot.

**Windows:**
```bat
run-server.bat
```

**Linux/macOS (llama-server):**
```bash
llama-server \
  -m models/qwen3-1.7b-q4_k_m.gguf \
  --jinja \
  -c 8192 \
  -n 256 \
  --temp 0.7 --top-k 20 --top-p 0.8 \
  --port 8000
```

**Linux/macOS (llama_cpp.server python wrapper):**
```bash
uv run --with uvicorn --with fastapi --with sse-starlette --with starlette-context --with pydantic-settings \
  python -m llama_cpp.server --model models/qwen3-1.7b-q4_k_m.gguf --n_ctx 8192 --host 127.0.0.1 --port 8000
```

Quick verification checks:

```bash
# 1) plain response
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model models/qwen3-1.7b-q4_k_m.gguf chat --no-speak "Reply with OK"

# 2) tools on
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model models/qwen3-1.7b-q4_k_m.gguf chat --tools --no-speak "What is 2+2? Use calculator tool."
```

### Troubleshooting: `llama.cpp binary not found ... TALKBOT_LLAMACPP_BIN`

This applies only when using `provider=local`. Use `local_server` instead (recommended), or:

```bash
# Fix A: install python backend
uv add llama-cpp-python

# Fix B: point to external binary
echo 'TALKBOT_LLAMACPP_BIN=/full/path/to/llama-cli' >> .env
```

### Memory Sizing Guide (local_server mode)

Measured on a host with the `qwen3-1.7b-q4_k_m.gguf` model (~`1.1 GiB`), CPU inference:

- `TALKBOT_LOCAL_N_CTX=2048`: lower memory, shorter context
- `TALKBOT_LOCAL_N_CTX=8192`: recommended — ~`+0.66 GiB` vs 2k, safe on 8+ GiB RAM systems

Rough rule of thumb for this model: ~`112 MB` per additional `+1k` context tokens.

Actual memory depends on model size/quantization, STT model choice, TTS backend, and concurrent load.

### CLI Commands

#### Single Message
```bash
# Basic chat
talkbot chat "Hello, how are you?"

# With explicit provider/model
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model models/qwen3-1.7b-q4_k_m.gguf chat "Local run"
talkbot --provider openrouter --api-key "$OPENROUTER_API_KEY" --model openai/gpt-4o-mini chat "Remote run"

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
talkbot say --tools --system "You are a brief voice assistant."

# Or set TALKBOT_AGENT_PROMPT in .env / env and omit --system
export TALKBOT_AGENT_PROMPT="You are a brief voice assistant."
talkbot say --tools

# For multiline markdown prompts, keep them in a file
talkbot say --tools --system "$(cat prompts/agent.md)"
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

# Timers and reminders
talkbot tool "Set a 5 minute pasta timer"
talkbot tool "Remind me to take my pills in 10 minutes"
talkbot tool "What timers are running?"
talkbot tool "Cancel timer 1"

# Web search (DuckDuckGo instant answers)
talkbot tool "How many feet in a mile?"
talkbot tool "What is the speed of light?"

# Shopping / named lists
talkbot tool "Add milk to my shopping list"
talkbot tool "What's on my shopping list?"
talkbot tool "Show me all my lists"
talkbot tool "Remove milk from my shopping list"
talkbot tool "Clear my shopping list"

# Memory / user preferences
talkbot tool "Remember that my name is Rick"
talkbot tool "What do you remember about me?"
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
| `set_timer` | Timer | Named countdown — fires spoken "{label} is done!" alert |
| `set_reminder` | Timer | Custom spoken message fires at a future time |
| `cancel_timer` | Timer | Cancel an active timer or reminder by ID |
| `list_timers` | Timer | Show all running timers/reminders with remaining time |
| `web_search` | Search | DuckDuckGo instant answers (facts, definitions, conversions) |
| `create_list` | Lists | Create a new empty named list |
| `add_to_list` | Lists | Add a single item to a named list (default: `shopping`) |
| `add_items_to_list` | Lists | Add multiple items at once (e.g. "add lettuce, tomato, and onion") |
| `get_list` | Lists | Read all items from a named list |
| `remove_from_list` | Lists | Remove an item from a named list (case-insensitive) |
| `clear_list` | Lists | Empty a named list |
| `list_all_lists` | Lists | Show all named lists and their contents |
| `remember` | Memory | Store a key-value preference that persists across sessions |
| `recall` | Memory | Look up a stored preference by key |
| `recall_all` | Memory | Dump all stored preferences |

Lists are stored in `~/.talkbot/lists.json`; memory in `~/.talkbot/memory.json`.

## TTS Backends

The application automatically selects the best available TTS backend:

### 1. KittenTTS (Local Neural) ★ Default
- **8 neural voices** (model-defined IDs, shown in `talkbot voices --backend kittentts`)
- Runs fully offline — no internet required after model download
- Lightweight models (15–80MB), CPU-optimized
- Requires Python 3.12+

**Models** (auto-downloaded on first use):
- `KittenML/kitten-tts-nano` (15M params, 56MB) — default
- `KittenML/kitten-tts-nano-int8` (15M params, 25MB) — smallest
- `KittenML/kitten-tts-micro` (40M params, 41MB)
- `KittenML/kitten-tts-mini` (80M params, 80MB) — highest quality

### 2. Microsoft Edge TTS (Online)
- **322 high-quality voices** in 100+ languages
- Neural voices sound very natural
- Requires internet connection
- Fast synthesis

**Example voices:**
- `en-US-AriaNeural` - English (US) Female
- `en-GB-SoniaNeural` - English (UK) Female
- `en-US-GuyNeural` - English (US) Male

### 3. pyttsx3 (Offline Fallback)
- Works offline
- Uses system TTS (eSpeak on Linux, SAPI on Windows)
- Lower quality but always available

### GUI Mode

The GUI features a modern dark theme with:
- 🎨 Beautiful dark color scheme
- 🔘 Rounded buttons with hover effects
- ⏹️ Stop button to interrupt AI responses
- 🎚️ Real-time sliders for rate and volume
- 💬 Styled chat history with user/AI colors
- 🔄 **Backend switcher** — Toggle between online/offline TTS modes
- 🧰 **Use Tools toggle** — Enable all 19 built-in tools for chat and voice
- ⏰ **Timers tab** — Live countdown display, updates every second
- 📋 **Lists tab** — Live view of all named lists, updates every 2 seconds
- 📝 **Prompt tab** — Edit the agent system prompt live; pre-populated from `TALKBOT_AGENT_PROMPT` on launch

**Backend Selection:**
The GUI includes a dropdown to switch between TTS backends:
- 🐱 **KittenTTS** (Local) — Neural voices, fully offline, CPU-optimized (default)
- 🌐 **Edge-TTS** (Online) — 322 voices, requires internet
- 💻 **pyttsx3** (Offline) — System voices, always available

```bash
talkbot-gui
# Windows: use run-gui.bat instead
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

For local inference, any GGUF-format model supported by llama.cpp works. Default: `Qwen3-1.7B-Q4_K_M`.

## Project Structure

```
talkbot/
├── src/talkbot/
│   ├── __init__.py        # Package initialization
│   ├── openrouter.py      # OpenRouter API client with tool support
│   ├── llm.py             # LLM provider abstraction (local, local_server, openrouter)
│   ├── tools.py           # Built-in tools (calculator, timers, lists, memory, etc.)
│   ├── tts.py             # Text-to-speech manager
│   ├── voice.py           # Voice pipeline (VAD + STT + LLM + TTS)
│   ├── cli.py             # Click CLI interface
│   └── gui.py             # Modern themed tkinter GUI
├── models/                # GGUF model files (git-ignored)
├── tools/llama-cpp/       # llama-server binary and DLLs (Windows)
├── scripts/
│   ├── download-model.sh  # Download default GGUF (Linux/macOS)
│   └── download-model.bat # Download default GGUF (Windows)
├── run-server.bat         # Start llama-server (Windows)
├── run-gui.bat            # Start GUI with correct env vars (Windows)
├── pyproject.toml         # Project configuration
├── .env.example           # Environment template
└── README.md              # This file
```

## Dependencies

- `click>=8.0` — CLI framework
- `edge-tts>=6.1` — Microsoft Edge TTS (online)
- `httpx>=0.24` — HTTP client
- `kittentts` — Local neural TTS (KittenTTS 0.8)
- `pygame>=2.5` — Audio playback
- `pyttsx3>=2.90` — System TTS (offline fallback)
- `python-dotenv>=1.0` — Environment variable management

**Optional voice extras (`uv sync --extra voice`):**
- `sounddevice` — Microphone capture and playback streams
- `silero-vad` — Voice activity detection (pause/speech gating)
- `faster-whisper` — CPU-optimized STT (int8)
- `soundfile` — Audio file decode for voice playback path

## License

MIT License
