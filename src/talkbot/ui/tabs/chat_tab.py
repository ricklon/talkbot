"""Chat tab UI components."""
import tkinter as tk
from talkbot.ui.components import ModernStyle

def create_chat_tab(parent: tk.Widget) -> tuple[tk.Text, tk.Widget]:
    """Create the Conversation tab and return the text widget."""
    tab_chat = tk.Frame(parent, bg=ModernStyle.BG_SECONDARY)
    
    chat_history = tk.Text(
        tab_chat,
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
    chat_history.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Configure text tags for styling
    chat_history.tag_configure(
        "user",
        foreground=ModernStyle.ACCENT,
        font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
    )
    chat_history.tag_configure(
        "ai",
        foreground=ModernStyle.SUCCESS,
        font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
    )
    chat_history.tag_configure("text", foreground=ModernStyle.TEXT_PRIMARY)
    
    return chat_history, tab_chat
