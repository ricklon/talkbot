"""Prompt tab UI components."""
import tkinter as tk
import os
from talkbot.ui.components import ModernStyle

def create_prompt_tab(parent: tk.Widget) -> tuple[tk.Text, tk.Widget]:
    """Create the Prompt tab and return the text widget."""
    tab_prompt = tk.Frame(parent, bg=ModernStyle.BG_SECONDARY)
    
    prompt_help = tk.Label(
        tab_prompt,
        text="System prompt used for text and voice conversations.",
        bg=ModernStyle.BG_SECONDARY,
        fg=ModernStyle.TEXT_SECONDARY,
        font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        anchor=tk.W,
    )
    prompt_help.pack(fill=tk.X, padx=8, pady=(8, 4))

    prompt_text = tk.Text(
        tab_prompt,
        wrap=tk.WORD,
        bg=ModernStyle.BG_TERTIARY,
        fg=ModernStyle.TEXT_PRIMARY,
        font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        padx=10,
        pady=10,
        relief=tk.FLAT,
        bd=0,
        height=14,
    )
    prompt_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    # Pre-populate from env var if set
    env_prompt = os.getenv("TALKBOT_AGENT_PROMPT", "").strip()
    if env_prompt:
        prompt_text.insert("1.0", env_prompt)
        
    return prompt_text, tab_prompt
