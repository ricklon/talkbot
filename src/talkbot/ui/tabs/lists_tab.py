"""Lists tab UI components."""
import tkinter as tk
from talkbot.ui.components import ModernStyle

def create_lists_tab(parent: tk.Widget) -> tuple[tk.Listbox, tk.Widget]:
    """Create the Lists tab and return the listbox widget."""
    tab_lists = tk.Frame(parent, bg=ModernStyle.BG_SECONDARY)
    
    tk.Label(
        tab_lists,
        text="Stored lists update every 2 seconds.",
        bg=ModernStyle.BG_SECONDARY,
        fg=ModernStyle.TEXT_SECONDARY,
        font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        anchor=tk.W,
    ).pack(fill=tk.X, padx=8, pady=(8, 4))

    lists_box = tk.Listbox(
        tab_lists,
        bg=ModernStyle.BG_TERTIARY,
        fg=ModernStyle.TEXT_PRIMARY,
        font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
        selectmode=tk.SINGLE,
        relief=tk.FLAT,
        bd=0,
        highlightthickness=0,
        activestyle="none",
    )
    lists_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    return lists_box, tab_lists
