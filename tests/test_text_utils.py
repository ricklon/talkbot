from talkbot.text_utils import normalize_for_tts, strip_thinking


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

