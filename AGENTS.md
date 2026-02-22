# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TalkBot is a conversational AI assistant that uses the OpenRouter API for LLM access and supports text-to-speech output via Microsoft Edge TTS (online) or pyttsx3 (offline fallback). It provides both a Click-based CLI and a tkinter GUI.

## Commands

```bash
# Install dependencies
uv sync

# Run CLI commands
uv run talkbot chat "Hello"          # Single message
uv run talkbot say                   # Interactive chat loop
uv run talkbot tool "What time?"     # Chat with tool calling
uv run talkbot voices                # List TTS voices
uv run talkbot save "Text" out.wav   # Save TTS to file

# Run GUI
uv run python -m talkbot.gui
```

No test suite or linter is configured yet.

## Architecture

All source lives in `src/talkbot/`. The package exposes `OpenRouterClient`, `TTSManager`, and `tools` from `__init__.py`.

**openrouter.py** — `OpenRouterClient` wraps the OpenRouter API (`httpx`). Key method is `chat_with_tools()` which implements the function-calling loop: send messages → receive tool calls → execute tools → send results back, up to a configurable max iterations.

**tools.py** — Defines built-in tools (calculator, time, dice, coin, random number) with JSON Schema definitions in `TOOL_DEFINITIONS` and function references in `TOOLS` dict. `register_all_tools(client)` wires them into an `OpenRouterClient`.

**tts.py** — `TTSManager` provides a unified interface over two backends: `EdgeTTS` (async, 322 voices, uses pygame for playback) and `Pyttsx3TTS` (offline, system voices). Auto-detects the best available backend. Uses an internal queue and worker thread for non-blocking speech.

**cli.py** — Click command group with subcommands (`chat`, `say`, `tool`, `voices`, `save`). Loads `.env` via python-dotenv.

**gui.py** — Tkinter GUI with dark theme (Catppuccin-inspired). Uses worker threads for API calls and TTS to keep the UI responsive, coordinated via `root.after()` callbacks and a stop event.

## Key Patterns

- `OpenRouterClient` is a context manager (ensures httpx client cleanup)
- Edge TTS is async; TTS module bridges this with `asyncio.run()` inside worker threads
- GUI threading: response and speaking run in background threads; all UI updates go through `root.after()`
- Environment config: `OPENROUTER_API_KEY` (required), `OPENROUTER_SITE_URL`, `OPENROUTER_SITE_NAME` loaded from `.env`
- Entry point: `talkbot` CLI command → `talkbot.cli:main`
- Build system: Hatchling with source layout (`src/talkbot/`)
- Python version: 3.10+
