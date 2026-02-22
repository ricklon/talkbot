from talkbot.text_utils import strip_thinking


def test_strip_thinking_removes_think_blocks():
    text = "<think>internal</think>\nFinal answer."
    assert strip_thinking(text) == "Final answer."


def test_strip_thinking_keeps_regular_text():
    assert strip_thinking("Hello there") == "Hello there"

