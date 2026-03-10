"""Shared pytest fixtures for TalkBot tests."""

import pytest


class FakeBenchClient:
    """Minimal fake LLM client for benchmark tests. No real API calls."""

    supports_tools = True
    provider_name = "fake"

    def __init__(self):
        self.tools = {}
        self.last_usage = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def clear_tools(self):
        self.tools.clear()

    def register_tool(self, name, func, description, parameters):
        del description, parameters
        self.tools[name] = func

    def chat_completion(self, messages, temperature=0.0, max_tokens=None):
        del messages, temperature, max_tokens
        return {"choices": [{"message": {"content": "ok"}}]}

    def chat_with_tools(self, messages, temperature=0.0, max_tokens=None):
        del temperature, max_tokens
        user_text = str(messages[-1]["content"])
        self.last_usage = {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        }
        lower = user_text.lower()
        if "set a timer for 10" in lower:
            return self.tools["set_timer"](seconds=10)
        if "set a timer for 0" in lower:
            return self.tools["set_timer"](seconds=0)
        if "retry that timer with 6" in lower:
            return self.tools["set_timer"](seconds=6)
        if "list timers" in lower:
            return self.tools["list_timers"]()
        if "cancel timer 1" in lower:
            return self.tools["cancel_timer"](timer_id="1")
        if "create a packing list" in lower:
            return self.tools["create_list"](list_name="packing")
        if "add socks and charger to the packing list" in lower:
            return self.tools["add_to_list"](
                items=["socks", "charger"],
                list_name="packing",
            )
        if "show me the packing list" in lower:
            return self.tools["get_list"](list_name="packing")
        if "create a grocery list" in lower:
            return self.tools["create_list"](list_name="grocery")
        if "add milk to the grocery list" in lower:
            return self.tools["add_to_list"](items="milk", list_name="grocery")
        if "what lists do you have" in lower:
            return self.tools["list_all_lists"]()
        if "remember that the launch codename is atlas" in lower:
            return self.tools["remember"](key="launch_codename", value="atlas")
        if "what launch codename did i ask you to remember" in lower:
            return self.tools["recall"](key="launch_codename")
        if "remember that my favorite color is blue" in lower:
            return self.tools["remember"](key="favorite_color", value="blue")
        if "what is my favorite color" in lower:
            return self.tools["recall"](key="favorite_color")
        if "what is 15 percent of 47" in lower:
            return self.tools["calculator"]("15 * 0.01 * 47")
        if "now divide that by 3" in lower:
            return self.tools["calculator"]("7.05 / 3")
        if "what time is it" in lower or "what time is it right now" in lower:
            return self.tools["get_current_time"]()
        if "set a timer for 5 minutes" in lower:
            return self.tools["set_timer"](seconds=300)
        if "add 'check the timer' to my reminders list" in lower:
            self.tools["create_list"](list_name="reminders")
            return self.tools["add_to_list"](items="check the timer", list_name="reminders")
        if "what's today's date" in lower:
            return self.tools["get_current_date"]()
        if "cancel timer #99" in lower:
            self.tools["set_timer"](seconds=0)  # produces error trace for tool_call_error_rate
            return self.tools["cancel_timer"](timer_id="99")
        if "list my timers so i can see" in lower:
            return self.tools["list_timers"]()
        return "Unhandled"


@pytest.fixture
def fake_bench_client_factory():
    """Returns a client_factory function that always yields a FakeBenchClient."""
    return lambda p: FakeBenchClient()
