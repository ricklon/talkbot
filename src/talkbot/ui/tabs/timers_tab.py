"""Timers tab UI components."""
import tkinter as tk
from talkbot.ui.components import ModernStyle

def create_timers_tab(parent: tk.Widget) -> tuple[tk.Listbox, tk.Widget]:
    """Create the Timers tab and return the listbox widget."""
    tab_timers = tk.Frame(parent, bg=ModernStyle.BG_SECONDARY)
    
    tk.Label(
        tab_timers,
        text="Active timers and reminders update every second.",
        bg=ModernStyle.BG_SECONDARY,
        fg=ModernStyle.TEXT_SECONDARY,
        font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        anchor=tk.W,
    ).pack(fill=tk.X, padx=8, pady=(8, 4))

    timers_list = tk.Listbox(
        tab_timers,
        bg=ModernStyle.BG_TERTIARY,
        fg=ModernStyle.TEXT_PRIMARY,
        font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        selectmode=tk.SINGLE,
        relief=tk.FLAT,
        bd=0,
        highlightthickness=0,
        activestyle="none",
    )
    timers_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    return timers_list, tab_timers
