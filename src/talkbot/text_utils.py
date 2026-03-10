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


# Pre-compiled regexes for TTS normalization
_MD_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.DOTALL)
_MD_CODE_SPAN_RE = re.compile(r"`([^`]+)`")
_MD_BOLD_ITALIC_RE = re.compile(r"\*{1,3}([^*]+)\*{1,3}")
_MD_HEADER_RE = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_MD_BULLET_RE = re.compile(r"^\s*[-*]\s+", re.MULTILINE)
_MD_NUMBERED_RE = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)
_MD_HR_RE = re.compile(r"^[-*_]{3,}\s*$", re.MULTILINE)
_UNDERSCORE_ID_RE = re.compile(r"\b([a-z][a-z0-9]*)_([a-z][a-z0-9_]*)\b")
_LABEL_ID_RE = re.compile(r"\bID\s*[:=]\s*(\d+)", re.IGNORECASE)


def tts_friction_score(text: str) -> tuple[int, dict[str, int]]:
    """Count TTS-hostile token patterns in text before normalization.

    Returns (total_score, detail_dict) where detail_dict breaks the count
    down by category. A score of 0 means the text is clean for TTS.

    Categories:
      markdown  — code fences, inline code, bold/italic, headers, bullets, HRs
      identifiers — underscore_identifiers (snake_case tokens)
      label_ids   — "Timer ID: 3" style patterns
    """
    if not text:
        return 0, {}

    detail: dict[str, int] = {}

    md_count = (
        len(_MD_CODE_FENCE_RE.findall(text))
        + len(_MD_CODE_SPAN_RE.findall(text))
        + len(_MD_BOLD_ITALIC_RE.findall(text))
        + len(_MD_HEADER_RE.findall(text))
        + len(_MD_BULLET_RE.findall(text))
        + len(_MD_NUMBERED_RE.findall(text))
        + len(_MD_HR_RE.findall(text))
    )
    if md_count:
        detail["markdown"] = md_count

    id_count = len(_UNDERSCORE_ID_RE.findall(text))
    if id_count:
        detail["identifiers"] = id_count

    label_count = len(_LABEL_ID_RE.findall(text))
    if label_count:
        detail["label_ids"] = label_count

    return sum(detail.values()), detail


def normalize_for_tts(text: str) -> str:
    """Normalize LLM output for natural-sounding TTS synthesis."""
    if not text:
        return ""
    text = _MD_CODE_FENCE_RE.sub("", text)         # remove code blocks
    text = _MD_CODE_SPAN_RE.sub(r"\1", text)        # `code` → code
    text = _MD_BOLD_ITALIC_RE.sub(r"\1", text)      # **bold** → bold
    text = _MD_HEADER_RE.sub("", text)              # ## Header → Header
    text = _MD_BULLET_RE.sub("", text)              # - item → item
    text = _MD_NUMBERED_RE.sub("", text)            # 1. item → item
    text = _MD_HR_RE.sub("", text)                  # --- → removed
    # Apply iteratively to handle chained identifiers: set_a_timer → set a timer
    while True:
        replaced = _UNDERSCORE_ID_RE.sub(r"\1 \2", text)
        if replaced == text:
            break
        text = replaced
    text = _LABEL_ID_RE.sub(r"\1", text)             # Timer ID: 3 → Timer 3
    return text.strip()

