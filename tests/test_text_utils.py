from talkbot.text_utils import normalize_for_tts, strip_thinking, tts_friction_score


def test_strip_thinking_removes_think_blocks():
    text = "<think>internal</think>\nFinal answer."
    assert strip_thinking(text) == "Final answer."


def test_strip_thinking_keeps_regular_text():
    assert strip_thinking("Hello there") == "Hello there"


# --- normalize_for_tts tests ---


def test_normalize_bold():
    assert normalize_for_tts("This is **bold** text.") == "This is bold text."


def test_normalize_italic():
    assert normalize_for_tts("This is *italic* text.") == "This is italic text."


def test_normalize_bold_italic():
    assert normalize_for_tts("This is ***both*** text.") == "This is both text."


def test_normalize_code_span():
    assert normalize_for_tts("Use `cancel_timer` now.") == "Use cancel timer now."


def test_normalize_code_fence_removed():
    text = "Here:\n```python\nprint('hi')\n```\nDone."
    result = normalize_for_tts(text)
    assert "```" not in result
    assert "print" not in result
    assert "Done." in result


def test_normalize_header():
    assert normalize_for_tts("## Results") == "Results"


def test_normalize_header_h1():
    assert normalize_for_tts("# Title\nSome text.") == "Title\nSome text."


def test_normalize_bullet_dash():
    text = "- First item\n- Second item"
    result = normalize_for_tts(text)
    assert "- " not in result
    assert "First item" in result
    assert "Second item" in result


def test_normalize_bullet_star():
    text = "* Item one"
    result = normalize_for_tts(text)
    assert "* " not in result
    assert "Item one" in result


def test_normalize_numbered_list():
    text = "1. First\n2. Second"
    result = normalize_for_tts(text)
    assert "1. " not in result
    assert "First" in result


def test_normalize_horizontal_rule():
    text = "Above\n---\nBelow"
    result = normalize_for_tts(text)
    assert "---" not in result
    assert "Above" in result
    assert "Below" in result


def test_normalize_underscore_identifier():
    assert normalize_for_tts("cancel_timer") == "cancel timer"


def test_normalize_underscore_chained():
    assert normalize_for_tts("set_a_timer") == "set a timer"


def test_normalize_label_id():
    assert normalize_for_tts("Timer ID: 3 has been set.") == "Timer 3 has been set."
    assert normalize_for_tts("Timer ID=42 is active.") == "Timer 42 is active."


def test_normalize_plain_text_unchanged():
    text = "The timer is set for five minutes."
    assert normalize_for_tts(text) == text


def test_normalize_empty_string():
    assert normalize_for_tts("") == ""


def test_normalize_whitespace_only():
    assert normalize_for_tts("   ") == ""


def test_normalize_idempotent():
    text = "A simple response with no markdown."
    assert normalize_for_tts(normalize_for_tts(text)) == normalize_for_tts(text)


def test_normalize_uppercase_not_affected():
    # ALL_CAPS constants should not be split
    assert normalize_for_tts("TALKBOT_DATA_DIR") == "TALKBOT_DATA_DIR"


def test_normalize_file_path_not_affected():
    # Paths with slashes should not be altered by underscore rule
    text = "See /home/user/my_file for details."
    result = normalize_for_tts(text)
    # The path segment itself may be altered but the slash prevents full match
    assert "/home/user/" in result


# --- tts_friction_score tests ---


def test_friction_clean_text_is_zero():
    score, detail = tts_friction_score("The timer is set for five minutes.")
    assert score == 0
    assert detail == {}


def test_friction_empty_string():
    score, detail = tts_friction_score("")
    assert score == 0
    assert detail == {}


def test_friction_counts_markdown_bold():
    score, detail = tts_friction_score("This is **bold** text.")
    assert score >= 1
    assert "markdown" in detail


def test_friction_counts_code_fence():
    score, detail = tts_friction_score("Here:\n```python\nprint('hi')\n```")
    assert "markdown" in detail
    assert detail["markdown"] >= 1


def test_friction_counts_bullet():
    score, detail = tts_friction_score("Options:\n- First\n- Second")
    assert "markdown" in detail


def test_friction_counts_underscore_identifier():
    score, detail = tts_friction_score("Call cancel_timer to stop it.")
    assert score >= 1
    assert "identifiers" in detail
    assert detail["identifiers"] == 1


def test_friction_counts_label_id():
    score, detail = tts_friction_score("Timer ID: 3 is running.")
    assert "label_ids" in detail
    assert detail["label_ids"] == 1


def test_friction_multiple_categories():
    text = "**cancel_timer** for Timer ID: 5"
    score, detail = tts_friction_score(text)
    assert score >= 3
    assert "markdown" in detail
    assert "identifiers" in detail
    assert "label_ids" in detail


def test_friction_detail_sums_to_total():
    text = "**bold** `code` cancel_timer Timer ID: 2"
    score, detail = tts_friction_score(text)
    assert score == sum(detail.values())


def test_friction_score_before_normalization():
    """Score is computed on raw text, not normalized text."""
    raw = "Use cancel_timer now."
    score_raw, _ = tts_friction_score(raw)
    normalized = normalize_for_tts(raw)
    score_after, _ = tts_friction_score(normalized)
    assert score_raw >= 1
    assert score_after == 0


# --- Phase 2 normalization tests ---


def test_normalize_percent():
    assert normalize_for_tts("15% off today.") == "15 percent off today."


def test_normalize_percent_with_space():
    assert normalize_for_tts("Score: 98 %.") == "Score: 98 percent."


def test_normalize_percent_decimal():
    assert normalize_for_tts("Rate is 3.5%.") == "Rate is 3.5 percent."


def test_normalize_currency_whole():
    assert normalize_for_tts("It costs $42.") == "It costs 42 dollars."


def test_normalize_currency_cents():
    assert normalize_for_tts("Price: $3.99.") == "Price: 3 dollars and 99 cents."


def test_normalize_currency_cents_only():
    assert normalize_for_tts("Just $0.50 more.") == "Just 50 cents more."


def test_normalize_currency_thousands():
    assert normalize_for_tts("Costs $1,200.") == "Costs 1 200 dollars."


def test_normalize_ordinal_1st():
    assert normalize_for_tts("You finished 1st!") == "You finished first!"


def test_normalize_ordinal_2nd():
    assert normalize_for_tts("The 2nd item.") == "The second item."


def test_normalize_ordinal_3rd():
    assert normalize_for_tts("3rd place.") == "third place."


def test_normalize_ordinal_12th():
    assert normalize_for_tts("December 12th.") == "December twelfth."


def test_normalize_ordinal_above_20_unchanged():
    # 21st and above fall through unchanged
    assert normalize_for_tts("The 21st century.") == "The 21st century."


def test_normalize_time_afternoon():
    assert normalize_for_tts("Meeting at 14:30.") == "Meeting at 2 30 PM."


def test_normalize_time_morning():
    assert normalize_for_tts("Alarm set for 09:05.") == "Alarm set for 9 05 AM."


def test_normalize_time_midnight():
    assert normalize_for_tts("Starts at 00:00.") == "Starts at 12 00 AM."


def test_normalize_time_noon():
    assert normalize_for_tts("Lunch at 12:00.") == "Lunch at 12 00 PM."


def test_normalize_time_not_affected_by_date():
    # "2026/03/10" should not be matched (followed by /)
    result = normalize_for_tts("Date: 2026/03/10.")
    assert "2026/03/10" in result


def test_friction_counts_percent():
    score, detail = tts_friction_score("Save 20% today!")
    assert "symbols" in detail
    assert detail["symbols"] >= 1


def test_friction_counts_currency():
    score, detail = tts_friction_score("It costs $9.99.")
    assert "symbols" in detail
    assert detail["symbols"] >= 1


def test_friction_counts_ordinal():
    score, detail = tts_friction_score("You are 3rd in line.")
    assert "symbols" in detail


def test_friction_counts_time():
    score, detail = tts_friction_score("Call at 15:00.")
    assert "symbols" in detail


def test_normalize_phase2_idempotent():
    text = "Pay $10 by 14:00 on the 3rd."
    once = normalize_for_tts(text)
    twice = normalize_for_tts(once)
    assert once == twice
