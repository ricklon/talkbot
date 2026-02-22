"""CLI for the talking bot using Click."""

import os
import sys
import tempfile
from pathlib import Path

import click
from dotenv import load_dotenv

from talkbot.openrouter import OpenRouterClient
from talkbot.tools import register_all_tools
from talkbot.tts import TTSManager

# Load environment variables from .env file
env_path = Path.cwd() / ".env"
if env_path.exists():
    load_dotenv(env_path)


@click.group()
@click.option("--api-key", envvar="OPENROUTER_API_KEY", help="OpenRouter API key")
@click.option("--model", default="openai/gpt-3.5-turbo", help="Model to use")
@click.pass_context
def cli(ctx: click.Context, api_key: str, model: str) -> None:
    """TalkBot - A talking AI assistant using OpenRouter and pyttsx3."""
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["model"] = model


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
def chat(
    ctx: click.Context,
    message: str,
    speak: bool,
    backend: str,
    voice: str,
    rate: int,
    volume: float,
    system: str,
) -> None:
    """Chat with the AI and hear the response."""
    try:
        with OpenRouterClient(
            api_key=ctx.obj["api_key"], model=ctx.obj["model"]
        ) as client:
            click.echo(f"You: {message}")
            response = client.simple_chat(message, system_prompt=system)
            click.echo(f"AI: {response}")

            if speak:
                tts = TTSManager(rate=rate, volume=volume, backend=backend)
                if voice:
                    tts.set_voice(voice)
                tts.speak(response)
    except ValueError as e:
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
def say(backend: str, voice: str, rate: int, volume: float) -> None:
    """Interactive mode - type messages and hear responses."""
    tts = TTSManager(rate=rate, volume=volume, backend=backend)
    if voice:
        tts.set_voice(voice)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        click.echo("Error: OPENROUTER_API_KEY environment variable not set", err=True)
        sys.exit(1)

    with OpenRouterClient(api_key=api_key) as client:
        click.echo("Interactive mode started. Type 'exit' or 'quit' to stop.")
        click.echo()

        while True:
            try:
                message = click.prompt("You", type=str)

                if message.lower() in ("exit", "quit"):
                    break

                response = client.simple_chat(message)
                click.echo(f"AI: {response}")
                tts.speak(response)

            except KeyboardInterrupt:
                click.echo("\nGoodbye!")
                break
            except EOFError:
                break


@cli.command()
@click.option(
    "--backend",
    type=click.Choice(["edge-tts", "kittentts", "pyttsx3"]),
    default=None,
    help="TTS backend to use (auto-detect if omitted)",
)
def voices(backend: str) -> None:
    """List available TTS voices."""
    tts = TTSManager(backend=backend)
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
    tts = TTSManager(rate=rate, backend=backend)
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
        with OpenRouterClient(
            api_key=ctx.obj["api_key"], model=ctx.obj["model"]
        ) as client:
            # Register all built-in tools
            register_all_tools(client)

            click.echo(f"You: {message}")
            response = client.chat_with_system_tools(message, system_prompt=system)
            click.echo(f"AI: {response}")

            if speak:
                tts = TTSManager(rate=rate, volume=volume, backend=backend)
                if voice:
                    tts.set_voice(voice)
                tts.speak(response)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
