# TalkBot

A talking AI assistant with local-first LLM + TTS defaults, plus optional OpenRouter for remote models. TTS supports KittenTTS (local neural, default), edge-tts (online), and pyttsx3.

## Features

- **AI Chat**: Local llama-server provider by default, with OpenRouter optional
- **Agent Personality**: Set a system prompt once via `TALKBOT_AGENT_PROMPT_FILE` or `TALKBOT_AGENT_PROMPT`; prompt presets are cataloged under `prompts/`
- **21 Built-in Tools**: Calculator, timers, reminders, web search, shopping lists, memory/preferences, dice, and more
- **Timers & Reminders**: `set_timer` for simple countdowns; `set_reminder` for custom spoken messages — cancellable, with live GUI display
- **Persistent Lists & Memory**: Named lists and user preferences survive across sessions (`~/.talkbot/`)
- **Text-to-Speech**: KittenTTS (local neural, default), Edge TTS (322 voices), or pyttsx3
- **Modern GUI**: Dark-themed tkinter interface with Conversation, Timers, Lists, and Prompt tabs
- **Stop Button**: Instantly stop AI responses and speech
- **CLI Interface**: Command-line interface with Click
- **Configurable**: Voice, rate, volume, model, and agent prompt settings

## Quick Start

TalkBot uses `uv` for easy, platform-agnostic dependency management.

```bash
# Optional but recommended: keep uv cache local to this repo
export UV_CACHE_DIR=.uv-cache

# 1) Install dependencies
uv sync --extra voice

# 2) Download recommended model (qwen3.5-0.8b Q8_0)
wget "https://huggingface.co/bartowski/Qwen_Qwen3.5-0.8B-GGUF/resolve/main/Qwen_Qwen3.5-0.8B-Q8_0.gguf" \
  -O models/qwen3.5-0.8b-q8_0.gguf

# 3) Copy and edit config
cp .env.example .env

# 4) Start local llama-server (in a separate terminal)
# Linux (CPU):
llama-server \
  -m models/qwen3.5-0.8b-q8_0.gguf \
  --port 8000 --ctx-size 4096 --n-predict 512 --no-mmap -t 4 --reasoning-budget 0

# macOS Apple Silicon (Metal GPU — install first: brew install llama.cpp):
# llama-server \
#   -m models/qwen3.5-0.8b-q8_0.gguf \
#   --port 8000 --ctx-size 4096 --n-predict 512 --gpu-layers -1 --reasoning-budget 0

# 5) Start the GUI
uv run talkbot-gui
```

## Platform Compatibility

| Component | Windows 11 | Linux | macOS (Apple Silicon) | Notes |
|---|---|---|---|---|
| **local_server** (default LLM) | ✅ | ✅ | ✅ Metal GPU | `brew install llama.cpp` on macOS; pre-built binary from llama.cpp releases on Linux/Windows |
| **local** (in-process LLM) | ⚠️ | ✅ | ✅ | Requires MSVC on Windows; `llama-cpp-python` 0.3.16 does not support Qwen3.5 — use `local_server` |
| **openrouter** (cloud LLM) | ✅ | ✅ | ✅ | No platform concerns |
| **kittentts** (default TTS) | ✅ | ✅ | ✅ | Needs `espeak-ng` (`brew install espeak-ng` on macOS) |
| **edge-tts** (online TTS) | ✅ | ✅ | ✅ | asyncio + pygame, no issues |
| **pyttsx3** (offline TTS) | ✅ | ✅ | ✅ | Uses SAPI5 on Windows, eSpeak on Linux/macOS |
| **faster-whisper** (STT) | ✅ | ✅ | ✅ | Pre-built PyPI wheels; CPU int8 inference |
| **silero-vad** (VAD) | ✅ | ✅ | ✅ | Pre-built PyPI wheels |
| **sounddevice / soundfile** | ✅ | ✅ | ✅ | Needs `brew install portaudio` on macOS |
| **GUI (tkinter)** | ✅ | ✅ | ✅ | Needs `brew install python-tk` on macOS |

> **Dependency note:** TalkBot pins `kittentts==0.8.1` via direct GitHub release wheel (not on PyPI). `uv sync` fetches it automatically.

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

```bash
# Required for GUI (tkinter is not bundled with Homebrew Python)
brew install python-tk

# Required for voice pipeline (sounddevice uses PortAudio)
brew install portaudio

# Required for KittenTTS TTS backend
brew install espeak-ng
```

### Prerequisites (Windows)

The recommended Windows setup uses the pre-built `llama-server.exe` binary (no MSVC required):

1. Download a pre-built llama.cpp release from https://github.com/ggerganov/llama.cpp/releases
2. Extract and place `llama-server.exe` (and its `.dll` files) in `tools/llama-cpp/`
3. Run the server manually: `tools\llama-cpp\llama-server.exe -m models\qwen3.5-0.8b-q8_0.gguf --ctx-size 4096 --n-predict 512 --no-mmap -t 4 --reasoning-budget 0 --port 8000`
4. Use `uv run talkbot-gui` to launch the GUI.

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
# Optional but recommended: keep uv cache local to this repo
export UV_CACHE_DIR=.uv-cache
uv sync
```

#### Troubleshooting: cache/lock mismatch

If dependency resolution behaves inconsistently after updates:

```bash
export UV_CACHE_DIR=.uv-cache
uv sync --refresh
```

If needed, remove only the project cache and retry:

```bash
rm -rf .uv-cache
uv sync
```

### Local LLM: llama-server (recommended)

The default provider is `local_server`, which requires llama-server to be running before TalkBot starts.

**Recommended model: `qwen3.5-0.8b-q8_0.gguf`** (774 MB, 90% benchmark success)

Download (Linux):
```bash
wget "https://huggingface.co/bartowski/Qwen_Qwen3.5-0.8B-GGUF/resolve/main/Qwen_Qwen3.5-0.8B-Q8_0.gguf" \
  -O models/qwen3.5-0.8b-q8_0.gguf
```

Download (macOS — `wget` not pre-installed, use `curl`):
```bash
curl -L "https://huggingface.co/bartowski/Qwen_Qwen3.5-0.8B-GGUF/resolve/main/Qwen_Qwen3.5-0.8B-Q8_0.gguf" \
  -o models/qwen3.5-0.8b-q8_0.gguf
```

**Getting `llama-server` (macOS — Apple Silicon):**
```bash
brew install llama.cpp
```
This installs a Metal-enabled build. `llama-server` will be on your PATH.

Start the server (Linux — CPU):
```bash
llama-server \
  -m models/qwen3.5-0.8b-q8_0.gguf \
  --port 8000 \
  --ctx-size 4096 \
  --n-predict 512 \
  --no-mmap \
  -t 4 \
  --reasoning-budget 0
```

Start the server (macOS — Apple Silicon, Metal GPU):
```bash
llama-server \
  -m models/qwen3.5-0.8b-q8_0.gguf \
  --port 8000 \
  --ctx-size 4096 \
  --n-predict 512 \
  --gpu-layers -1 \
  --reasoning-budget 0
```

Start the server (Windows):
```bat
tools\llama-cpp\llama-server.exe -m models\qwen3.5-0.8b-q8_0.gguf --port 8000 --ctx-size 4096 --n-predict 512 --no-mmap -t 4 --reasoning-budget 0
```

**Flag notes:**
- `--gpu-layers -1`: offload all layers to Metal GPU (Apple Silicon) — expect 3-5s turns vs ~18s on CPU
- `--no-mmap`: loads weights into RAM entirely — better for Linux CPU; skip on Apple Silicon with GPU offload
- `--reasoning-budget 0`: disables extended thinking mode (faster, cleaner tool responses)
- `-t 4`: CPU thread count — tune to your core count; not needed when using Metal
- `--ctx-size 4096`: supports 16-tool prompts (~2400 tokens) plus conversation history

**Alternative: `local` provider (llama-cpp-python)**

If you prefer in-process inference without a server:

```bash
uv add llama-cpp-python
# or point to an external llama-cli binary:
echo 'TALKBOT_LLAMACPP_BIN=/full/path/to/llama-cli' >> .env
```

Note: `llama-cpp-python` 0.3.16 (current PyPI release) does not support Qwen3.5 models. Use `local_server` with a pre-built llama-server binary for Qwen3.5.

### Install voice pipeline extras (VAD + STT + audio I/O)

```bash
uv sync --extra voice
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
TALKBOT_LOCAL_SERVER_MODEL=qwen3.5-0.8b-q8_0
TALKBOT_LOCAL_MODEL_PATH=./models/qwen3.5-0.8b-q8_0.gguf
TALKBOT_MAX_TOKENS=512
TALKBOT_DEFAULT_USE_TOOLS=1
TALKBOT_ENABLE_THINKING=0
TALKBOT_DEFAULT_TTS_BACKEND=kittentts

# Agent personality (optional) — applied to all CLI commands and GUI Prompt tab
# TALKBOT_AGENT_PROMPT_FILE=./prompts/tool_reliability.md
# Backward-compatible alternative:
# TALKBOT_AGENT_PROMPT="You are a brief voice assistant."
```

Optional remote provider:
```bash
TALKBOT_LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_api_key_here
```

Get OpenRouter keys at [OpenRouter](https://openrouter.ai/keys).

The application automatically loads environment variables from `.env` using python-dotenv.
Prompt presets can live in `prompts/`; switch between them by changing `TALKBOT_AGENT_PROMPT_FILE`.

### Prompt Review Workflow

Prompt files are tracked in [`prompts/catalog.json`](prompts/catalog.json) with:
- a stable preset name
- a short summary and review notes
- declared goals for linting
- the benchmark/UAT scenarios that should be used to review the prompt

Review the presets and lint them:

```bash
uv run python scripts/review_prompts.py
```

Run the prompt review scenarios as a benchmark for each preset:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/review_prompts.py \
  --run-benchmark \
  --provider local_server \
  --model qwen3.5-0.8b-q8_0 \
  --local-server-url http://127.0.0.1:8000/v1
```

If the review script reports prompt errors, fix those before trusting benchmark results. The current lint checks catch things like missing review scenarios, missing tool/voice guidance, and references to tools that do not exist.

For ad hoc benchmark A/B runs on a single prompt preset, `scripts/benchmark_conversations.py` also supports:

```bash
uv run python scripts/benchmark_conversations.py \
  --prompt-preset tool_reliability \
  --provider local_server \
  --model qwen3.5-0.8b-q8_0 \
  --local-server-url http://127.0.0.1:8000/v1
```

The generated leaderboard now includes a `Prompt` column on run tables plus a `Prompt Impact` section that compares prompt variants on the same model/runtime slice.

### Default Runtime Behavior

- Default LLM provider: `local_server`
- Default TTS backend: `kittentts`
- Default thinking mode: OFF (`TALKBOT_ENABLE_THINKING=0`) — faster conversational turns
- Default tools toggle: ON in GUI (`TALKBOT_DEFAULT_USE_TOOLS=1`)
- `TALKBOT_MAX_TOKENS`: generation cap used by the GUI Max Tokens field (default 512)
- `TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=1`: enables deterministic local intent routing (off by default)

## Usage

### Provider Feature Matrix

| Provider | Runs Where | Tool Calling | Setup Complexity | Recommended For |
|---|---|---|---|---|
| `local_server` | OpenAI-compatible local server (`llama-server`) | Yes (standard tools flow; includes `<tool_call>` text fallback) | Medium | **Default — best local option for tool-calling** |
| `local` | In-process (`llama-cpp-python` or `llama-cli`) | Yes (text-call tool parsing + local execution) | Low | Fastest local CPU path without server |
| `openrouter` | Remote API | Yes | Low | Easiest cloud setup / strongest tool reliability |

### LLM Provider Selection

```bash
# Local server (default)
talkbot --provider local_server --local-server-url http://127.0.0.1:8000/v1 --model qwen3.5-0.8b-q8_0 chat "Hello"

# Local in-process
talkbot --provider local --local-model-path ./models/qwen3.5-0.8b-q8_0.gguf chat "Hello"

# OpenRouter
talkbot --provider openrouter --api-key "$OPENROUTER_API_KEY" --model openai/gpt-4o-mini chat "Hello"

# Toggle thinking mode (default is --no-thinking)
talkbot --thinking chat "Think deeply"
talkbot --no-thinking chat "Respond quickly"
```

### Troubleshooting: `llama.cpp binary not found ... TALKBOT_LLAMACPP_BIN`

This applies only when using `provider=local`. Use `local_server` instead (recommended), or:

```bash
# Fix A: install python backend
uv add llama-cpp-python

# Fix B: point to external binary
echo 'TALKBOT_LLAMACPP_BIN=/full/path/to/llama-cli' >> .env
```

### CLI Commands

#### Single Message
```bash
# Basic chat
talkbot chat "Hello, how are you?"

# Without speaking
talkbot chat --no-speak "Just text please"

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

# Or set TALKBOT_AGENT_PROMPT_FILE / TALKBOT_AGENT_PROMPT in .env / env and omit --system
export TALKBOT_AGENT_PROMPT_FILE=./prompts/tool_reliability.md
talkbot say --tools
```

List and review prompt presets before changing the default:

```bash
uv run python scripts/review_prompts.py --preset tool_reliability
```

#### Local Voice Chat (Half-Duplex, VAD-Gated)
```bash
# Start local voice loop (Ctrl+C to stop)
talkbot voice-chat

# Enable tools while in voice loop
talkbot voice-chat --tools

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
talkbot doctor-tts
talkbot doctor-tts --backend kittentts
talkbot doctor-tts --synthesize   # deep check with real synthesis
```

#### Diagnose Voice Pipeline
```bash
talkbot doctor-voice
talkbot doctor-voice --stt-model small.en
```

#### Test Transcription Only (No LLM/TTS)
```bash
talkbot test-stt
talkbot test-stt --file sample.wav
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
talkbot tool "How long until 5pm?"
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
talkbot tool "Add eggs, butter, and flour to my grocery list"
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
| `time_until` | Utility | Time remaining until a given time or date |
| `calculator` | Utility | Safe math: `+`, `-`, `*`, `/`, `sqrt`, `sin`, `log`, `pi`, … |
| `roll_dice` | Utility | Roll N dice with D sides |
| `flip_coin` | Utility | Heads or tails |
| `random_number` | Utility | Random integer in a range |
| `web_search` | Search | DuckDuckGo instant answers (facts, definitions, conversions) |
| `set_timer` | Timer | Named countdown — fires spoken "{label} is done!" alert |
| `set_reminder` | Timer | Custom spoken message fires at a future time |
| `cancel_timer` | Timer | Cancel an active timer or reminder by ID |
| `list_timers` | Timer | Show all running timers/reminders with remaining time |
| `create_list` | Lists | Create a new empty named list |
| `add_to_list` | Lists | Add one or more items to a named list (accepts string or array) |
| `get_list` | Lists | Read all items from a named list |
| `remove_from_list` | Lists | Remove an item from a named list (case-insensitive) |
| `clear_list` | Lists | Empty a named list |
| `list_all_lists` | Lists | Show all named lists and their contents |
| `remember` | Memory | Store a key-value preference that persists across sessions |
| `recall` | Memory | Look up a stored preference by key |
| `recall_all` | Memory | Dump all stored preferences |

Lists are stored in `~/.talkbot/lists.json`; memory in `~/.talkbot/memory.json`.

## Available Models

### Recommended Local Models (llama-server, CPU)

Benchmarked on i7-10610U (15W, CPU-only, ~40 GB/s memory bandwidth). See `benchmarks/published/latest/leaderboard.md` for current results.

| Model | File | Size | Success | Gen/s | Notes |
|---|---|---|---|---|---|
| qwen3.5-0.8b Q8_0 | `qwen3.5-0.8b-q8_0.gguf` | 775 MB | **90%** | 21 | **Recommended default** |
| qwen3.5-0.8b Q4_K_M | `qwen3.5-0.8b-q4_k_m.gguf` | 508 MB | 80% | 23 | Fastest; slight arg precision loss |
| qwen3.5-2b Q4_K_M | `qwen3.5-2b-q4_k_m.gguf` | 1.2 GB | 90% | 11 | Ties 0.8b, 2× slower |
| qwen3.5-4b Q4_K_M | `qwen3.5-4b-q4_k_m.gguf` | 2.7 GB | 70% | 6 | Borderline for voice; not recommended |

> **Non-monotonic scaling:** larger models are not better for tool use on this hardware class. The 0.8b Q8_0 matches or beats larger models while using 3–4× less memory.

Download models from [bartowski/Qwen_Qwen3.5 GGUF](https://huggingface.co/bartowski) on HuggingFace.

### Remote Models (OpenRouter)

Any model available on OpenRouter can be used. See [OpenRouter Models](https://openrouter.ai/models) for the full list.

## TTS Backends

The application automatically selects the best available TTS backend:

### 1. KittenTTS (Local Neural) — Default
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
- Beautiful dark color scheme
- Rounded buttons with hover effects
- Stop button to interrupt AI responses
- Real-time sliders for rate and volume
- Styled chat history with user/AI colors
- **Backend switcher** — Toggle between online/offline TTS modes
- **Use Tools toggle** — Enable all 21 built-in tools for chat and voice
- **Timers tab** — Live countdown display, updates every second
- **Lists tab** — Live view of all named lists, updates every 2 seconds
- **Prompt tab** — Edit the agent system prompt live; pre-populated from `TALKBOT_AGENT_PROMPT_FILE` or `TALKBOT_AGENT_PROMPT` on launch

```bash
uv run talkbot-gui
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

## Conversation Benchmarking

TalkBot evaluates the full voice pipeline — STT accuracy, LLM tool use, and TTS latency — to find the best model combinations per hardware class. See **[`benchmarks/README.md`](benchmarks/README.md)** for the full evaluation framework, current leaderboards, and how to add a new machine.

Use scripted multi-turn conversations to score tool reliability, latency, context usage, and memory footprint.

### Run a benchmark

```bash
# Start llama-server first (see above), then:
uv run python scripts/benchmark_conversations.py \
  --provider local_server \
  --local-server-url "http://127.0.0.1:8000/v1" \
  --local-model-path "models/qwen3.5-0.8b-q8_0.gguf" \
  --model "qwen3.5-0.8b-q8_0" \
  --run-name "my-run" \
  --runner-label "my-machine"
```

### Run a model matrix

```bash
uv run python scripts/benchmark_conversations.py \
  --matrix benchmarks/model_matrix.example.json \
  --runner-label my-machine
```

Matrix profiles can also set `prompt_preset`, `prompt_catalog`, or `prompt_file` so the same model can be benchmarked across multiple prompt variants as a first-class comparison.

See `benchmarks/model_matrix.example.json` for the current active model set and `benchmarks/decision_strategy.md` for hardware-specific decisions.

### Run a prompt matrix

```bash
uv run python scripts/benchmark_conversations.py \
  --matrix benchmarks/model_matrix.prompts.example.json \
  --runner-label my-machine
```

Use `benchmarks/model_matrix.prompts.example.json` when you want prompt A/B comparisons on the same model/runtime slice. The resulting leaderboard will populate the `Prompt Impact` section directly.

### Benchmark outputs

- `benchmark_results/latest/results.json` — per-run traces + metrics
- `benchmark_results/latest/leaderboard.md` — ranking board
- `benchmarks/published/latest/leaderboard.md` — repo-published snapshot (check this for "what model to use")
- `benchmarks/published/runs/<run_name>/` — archived run history

Key metrics: `task_success_rate`, `tool_selection_accuracy`, `argument_accuracy`, `avg_turn_latency_ms`, `avg_gen_tok_s`, `peak_memory_mb`.

### Benchmark scenario suite (10 scenarios)

Scenarios live in `tests/conversations/` and support per-turn assertions:
- expected tool names (`name` or `name_any`)
- argument subset checks (`args_contains`)
- response checks (`response_contains`, `response_regex`)

Categories:
- `core`: timer/list/memory tool correctness
- `recovery`: invalid request then retry/fix behavior
- `multistep`: chained workflows across multiple turns
- `context`: retrieval under longer conversational history
- `robustness`: noisy/edge-case prompts

Decision policy and hardware notes: `benchmarks/decision_strategy.md`

### OpenRouter benchmarking (apples-to-apples)

To force native tool-calling compatibility:

```bash
export TALKBOT_OPENROUTER_TOOL_TRANSPORT=native
export TALKBOT_OPENROUTER_TOOL_PREFLIGHT=1
```

Models/routes that do not advertise native `tools` + `tool_choice` will fail fast instead of using prompt-tool fallback.

## Project Structure

```
talkbot/
├── src/talkbot/
│   ├── __init__.py        # Package initialization
│   ├── openrouter.py      # OpenRouter API client with tool support
│   ├── llm.py             # LLM provider abstraction (local, local_server, openrouter)
│   ├── tools.py           # 21 built-in tools (calculator, timers, lists, memory, etc.)
│   ├── tts.py             # Text-to-speech manager
│   ├── voice.py           # Voice pipeline (VAD + STT + LLM + TTS)
│   ├── cli.py             # Click CLI interface
│   └── gui.py             # Modern themed tkinter GUI
├── models/                # GGUF model files (git-ignored)
├── scripts/
│   ├── benchmark_conversations.py  # Conversation benchmark runner
│   ├── ollama_nothink_proxy.py     # Ollama think:false proxy (comparison baseline)
│   └── download_model.py           # GGUF downloader
├── benchmarks/
│   ├── model_matrix.example.json   # Active benchmark model set
│   ├── model_matrix.prompts.example.json # Prompt A/B matrix example
│   ├── decision_strategy.md        # Hardware-specific model decisions
│   └── published/                  # Published benchmark results
│       ├── latest/                 # Current best result
│       └── runs/                   # Per-run history
├── tests/conversations/   # Benchmark conversation scenarios (10 scenarios)
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
