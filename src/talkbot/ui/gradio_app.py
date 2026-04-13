"""Gradio web interface for TalkBot.

Provides a browser-based chat UI with KittenTTS audio playback — no local
speakers required. Audio is generated to a temp file and served back to the
browser via Gradio's audio component.

Usage:
    uv run talkbot serve                     # default: local_server on :8000
    uv run talkbot serve --port 7860
    uv run talkbot serve --share             # Gradio public tunnel
    TALKBOT_AGENT_PROMPT="..." uv run talkbot serve
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

env_path = Path.cwd() / ".env"
if env_path.exists():
    load_dotenv(env_path)


def _agent_prompt() -> str:
    return os.getenv(
        "TALKBOT_AGENT_PROMPT",
        "You are a coaching assistant for a robot arm. Help the student record quality demonstration episodes.",
    )


def _tts_backend() -> str:
    return os.getenv("TALKBOT_DEFAULT_TTS_BACKEND", "kittentts")


def create_app(
    provider: str = "local_server",
    model: str = "qwen3.5-0.8b-q8_0",
    local_server_url: str = "http://127.0.0.1:8000/v1",
    local_server_api_key: str = "",
    system_prompt: Optional[str] = None,
    tts_backend: Optional[str] = None,
    tts_rate: int = 175,
    tts_volume: float = 1.0,
    enable_tts: bool = True,
):
    """Build and return the Gradio Blocks app."""
    import gradio as gr

    from talkbot.llm import LLMProviderError, create_llm_client, supports_tools
    from talkbot.text_utils import strip_thinking
    from talkbot.tools import register_all_tools
    from talkbot.tts import TTSManager

    effective_system = system_prompt or _agent_prompt()
    effective_tts_backend = tts_backend or _tts_backend()

    # Lazy-initialise a single LLM client shared across requests (thread-safe
    # because LocalServerClient is stateless between calls).
    _client_cache: dict = {}

    def _get_client():
        if "client" not in _client_cache:
            client = create_llm_client(
                provider=provider,
                model=model,
                local_server_url=local_server_url or None,
                local_server_api_key=local_server_api_key or None,
            )
            # Register tools once; the client holds them.
            if supports_tools(client):
                register_all_tools(client)
            _client_cache["client"] = client
        return _client_cache["client"]

    def _speak(text: str) -> Optional[str]:
        """Generate audio to a temp file; return path (Gradio will serve it)."""
        if not enable_tts or not text.strip():
            return None
        try:
            tts = TTSManager(
                rate=tts_rate,
                volume=tts_volume,
                backend=effective_tts_backend,
            )
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp = f.name
            tts.save_to_file(text, tmp)
            return tmp
        except Exception as e:
            print(f"TTS error: {e}")
            return None

    def respond(
        user_message: str,
        history: list,
        system: str,
        speak: bool,
    ):
        """Gradio chat handler — yields (updated_history, audio_path)."""
        if not user_message.strip():
            yield history, None
            return

        history = history + [{"role": "user", "content": user_message}]
        yield history, None  # show user turn immediately

        try:
            client = _get_client()
            reply = client.chat_with_system_tools(
                user_message, system_prompt=system or effective_system
            )
            visible = strip_thinking(reply)
        except LLMProviderError as e:
            visible = f"[LLM error: {e}]"
        except Exception as e:
            visible = f"[Error: {e}]"

        history = history + [{"role": "assistant", "content": visible}]
        audio_path = _speak(visible) if speak else None
        yield history, audio_path

    # ── UI layout ────────────────────────────────────────────────────────────
    with gr.Blocks(title="TalkBot") as demo:
        gr.Markdown("## TalkBot — Robot Coaching Assistant")

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=480,
                    buttons=["copy_all"],
                )
                with gr.Row():
                    msg_box = gr.Textbox(
                        placeholder="Type a message and press Enter…",
                        label="",
                        scale=5,
                        autofocus=True,
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)

            with gr.Column(scale=1):
                system_box = gr.Textbox(
                    value=effective_system,
                    label="System prompt",
                    lines=6,
                )
                speak_toggle = gr.Checkbox(
                    value=enable_tts,
                    label=f"Speak reply ({effective_tts_backend})",
                )
                audio_out = gr.Audio(
                    label="Last reply audio",
                    autoplay=True,
                )
                gr.Markdown(
                    f"**Model:** `{model}`  \n**Provider:** `{provider}`  \n"
                    f"**Server:** `{local_server_url}`"
                )
                clear_btn = gr.Button("Clear conversation", variant="secondary")

        # Wire up events
        submit_args = dict(
            fn=respond,
            inputs=[msg_box, chatbot, system_box, speak_toggle],
            outputs=[chatbot, audio_out],
        )
        msg_box.submit(**submit_args).then(
            fn=lambda: "", inputs=None, outputs=msg_box
        )
        send_btn.click(**submit_args).then(
            fn=lambda: "", inputs=None, outputs=msg_box
        )
        clear_btn.click(fn=lambda: ([], None), outputs=[chatbot, audio_out])

    return demo


def main(
    host: str = "0.0.0.0",
    port: int = 7860,
    share: bool = False,
    provider: str | None = None,
    model: str | None = None,
    local_server_url: str | None = None,
    system_prompt: str | None = None,
    no_tts: bool = False,
):
    """Launch the Gradio app (called from CLI `talkbot serve`)."""
    from talkbot.cli import DEFAULT_LOCAL_SERVER_MODEL

    app = create_app(
        provider=provider or os.getenv("TALKBOT_LLM_PROVIDER", "local_server"),
        model=model or os.getenv("TALKBOT_LOCAL_SERVER_MODEL", DEFAULT_LOCAL_SERVER_MODEL),
        local_server_url=local_server_url or os.getenv("TALKBOT_LOCAL_SERVER_URL", "http://127.0.0.1:8000/v1"),
        local_server_api_key=os.getenv("TALKBOT_LOCAL_SERVER_API_KEY", ""),
        system_prompt=system_prompt or _agent_prompt(),
        enable_tts=not no_tts,
    )
    app.launch(server_name=host, server_port=port, share=share)
