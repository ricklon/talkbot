"""Helpers for loading, cataloging, and reviewing prompt presets."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from talkbot.tools import TOOLS


DEFAULT_PROMPT_CATALOG = Path("prompts/catalog.json")


@dataclass(frozen=True)
class PromptPreset:
    """Named prompt preset tracked in the prompt catalog."""

    name: str
    path: Path
    summary: str = ""
    goals: tuple[str, ...] = ()
    scenarios: tuple[str, ...] = ()
    review_notes: str = ""

    def load_text(self) -> str:
        try:
            return self.path.read_text(encoding="utf-8").strip()
        except OSError:
            return ""


@dataclass(frozen=True)
class PromptReviewFinding:
    """Single prompt review issue or note."""

    severity: str
    code: str
    message: str


def _resolve_prompt_file(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _resolve_catalog_path(path: str | Path | None = None) -> Path:
    candidate = Path(path) if path is not None else DEFAULT_PROMPT_CATALOG
    candidate = candidate.expanduser()
    if candidate.is_absolute():
        return candidate
    return Path.cwd() / candidate


def describe_prompt_path(path: Path) -> str:
    """Return a stable display label for a prompt file path."""
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def load_prompt_catalog(path: str | Path | None = None) -> list[PromptPreset]:
    """Load prompt presets from a JSON catalog."""
    catalog_path = _resolve_catalog_path(path)
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    raw_prompts = payload.get("prompts", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_prompts, list):
        raise ValueError(f"Prompt catalog at '{catalog_path}' must contain a prompt list.")

    presets: list[PromptPreset] = []
    for index, entry in enumerate(raw_prompts):
        if not isinstance(entry, dict):
            raise ValueError(f"Prompt catalog entry #{index} must be an object.")
        name = str(entry.get("name") or "").strip()
        file_value = str(entry.get("file") or "").strip()
        if not name or not file_value:
            raise ValueError(f"Prompt catalog entry #{index} must define 'name' and 'file'.")

        file_path = Path(file_value).expanduser()
        if not file_path.is_absolute():
            file_path = (catalog_path.parent / file_path).resolve()

        goals = tuple(str(goal).strip() for goal in entry.get("goals") or [] if str(goal).strip())
        scenarios = tuple(
            str(scenario).strip() for scenario in entry.get("scenarios") or [] if str(scenario).strip()
        )
        presets.append(
            PromptPreset(
                name=name,
                path=file_path,
                summary=str(entry.get("summary") or "").strip(),
                goals=goals,
                scenarios=scenarios,
                review_notes=str(entry.get("review_notes") or "").strip(),
            )
        )

    return sorted(presets, key=lambda preset: preset.name)


def get_prompt_preset(name: str, path: str | Path | None = None) -> PromptPreset:
    """Return a prompt preset by catalog name."""
    target = str(name or "").strip().lower()
    for preset in load_prompt_catalog(path):
        if preset.name.lower() == target:
            return preset
    raise KeyError(f"Unknown prompt preset '{name}'.")


def resolve_prompt_reference(
    *,
    prompt_preset: str | None = None,
    prompt_file: str | Path | None = None,
    prompt_text: str | None = None,
    catalog_path: str | Path | None = None,
) -> tuple[str | None, str | None, str | None]:
    """Resolve prompt text plus stable preset/source metadata.

    Returns ``(text, preset_name, source_label)``.
    """
    preset_name = str(prompt_preset or "").strip()
    file_value = str(prompt_file or "").strip()
    text_value = str(prompt_text or "").strip()

    specified = sum(bool(value) for value in (preset_name, file_value, text_value))
    if specified > 1:
        raise ValueError("Specify only one of prompt_preset, prompt_file, or prompt_text.")

    if preset_name:
        preset = get_prompt_preset(preset_name, catalog_path)
        return preset.load_text() or None, preset.name, f"preset:{preset.name}"

    if file_value:
        resolved = _resolve_prompt_file(file_value)
        try:
            text = resolved.read_text(encoding="utf-8").strip()
        except OSError:
            text = ""
        return text or None, None, f"file:{describe_prompt_path(resolved)}"

    if text_value:
        return text_value, None, "inline"

    return None, None, None


def _extract_tool_references(text: str) -> set[str]:
    refs = set(re.findall(r"`([a-z_][a-z0-9_]*)`", text))
    refs.update(re.findall(r"\b([a-z_][a-z0-9_]*)\(", text))
    return refs


def review_prompt_preset(
    preset: PromptPreset,
    *,
    available_scenarios: set[str] | None = None,
) -> list[PromptReviewFinding]:
    """Return heuristic prompt review findings for a preset."""
    findings: list[PromptReviewFinding] = []
    text = preset.load_text()
    lowered = text.lower()

    if not preset.path.exists():
        findings.append(
            PromptReviewFinding(
                severity="error",
                code="missing_file",
                message=f"Prompt file does not exist: {preset.path}",
            )
        )
        return findings

    if not text:
        findings.append(
            PromptReviewFinding(
                severity="error",
                code="empty_prompt",
                message="Prompt file is empty.",
            )
        )
        return findings

    if not preset.summary:
        findings.append(
            PromptReviewFinding(
                severity="warning",
                code="missing_summary",
                message="Prompt catalog entry is missing a summary.",
            )
        )

    if not preset.goals:
        findings.append(
            PromptReviewFinding(
                severity="warning",
                code="missing_goals",
                message="Prompt catalog entry has no declared goals.",
            )
        )

    if not preset.scenarios:
        findings.append(
            PromptReviewFinding(
                severity="warning",
                code="missing_scenarios",
                message="Prompt catalog entry has no review scenarios.",
            )
        )

    if len(text) < 120:
        findings.append(
            PromptReviewFinding(
                severity="warning",
                code="prompt_too_short",
                message="Prompt is very short; review whether it carries enough behavioral guidance.",
            )
        )

    if len(text) > 4000:
        findings.append(
            PromptReviewFinding(
                severity="warning",
                code="prompt_too_long",
                message="Prompt is long enough to risk avoidable context cost and instruction conflicts.",
            )
        )

    if "tool_first" in preset.goals and "tool" not in lowered:
        findings.append(
            PromptReviewFinding(
                severity="error",
                code="missing_tool_guidance",
                message="Prompt goal says tool-first, but the prompt text never mentions tools.",
            )
        )

    if "voice" in preset.goals and not any(
        token in lowered for token in ("voice", "spoken", "speak", "speaking", "aloud")
    ):
        findings.append(
            PromptReviewFinding(
                severity="warning",
                code="missing_voice_guidance",
                message="Voice-oriented preset does not clearly mention spoken or voice output.",
            )
        )

    if "exact_args" in preset.goals and not any(
        phrase in lowered
        for phrase in ("exact parameter", "parameter name", "exact tool parameter", "exact argument")
    ):
        findings.append(
            PromptReviewFinding(
                severity="warning",
                code="missing_exact_args_guidance",
                message="Preset expects exact tool arguments, but the prompt does not state that clearly.",
            )
        )

    if available_scenarios is not None:
        missing_scenarios = sorted(set(preset.scenarios) - set(available_scenarios))
        for scenario_id in missing_scenarios:
            findings.append(
                PromptReviewFinding(
                    severity="error",
                    code="unknown_scenario",
                    message=f"Catalog references unknown review scenario '{scenario_id}'.",
                )
            )

    known_tools = set(TOOLS)
    unknown_tool_refs = sorted(
        ref for ref in _extract_tool_references(text) if ref not in known_tools
    )
    for tool_name in unknown_tool_refs:
        findings.append(
            PromptReviewFinding(
                severity="error",
                code="unknown_tool_reference",
                message=f"Prompt references unknown tool '{tool_name}'.",
            )
        )

    return findings


def get_agent_prompt_details() -> tuple[str | None, str]:
    """Return the default agent prompt and a human-readable source label.

    Precedence:
    1. ``TALKBOT_AGENT_PROMPT_FILE``
    2. ``TALKBOT_AGENT_PROMPT``
    """
    prompt_file = (os.getenv("TALKBOT_AGENT_PROMPT_FILE") or "").strip()
    if prompt_file:
        resolved = _resolve_prompt_file(prompt_file)
        try:
            text = resolved.read_text(encoding="utf-8").strip()
        except OSError:
            text = ""
        if text:
            display = describe_prompt_path(resolved)
            return text, f"file: {display}"

    prompt = (os.getenv("TALKBOT_AGENT_PROMPT") or "").strip()
    if prompt:
        return prompt, "env: TALKBOT_AGENT_PROMPT"
    return None, "default: empty"


def load_agent_prompt() -> str | None:
    """Load the default agent prompt from env or an external file."""
    prompt, _source = get_agent_prompt_details()
    return prompt
