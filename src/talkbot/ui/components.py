"""Tkinter GUI for the talking bot with modern styling."""

import datetime
import os
import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

from dotenv import load_dotenv

# Load environment variables from .env file before importing runtime modules.
env_path = Path.cwd() / ".env"
if env_path.exists():
    load_dotenv(env_path)

from talkbot.llm import LLMProviderError, create_llm_client, supports_tools
from talkbot.thinking import apply_thinking_system_prompt, env_thinking_default
from talkbot.text_utils import strip_thinking
from talkbot.tools import register_all_tools, set_alert_callback
from talkbot.tts import TTSManager
from talkbot.voice import MissingVoiceDependencies, VoiceConfig, VoicePipeline

OPENROUTER_MODELS = [
    "mistralai/ministral-3b-2512",
    "google/gemini-2.5-flash-lite",
    "google/gemini-2.0-flash-lite-001",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "qwen/qwen3-8b",
    "qwen/qwen3-4b:free",
]


def _default_local_model_path() -> str:
    configured = os.getenv("TALKBOT_LOCAL_MODEL_PATH", "").strip()
    if configured:
        return configured
    default_path = Path("models/default.gguf")
    if default_path.exists():
        return str(default_path)
    return ""


def _default_llamacpp_bin() -> str:
    configured = os.getenv("TALKBOT_LLAMACPP_BIN", "").strip()
    if configured:
        return configured
    for candidate in ("llama-cli", "llama"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return "llama-cli"


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, *, min_value: int, max_value: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = int(value.strip())
    except ValueError:
        return default
    return max(min_value, min(max_value, parsed))


class ModernStyle:
    """Modern color scheme and styling for the GUI."""

    # Colors
    BG_PRIMARY = "#1e1e2e"
    BG_SECONDARY = "#252537"
    BG_TERTIARY = "#313244"
    ACCENT = "#89b4fa"
    ACCENT_HOVER = "#b4befe"
    TEXT_PRIMARY = "#cdd6f4"
    TEXT_SECONDARY = "#a6adc8"
    SUCCESS = "#a6e3a1"
    WARNING = "#f9e2af"
    ERROR = "#f38ba8"
    BORDER = "#45475a"

    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_SMALL = 9


class RoundedButton(tk.Canvas):
    """Custom rounded button widget."""

    def __init__(
        self,
        parent,
        text,
        command=None,
        width=100,
        height=32,
        bg_color=ModernStyle.ACCENT,
        fg_color=ModernStyle.BG_PRIMARY,
        hover_color=ModernStyle.ACCENT_HOVER,
        **kwargs,
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent["bg"],
            highlightthickness=0,
            **kwargs,
        )

        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.current_color = bg_color

        # Draw rounded rectangle
        self.radius = 8
        self._draw_button(text)

        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw_button(self, text):
        """Draw the rounded button."""
        self.delete("all")
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()

        # Create rounded rectangle
        self.create_rounded_rect(
            2,
            2,
            width - 2,
            height - 2,
            self.radius,
            fill=self.current_color,
            outline="",
            tags="rect",
        )

        # Add text
        self.create_text(
            width // 2,
            height // 2,
            text=text,
            fill=self.fg_color,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
            tags="text",
        )

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle."""
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, event):
        """Mouse enter event."""
        self.current_color = self.hover_color
        self.itemconfig("rect", fill=self.current_color)

    def _on_leave(self, event):
        """Mouse leave event."""
        self.current_color = self.bg_color
        self.itemconfig("rect", fill=self.current_color)

    def _on_click(self, event):
        """Mouse click event."""
        if self.command:
            self.command()

