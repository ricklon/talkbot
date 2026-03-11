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

# Phase 2: symbols and numeric forms hostile to TTS
# Percent: "15%" or "15 %" → "15 percent"
_PERCENT_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*%")
# Currency: "$42", "$3.99", "$1,200" → "42 dollars", "3.99 dollars", "1,200 dollars"
# Cents: "$0.50" → "50 cents"  (special-cased in the replacement function)
_CURRENCY_RE = re.compile(r"\$(\d[\d,]*(?:\.\d+)?)")
# Ordinals: "1st", "2nd", "3rd", "4th" … "20th" → written form
# Covers 1–19 uniquely; 20+ fall through to generic "Nth" handler
_ORDINAL_RE = re.compile(r"\b(\d+)(st|nd|rd|th)\b", re.IGNORECASE)
_ORDINAL_MAP = {
    1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
    6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
    11: "eleventh", 12: "twelfth", 13: "thirteenth", 14: "fourteenth",
    15: "fifteenth", 16: "sixteenth", 17: "seventeenth", 18: "eighteenth",
    19: "nineteenth", 20: "twentieth",
}
# Time: unambiguous HH:MM — only 00:00–23:59, not followed by more digits or "/"
# Converts to 12-hour spoken form: "14:32" → "2 32 PM", "09:05" → "9 05 AM"
_TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b(?![\d/])")


def _replace_currency(m: re.Match) -> str:
    """'$3.99' → '3 dollars and 99 cents', '$0.45' → '45 cents', '$42' → '42 dollars'."""
    raw = m.group(1).replace(",", "")
    try:
        value = float(raw)
    except ValueError:
        return m.group(0)
    dollars = int(value)
    cents = round((value - dollars) * 100)
    if dollars == 0:
        return f"{cents} cents"
    if cents == 0:
        return f"{dollars:,} dollars".replace(",", " ")
    return f"{dollars:,} dollars and {cents} cents".replace(",", " ")


def _replace_ordinal(m: re.Match) -> str:
    """'1st' → 'first', '21st' → '21st' (unchanged above 20)."""
    n = int(m.group(1))
    return _ORDINAL_MAP.get(n, m.group(0))


def _replace_time(m: re.Match) -> str:
    """'14:32' → '2 32 PM', '09:05' → '9 05 AM', '00:00' → '12 00 AM'."""
    hour = int(m.group(1))
    minute = int(m.group(2))
    period = "AM" if hour < 12 else "PM"
    hour12 = hour % 12 or 12
    min_str = f"{minute:02d}"
    return f"{hour12} {min_str} {period}"


def tts_friction_score(text: str) -> tuple[int, dict[str, int]]:
    """Count TTS-hostile token patterns in text before normalization.

    Returns (total_score, detail_dict) where detail_dict breaks the count
    down by category. A score of 0 means the text is clean for TTS.

    Categories:
      markdown    — code fences, inline code, bold/italic, headers, bullets, HRs
      identifiers — underscore_identifiers (snake_case tokens)
      label_ids   — "Timer ID: 3" style patterns
      symbols     — %, $, ordinals (1st/2nd/3rd), HH:MM time
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

    symbol_count = (
        len(_PERCENT_RE.findall(text))
        + len(_CURRENCY_RE.findall(text))
        + len(_ORDINAL_RE.findall(text))
        + len(_TIME_RE.findall(text))
    )
    if symbol_count:
        detail["symbols"] = symbol_count

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
    # Phase 2: symbols and numeric forms
    text = _PERCENT_RE.sub(r"\1 percent", text)      # 15% → 15 percent
    text = _CURRENCY_RE.sub(_replace_currency, text) # $42 → 42 dollars
    text = _ORDINAL_RE.sub(_replace_ordinal, text)   # 1st → first
    text = _TIME_RE.sub(_replace_time, text)         # 14:32 → 2 32 PM
    return text.strip()

