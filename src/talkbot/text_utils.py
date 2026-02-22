"""Text cleanup helpers for user-facing output."""

from __future__ import annotations

import re

_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


def strip_thinking(text: str) -> str:
    """Remove model thought blocks from user-visible output."""
    if not text:
        return ""
    cleaned = _THINK_BLOCK_RE.sub("", text)
    return cleaned.strip()

