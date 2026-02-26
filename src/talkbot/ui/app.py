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

from talkbot.ui.components import ModernStyle, RoundedButton
from talkbot.ui.tabs.chat_tab import create_chat_tab
from talkbot.ui.tabs.timers_tab import create_timers_tab
from talkbot.ui.tabs.lists_tab import create_lists_tab
from talkbot.ui.tabs.prompt_tab import create_prompt_tab

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


from talkbot.ui.components import ModernStyle, RoundedButton

class TalkBotGUI:
    """GUI for the TalkBot application with modern styling."""

    def __init__(self, api_key: str = None, model: str = None):
        """Initialize the GUI."""
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.provider = os.getenv("TALKBOT_LLM_PROVIDER", "local")
        default_model = (os.getenv("TALKBOT_DEFAULT_MODEL") or "").strip()
        if not default_model:
            default_model = (
                "mistralai/ministral-3b-2512"
                if self.provider == "openrouter"
                else "qwen/qwen3-1.7b"
            )
        self.model = model or default_model
        self.local_model_path = _default_local_model_path()
        self.llamacpp_bin = _default_llamacpp_bin()
        self.local_server_url = os.getenv(
            "TALKBOT_LOCAL_SERVER_URL", "http://127.0.0.1:8000/v1"
        )
        self.local_server_api_key = os.getenv("TALKBOT_LOCAL_SERVER_API_KEY")
        self.client = None
        self.tts: TTSManager = None
        self.speaking_thread: threading.Thread = None
        self.response_thread: threading.Thread = None
        self.voice_thread: threading.Thread = None
        self.voice_pipeline: VoicePipeline | None = None
        self.voice_active = False
        self.stt_test_pipeline: VoicePipeline | None = None
        self.stt_test_active = False
        self.stop_requested = threading.Event()
        self.default_tts_backend = os.getenv("TALKBOT_DEFAULT_TTS_BACKEND", "edge-tts")
        self.default_use_tools = _env_bool("TALKBOT_DEFAULT_USE_TOOLS", True)
        self.enable_thinking = env_thinking_default()
        self.default_max_tokens = _env_int(
            "TALKBOT_MAX_TOKENS", 512, min_value=32, max_value=8192
        )
        self._all_voices: list[dict] = []

        self.root = tk.Tk()
        self.root.title("TalkBot - AI Talking Assistant")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        self.root.configure(bg=ModernStyle.BG_PRIMARY)

        # Configure ttk styles
        self._configure_styles()

        self._create_widgets()
        self._populate_audio_devices()
        self.root.after(100, self._setup_tts)

    def _configure_styles(self):
        """Configure modern ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure colors
        style.configure("Modern.TFrame", background=ModernStyle.BG_PRIMARY)
        style.configure(
            "Modern.TLabel",
            background=ModernStyle.BG_PRIMARY,
            foreground=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        )
        style.configure(
            "Modern.TLabelframe",
            background=ModernStyle.BG_SECONDARY,
            foreground=ModernStyle.TEXT_PRIMARY,
        )
        style.configure(
            "Modern.TLabelframe.Label",
            background=ModernStyle.BG_SECONDARY,
            foreground=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
        )
        style.configure(
            "Modern.TCombobox",
            background=ModernStyle.BG_TERTIARY,
            foreground=ModernStyle.TEXT_PRIMARY,
            fieldbackground=ModernStyle.BG_TERTIARY,
            selectbackground=ModernStyle.ACCENT,
            selectforeground=ModernStyle.BG_PRIMARY,
        )
        # ttk combobox needs explicit state maps for readonly values to remain visible.
        style.map(
            "Modern.TCombobox",
            fieldbackground=[
                ("readonly", ModernStyle.BG_TERTIARY),
                ("!disabled", ModernStyle.BG_TERTIARY),
            ],
            foreground=[
                ("readonly", ModernStyle.TEXT_PRIMARY),
                ("!disabled", ModernStyle.TEXT_PRIMARY),
            ],
            selectbackground=[
                ("readonly", ModernStyle.ACCENT),
                ("!disabled", ModernStyle.ACCENT),
            ],
            selectforeground=[
                ("readonly", ModernStyle.BG_PRIMARY),
                ("!disabled", ModernStyle.BG_PRIMARY),
            ],
        )
        style.configure(
            "Modern.TScale",
            background=ModernStyle.BG_SECONDARY,
            troughcolor=ModernStyle.BG_TERTIARY,
            bordercolor=ModernStyle.BORDER,
        )
        style.configure(
            "Modern.TCheckbutton",
            background=ModernStyle.BG_PRIMARY,
            foreground=ModernStyle.TEXT_PRIMARY,
        )
        style.configure(
            "Modern.TEntry",
            fieldbackground=ModernStyle.BG_TERTIARY,
            foreground=ModernStyle.TEXT_PRIMARY,
            insertcolor=ModernStyle.TEXT_PRIMARY,
        )
        style.configure(
            "Modern.TNotebook",
            background=ModernStyle.BG_PRIMARY,
            borderwidth=0,
        )
        style.configure(
            "Modern.TNotebook.Tab",
            background=ModernStyle.BG_TERTIARY,
            foreground=ModernStyle.TEXT_SECONDARY,
            padding=(10, 6),
        )
        style.map(
            "Modern.TNotebook.Tab",
            background=[("selected", ModernStyle.BG_SECONDARY)],
            foreground=[("selected", ModernStyle.TEXT_PRIMARY)],
        )

    def _create_widgets(self) -> None:
        """Create the GUI widgets."""
        # Main container with padding
        main_container = tk.Frame(self.root, bg=ModernStyle.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)

        # Header
        header = tk.Frame(main_container, bg=ModernStyle.BG_PRIMARY)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        title = tk.Label(
            header,
            text="TalkBot",
            font=(ModernStyle.FONT_FAMILY, 24, "bold"),
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.ACCENT,
        )
        title.pack(side=tk.LEFT)

        subtitle = tk.Label(
            header,
            text="AI Talking Assistant",
            font=(ModernStyle.FONT_FAMILY, 12),
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.TEXT_SECONDARY,
        )
        subtitle.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))

        # Settings panel
        settings_frame = tk.LabelFrame(
            main_container,
            text=" Configuration ",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, 10, "bold"),
            padx=10,
            pady=10,
        )
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        # LLM row: provider + model + toggle buttons
        row1 = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)
        row1.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            row1,
            text="Provider:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)

        self.provider_var = tk.StringVar(value=self.provider)
        self.provider_combo = ttk.Combobox(
            row1,
            textvariable=self.provider_var,
            values=["local", "local_server", "openrouter"],
            width=12,
            style="Modern.TCombobox",
            state="readonly",
        )
        self.provider_combo.pack(side=tk.LEFT, padx=(10, 20))
        self.provider_combo.bind("<<ComboboxSelected>>", self._on_provider_changed)

        tk.Label(
            row1,
            text="Model:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)

        self.model_var = tk.StringVar(value=self.model)
        self.model_combo = ttk.Combobox(
            row1,
            textvariable=self.model_var,
            values=[],
            width=35,
            style="Modern.TCombobox",
        )
        self.model_combo.pack(side=tk.LEFT, padx=(10, 20))

        self.thinking_var = tk.BooleanVar(value=self.enable_thinking)
        self.thinking_btn = tk.Button(
            row1,
            text=self._thinking_label(),
            bg=self._thinking_bg(),
            fg=self._thinking_fg(),
            command=self._toggle_thinking,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.thinking_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.tools_var = tk.BooleanVar(value=self.default_use_tools)
        self.tools_btn = tk.Button(
            row1,
            text=self._tools_label(),
            bg=self._tools_bg(),
            fg=self._tools_fg(),
            command=self._toggle_tools,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.tools_btn.pack(side=tk.LEFT)

        # TTS row: backend + status indicator + voice dropdown
        row_tts = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)
        row_tts.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            row_tts,
            text="TTS:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)

        self.backend_var = tk.StringVar(value=self.default_tts_backend)
        backend_combo = ttk.Combobox(
            row_tts,
            textvariable=self.backend_var,
            values=["edge-tts", "kittentts", "pyttsx3"],
            width=12,
            style="Modern.TCombobox",
            state="readonly",
        )
        backend_combo.pack(side=tk.LEFT, padx=(10, 12))
        backend_combo.bind("<<ComboboxSelected>>", self._on_backend_changed)

        self.backend_status_label = tk.Label(
            row_tts,
            text="🌐 Online",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.SUCCESS,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        )
        self.backend_status_label.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            row_tts,
            text="Voice:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)

        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(
            row_tts, textvariable=self.voice_var, width=40, style="Modern.TCombobox"
        )
        self.voice_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.voice_combo.bind("<<ComboboxSelected>>", self._on_voice_selected)

        self.english_only_var = tk.BooleanVar(value=True)
        self.english_only_check = tk.Checkbutton(
            row_tts,
            text="English only",
            variable=self.english_only_var,
            command=self._on_voice_filter_toggled,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            selectcolor=ModernStyle.BG_TERTIARY,
            activebackground=ModernStyle.BG_SECONDARY,
            activeforeground=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
        )
        self.english_only_check.pack(side=tk.LEFT, padx=(12, 0))

        # Local paths row — shown only when provider=local, packed dynamically
        self.local_row = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)

        tk.Label(
            self.local_row,
            text="Local GGUF:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)
        self.local_model_path_var = tk.StringVar(value=self.local_model_path)
        self.local_model_entry = tk.Entry(
            self.local_row,
            textvariable=self.local_model_path_var,
            width=34,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=4,
        )
        self.local_model_entry.pack(side=tk.LEFT, padx=(8, 12))

        tk.Label(
            self.local_row,
            text="Llama Bin:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)
        self.llamacpp_bin_var = tk.StringVar(value=self.llamacpp_bin)
        self.llamacpp_bin_entry = tk.Entry(
            self.local_row,
            textvariable=self.llamacpp_bin_var,
            width=24,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=4,
        )
        self.llamacpp_bin_entry.pack(side=tk.LEFT, padx=(8, 12))

        # Sliders row
        row2 = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)
        row2.pack(fill=tk.X)
        self._slider_row_ref = row2

        # Rate slider
        rate_frame = tk.Frame(row2, bg=ModernStyle.BG_SECONDARY)
        rate_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            rate_frame,
            text="Rate:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)

        self.rate_var = tk.IntVar(value=175)
        rate_scale = tk.Scale(
            rate_frame,
            from_=50,
            to=300,
            variable=self.rate_var,
            orient=tk.HORIZONTAL,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            troughcolor=ModernStyle.BG_TERTIARY,
            highlightthickness=0,
            bd=0,
            length=150,
            showvalue=False,
        )
        rate_scale.pack(side=tk.LEFT, padx=(10, 5))

        self.rate_label = tk.Label(
            rate_frame,
            text="175",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.ACCENT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
        )
        self.rate_label.pack(side=tk.LEFT)
        rate_scale.configure(
            command=lambda v: self.rate_label.config(text=str(int(float(v))))
        )

        # Volume slider
        vol_frame = tk.Frame(row2, bg=ModernStyle.BG_SECONDARY)
        vol_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            vol_frame,
            text="Volume:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)

        self.volume_var = tk.DoubleVar(value=1.0)
        vol_scale = tk.Scale(
            vol_frame,
            from_=0.0,
            to=1.0,
            variable=self.volume_var,
            orient=tk.HORIZONTAL,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            troughcolor=ModernStyle.BG_TERTIARY,
            highlightthickness=0,
            bd=0,
            length=150,
            resolution=0.1,
            showvalue=False,
        )
        vol_scale.pack(side=tk.LEFT, padx=(10, 5))

        self.volume_label = tk.Label(
            vol_frame,
            text="100%",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.ACCENT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
        )
        self.volume_label.pack(side=tk.LEFT)
        vol_scale.configure(
            command=lambda v: self.volume_label.config(text=f"{int(float(v) * 100)}%")
        )

        # Max tokens control
        tokens_frame = tk.Frame(row2, bg=ModernStyle.BG_SECONDARY)
        tokens_frame.pack(side=tk.LEFT, padx=(12, 0))
        tk.Label(
            tokens_frame,
            text="Max Tokens:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)
        self.max_tokens_var = tk.StringVar(value=str(self.default_max_tokens))
        self.max_tokens_entry = tk.Entry(
            tokens_frame,
            textvariable=self.max_tokens_var,
            width=6,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=4,
        )
        self.max_tokens_entry.pack(side=tk.LEFT, padx=(8, 0))

        # Voice chat controls
        row3 = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)
        row3.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            row3,
            text="Mic:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)
        self.mic_var = tk.StringVar(value="default")
        self.mic_combo = ttk.Combobox(
            row3,
            textvariable=self.mic_var,
            width=22,
            style="Modern.TCombobox",
            state="readonly",
        )
        self.mic_combo.pack(side=tk.LEFT, padx=(8, 12))

        tk.Label(
            row3,
            text="Speaker:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)
        self.spk_var = tk.StringVar(value="default")
        self.spk_combo = ttk.Combobox(
            row3,
            textvariable=self.spk_var,
            width=22,
            style="Modern.TCombobox",
            state="readonly",
        )
        self.spk_combo.pack(side=tk.LEFT, padx=(8, 12))

        self.voice_start_btn = RoundedButton(
            row3,
            text="Start Voice",
            command=self._start_voice_chat,
            bg_color=ModernStyle.SUCCESS,
            fg_color=ModernStyle.BG_PRIMARY,
            hover_color="#c8f0c3",
            width=100,
            height=30,
        )
        self.voice_start_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.voice_stop_btn = RoundedButton(
            row3,
            text="Stop Voice",
            command=self._stop_voice_chat,
            bg_color=ModernStyle.ERROR,
            fg_color=ModernStyle.TEXT_PRIMARY,
            hover_color="#f5a0b5",
            width=100,
            height=30,
        )
        self.voice_stop_btn.pack(side=tk.LEFT)
        self.voice_test_btn = RoundedButton(
            row3,
            text="Test STT",
            command=self._test_stt_once,
            bg_color=ModernStyle.BG_TERTIARY,
            fg_color=ModernStyle.TEXT_SECONDARY,
            hover_color=ModernStyle.BORDER,
            width=90,
            height=30,
        )
        self.voice_test_btn.pack(side=tk.LEFT, padx=(8, 0))
        self.voice_sim_btn = RoundedButton(
            row3,
            text="Sim STT",
            command=self._simulate_stt_once,
            bg_color=ModernStyle.BG_TERTIARY,
            fg_color=ModernStyle.TEXT_SECONDARY,
            hover_color=ModernStyle.BORDER,
            width=90,
            height=30,
        )
        self.voice_sim_btn.pack(side=tk.LEFT, padx=(8, 0))

        row4 = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)
        row4.pack(fill=tk.X, pady=(8, 0))

        tk.Label(
            row4,
            text="STT Model:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)
        self.stt_model_var = tk.StringVar(value="small.en")
        self.stt_model_combo = ttk.Combobox(
            row4,
            textvariable=self.stt_model_var,
            values=["base.en", "small.en", "medium.en"],
            width=12,
            style="Modern.TCombobox",
            state="readonly",
        )
        self.stt_model_combo.pack(side=tk.LEFT, padx=(8, 12))

        tk.Label(
            row4,
            text="Lang:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)
        self.stt_lang_var = tk.StringVar(value="en")
        self.stt_lang_entry = tk.Entry(
            row4,
            textvariable=self.stt_lang_var,
            width=6,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=4,
        )
        self.stt_lang_entry.pack(side=tk.LEFT, padx=(8, 12))

        tk.Label(
            row4,
            text="VAD:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)
        self.vad_threshold_var = tk.DoubleVar(value=0.3)
        vad_scale = tk.Scale(
            row4,
            from_=0.1,
            to=0.9,
            variable=self.vad_threshold_var,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            troughcolor=ModernStyle.BG_TERTIARY,
            highlightthickness=0,
            bd=0,
            length=120,
            showvalue=False,
        )
        vad_scale.pack(side=tk.LEFT, padx=(8, 5))
        self.vad_label = tk.Label(
            row4,
            text="0.30",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.ACCENT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
        )
        self.vad_label.pack(side=tk.LEFT, padx=(0, 12))
        vad_scale.configure(
            command=lambda v: self.vad_label.config(text=f"{float(v):.2f}")
        )

        tk.Label(
            row4,
            text="Silence(ms):",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)
        self.vad_silence_var = tk.IntVar(value=1200)
        self.vad_silence_entry = tk.Entry(
            row4,
            textvariable=self.vad_silence_var,
            width=6,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=4,
        )
        self.vad_silence_entry.pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(
            row4,
            text="Mic Level:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT, padx=(12, 6))
        self.mic_meter = tk.Canvas(
            row4,
            width=120,
            height=14,
            bg=ModernStyle.BG_TERTIARY,
            highlightthickness=1,
            highlightbackground=ModernStyle.BORDER,
        )
        self.mic_meter.pack(side=tk.LEFT)
        self.mic_meter_fill = self.mic_meter.create_rectangle(
            0, 0, 0, 14, fill=ModernStyle.SUCCESS, width=0
        )

        row5 = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)
        row5.pack(fill=tk.X, pady=(8, 0))
        self.voice_phase_var = tk.StringVar(value="Voice: idle")
        self.voice_transcript_var = tk.StringVar(value="Last transcript: (none)")
        tk.Label(
            row5,
            textvariable=self.voice_phase_var,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.ACCENT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 14))
        tk.Label(
            row5,
            textvariable=self.voice_transcript_var,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            anchor=tk.W,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Conversation + prompt tabs
        notebook = ttk.Notebook(main_container, style="Modern.TNotebook")
        notebook.grid(row=2, column=0, sticky="nsew", pady=(0, 15))

        self.chat_history, tab_chat = create_chat_tab(notebook)
        self.timers_list, tab_timers = create_timers_tab(notebook)
        self.lists_box, tab_lists = create_lists_tab(notebook)
        self.prompt_text, tab_prompt = create_prompt_tab(notebook)
        
        notebook.add(tab_chat, text="Conversation")
        notebook.add(tab_timers, text="Timers")
        notebook.add(tab_lists, text="Lists")
        notebook.add(tab_prompt, text="Prompt")

        self._poll_timers()
        self._poll_lists()

        # Input area
        input_frame = tk.Frame(main_container, bg=ModernStyle.BG_PRIMARY)
        input_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        self.input_field = tk.Entry(
            input_frame,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            relief=tk.FLAT,
            bd=8,
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_field.bind("<Return>", self._on_send)

        # Send button (custom rounded)
        self.send_button = RoundedButton(
            input_frame,
            text="Send",
            command=self._on_send,
            bg_color=ModernStyle.ACCENT,
            fg_color=ModernStyle.BG_PRIMARY,
            hover_color=ModernStyle.ACCENT_HOVER,
            width=80,
            height=36,
        )
        self.send_button.pack(side=tk.LEFT, padx=(0, 10))

        # Stop button
        self.stop_button = RoundedButton(
            input_frame,
            text="Stop",
            command=self._stop_all,
            bg_color=ModernStyle.ERROR,
            fg_color=ModernStyle.TEXT_PRIMARY,
            hover_color="#f5a0b5",
            width=80,
            height=36,
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        # Speak checkbox
        self.speak_var = tk.BooleanVar(value=True)
        speak_check = tk.Checkbutton(
            input_frame,
            text="🔊 Speak",
            variable=self.speak_var,
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.TEXT_SECONDARY,
            selectcolor=ModernStyle.BG_TERTIARY,
            activebackground=ModernStyle.BG_PRIMARY,
            activeforeground=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        )
        speak_check.pack(side=tk.LEFT)

        # Bottom toolbar
        toolbar = tk.Frame(main_container, bg=ModernStyle.BG_PRIMARY)
        toolbar.grid(row=4, column=0, sticky="ew")

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(
            toolbar,
            textvariable=self.status_var,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            padx=10,
            pady=5,
            anchor=tk.W,
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Token / context usage counter (right-aligned)
        self.token_var = tk.StringVar(value="")
        tk.Label(
            toolbar,
            textvariable=self.token_var,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            padx=8,
            pady=5,
        ).pack(side=tk.RIGHT)

        # Toolbar buttons
        self.clear_btn = RoundedButton(
            toolbar,
            text="Clear Chat",
            command=self._clear_chat,
            bg_color=ModernStyle.BG_TERTIARY,
            fg_color=ModernStyle.TEXT_SECONDARY,
            hover_color=ModernStyle.BORDER,
            width=90,
            height=28,
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.test_btn = RoundedButton(
            toolbar,
            text="Test Voice",
            command=self._test_voice,
            bg_color=ModernStyle.BG_TERTIARY,
            fg_color=ModernStyle.TEXT_SECONDARY,
            hover_color=ModernStyle.BORDER,
            width=90,
            height=28,
        )
        self.test_btn.pack(side=tk.LEFT)

        self._set_voice_controls(active=False)
        self._on_provider_changed()

    def _setup_tts(self) -> None:
        """Setup TTS and populate voice list."""
        try:
            backend = self.backend_var.get()
            self.tts = TTSManager(backend=backend)
            set_alert_callback(self.tts.speak)
            voices = self.tts.available_voices
            self._all_voices = voices

            self._refresh_voice_dropdown(voices)
            if voices:
                # Update status label
                if backend == "edge-tts":
                    self.backend_status_label.config(
                        text="🌐 Online", fg=ModernStyle.SUCCESS
                    )
                elif backend == "kittentts":
                    self.backend_status_label.config(
                        text="🐱 Local", fg=ModernStyle.ACCENT
                    )
                else:
                    self.backend_status_label.config(
                        text="💻 Offline", fg=ModernStyle.WARNING
                    )

        except Exception as e:
            messagebox.showwarning(
                "TTS Warning",
                f"Could not initialize text-to-speech: {e}\n"
                "The application will work but won't be able to speak.",
            )

    def _populate_audio_devices(self) -> None:
        """Populate mic and speaker choices."""
        try:
            devices = VoicePipeline.list_audio_devices()
            input_values = ["default"]
            output_values = ["default"]

            for dev in devices:
                label = f"{dev['index']}: {dev['name']}"
                if dev["max_input_channels"] > 0:
                    input_values.append(label)
                if dev["max_output_channels"] > 0:
                    output_values.append(label)

            self.mic_combo["values"] = input_values
            self.spk_combo["values"] = output_values
            self.mic_var.set(input_values[0])
            self.spk_var.set(output_values[0])
        except Exception:
            self.mic_combo["values"] = ["default"]
            self.spk_combo["values"] = ["default"]
            self.mic_var.set("default")
            self.spk_var.set("default")

    def _parse_device_selection(self, value: str):
        if not value or value == "default":
            return None
        idx = value.split(":", 1)[0].strip()
        return int(idx) if idx.isdigit() else value

    def _provider_ready(self) -> bool:
        provider = self.provider_var.get()
        if provider == "openrouter":
            return bool(self.api_key)
        if provider == "local_server":
            return bool(self.local_server_url)
        return bool(self.local_model_path_var.get().strip())

    def _create_client(self):
        self.llamacpp_bin = self.llamacpp_bin_var.get().strip() or "llama-cli"
        return create_llm_client(
            provider=self.provider_var.get(),
            model=self.model_var.get(),
            api_key=self.api_key,
            site_url=os.getenv("OPENROUTER_SITE_URL"),
            site_name=os.getenv("OPENROUTER_SITE_NAME"),
            local_model_path=self.local_model_path_var.get().strip() or None,
            llamacpp_bin=self.llamacpp_bin,
            local_server_url=self.local_server_url,
            local_server_api_key=self.local_server_api_key,
            enable_thinking=self.thinking_var.get(),
        )

    def _thinking_label(self) -> str:
        return "💭 Thinking: ON" if self.thinking_var.get() else "💭 Thinking: OFF"

    def _thinking_bg(self) -> str:
        return ModernStyle.WARNING if self.thinking_var.get() else ModernStyle.BG_TERTIARY

    def _thinking_fg(self) -> str:
        return ModernStyle.BG_PRIMARY if self.thinking_var.get() else ModernStyle.TEXT_SECONDARY

    def _toggle_thinking(self) -> None:
        self.thinking_var.set(not self.thinking_var.get())
        self.thinking_btn.config(
            text=self._thinking_label(), bg=self._thinking_bg(), fg=self._thinking_fg()
        )

    def _tools_label(self) -> str:
        return "🔧 Tools: ON" if self.tools_var.get() else "🔧 Tools: OFF"

    def _tools_bg(self) -> str:
        return ModernStyle.ACCENT if self.tools_var.get() else ModernStyle.BG_TERTIARY

    def _tools_fg(self) -> str:
        return ModernStyle.BG_PRIMARY if self.tools_var.get() else ModernStyle.TEXT_SECONDARY

    def _toggle_tools(self) -> None:
        self.tools_var.set(not self.tools_var.get())
        self.tools_btn.config(
            text=self._tools_label(), bg=self._tools_bg(), fg=self._tools_fg()
        )

    def _poll_timers(self) -> None:
        """Update the Timers tab with current active timers every second."""
        try:
            from talkbot.tools import _timers, _timer_lock
            import time as _time
            with _timer_lock:
                snapshot = dict(_timers)
            now = _time.time()
            self.timers_list.delete(0, tk.END)
            if snapshot:
                for tid, (label, _, fire_at) in sorted(snapshot.items(), key=lambda x: x[1][2]):
                    remaining = max(0, int(fire_at - now))
                    mins, secs = divmod(remaining, 60)
                    hrs, mins = divmod(mins, 60)
                    if hrs:
                        time_str = f"{hrs}h {mins}m {secs}s"
                    elif mins:
                        time_str = f"{mins}m {secs}s"
                    else:
                        time_str = f"{secs}s"
                    self.timers_list.insert(tk.END, f"#{tid}  {time_str:>8}  —  {label}")
            else:
                self.timers_list.insert(tk.END, "No active timers or reminders.")
        except Exception as e:
            self.timers_list.delete(0, tk.END)
            self.timers_list.insert(tk.END, f"[Error: {e}]")
        finally:
            self.root.after(1000, self._poll_timers)

    def _poll_lists(self) -> None:
        """Update the Lists tab with current list contents every 2 seconds."""
        try:
            from talkbot.tools import _load_json
            data = _load_json("lists.json")
            self.lists_box.delete(0, tk.END)
            if data:
                for list_name, items in data.items():
                    self.lists_box.insert(tk.END, f"[ {list_name} ]")
                    if items:
                        for item in items:
                            self.lists_box.insert(tk.END, f"    * {item}")
                    else:
                        self.lists_box.insert(tk.END, "    (empty)")
            else:
                self.lists_box.insert(tk.END, "No lists yet.")
        except Exception as e:
            self.lists_box.delete(0, tk.END)
            self.lists_box.insert(tk.END, f"[Error: {e}]")
        finally:
            self.root.after(2000, self._poll_lists)

    def _find_local_models(self) -> list[str]:
        models_dir = Path("models")
        if models_dir.exists():
            found = sorted(str(p) for p in models_dir.glob("*.gguf"))
            if found:
                return found
        current = self.local_model_path_var.get().strip()
        return [current] if current else []

    def _is_english_voice(self, voice: dict) -> bool:
        """Best-effort English detection across backend voice metadata."""

        def normalize(value: object) -> str:
            if value is None:
                return ""
            if isinstance(value, bytes):
                text = value.decode("utf-8", errors="ignore")
            else:
                text = str(value)
            filtered = "".join(
                ch.lower() if ch.isalnum() or ch in {" ", "-", "_"} else " "
                for ch in text
            )
            return " ".join(filtered.split())

        candidates: list[object] = [voice.get("id"), voice.get("name")]
        languages = voice.get("languages", [])
        if isinstance(languages, (list, tuple, set)):
            candidates.extend(languages)
        else:
            candidates.append(languages)

        for candidate in candidates:
            text = normalize(candidate).replace("_", "-")
            if not text:
                continue
            if "english" in text:
                return True
            if text.startswith("en"):
                return True
            if any(token in {"en", "eng"} for token in text.replace("-", " ").split()):
                return True
        return False

    def _voice_id_for_name(self, voice_name: str) -> str | None:
        for voice in self._all_voices:
            if voice["name"] == voice_name:
                return voice["id"]
        return None

    def _refresh_voice_dropdown(
        self, voices: list[dict], preferred_name: str | None = None
    ) -> None:
        selected_name = preferred_name or self.voice_var.get().strip()
        visible_voices = (
            [v for v in voices if self._is_english_voice(v)]
            if self.english_only_var.get()
            else voices
        )
        self.voice_combo["values"] = [v["name"] for v in visible_voices]
        if not visible_voices:
            self.voice_var.set("")
            return

        selected_voice = next(
            (v for v in visible_voices if v["name"] == selected_name), None
        )
        if selected_voice is None:
            selected_voice = next(
                (v for v in visible_voices if self._is_english_voice(v)),
                visible_voices[0],
            )

        self.voice_var.set(selected_voice["name"])
        if self.tts:
            self.tts.set_voice(selected_voice["id"])

    def _on_voice_filter_toggled(self) -> None:
        if not self.tts:
            return
        self._refresh_voice_dropdown(self._all_voices)

    def _on_voice_selected(self, event=None) -> None:
        """Apply the selected voice immediately when the user picks from the dropdown."""
        del event
        if not self.tts:
            return
        voice_id = self._voice_id_for_name(self.voice_var.get())
        if voice_id:
            self.tts.set_voice(voice_id)

    def _on_provider_changed(self, event=None) -> None:
        del event
        provider = self.provider_var.get()
        if provider == "openrouter":
            self.model_combo["values"] = OPENROUTER_MODELS
            self.model_combo.config(state="readonly")
            if self.model_var.get() not in OPENROUTER_MODELS:
                self.model_var.set(OPENROUTER_MODELS[0])
            self.local_row.pack_forget()
            self.status_var.set("Provider: OpenRouter")
        elif provider == "local_server":
            self.model_combo["values"] = []
            self.model_combo.config(state="normal")
            self.local_row.pack_forget()
            self.status_var.set("Provider: Local Server (OpenAI API)")
        else:  # local
            local_models = self._find_local_models()
            self.model_combo["values"] = local_models
            self.model_combo.config(state="readonly" if local_models else "normal")
            if local_models and self.model_var.get() not in local_models:
                self.model_var.set(local_models[0])
            self.local_row.pack(fill=tk.X, pady=(0, 8), before=self._slider_row_ref)
            self.status_var.set("Provider: Local (non-server)")

    def _get_system_prompt(self) -> str | None:
        text = self.prompt_text.get("1.0", tk.END).strip()
        return apply_thinking_system_prompt(text or None, self.thinking_var.get())

    def _current_max_tokens(self) -> int:
        try:
            value = int(self.max_tokens_var.get().strip())
        except Exception:
            value = self.default_max_tokens
        value = max(32, min(8192, value))
        self.max_tokens_var.set(str(value))
        return value

    def _display_response_text(self, response: str) -> str:
        """Return chat-display text based on thinking toggle."""
        if self.thinking_var.get():
            text = response.strip()
        else:
            text = strip_thinking(response).strip()
        # Strip Qwen3 /no_think leading artifact (e.g. leading "." before actual content)
        return text.lstrip(".")

    def _speech_response_text(self, response: str) -> str:
        """Always speak concise output without hidden thinking blocks."""
        return strip_thinking(response).strip()

    def _set_voice_controls(self, active: bool) -> None:
        """Update visual state for Start/Stop voice controls."""
        if active:
            self.voice_start_btn.itemconfig("rect", fill=ModernStyle.BG_TERTIARY)
            self.voice_start_btn.itemconfig("text", text="Voice ON")
            self.voice_stop_btn.itemconfig("rect", fill=ModernStyle.ERROR)
        else:
            self.voice_start_btn.itemconfig("rect", fill=ModernStyle.SUCCESS)
            self.voice_start_btn.itemconfig("text", text="Start Voice")
            self.voice_stop_btn.itemconfig("rect", fill=ModernStyle.BG_TERTIARY)

    def _set_test_stt_running(self, running: bool) -> None:
        """Update visual state for STT test button."""
        if running:
            self.voice_test_btn.itemconfig("rect", fill=ModernStyle.ACCENT)
            self.voice_test_btn.itemconfig("text", text="Testing...")
            self.voice_sim_btn.itemconfig("rect", fill=ModernStyle.ACCENT)
            self.voice_sim_btn.itemconfig("text", text="Sim...")
        else:
            self.voice_test_btn.itemconfig("rect", fill=ModernStyle.BG_TERTIARY)
            self.voice_test_btn.itemconfig("text", text="Test STT")
            self.voice_sim_btn.itemconfig("rect", fill=ModernStyle.BG_TERTIARY)
            self.voice_sim_btn.itemconfig("text", text="Sim STT")

    def _set_test_tts_running(self, running: bool) -> None:
        """Update visual state for TTS test button."""
        if running:
            self.test_btn.itemconfig("rect", fill=ModernStyle.ACCENT)
            self.test_btn.itemconfig("text", text="Testing...")
        else:
            self.test_btn.itemconfig("rect", fill=ModernStyle.BG_TERTIARY)
            self.test_btn.itemconfig("text", text="Test Voice")

    def _start_voice_chat(self) -> None:
        """Start local half-duplex voice chat."""
        if self.voice_active:
            return
        if not self._provider_ready():
            if self.provider_var.get() == "openrouter":
                messagebox.showerror(
                    "Provider Not Ready",
                    "OpenRouter selected but OPENROUTER_API_KEY is not set.",
                )
            elif self.provider_var.get() == "local_server":
                messagebox.showerror(
                    "Provider Not Ready",
                    "Local server selected but TALKBOT_LOCAL_SERVER_URL is empty.",
                )
            else:
                messagebox.showerror(
                    "Provider Not Ready",
                    "Local provider selected but Local GGUF path is empty.",
                )
            return

        self.voice_active = True
        self._set_voice_controls(active=True)
        self.status_var.set("Voice mode starting...")

        def worker() -> None:
            try:
                cfg = VoiceConfig(
                    sample_rate=16000,
                    vad_threshold=float(self.vad_threshold_var.get()),
                    min_speech_ms=250,
                    min_silence_ms=int(self.vad_silence_var.get()),
                    max_utterance_sec=12.0,
                    stt_model=self.stt_model_var.get(),
                    stt_language=self.stt_lang_var.get().strip() or "en",
                    device_in=self._parse_device_selection(self.mic_var.get()),
                    device_out=self._parse_device_selection(self.spk_var.get()),
                    allow_barge_in=True,
                )
                tts_voice_id = (
                    self._voice_id_for_name(self.voice_var.get()) if self.tts else None
                )
                self.voice_pipeline = VoicePipeline(
                    api_key=self.api_key,
                    provider=self.provider_var.get(),
                    model=self.model_var.get(),
                    enable_thinking=self.thinking_var.get(),
                    local_model_path=self.local_model_path_var.get().strip() or None,
                    llamacpp_bin=self.llamacpp_bin,
                    local_server_url=self.local_server_url,
                    local_server_api_key=self.local_server_api_key,
                    site_url=os.getenv("OPENROUTER_SITE_URL"),
                    site_name=os.getenv("OPENROUTER_SITE_NAME"),
                    tts_backend=self.backend_var.get(),
                    tts_voice=tts_voice_id,
                    tts_rate=self.rate_var.get(),
                    tts_volume=self.volume_var.get(),
                    speak=self.speak_var.get(),
                    system_prompt=self._get_system_prompt(),
                    use_tools=self.tools_var.get(),
                    config=cfg,
                )
                self.voice_pipeline.run(
                    on_event=lambda e: self.root.after(0, self._on_voice_event, e)
                )
            except MissingVoiceDependencies as e:
                error_text = str(e)
                self.root.after(
                    0,
                    lambda msg=error_text: messagebox.showerror(
                        "Voice Dependencies",
                        f"{msg}\nInstall with: uv sync --extra voice",
                    ),
                )
            except LLMProviderError as e:
                error_text = str(e)
                self.root.after(
                    0,
                    lambda msg=error_text: messagebox.showerror(
                        "LLM Provider Error",
                        msg,
                    ),
                )
            except Exception as e:
                error_text = str(e)
                self.root.after(
                    0, lambda msg=error_text: messagebox.showerror("Voice Chat Error", msg)
                )
            finally:
                self.voice_pipeline = None
                self.voice_active = False
                self.root.after(0, lambda: self.status_var.set("Ready"))
                self.root.after(0, lambda: self.voice_phase_var.set("Voice: idle"))
                self.root.after(0, lambda: self._set_mic_level(0.0))
                self.root.after(0, lambda: self._set_voice_controls(active=False))

        self.voice_thread = threading.Thread(target=worker, daemon=True)
        self.voice_thread.start()

    def _stop_voice_chat(self) -> None:
        """Stop local voice chat loop."""
        if self.voice_pipeline:
            self.voice_pipeline.stop()
        if self.stt_test_pipeline:
            self.stt_test_pipeline.stop()
        self.voice_active = False
        self.stt_test_active = False
        self._set_mic_level(0.0)
        self.voice_phase_var.set("Voice: stopped")
        self._set_voice_controls(active=False)

    def _set_mic_level(self, level: float) -> None:
        """Update mic level meter."""
        level = max(0.0, min(1.0, float(level)))
        width = int(120 * level)
        if level > 0.75:
            color = ModernStyle.ERROR
        elif level > 0.45:
            color = ModernStyle.WARNING
        else:
            color = ModernStyle.SUCCESS
        self.mic_meter.coords(self.mic_meter_fill, 0, 0, width, 14)
        self.mic_meter.itemconfig(self.mic_meter_fill, fill=color)

    def _on_voice_event(self, event: dict) -> None:
        """Handle voice pipeline event on UI thread."""
        event_type = event.get("type")
        if event_type == "listening":
            self.status_var.set("Listening...")
            self.voice_phase_var.set("Voice: listening")
        elif event_type == "speech_started":
            self.status_var.set("Recording...")
            self.voice_phase_var.set("Voice: recording")
        elif event_type == "speech_ended":
            self.status_var.set("Speech ended")
            self.voice_phase_var.set("Voice: processing")
        elif event_type == "transcribing":
            self.status_var.set("Transcribing...")
            self.voice_phase_var.set("Voice: transcribing")
        elif event_type == "thinking":
            if self.thinking_var.get():
                self.status_var.set("Thinking...")
                self.voice_phase_var.set("Voice: thinking")
            else:
                self.status_var.set("Responding...")
                self.voice_phase_var.set("Voice: processing")
        elif event_type == "speaking":
            self.status_var.set("Speaking...")
            self.voice_phase_var.set("Voice: speaking")
        elif event_type == "tts_interrupted":
            self.status_var.set("Interrupted by speech")
            self.voice_phase_var.set("Voice: interrupted")
        elif event_type == "transcript":
            text = event.get("text", "")
            self._add_message("You (voice)", text, is_user=True)
            preview = (text[:90] + "...") if len(text) > 90 else text
            self.voice_transcript_var.set(f"Last transcript: {preview}")
        elif event_type == "transcript_rejected":
            self.status_var.set("Audio too short, keep speaking...")
            self.voice_phase_var.set("Voice: listening")
            self._add_message(
                "System",
                "Heard audio, but transcript was too short. Please speak a bit longer.",
                is_user=False,
            )
        elif event_type == "transcript_empty":
            self.status_var.set("No speech recognized, keep speaking...")
            self.voice_phase_var.set("Voice: listening")
            self._add_message(
                "System",
                "Heard audio, but couldn't transcribe speech. Try speaking louder or reducing VAD threshold.",
                is_user=False,
            )
        elif event_type == "response":
            visible_response = self._display_response_text(event.get("text", ""))
            self._add_message("AI", visible_response, is_user=False)
            self.voice_phase_var.set("Voice: listening")
        elif event_type == "timer_alert":
            self._add_message("Timer", event.get("text", ""), is_user=False)
        elif event_type == "token_usage":
            usage = event.get("usage", {})
            total = usage.get("total_tokens", 0)
            prompt = usage.get("prompt_tokens", 0)
            completion = usage.get("completion_tokens", 0)
            self.token_var.set(f"{total:,} tok  ({prompt:,}+{completion})")
        elif event_type == "no_speech_detected":
            max_rms = float(event.get("max_rms", 0.0))
            self.status_var.set(f"No speech detected (RMS={max_rms:.4f})")
            self.voice_phase_var.set("Voice: listening")
        elif event_type == "barge_in_unavailable":
            self.status_var.set("Barge-in unavailable on current device")
            self.voice_phase_var.set("Voice: speaking")
            self._add_message(
                "System",
                "Mic monitoring during playback is unavailable on this audio device. "
                "Try choosing explicit separate Mic/Speaker devices.",
                is_user=False,
            )
        elif event_type == "mic_level":
            self._set_mic_level(event.get("level", 0.0))

    def _test_stt_once(self) -> None:
        """Capture one utterance and show raw transcript."""
        if self.voice_active or self.stt_test_active:
            return

        self.stt_test_active = True
        self.status_var.set("STT test: speak once and pause...")
        self.voice_phase_var.set("Voice: stt-test")
        self._set_test_stt_running(True)

        def worker() -> None:
            try:
                cfg = VoiceConfig(
                    sample_rate=16000,
                    vad_threshold=float(self.vad_threshold_var.get()),
                    min_speech_ms=250,
                    min_silence_ms=int(self.vad_silence_var.get()),
                    max_utterance_sec=12.0,
                    stt_model=self.stt_model_var.get(),
                    stt_language=self.stt_lang_var.get().strip() or "en",
                    device_in=self._parse_device_selection(self.mic_var.get()),
                    device_out=self._parse_device_selection(self.spk_var.get()),
                    allow_barge_in=True,
                )
                self.stt_test_pipeline = VoicePipeline(
                    api_key=self.api_key or "stt-test",
                    model=self.model_var.get(),
                    speak=False,
                    system_prompt=self._get_system_prompt(),
                    use_tools=self.tools_var.get(),
                    config=cfg,
                )
                transcript = self.stt_test_pipeline.transcribe_once(
                    on_event=lambda e: self.root.after(0, self._on_voice_event, e)
                )
                if transcript:
                    self.root.after(
                        0,
                        lambda t=transcript: self._add_message(
                            "STT Test", t, is_user=True
                        ),
                    )
                    self.root.after(0, lambda: self.status_var.set("STT test complete"))
                else:
                    self.root.after(
                        0,
                        lambda: self._add_message(
                            "STT Test",
                            "No transcript generated. Try speaking louder/longer.",
                            is_user=False,
                        ),
                    )
                    self.root.after(
                        0, lambda: self.status_var.set("STT test: no transcript")
                    )
            except MissingVoiceDependencies as e:
                self.root.after(
                    0,
                    lambda msg=str(e): messagebox.showerror(
                        "Voice Dependencies",
                        f"{msg}\nInstall with: uv sync --extra voice",
                    ),
                )
            except Exception as e:
                self.root.after(
                    0,
                    lambda msg=str(e): messagebox.showerror("STT Test Error", msg),
                )
            finally:
                self.stt_test_pipeline = None
                self.stt_test_active = False
                self.root.after(0, lambda: self.voice_phase_var.set("Voice: idle"))
                self.root.after(0, lambda: self._set_mic_level(0.0))
                self.root.after(0, lambda: self._set_test_stt_running(False))

        threading.Thread(target=worker, daemon=True).start()

    def _simulate_stt_once(self) -> None:
        """Play a prompt phrase, then run one-shot STT capture."""
        if self.voice_active or self.stt_test_active:
            return

        self.stt_test_active = True
        self.status_var.set("STT simulation: playing prompt...")
        self.voice_phase_var.set("Voice: stt-sim")
        self._set_test_stt_running(True)

        def worker() -> None:
            prompt = "What is the weather like today?"
            try:
                tts = TTSManager(
                    backend=self.backend_var.get(),
                    rate=self.rate_var.get(),
                    volume=self.volume_var.get(),
                )
                tts.speak(prompt)

                cfg = VoiceConfig(
                    sample_rate=16000,
                    vad_threshold=float(self.vad_threshold_var.get()),
                    min_speech_ms=250,
                    min_silence_ms=int(self.vad_silence_var.get()),
                    max_utterance_sec=12.0,
                    stt_model=self.stt_model_var.get(),
                    stt_language=self.stt_lang_var.get().strip() or "en",
                    device_in=self._parse_device_selection(self.mic_var.get()),
                    device_out=self._parse_device_selection(self.spk_var.get()),
                    allow_barge_in=True,
                )
                self.stt_test_pipeline = VoicePipeline(
                    api_key=self.api_key or "stt-test",
                    model=self.model_var.get(),
                    speak=False,
                    system_prompt=self._get_system_prompt(),
                    use_tools=self.tools_var.get(),
                    config=cfg,
                )
                self.root.after(
                    0, lambda: self._add_message("STT Prompt", prompt, is_user=False)
                )
                self.root.after(
                    0, lambda: self.status_var.set("STT simulation: listening...")
                )
                transcript = self.stt_test_pipeline.transcribe_once(
                    on_event=lambda e: self.root.after(0, self._on_voice_event, e)
                )
                if transcript:
                    self.root.after(
                        0,
                        lambda t=transcript: self._add_message(
                            "STT Sim Result", t, is_user=True
                        ),
                    )
                    self.root.after(
                        0, lambda: self.status_var.set("STT simulation complete")
                    )
                else:
                    self.root.after(
                        0,
                        lambda: self._add_message(
                            "STT Sim Result",
                            "No transcript generated from simulated prompt.",
                            is_user=False,
                        ),
                    )
                    self.root.after(
                        0,
                        lambda: self.status_var.set("STT simulation: no transcript"),
                    )
            except Exception as e:
                self.root.after(
                    0,
                    lambda msg=str(e): messagebox.showerror("STT Simulation Error", msg),
                )
            finally:
                self.stt_test_pipeline = None
                self.stt_test_active = False
                self.root.after(0, lambda: self.voice_phase_var.set("Voice: idle"))
                self.root.after(0, lambda: self._set_mic_level(0.0))
                self.root.after(0, lambda: self._set_test_stt_running(False))

        threading.Thread(target=worker, daemon=True).start()

    def _on_send(self, event=None) -> None:
        """Handle send button click."""
        message = self.input_field.get().strip()
        if not message:
            return

        # Check if already processing
        if self.response_thread and self.response_thread.is_alive():
            return

        # Clear stop flag
        self.stop_requested.clear()

        self.input_field.delete(0, tk.END)
        self._add_message("You", message, is_user=True)

        # Disable input while processing
        self.input_field.config(state=tk.DISABLED)
        self.send_button.itemconfig("rect", fill=ModernStyle.BG_TERTIARY)
        self.status_var.set("Thinking..." if self.thinking_var.get() else "Responding...")

        # Process in background thread
        self.response_thread = threading.Thread(
            target=self._get_response, args=(message,)
        )
        self.response_thread.daemon = True
        self.response_thread.start()

    def _get_response(self, message: str) -> None:
        """Get AI response in background thread."""
        try:
            if self.stop_requested.is_set():
                return

            # Update TTS settings
            if self.tts:
                self.tts.set_rate(self.rate_var.get())
                self.tts.set_volume(self.volume_var.get())

                # Find voice ID from name
                voice_id = self._voice_id_for_name(self.voice_var.get())
                if voice_id:
                    self.tts.set_voice(voice_id)

            # Get response
            max_tokens = self._current_max_tokens()
            with self._create_client() as client:
                system_prompt = self._get_system_prompt()
                use_tools = self.tools_var.get()
                messages: list[dict] = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": message})

                usage: dict = {}
                if use_tools and supports_tools(client):
                    register_all_tools(client)
                    response = client.chat_with_tools(messages, max_tokens=max_tokens)
                else:
                    data = client.chat_completion(messages, max_tokens=max_tokens)
                    usage = data.get("usage") or {}
                    choices = data.get("choices")
                    if isinstance(choices, list) and choices:
                        first = choices[0] if isinstance(choices[0], dict) else {}
                        message = first.get("message", {}) if isinstance(first, dict) else {}
                        content = message.get("content", "") if isinstance(message, dict) else ""
                        response = str(content)
                    else:
                        response = ""

                if not usage:
                    usage = getattr(client, "last_usage", {}) or {}
                provider_name = getattr(client, "provider_name", self.provider_var.get())

                if self.stop_requested.is_set():
                    return

            # Update UI in main thread
            self.root.after(0, self._on_response, response, usage, provider_name)
        except (LLMProviderError, Exception) as e:
            if not self.stop_requested.is_set():
                self.root.after(0, self._on_error, str(e))

    def _on_response(self, response: str, usage: dict | None = None, provider: str = "") -> None:
        """Handle AI response."""
        if self.stop_requested.is_set():
            self._reset_ui()
            return

        display_response = self._display_response_text(response)
        speech_response = self._speech_response_text(response)
        self._add_message("AI", display_response, is_user=False)
        if usage:
            total = int(usage.get("total_tokens", 0) or 0)
            prompt = int(usage.get("prompt_tokens", 0) or 0)
            completion = int(usage.get("completion_tokens", 0) or 0)
            self.token_var.set(f"{total:,} tok  ({prompt:,}+{completion:,})")
        elif provider == "local":
            self.token_var.set("tok n/a (local)")

        if self.speak_var.get() and self.tts and not self.stop_requested.is_set():
            self.status_var.set("Speaking...")
            self.speaking_thread = threading.Thread(
                target=self._speak_response, args=(speech_response,)
            )
            self.speaking_thread.daemon = True
            self.speaking_thread.start()
        else:
            self.status_var.set("Ready")
            self._reset_ui()

    def _speak_response(self, response: str) -> None:
        """Speak the response."""
        try:
            if not self.stop_requested.is_set():
                self.tts.speak(response)
        finally:
            if not self.stop_requested.is_set():
                self.root.after(0, lambda: self.status_var.set("Ready"))
            self.root.after(0, self._reset_ui)

    def _on_error(self, error: str) -> None:
        """Handle error."""
        self._add_message("Error", f"Failed to get response: {error}", is_user=False)
        self.status_var.set("Error occurred")
        self._reset_ui()

    def _reset_ui(self) -> None:
        """Reset UI to ready state."""
        self.input_field.config(state=tk.NORMAL)
        self.send_button.itemconfig("rect", fill=ModernStyle.ACCENT)
        self.input_field.focus()

    def _stop_all(self) -> None:
        """Stop all ongoing operations."""
        self.stop_requested.set()
        self._stop_voice_chat()

        # Stop TTS
        if self.tts:
            self.tts.stop()

        self.status_var.set("Stopped")
        self.root.after(100, self._reset_ui)

    def _add_message(self, sender: str, message: str, is_user: bool = False) -> None:
        """Add message to chat history."""
        self.chat_history.config(state=tk.NORMAL)

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        tag = "user" if is_user else "ai"
        self.chat_history.insert(tk.END, f"[{ts}] {sender}: ", tag)
        self.chat_history.insert(tk.END, f"{message}\n\n", "text")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def _clear_chat(self) -> None:
        """Clear chat history."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def _on_backend_changed(self, event=None) -> None:
        """Handle TTS backend change."""
        new_backend = self.backend_var.get()
        previous_backend = self.tts.backend_name if self.tts else "edge-tts"

        # Stop any current speech
        if self.tts:
            self.tts.stop()

        # Update status label
        if new_backend == "edge-tts":
            self.backend_status_label.config(text="🌐 Online", fg=ModernStyle.SUCCESS)
        elif new_backend == "kittentts":
            self.backend_status_label.config(text="🐱 Local", fg=ModernStyle.ACCENT)
        else:
            self.backend_status_label.config(text="💻 Offline", fg=ModernStyle.WARNING)

        # Reinitialize TTS with new backend
        try:
            self.tts = TTSManager(backend=new_backend)
            set_alert_callback(self.tts.speak)
            voices = self.tts.available_voices
            self._all_voices = voices

            # Update voice dropdown
            self._refresh_voice_dropdown(voices)

            self.status_var.set(f"Switched to {new_backend}")
        except Exception as e:
            messagebox.showerror(
                "Backend Error",
                f"Failed to switch to {new_backend}: {e}\n"
                "Falling back to previous backend.",
            )
            # Revert selection and restore a working TTS backend.
            self.backend_var.set(previous_backend)
            self.tts = TTSManager(backend=previous_backend)

    def _test_voice(self) -> None:
        """Test the voice."""
        if self.tts:
            self.tts.set_rate(self.rate_var.get())
            self.tts.set_volume(self.volume_var.get())
            self._set_test_tts_running(True)

            def worker() -> None:
                try:
                    self.tts.speak("Hello! This is how I sound.")
                finally:
                    self.root.after(0, lambda: self._set_test_tts_running(False))

            threading.Thread(target=worker, daemon=True).start()

    def run(self) -> None:
        """Run the GUI."""
        self.root.mainloop()


def main() -> None:
    """Entry point for the GUI."""
    gui = TalkBotGUI()
    try:
        gui.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
