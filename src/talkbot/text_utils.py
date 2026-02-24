"""Text cleanup helpers for user-facing output."""

from __future__ import annotations

import re

_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
_LONE_CLOSE_THINK_RE = re.compile(r"</think>", re.IGNORECASE)


def strip_thinking(text: str) -> str:
    """Remove model thought blocks from user-visible output."""
    if not text:
        return ""
    cleaned = _THINK_BLOCK_RE.sub("", text)
    # Also remove lone </think> tags (model emitted closing tag without opening)
    cleaned = _LONE_CLOSE_THINK_RE.sub("", cleaned)
    return cleaned.strip()

