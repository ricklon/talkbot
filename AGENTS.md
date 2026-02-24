# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TalkBot is a voice-first conversational AI assistant with a configurable agent personality. It uses local llama.cpp (default), an OpenAI-compatible local server, or OpenRouter for LLM access. TTS is handled by KittenTTS (local neural, default), Microsoft Edge TTS (online), or pyttsx3 (offline fallback). Provides both a Click-based CLI and a tkinter GUI.

## Commands

```bash
# Install dependencies
uv sync

# Run CLI commands
uv run talkbot chat "Hello"                          # Single message
uv run talkbot say                                   # Interactive chat loop
uv run talkbot say --tools --system "You are Alexa" # Interactive with tools + persona
uv run talkbot tool "What time?"                     # Chat with tool calling
uv run talkbot voice-chat --tools                    # Voice loop with tools
uv run talkbot voices                                # List TTS voices
uv run talkbot save "Text" out.wav                   # Save TTS to file
uv run talkbot doctor-tts                            # TTS backend diagnostics
uv run talkbot doctor-voice                          # Voice pipeline diagnostics

# Run GUI
uv run python -m talkbot.gui

# Agent prompt via env (applies to all commands)
export TALKBOT_AGENT_PROMPT="You are a brief voice assistant. Always prefer tool calls."
uv run talkbot say --tools
```

No test suite or linter is configured yet.

## Dependency Note

- As of 2026-02-24, `kittentts` is installed from PyPI (`kittentts>=0.1.0`) instead of a direct GitHub wheel URL.
- This avoids `uv` lockfile parse failures caused by wheel filename/version mismatches.
- `UV_SKIP_WHEEL_FILENAME_CHECK` is no longer required for normal `uv` commands in this repo.

## Architecture

All source lives in `src/talkbot/`. The package exposes `OpenRouterClient`, `TTSManager`, and `tools` from `__init__.py`.

**openrouter.py** — `OpenRouterClient` wraps the OpenRouter API (`httpx`). Key method is `chat_with_tools()` which implements the function-calling loop: send messages → receive tool calls → execute tools → send results back, up to a configurable max iterations.

**tools.py** — 17 built-in tools in four categories:
- *Utility*: `get_current_time`, `get_current_date`, `calculator`, `roll_dice`, `flip_coin`, `random_number`
- *Timer*: `set_timer` (returns ID, fires via TTS alert callback), `cancel_timer`, `list_timers`
- *Lists*: `add_to_list`, `get_list`, `remove_from_list`, `clear_list` (persisted to `~/.talkbot/lists.json`)
- *Memory*: `remember`, `recall`, `recall_all` (persisted to `~/.talkbot/memory.json`)

JSON Schema definitions live in `TOOL_DEFINITIONS`; callable references in `TOOLS` dict. `register_all_tools(client)` wires them into a client. `set_alert_callback(fn)` injects the TTS speak function so timer alerts are spoken rather than just printed.

**tts.py** — `TTSManager` provides a unified interface over two backends: `EdgeTTS` (async, 322 voices, uses pygame for playback) and `Pyttsx3TTS` (offline, system voices). Auto-detects the best available backend. Uses an internal queue and worker thread for non-blocking speech.

**cli.py** — Click command group. Subcommands: `chat`, `say`, `tool`, `voice-chat`, `voices`, `save`, `doctor-tts`, `doctor-voice`, `test-stt`. All conversation commands accept `--system/-s` (or `TALKBOT_AGENT_PROMPT` env var fallback). Loads `.env` via python-dotenv.

**gui.py** — Tkinter GUI with dark theme (Catppuccin-inspired). Uses worker threads for API calls and TTS to keep the UI responsive, coordinated via `root.after()` callbacks and a stop event. Includes a **Prompt tab** for editing the agent system prompt live; pre-populated from `TALKBOT_AGENT_PROMPT` on launch.

## Key Patterns

- `OpenRouterClient` is a context manager (ensures httpx client cleanup)
- Edge TTS is async; TTS module bridges this with `asyncio.run()` inside worker threads
- GUI threading: response and speaking run in background threads; all UI updates go through `root.after()`
- **Agent prompt**: `TALKBOT_AGENT_PROMPT` env var sets a default system prompt for all CLI commands; GUI pre-populates the Prompt tab from it
- **TTS alert callback**: `tools.set_alert_callback(tts.speak)` is called after TTS init in CLI and GUI so timer alerts are spoken; falls back to stdout print if unset
- **Timer cancel**: uses `threading.Event.wait(timeout=seconds)` — setting the event cancels instantly with no polling
- **Persistent storage**: lists and memory tools store JSON files under `~/.talkbot/`; available across sessions
- Environment config: `OPENROUTER_API_KEY` (required for openrouter), `OPENROUTER_SITE_URL`, `OPENROUTER_SITE_NAME` loaded from `.env`
- Entry point: `talkbot` CLI command → `talkbot.cli:main`
- Build system: Hatchling with source layout (`src/talkbot/`)
- Python version: 3.10+
