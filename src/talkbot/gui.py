"""Tkinter GUI for the talking bot with modern styling."""

import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, scrolledtext, messagebox

from dotenv import load_dotenv

from talkbot.openrouter import OpenRouterClient
from talkbot.tts import TTSManager

# Load environment variables from .env file
env_path = Path.cwd() / ".env"
if env_path.exists():
    load_dotenv(env_path)


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


class TalkBotGUI:
    """GUI for the TalkBot application with modern styling."""

    def __init__(self, api_key: str = None, model: str = "openai/gpt-3.5-turbo"):
        """Initialize the GUI."""
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.client: OpenRouterClient = None
        self.tts: TTSManager = None
        self.speaking_thread: threading.Thread = None
        self.response_thread: threading.Thread = None
        self.stop_requested = threading.Event()

        self.root = tk.Tk()
        self.root.title("TalkBot - AI Talking Assistant")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        self.root.configure(bg=ModernStyle.BG_PRIMARY)

        # Configure ttk styles
        self._configure_styles()

        self._create_widgets()
        self._setup_tts()

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

        # Model and Backend row
        row1 = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)
        row1.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            row1,
            text="Model:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)

        self.model_var = tk.StringVar(value=self.model)
        model_combo = ttk.Combobox(
            row1,
            textvariable=self.model_var,
            values=[
                "openai/gpt-3.5-turbo",
                "openai/gpt-4",
                "anthropic/claude-3-haiku",
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-opus",
                "google/gemini-flash-1.5",
                "meta-llama/llama-3.1-8b-instruct",
                "meta-llama/llama-3.1-70b-instruct",
            ],
            width=35,
            style="Modern.TCombobox",
        )
        model_combo.pack(side=tk.LEFT, padx=(10, 20))

        tk.Label(
            row1,
            text="TTS Backend:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)

        self.backend_var = tk.StringVar(value="edge-tts")
        backend_combo = ttk.Combobox(
            row1,
            textvariable=self.backend_var,
            values=["edge-tts", "kittentts", "pyttsx3"],
            width=12,
            style="Modern.TCombobox",
            state="readonly",
        )
        backend_combo.pack(side=tk.LEFT, padx=(10, 20))
        backend_combo.bind("<<ComboboxSelected>>", self._on_backend_changed)

        # Backend status indicator
        self.backend_status_label = tk.Label(
            row1,
            text="🌐 Online",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.SUCCESS,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        )
        self.backend_status_label.pack(side=tk.LEFT)

        # Voice row
        row1b = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)
        row1b.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            row1b,
            text="Voice:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        ).pack(side=tk.LEFT)

        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(
            row1b, textvariable=self.voice_var, width=40, style="Modern.TCombobox"
        )
        self.voice_combo.pack(side=tk.LEFT, padx=(10, 0))

        # Sliders row
        row2 = tk.Frame(settings_frame, bg=ModernStyle.BG_SECONDARY)
        row2.pack(fill=tk.X)

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

        # Chat display
        chat_frame = tk.LabelFrame(
            main_container,
            text=" Conversation ",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, 10, "bold"),
        )
        chat_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))

        self.chat_history = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            padx=10,
            pady=10,
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=0,
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure text tags for styling
        self.chat_history.tag_configure(
            "user",
            foreground=ModernStyle.ACCENT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
        )
        self.chat_history.tag_configure(
            "ai",
            foreground=ModernStyle.SUCCESS,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
        )
        self.chat_history.tag_configure("text", foreground=ModernStyle.TEXT_PRIMARY)

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

    def _setup_tts(self) -> None:
        """Setup TTS and populate voice list."""
        try:
            backend = self.backend_var.get()
            self.tts = TTSManager(backend=backend)
            voices = self.tts.available_voices

            self.voice_combo["values"] = [v["name"] for v in voices]
            if voices:
                # Find English voice as default
                default_voice = next(
                    (v for v in voices if "en" in v.get("languages", [])), voices[0]
                )
                self.voice_var.set(default_voice["name"])
                self.tts.set_voice(default_voice["id"])

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
        self.status_var.set("Thinking...")

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
                for voice in self.tts.available_voices:
                    if voice["name"] == self.voice_var.get():
                        self.tts.set_voice(voice["id"])
                        break

            # Get response
            with OpenRouterClient(
                api_key=self.api_key, model=self.model_var.get()
            ) as client:
                response = client.simple_chat(message)

                if self.stop_requested.is_set():
                    return

            # Update UI in main thread
            self.root.after(0, self._on_response, response)
        except Exception as e:
            if not self.stop_requested.is_set():
                self.root.after(0, self._on_error, str(e))

    def _on_response(self, response: str) -> None:
        """Handle AI response."""
        if self.stop_requested.is_set():
            self._reset_ui()
            return

        self._add_message("AI", response, is_user=False)

        if self.speak_var.get() and self.tts and not self.stop_requested.is_set():
            self.status_var.set("Speaking...")
            self.speaking_thread = threading.Thread(
                target=self._speak_response, args=(response,)
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

        # Stop TTS
        if self.tts:
            self.tts.stop()

        self.status_var.set("Stopped")
        self.root.after(100, self._reset_ui)

    def _add_message(self, sender: str, message: str, is_user: bool = False) -> None:
        """Add message to chat history."""
        self.chat_history.config(state=tk.NORMAL)

        tag = "user" if is_user else "ai"
        self.chat_history.insert(tk.END, f"{sender}: ", tag)
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
            voices = self.tts.available_voices

            # Update voice dropdown
            self.voice_combo["values"] = [v["name"] for v in voices]
            if voices:
                # Try to find an English voice
                default_voice = next(
                    (v for v in voices if "en" in v.get("languages", [])), voices[0]
                )
                self.voice_var.set(default_voice["name"])
                self.tts.set_voice(default_voice["id"])

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
            threading.Thread(
                target=self.tts.speak, args=("Hello! This is how I sound.",)
            ).start()

    def run(self) -> None:
        """Run the GUI."""
        if not self.api_key:
            messagebox.showerror(
                "API Key Required",
                "Please set the OPENROUTER_API_KEY environment variable.",
            )
            sys.exit(1)

        self.root.mainloop()


def main() -> None:
    """Entry point for the GUI."""
    gui = TalkBotGUI()
    gui.run()


if __name__ == "__main__":
    main()
