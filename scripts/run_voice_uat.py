#!/usr/bin/env python3
"""Guided voice UAT: user says prompted phrases, then hears the response.

This is a manual acceptance script for the real user flow:
mic -> STT -> LLM/tools -> TTS

It prints the phrase to say for each step, listens once, shows the transcript,
speaks the assistant response, and records a simple pass/fail summary.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from talkbot.llm import LLMProviderError, create_llm_client, supports_tools
from talkbot.text_utils import strip_thinking
from talkbot.tools import register_all_tools, set_alert_callback
from talkbot.tts import TTSManager
from talkbot.voice import MissingVoiceDependencies, VoiceConfig, VoicePipeline


load_dotenv()


DEFAULT_LOCAL_SERVER_MODEL = "qwen3.5-0.8b-q8_0.gguf"


@dataclass(frozen=True)
class VoiceStep:
    name: str
    phrase: str
    expect: str


STEPS = [
    VoiceStep("Ask Time", "What time is it?", "Hear the current time."),
    VoiceStep(
        "Ask Information",
        "What is 15 percent of 47 dollars?",
        "Hear a calculator answer close to 7.05.",
    ),
    VoiceStep(
        "Remember Something",
        "Remember that my project codename is Falcon.",
        "Hear a confirmation that Falcon was remembered.",
    ),
    VoiceStep(
        "Recall Something",
        "What did you remember about my project codename?",
        "Hear Falcon read back.",
    ),
    VoiceStep(
        "Make Grocery List",
        "Create a grocery list and add milk.",
        "Hear confirmation that milk was added to the grocery list.",
    ),
    VoiceStep(
        "Read Grocery List",
        "What is on my grocery list?",
        "Hear milk read back from the grocery list.",
    ),
    VoiceStep(
        "Set Timer",
        "Set a timer for 3 seconds.",
        "Hear timer confirmation now, then a spoken timer alert a few seconds later.",
    ),
]


def _default_provider() -> str:
    return os.getenv("TALKBOT_LLM_PROVIDER", "local_server")


def _default_model(provider: str) -> str:
    if provider == "local_server":
        configured = (os.getenv("TALKBOT_LOCAL_SERVER_MODEL") or "").strip()
        return configured or DEFAULT_LOCAL_SERVER_MODEL
    if provider == "openrouter":
        return (os.getenv("TALKBOT_DEFAULT_MODEL") or "mistralai/ministral-3b-2512").strip()
    return (os.getenv("TALKBOT_DEFAULT_MODEL") or "qwen/qwen3-1.7b").strip()


def _maybe_int(value: str | None):
    if value is None:
        return None
    return int(value) if value.isdigit() else value


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
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Persistent tool data directory. Defaults to a temporary isolated directory.",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Keep the temporary data directory when the script exits.",
    )
    return parser.parse_args(argv)


def _prompt_choice(prompt: str, valid: set[str]) -> str:
    while True:
        value = input(prompt).strip().lower()
        if value in valid:
            return value


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if args.data_dir:
        data_dir = Path(args.data_dir).expanduser()
        data_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = tempfile.TemporaryDirectory(prefix="talkbot-voice-uat-")
        data_dir = Path(temp_dir.name)

    os.environ["TALKBOT_DATA_DIR"] = str(data_dir)
    os.environ["TALKBOT_LOCAL_DIRECT_TOOL_ROUTING"] = "1"

    config = VoiceConfig(
        sample_rate=args.sample_rate,
        vad_threshold=args.vad_threshold,
        min_silence_ms=args.vad_min_silence_ms,
        stt_model=args.stt_model,
        stt_language=args.language,
        device_in=_maybe_int(args.device_in),
        device_out=_maybe_int(args.device_out),
    )

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

    print("Voice UAT")
    print("=========")
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model}")
    print(f"Server: {args.local_server_url}")
    print(f"Data dir: {data_dir}")
    print(f"TTS: {'off' if args.no_speak else args.backend}")
    print()
    print("For each step:")
    print("1. press Enter")
    print("2. say the shown phrase")
    print("3. pause and let STT finish")
    print("4. listen to the spoken result")
    print()

    messages: list[dict[str, str]] = []
    if args.system:
        messages.append({"role": "system", "content": args.system})

    results: list[tuple[str, bool]] = []

    try:
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

            tts = None
            if not args.no_speak:
                tts = TTSManager(rate=args.rate, volume=args.volume, backend=args.backend or None)
                if args.voice:
                    tts.set_voice(args.voice)
                set_alert_callback(tts.speak)
                print("TTS: Ready to go.")
                tts.speak("Ready to go.")
            else:
                print("Ready to go.")

            for idx, step in enumerate(STEPS, start=1):
                print(f"[{idx}/{len(STEPS)}] {step.name}")
                print(f"Say: {step.phrase}")
                print(f"Expected: {step.expect}")

                while True:
                    action = _prompt_choice(
                        "Press Enter to listen, or type [s]kip / [q]uit: ",
                        {"", "s", "q"},
                    )
                    if action == "s":
                        results.append((step.name, False))
                        print("Skipped.\n")
                        break
                    if action == "q":
                        raise KeyboardInterrupt

                    print("Listening...", flush=True)
                    transcript = pipeline.transcribe_once()
                    if not transcript:
                        retry = _prompt_choice(
                            "No transcript. Retry? [Enter=yes / s=skip / q=quit]: ",
                            {"", "s", "q"},
                        )
                        if retry == "":
                            continue
                        if retry == "s":
                            results.append((step.name, False))
                            print("Skipped.\n")
                            break
                        raise KeyboardInterrupt

                    print(f"STT: {transcript}")
                    messages.append({"role": "user", "content": transcript})

                    if not args.no_tools and supports_tools(client):
                        response = client.chat_with_tools(messages)
                    else:
                        response = client.simple_chat(transcript, system_prompt=args.system or None)

                    visible = strip_thinking(response)
                    print(f"AI: {visible}")
                    messages.append({"role": "assistant", "content": visible})

                    if tts is not None:
                        tts.speak(visible)

                    verdict = _prompt_choice(
                        "Did this step work for you? [Enter=yes / n=no / r=retry / q=quit]: ",
                        {"", "n", "r", "q"},
                    )
                    if verdict == "":
                        results.append((step.name, True))
                        print()
                        break
                    if verdict == "n":
                        results.append((step.name, False))
                        print()
                        break
                    if verdict == "r":
                        messages.pop()
                        messages.pop()
                        print("Retrying the same step.\n")
                        continue
                    raise KeyboardInterrupt

            print("Summary")
            print("=======")
            passed = sum(1 for _name, ok in results if ok)
            print(f"Passed: {passed}/{len(results)}")
            for name, ok in results:
                print(f"[{'PASS' if ok else 'FAIL'}] {name}")
            return 0 if passed == len(STEPS) else 1
    except MissingVoiceDependencies as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print("Install voice dependencies with: uv sync --extra voice", file=sys.stderr)
        return 1
    except (LLMProviderError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nStopped.")
        return 130
    finally:
        if temp_dir is not None and not args.keep_data:
            temp_dir.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
