"""Thinking-mode helpers for response behavior."""

from __future__ import annotations

import os


NO_THINK_INSTRUCTION = (
    "Respond directly with concise final answers. "
    "Do not include chain-of-thought or <think> tags."
)


def env_thinking_default() -> bool:
    value = (os.getenv("TALKBOT_ENABLE_THINKING", "0") or "0").strip().lower()
    return value in {"1", "true", "yes", "on"}


def apply_thinking_system_prompt(system_prompt: str | None, enable_thinking: bool) -> str | None:
    if enable_thinking:
        return system_prompt
    if system_prompt:
        return f"{system_prompt}\n\n{NO_THINK_INSTRUCTION}"
    return NO_THINK_INSTRUCTION
