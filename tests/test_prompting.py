from pathlib import Path

from talkbot.prompting import (
    PromptPreset,
    get_prompt_preset,
    load_prompt_catalog,
    resolve_prompt_reference,
    review_prompt_preset,
)


def test_load_prompt_catalog_reads_repo_presets():
    presets = load_prompt_catalog()

    names = [preset.name for preset in presets]
    assert names == ["agent", "tool_benchmark", "tool_reliability"]
    assert all(preset.path.exists() for preset in presets)


def test_get_prompt_preset_returns_named_entry():
    preset = get_prompt_preset("tool_reliability")

    assert preset.name == "tool_reliability"
    assert preset.path == Path.cwd() / "prompts" / "tool_reliability.md"
    assert "tool_first" in preset.goals


def test_review_prompt_preset_flags_unknown_tool_reference(tmp_path):
    prompt_file = tmp_path / "bad.md"
    prompt_file.write_text("For list tasks call `add_items_to_list`.", encoding="utf-8")
    preset = PromptPreset(
        name="bad",
        path=prompt_file,
        summary="Bad prompt",
        goals=("tool_first",),
        scenarios=("list_basics",),
    )

    findings = review_prompt_preset(
        preset,
        available_scenarios={
            "list_basics",
        },
    )

    assert any(
        finding.code == "unknown_tool_reference" and "add_items_to_list" in finding.message
        for finding in findings
    )


def test_review_prompt_preset_flags_missing_review_scenario(tmp_path):
    prompt_file = tmp_path / "sample.md"
    prompt_file.write_text("Use tools when available.", encoding="utf-8")
    preset = PromptPreset(
        name="sample",
        path=prompt_file,
        summary="Sample prompt",
        goals=("tool_first",),
        scenarios=("missing_scenario",),
    )

    findings = review_prompt_preset(preset, available_scenarios={"utility_time_date"})

    assert any(finding.code == "unknown_scenario" for finding in findings)


def test_resolve_prompt_reference_from_preset():
    text, preset_name, source = resolve_prompt_reference(prompt_preset="tool_reliability")

    assert "Always call tools" in text
    assert preset_name == "tool_reliability"
    assert source == "preset:tool_reliability"
