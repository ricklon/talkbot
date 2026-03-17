#!/usr/bin/env python3
"""Single-turn voice smoke test: STT -> LLM/tools -> TTS.

Readable manual check for the user-facing pipeline on the current machine.

Examples:
  UV_CACHE_DIR=.uv-cache TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=1 \
    uv run python scripts/manual_voice_smoke.py

  UV_CACHE_DIR=.uv-cache TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=1 \
    uv run python scripts/manual_voice_smoke.py --no-speak
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from talkbot.llm import LLMProviderError, create_llm_client, supports_tools
from talkbot.text_utils import strip_thinking
from talkbot.tools import register_all_tools
from talkbot.tts import TTSManager
from talkbot.voice import MissingVoiceDependencies, VoiceConfig, VoicePipeline


load_dotenv()


DEFAULT_LOCAL_SERVER_MODEL = "qwen3.5-0.8b-q8_0.gguf"


def _default_provider() -> str:
    return os.getenv("TALKBOT_LLM_PROVIDER", "local_server")


def _default_model(provider: str) -> str:
    if provider == "local_server":
        return (os.getenv("TALKBOT_LOCAL_SERVER_MODEL") or DEFAULT_LOCAL_SERVER_MODEL).strip()
    if provider == "openrouter":
        return (os.getenv("TALKBOT_DEFAULT_MODEL") or "mistralai/ministral-3b-2512").strip()
    return (os.getenv("TALKBOT_DEFAULT_MODEL") or "qwen/qwen3-1.7b").strip()


def parse_args(argv: list[str]) -> argparse.Namespace:
    provider = _default_provider()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", default=provider, choices=["local", "local_server", "openrouter"])
    parser.add_argument("--model", default=_default_model(provider))
    parser.add_argument("--local-server-url", default=os.getenv("TALKBOT_LOCAL_SERVER_URL", "http://127.0.0.1:8000/v1"))
    parser.add_argument("--local-server-api-key", default=os.getenv("TALKBOT_LOCAL_SERVER_API_KEY", ""))
    parser.add_argument("--api-key", default=os.getenv("OPENROUTER_API_KEY", ""))
    parser.add_argument("--local-model-path", default=os.getenv("TALKBOT_LOCAL_MODEL_PATH", ""))
    parser.add_argument("--llamacpp-bin", default=os.getenv("TALKBOT_LLAMACPP_BIN", "llama-cli"))
    parser.add_argument("--backend", default=os.getenv("TALKBOT_DEFAULT_TTS_BACKEND", "kittentts"))
    parser.add_argument("--voice", default=None)
    parser.add_argument("--rate", type=int, default=175)
    parser.add_argument("--volume", type=float, default=1.0)
    parser.add_argument("--stt-model", default="small.en")
    parser.add_argument("--language", default="en")
    parser.add_argument("--vad-threshold", type=float, default=0.3)
    parser.add_argument("--vad-min-silence-ms", type=int, default=1200)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--device-in", default=None)
    parser.add_argument("--device-out", default=None)
    parser.add_argument("--system", default=os.getenv("TALKBOT_AGENT_PROMPT", ""))
    parser.add_argument("--no-tools", action="store_true")
    parser.add_argument("--no-speak", action="store_true")
    return parser.parse_args(argv)


def _maybe_int(value: str | None):
    if value is None:
        return None
    return int(value) if value.isdigit() else value


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    config = VoiceConfig(
        sample_rate=args.sample_rate,
        vad_threshold=args.vad_threshold,
        min_silence_ms=args.vad_min_silence_ms,
        stt_model=args.stt_model,
        stt_language=args.language,
        device_in=_maybe_int(args.device_in),
        device_out=_maybe_int(args.device_out),
    )

    try:
        print("STT: speak once, then pause.", flush=True)
        pipeline = VoicePipeline(
            api_key=args.api_key or None,
            provider=args.provider,
            model=args.model,
            local_model_path=args.local_model_path or None,
            llamacpp_bin=args.llamacpp_bin or None,
            local_server_url=args.local_server_url or None,
            local_server_api_key=args.local_server_api_key or None,
            tts_backend=args.backend or None,
            tts_voice=args.voice,
            tts_rate=args.rate,
            tts_volume=args.volume,
            speak=False,
            system_prompt=args.system or None,
            use_tools=not args.no_tools,
            config=config,
        )
        transcript = pipeline.transcribe_once()
        if not transcript:
            print("STT: no transcript generated.", flush=True)
            return 1
        print(f"STT: {transcript}", flush=True)

        print("LLM: generating response...", flush=True)
        with create_llm_client(
            provider=args.provider,
            model=args.model,
            api_key=args.api_key or None,
            local_model_path=args.local_model_path or None,
            llamacpp_bin=args.llamacpp_bin or None,
            local_server_url=args.local_server_url or None,
            local_server_api_key=args.local_server_api_key or None,
        ) as client:
            if not args.no_tools and supports_tools(client):
                register_all_tools(client)
                response = client.chat_with_system_tools(transcript, system_prompt=args.system or None)
            else:
                response = client.simple_chat(transcript, system_prompt=args.system or None)

        visible = strip_thinking(response)
        print(f"LLM: {visible}", flush=True)

        if args.no_speak:
            print("TTS: skipped (--no-speak).", flush=True)
            return 0

        print(f"TTS: speaking via {args.backend}...", flush=True)
        tts = TTSManager(rate=args.rate, volume=args.volume, backend=args.backend or None)
        if args.voice:
            tts.set_voice(args.voice)
        tts.speak(visible)
        print("TTS: done.", flush=True)
        return 0
    except MissingVoiceDependencies as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print("Install voice dependencies with: uv sync --extra voice", file=sys.stderr)
        return 1
    except (LLMProviderError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
