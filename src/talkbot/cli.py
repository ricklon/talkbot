"""CLI for the talking bot using Click."""

import os
import sys
import tempfile
from pathlib import Path

import click
from dotenv import load_dotenv

# Load environment variables from .env file before importing runtime modules.
env_path = Path.cwd() / ".env"
if env_path.exists():
    load_dotenv(env_path)

from talkbot.llm import LLMProviderError, create_llm_client, supports_tools
from talkbot.thinking import apply_thinking_system_prompt, env_thinking_default
from talkbot.text_utils import strip_thinking
from talkbot.tools import register_all_tools
from talkbot.tts import TTSManager
from talkbot.voice import (
    MissingVoiceDependencies,
    VoiceConfig,
    VoicePipeline,
    run_voice_diagnostics,
    transcribe_audio_file,
)


def _default_tts_backend() -> str:
    return os.getenv("TALKBOT_DEFAULT_TTS_BACKEND", "kittentts")


def _default_provider() -> str:
    return os.getenv("TALKBOT_LLM_PROVIDER", "local")


def _default_local_model_path() -> str:
    configured = os.getenv("TALKBOT_LOCAL_MODEL_PATH", "").strip()
    if configured:
        return configured
    default_path = Path("models/default.gguf")
    if default_path.exists():
        return str(default_path)
    return ""


def _create_client_from_ctx(ctx: click.Context):
    return create_llm_client(
        provider=ctx.obj["provider"],
        model=ctx.obj["model"],
        api_key=ctx.obj["api_key"],
        site_url=os.getenv("OPENROUTER_SITE_URL"),
        site_name=os.getenv("OPENROUTER_SITE_NAME"),
        local_model_path=ctx.obj["local_model_path"],
        llamacpp_bin=ctx.obj["llamacpp_bin"],
        local_server_url=ctx.obj["local_server_url"],
        local_server_api_key=ctx.obj["local_server_api_key"],
        enable_thinking=ctx.obj["enable_thinking"],
    )


@click.group()
@click.option("--api-key", envvar="OPENROUTER_API_KEY", help="OpenRouter API key")
@click.option(
    "--provider",
    type=click.Choice(["local", "local_server", "openrouter"]),
    default=lambda: _default_provider(),
    show_default="env:TALKBOT_LLM_PROVIDER or local",
    help="LLM provider",
)
@click.option(
    "--model",
    default=lambda: os.getenv("TALKBOT_DEFAULT_MODEL", "qwen/qwen3-1.7b"),
    show_default="env:TALKBOT_DEFAULT_MODEL or qwen/qwen3-1.7b",
    help="Model id (OpenRouter) or local label",
)
@click.option(
    "--local-model-path",
    default=lambda: _default_local_model_path(),
    show_default="env:TALKBOT_LOCAL_MODEL_PATH or models/default.gguf when present",
    help="Local GGUF path used when provider=local",
)
@click.option(
    "--llamacpp-bin",
    default=lambda: os.getenv("TALKBOT_LLAMACPP_BIN", "llama-cli"),
    show_default="env:TALKBOT_LLAMACPP_BIN or llama-cli",
    help="llama.cpp executable for provider=local",
)
@click.option(
    "--local-server-url",
    default=lambda: os.getenv("TALKBOT_LOCAL_SERVER_URL", "http://127.0.0.1:8000/v1"),
    show_default="env:TALKBOT_LOCAL_SERVER_URL or http://127.0.0.1:8000/v1",
    help="OpenAI-compatible local server base URL for provider=local_server",
)
@click.option(
    "--local-server-api-key",
    default=lambda: os.getenv("TALKBOT_LOCAL_SERVER_API_KEY", ""),
    show_default="env:TALKBOT_LOCAL_SERVER_API_KEY",
    help="Optional API key for provider=local_server",
)
@click.option(
    "--thinking/--no-thinking",
    default=lambda: env_thinking_default(),
    show_default="env:TALKBOT_ENABLE_THINKING or no-thinking",
    help="Enable deliberate thinking mode (slower)",
)
@click.pass_context
def cli(
    ctx: click.Context,
    api_key: str,
    provider: str,
    model: str,
    local_model_path: str,
    llamacpp_bin: str,
    local_server_url: str,
    local_server_api_key: str,
    thinking: bool,
) -> None:
    """TalkBot - A talking AI assistant using OpenRouter and pyttsx3."""
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["provider"] = provider
    ctx.obj["model"] = model
    ctx.obj["local_model_path"] = local_model_path or None
    ctx.obj["llamacpp_bin"] = llamacpp_bin or "llama-cli"
    ctx.obj["local_server_url"] = local_server_url or None
    ctx.obj["local_server_api_key"] = local_server_api_key or None
    ctx.obj["enable_thinking"] = thinking


@cli.command()
@click.argument("message")
@click.option("--speak/--no-speak", default=True, help="Speak the response")
@click.option(
    "--backend",
    type=click.Choice(["edge-tts", "kittentts", "pyttsx3"]),
    default=None,
    help="TTS backend to use (auto-detect if omitted)",
)
@click.option("--voice", help="Voice ID to use")
@click.option("--rate", default=150, help="Speech rate (words per minute)")
@click.option("--volume", default=1.0, help="Volume level (0.0 to 1.0)")
@click.option("--system", "-s", help="System prompt for context")
@click.option("--tools/--no-tools", default=False, help="Enable built-in tools")
@click.pass_context
def chat(
    ctx: click.Context,
    message: str,
    speak: bool,
    backend: str,
    voice: str,
    rate: int,
    volume: float,
    system: str,
    tools: bool,
) -> None:
    """Chat with the AI and hear the response."""
    try:
        selected_backend = backend or _default_tts_backend()
        system = apply_thinking_system_prompt(system, ctx.obj["enable_thinking"])
        with _create_client_from_ctx(ctx) as client:
            click.echo(f"You: {message}")
            if tools:
                if supports_tools(client):
                    register_all_tools(client)
                response = client.chat_with_system_tools(message, system_prompt=system)
            else:
                response = client.simple_chat(message, system_prompt=system)
            visible_response = strip_thinking(response)
            click.echo(f"AI: {visible_response}")

            if speak:
                tts = TTSManager(rate=rate, volume=volume, backend=selected_backend)
                if voice:
                    tts.set_voice(voice)
                tts.speak(visible_response)
    except (ValueError, LLMProviderError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--backend",
    type=click.Choice(["edge-tts", "kittentts", "pyttsx3"]),
    default=None,
    help="TTS backend to use (auto-detect if omitted)",
)
@click.option("--voice", help="Voice ID to use")
@click.option("--rate", default=150, help="Speech rate")
@click.option("--volume", default=1.0, help="Volume level")
@click.option("--tools/--no-tools", default=False, help="Enable built-in tools")
@click.pass_context
def say(
    ctx: click.Context, backend: str, voice: str, rate: int, volume: float, tools: bool
) -> None:
    """Interactive mode - type messages and hear responses."""
    try:
        selected_backend = backend or _default_tts_backend()
        tts = TTSManager(rate=rate, volume=volume, backend=selected_backend)
        if voice:
            tts.set_voice(voice)

        with _create_client_from_ctx(ctx) as client:
            click.echo("Interactive mode started. Type 'exit' or 'quit' to stop.")
            click.echo()

            while True:
                try:
                    message = click.prompt("You", type=str)

                    if message.lower() in ("exit", "quit"):
                        break

                    if tools:
                        if supports_tools(client):
                            register_all_tools(client)
                        system = apply_thinking_system_prompt(
                            None, ctx.obj["enable_thinking"]
                        )
                        response = client.chat_with_system_tools(
                            message, system_prompt=system
                        )
                    else:
                        system = apply_thinking_system_prompt(
                            None, ctx.obj["enable_thinking"]
                        )
                        response = client.simple_chat(message, system_prompt=system)
                    visible_response = strip_thinking(response)
                    click.echo(f"AI: {visible_response}")
                    tts.speak(visible_response)

                except KeyboardInterrupt:
                    click.echo("\nGoodbye!")
                    break
                except EOFError:
                    break
    except (ValueError, LLMProviderError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--backend",
    type=click.Choice(["edge-tts", "kittentts", "pyttsx3"]),
    default=None,
    help="TTS backend to use (auto-detect if omitted)",
)
def voices(backend: str) -> None:
    """List available TTS voices."""
    selected_backend = backend or _default_tts_backend()
    tts = TTSManager(backend=selected_backend)
    tts.list_voices()


@cli.command()
@click.argument("text")
@click.argument("output")
@click.option(
    "--backend",
    type=click.Choice(["edge-tts", "kittentts", "pyttsx3"]),
    default=None,
    help="TTS backend to use (auto-detect if omitted)",
)
@click.option("--voice", help="Voice ID to use")
@click.option("--rate", default=150, help="Speech rate")
def save(text: str, output: str, backend: str, voice: str, rate: int) -> None:
    """Save text to audio file.

    TEXT: The text to convert to speech
    OUTPUT: The output filename
    """
    selected_backend = backend or _default_tts_backend()
    tts = TTSManager(rate=rate, backend=selected_backend)
    if voice:
        tts.set_voice(voice)

    tts.save_to_file(text, output)
    click.echo(f"Saved to {output}")


@cli.command("doctor-tts")
@click.option(
    "--backend",
    "backends",
    type=click.Choice(["edge-tts", "kittentts", "pyttsx3"]),
    multiple=True,
    help="Specific backend(s) to test. Defaults to all.",
)
@click.option(
    "--synthesize/--no-synthesize",
    default=False,
    help="Also test synthesis to a temp file.",
)
def doctor_tts(backends: tuple[str, ...], synthesize: bool) -> None:
    """Run TTS backend diagnostics."""
    targets = list(backends) if backends else ["edge-tts", "kittentts", "pyttsx3"]
    failures = 0

    click.echo("TTS Diagnostics")
    click.echo("==============")

    for backend in targets:
        click.echo(f"\n[{backend}]")
        try:
            tts = TTSManager(backend=backend)
            voices = tts.available_voices
            active = tts.backend_name
            click.echo(f"init: OK (active={active})")
            click.echo(f"voices: OK ({len(voices)} found)")

            if synthesize:
                suffix = ".mp3" if active == "edge-tts" else ".wav"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                    out_path = f.name

                try:
                    tts.save_to_file("TalkBot TTS backend check.", out_path)
                    size = Path(out_path).stat().st_size if Path(out_path).exists() else 0
                    if size <= 0:
                        raise RuntimeError("output file was empty")
                    click.echo(f"synthesis: OK ({size} bytes)")
                finally:
                    try:
                        Path(out_path).unlink(missing_ok=True)
                    except Exception:
                        pass

        except Exception as e:
            failures += 1
            click.echo(f"FAILED: {e}")

    click.echo("\nSummary")
    click.echo("=======")
    click.echo(f"tested: {len(targets)} backend(s)")
    click.echo(f"failed: {failures}")

    if failures:
        sys.exit(1)


@cli.command()
@click.argument("message")
@click.option("--speak/--no-speak", default=True, help="Speak the response")
@click.option(
    "--backend",
    type=click.Choice(["edge-tts", "kittentts", "pyttsx3"]),
    default=None,
    help="TTS backend to use (auto-detect if omitted)",
)
@click.option("--voice", help="Voice ID to use")
@click.option("--rate", default=150, help="Speech rate (words per minute)")
@click.option("--volume", default=1.0, help="Volume level (0.0 to 1.0)")
@click.option("--system", "-s", help="System prompt for context")
@click.pass_context
def tool(
    ctx: click.Context,
    message: str,
    speak: bool,
    backend: str,
    voice: str,
    rate: int,
    volume: float,
    system: str,
) -> None:
    """Chat with AI using tools (calculator, time, dice, etc.)."""
    try:
        selected_backend = backend or _default_tts_backend()
        system = apply_thinking_system_prompt(system, ctx.obj["enable_thinking"])
        with _create_client_from_ctx(ctx) as client:
            # Register all built-in tools
            if supports_tools(client):
                register_all_tools(client)

            click.echo(f"You: {message}")
            response = client.chat_with_system_tools(message, system_prompt=system)
            visible_response = strip_thinking(response)
            click.echo(f"AI: {visible_response}")

            if speak:
                tts = TTSManager(rate=rate, volume=volume, backend=selected_backend)
                if voice:
                    tts.set_voice(voice)
                tts.speak(visible_response)
    except (ValueError, LLMProviderError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("voice-chat")
@click.option(
    "--backend",
    type=click.Choice(["edge-tts", "kittentts", "pyttsx3"]),
    default=None,
    help="TTS backend to use (auto-detect if omitted)",
)
@click.option("--voice", help="Voice ID to use")
@click.option("--rate", default=175, help="Speech rate")
@click.option("--volume", default=1.0, help="Volume level (0.0 to 1.0)")
@click.option("--system", "-s", help="System prompt")
@click.option("--stt-model", default="small.en", help="faster-whisper model")
@click.option("--language", default="en", help="STT language")
@click.option("--vad-threshold", default=0.3, type=float, help="Silero VAD threshold")
@click.option(
    "--energy-threshold",
    default=0.003,
    type=float,
    help="RMS fallback threshold for speech detection",
)
@click.option("--vad-min-speech-ms", default=250, type=int, help="Minimum speech ms")
@click.option(
    "--vad-min-silence-ms", default=1200, type=int, help="Silence to end utterance"
)
@click.option(
    "--max-utterance-sec", default=12.0, type=float, help="Maximum utterance duration"
)
@click.option("--device-in", default=None, help="Input device index or name")
@click.option("--device-out", default=None, help="Output device index or name")
@click.option("--sample-rate", default=16000, type=int, help="Audio sample rate")
@click.option("--no-speak", is_flag=True, help="Disable spoken responses")
@click.option("--tools/--no-tools", default=False, help="Enable built-in tools")
@click.pass_context
def voice_chat(
    ctx: click.Context,
    backend: str,
    voice: str,
    rate: int,
    volume: float,
    system: str,
    stt_model: str,
    language: str,
    vad_threshold: float,
    energy_threshold: float,
    vad_min_speech_ms: int,
    vad_min_silence_ms: int,
    max_utterance_sec: float,
    device_in: str,
    device_out: str,
    sample_rate: int,
    no_speak: bool,
    tools: bool,
) -> None:
    """Local half-duplex voice chat."""

    def _maybe_int(value: str | None):
        if value is None:
            return None
        return int(value) if value.isdigit() else value

    config = VoiceConfig(
        sample_rate=sample_rate,
        vad_threshold=vad_threshold,
        energy_threshold=energy_threshold,
        min_speech_ms=vad_min_speech_ms,
        min_silence_ms=vad_min_silence_ms,
        max_utterance_sec=max_utterance_sec,
        stt_model=stt_model,
        stt_language=language,
        device_in=_maybe_int(device_in),
        device_out=_maybe_int(device_out),
        allow_barge_in=True,
    )
    pipeline = VoicePipeline(
        api_key=ctx.obj["api_key"],
        provider=ctx.obj["provider"],
        model=ctx.obj["model"],
        enable_thinking=ctx.obj["enable_thinking"],
        local_model_path=ctx.obj["local_model_path"],
        llamacpp_bin=ctx.obj["llamacpp_bin"],
        local_server_url=ctx.obj["local_server_url"],
        local_server_api_key=ctx.obj["local_server_api_key"],
        site_url=os.getenv("OPENROUTER_SITE_URL"),
        site_name=os.getenv("OPENROUTER_SITE_NAME"),
        tts_backend=backend or _default_tts_backend(),
        tts_voice=voice,
        tts_rate=rate,
        tts_volume=volume,
        speak=not no_speak,
        system_prompt=system,
        use_tools=tools,
        config=config,
    )

    def _on_event(event: dict) -> None:
        event_type = event.get("type")
        if event_type == "listening":
            click.echo("Listening...")
        elif event_type == "speech_started":
            click.echo("Recording...")
        elif event_type == "speech_ended":
            click.echo("Speech ended.")
        elif event_type == "transcribing":
            click.echo("Transcribing...")
        elif event_type == "thinking":
            click.echo("Thinking...")
        elif event_type == "speaking":
            click.echo("Speaking...")
        elif event_type == "transcript":
            click.echo(f"You (voice): {event.get('text', '')}")
        elif event_type == "transcript_rejected":
            click.echo("Heard audio but transcript was too short; continuing...")
        elif event_type == "transcript_empty":
            click.echo("Heard audio but no speech could be transcribed; continuing...")
        elif event_type == "response":
            click.echo(f"AI: {event.get('text', '')}")
        elif event_type == "tts_interrupted":
            click.echo("Interrupted by speech.")
        elif event_type == "barge_in_unavailable":
            click.echo(
                "Barge-in monitor unavailable during playback: "
                f"{event.get('error', 'unknown error')}"
            )
        elif event_type == "no_speech_detected":
            max_rms = float(event.get("max_rms", 0.0))
            click.echo(
                f"No speech detected (max RMS={max_rms:.4f}). "
                "Try --energy-threshold 0.005 or choose --device-in."
            )

    click.echo("Voice chat started. Press Ctrl+C to stop.")
    try:
        pipeline.run(on_event=_on_event)
    except MissingVoiceDependencies as e:
        click.echo(f"Error: {e}", err=True)
        click.echo(
            "Install voice dependencies with: uv sync --extra voice",
            err=True,
        )
        sys.exit(1)
    except KeyboardInterrupt:
        pipeline.stop()
        click.echo("\nGoodbye!")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("doctor-voice")
@click.option("--stt-model", default="small.en", help="faster-whisper model to load")
def doctor_voice(stt_model: str) -> None:
    """Run local voice pipeline diagnostics."""
    click.echo("Voice Diagnostics")
    click.echo("=================")
    failures = 0

    try:
        report = run_voice_diagnostics(stt_model=stt_model)
        click.echo("dependencies: OK")
        click.echo(f"audio input devices: {report['input_devices']}")
        click.echo(f"audio output devices: {report['output_devices']}")
        click.echo(f"default input device: {report['default_input']}")
        click.echo(f"default output device: {report['default_output']}")
        click.echo(f"silero-vad model: {'OK' if report['vad_loaded'] else 'FAILED'}")
        click.echo(f"faster-whisper model: {'OK' if report['stt_loaded'] else 'FAILED'}")

        if not report["vad_loaded"] or not report["stt_loaded"]:
            failures += 1
    except MissingVoiceDependencies as e:
        failures += 1
        click.echo(f"dependencies: FAILED ({e})")
        click.echo("Install voice dependencies with: uv sync --extra voice")
    except Exception as e:
        failures += 1
        click.echo(f"diagnostic run: FAILED ({e})")

    click.echo("\nSummary")
    click.echo("=======")
    click.echo(f"failed: {failures}")
    if failures:
        sys.exit(1)


@cli.command("test-stt")
@click.option("--stt-model", default="small.en", help="faster-whisper model")
@click.option("--language", default="en", help="STT language")
@click.option("--vad-threshold", default=0.3, type=float, help="Silero VAD threshold")
@click.option(
    "--energy-threshold",
    default=0.003,
    type=float,
    help="RMS fallback threshold for speech detection",
)
@click.option(
    "--vad-min-silence-ms", default=1200, type=int, help="Silence to end utterance"
)
@click.option("--device-in", default=None, help="Input device index or name")
@click.option("--sample-rate", default=16000, type=int, help="Audio sample rate")
@click.option("--file", "audio_file", default=None, help="Transcribe existing audio file")
@click.option(
    "--simulate",
    is_flag=True,
    help="Play a prompt phrase, then listen once and transcribe",
)
@click.option(
    "--prompt-text",
    default="What is the weather like today?",
    help="Prompt phrase for simulated STT",
)
@click.option(
    "--backend",
    type=click.Choice(["edge-tts", "kittentts", "pyttsx3"]),
    default=None,
    help="TTS backend for simulated prompt playback",
)
@click.option("--voice", default=None, help="Voice ID for simulated prompt playback")
def test_stt(
    stt_model: str,
    language: str,
    vad_threshold: float,
    energy_threshold: float,
    vad_min_silence_ms: int,
    device_in: str,
    sample_rate: int,
    audio_file: str,
    simulate: bool,
    prompt_text: str,
    backend: str,
    voice: str,
) -> None:
    """Test speech-to-text independently from LLM/TTS."""

    def _maybe_int(value: str | None):
        if value is None:
            return None
        return int(value) if value.isdigit() else value

    try:
        if audio_file:
            text = transcribe_audio_file(
                audio_file, stt_model=stt_model, language=language
            )
            if text:
                click.echo(f"Transcript: {text}")
                return
            click.echo("No transcript generated from file.")
            sys.exit(1)

        config = VoiceConfig(
            sample_rate=sample_rate,
            vad_threshold=vad_threshold,
            energy_threshold=energy_threshold,
            min_silence_ms=vad_min_silence_ms,
            stt_model=stt_model,
            stt_language=language,
            device_in=_maybe_int(device_in),
        )
        pipeline = VoicePipeline(api_key="stt-test", model="stt-test", speak=False, config=config)
        if simulate:
            click.echo(f"Prompt: {prompt_text}")
            tts = TTSManager(backend=backend or _default_tts_backend())
            if voice:
                tts.set_voice(voice)
            tts.speak(prompt_text)
        click.echo("Speak once, then pause...")
        transcript = pipeline.transcribe_once()
        if transcript:
            click.echo(f"Transcript: {transcript}")
            return
        click.echo("No transcript generated.")
        sys.exit(1)
    except MissingVoiceDependencies as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("Install voice dependencies with: uv sync --extra voice", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
