import re

from talkbot import tools


class DummyClient:
    def __init__(self):
        self.calls = []

    def register_tool(self, name, func, description, parameters):
        self.calls.append(
            {
                "name": name,
                "func": func,
                "description": description,
                "parameters": parameters,
            }
        )


def test_calculator_evaluates_expression():
    assert tools.calculator("2 + 2") == "4"


def test_calculator_blocks_builtins():
    result = tools.calculator("__import__('os').system('echo hi')")
    assert result.startswith("Error:")


def test_roll_dice_single(monkeypatch):
    monkeypatch.setattr(tools.random, "randint", lambda _a, _b: 4)
    assert tools.roll_dice() == "Rolled 4"


def test_roll_dice_multiple(monkeypatch):
    values = iter([2, 5, 1])
    monkeypatch.setattr(tools.random, "randint", lambda _a, _b: next(values))
    assert tools.roll_dice(sides=6, count=3) == "Rolled 3d6: [2, 5, 1] = 8"


def test_random_number_validates_bounds():
    assert tools.random_number(5, 5) == "Error: min_val must be less than max_val"


def test_time_and_date_format():
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", tools.get_current_date())
    assert re.match(
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?: [A-Z0-9+\-:]+)?$",
        tools.get_current_time(),
    )


def test_register_all_tools_registers_every_definition():
    client = DummyClient()

    tools.register_all_tools(client)

    expected = set(tools.TOOL_DEFINITIONS.keys())
    got = {call["name"] for call in client.calls}

    assert got == expected
    assert len(client.calls) == len(expected)


def test_set_timer_accepts_seconds_string_and_can_cancel():
    tools._timers.clear()
    tools._timer_counter = 0

    msg = tools.set_timer("10 secs")
    assert "Timer #1 set." in msg
    assert "10 seconds" in msg
    assert tools.cancel_timer("1").startswith("Timer #1")


def test_list_tools_validate_and_parse_inputs(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "_data_dir", lambda: tmp_path)

    assert tools.create_list("   ") == "Error: list_name must not be empty."
    assert tools.add_to_list("  ", "shopping") == "Error: item must not be empty."

    assert tools.create_list("shopping") == "Created 'shopping' list."
    msg = tools.add_items_to_list("milk, eggs, bread", "shopping")
    assert "Added milk, eggs, bread to the shopping list." == msg
    got = tools.get_list("shopping")
    assert "- milk" in got and "- eggs" in got and "- bread" in got
