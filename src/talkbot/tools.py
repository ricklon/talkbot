"""Built-in tools for the talking bot."""

import datetime
import json
import math
import random
import threading
import time
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data directory for persistent storage
# ---------------------------------------------------------------------------

def _data_dir() -> Path:
    d = Path.home() / ".talkbot"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_json(filename: str) -> dict:
    p = _data_dir() / filename
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}


def _save_json(filename: str, data: dict) -> None:
    p = _data_dir() / filename
    p.write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Time / date
# ---------------------------------------------------------------------------

def get_current_time() -> str:
    """Get the current date and time with timezone."""
    now = datetime.datetime.now().astimezone()
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


def get_current_date() -> str:
    """Get the current date."""
    return datetime.date.today().isoformat()


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------

def calculator(expression: str) -> str:
    """Calculate a mathematical expression safely.

    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "sqrt(16)")
    """
    allowed_names = {
        "sqrt": math.sqrt,
        "pow": math.pow,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
    }

    import re as _re
    # Pre-process "X% of Y" → "(X/100)*Y"
    expression = _re.sub(
        r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)',
        lambda m: f"({m.group(1)}/100)*{m.group(2)}",
        expression,
        flags=_re.IGNORECASE,
    )
    # Pre-process remaining "X%" → "(X/100)"
    expression = _re.sub(r'(\d+(?:\.\d+)?)\s*%', r'(\1/100)', expression)

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


# ---------------------------------------------------------------------------
# Dice / randomness
# ---------------------------------------------------------------------------

def roll_dice(sides: int = 6, count: int = 1) -> str:
    """Roll dice and return the results.

    Args:
        sides: Number of sides on each die (default 6)
        count: Number of dice to roll (default 1)
    """
    if sides < 1 or count < 1:
        return "Error: sides and count must be at least 1"

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)

    if count == 1:
        return f"Rolled {rolls[0]}"
    else:
        return f"Rolled {count}d{sides}: {rolls} = {total}"


def flip_coin() -> str:
    """Flip a coin and return heads or tails."""
    return random.choice(["Heads", "Tails"])


def random_number(min_val: int = 1, max_val: int = 100) -> str:
    """Generate a random number within a range.

    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
    """
    if min_val >= max_val:
        return "Error: min_val must be less than max_val"
    return str(random.randint(min_val, max_val))


# ---------------------------------------------------------------------------
# Alert callback — lets callers (CLI, GUI) inject a speak function so timers
# fire through TTS rather than just printing to stdout.
# ---------------------------------------------------------------------------

_alert_callback: Any = None  # callable(text: str) | None


def set_alert_callback(fn) -> None:
    """Register a function to be called when a timer fires (e.g. tts.speak)."""
    global _alert_callback
    _alert_callback = fn


def clear_alert_callback() -> None:
    """Remove any registered alert callback."""
    global _alert_callback
    _alert_callback = None


def _fire_alert(text: str) -> None:
    """Deliver an alert via TTS callback if available, else print."""
    print(f"\n[TIMER] {text}", flush=True)
    if _alert_callback is not None:
        try:
            _alert_callback(text)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Timer registry
# ---------------------------------------------------------------------------

# Maps timer_id -> (label, cancel_event, fire_at_timestamp)
_timers: dict[str, tuple[str, threading.Event, float]] = {}
_timer_lock = threading.Lock()
_timer_counter = 0


def set_timer(seconds: int, label: str = "") -> str:
    """Set a timer that fires after the specified number of seconds.

    Args:
        seconds: How many seconds to wait before the timer fires
        label: Optional name for the timer (e.g., "pasta", "meeting")
    """
    global _timer_counter
    if seconds <= 0:
        return "Error: seconds must be a positive integer"

    display = label if label else f"{seconds}-second timer"

    with _timer_lock:
        _timer_counter += 1
        timer_id = str(_timer_counter)
        cancel_event = threading.Event()
        _timers[timer_id] = (display, cancel_event, time.time() + seconds)

    def _fire() -> None:
        cancelled = cancel_event.wait(timeout=seconds)
        with _timer_lock:
            _timers.pop(timer_id, None)
        if not cancelled:
            _fire_alert(f"{display} is done!")

    threading.Thread(target=_fire, daemon=True).start()
    return f"Timer #{timer_id} set. '{display}' will fire in {seconds} seconds."


def set_reminder(seconds: int, message: str) -> str:
    """Set a reminder that speaks a custom message when it fires.

    Args:
        seconds: How many seconds until the reminder fires
        message: The exact message to speak when the reminder fires (e.g., "Time to take your medication")
    """
    if seconds <= 0:
        return "Error: seconds must be a positive integer"
    if not message.strip():
        return "Error: message must not be empty"

    global _timer_counter
    with _timer_lock:
        _timer_counter += 1
        timer_id = str(_timer_counter)
        cancel_event = threading.Event()
        _timers[timer_id] = (message.strip(), cancel_event, time.time() + seconds)

    def _fire() -> None:
        cancelled = cancel_event.wait(timeout=seconds)
        with _timer_lock:
            _timers.pop(timer_id, None)
        if not cancelled:
            _fire_alert(message.strip())

    threading.Thread(target=_fire, daemon=True).start()
    mins, secs = divmod(seconds, 60)
    duration = f"{mins}m {secs}s" if mins else f"{secs}s"
    return f"Reminder #{timer_id} set for {duration}: \"{message.strip()}\""


def cancel_timer(timer_id: str) -> str:
    """Cancel an active timer by its ID.

    Args:
        timer_id: The timer ID returned by set_timer (e.g., "1")
    """
    with _timer_lock:
        entry = _timers.get(timer_id)
    if not entry:
        return f"No active timer with ID '{timer_id}'. Use list_timers to see active timers."
    label, cancel_event, _ = entry
    cancel_event.set()
    return f"Timer #{timer_id} ('{label}') cancelled."


def list_timers() -> str:
    """List all currently active timers and their remaining time."""
    with _timer_lock:
        snapshot = dict(_timers)
    if not snapshot:
        return "No active timers."
    now = time.time()
    lines = []
    for tid, (label, _, fire_at) in snapshot.items():
        remaining = max(0, int(fire_at - now))
        lines.append(f"#{tid}: '{label}' — {remaining}s remaining")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Web search
# ---------------------------------------------------------------------------

def web_search(query: str) -> str:
    """Search the web for an instant answer using DuckDuckGo.

    Args:
        query: The search query
    """
    try:
        import httpx

        resp = httpx.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": "1", "no_html": "1"},
            timeout=8.0,
            headers={"User-Agent": "TalkBot/1.0"},
        )
        data = resp.json()

        parts: list[str] = []
        if data.get("Answer"):
            parts.append(data["Answer"])
        abstract = data.get("AbstractText") or data.get("Abstract") or ""
        if abstract and abstract not in parts:
            parts.append(abstract)
        # Include top related topics if nothing else found
        if not parts:
            for topic in data.get("RelatedTopics", [])[:3]:
                text = topic.get("Text", "")
                if text:
                    parts.append(text)

        return "\n".join(parts) if parts else "No instant answer found for that query."
    except Exception as e:
        return f"Search error: {e}"


# ---------------------------------------------------------------------------
# Shopping / named lists
# ---------------------------------------------------------------------------

_LISTS_FILE = "lists.json"


def create_list(list_name: str) -> str:
    """Create a new empty named list. Use when the user wants to start a list but hasn't specified items yet.

    Args:
        list_name: The name of the list to create (e.g., 'shopping', 'todo', 'groceries')
    """
    data = _load_json(_LISTS_FILE)
    if list_name in data:
        items = data[list_name]
        if items:
            return f"The {list_name} list already exists with {len(items)} item(s)."
    data[list_name] = []
    _save_json(_LISTS_FILE, data)
    return f"Created '{list_name}' list."


def add_to_list(item: str, list_name: str = "shopping") -> str:
    """Add an item to a named list (default: shopping list).

    Args:
        item: The item to add
        list_name: Which list to add to (default 'shopping')
    """
    data = _load_json(_LISTS_FILE)
    lst = data.setdefault(list_name, [])
    if item in lst:
        return f"'{item}' is already on the {list_name} list."
    lst.append(item)
    _save_json(_LISTS_FILE, data)
    return f"Added '{item}' to the {list_name} list."


def add_items_to_list(items: list, list_name: str = "shopping") -> str:
    """Add multiple items to a named list at once.

    Args:
        items: List of items to add (e.g. ["lettuce", "tomato", "onion"])
        list_name: Which list to add to (default 'shopping')
    """
    data = _load_json(_LISTS_FILE)
    lst = data.setdefault(list_name, [])
    added = []
    skipped = []
    for item in items:
        item = str(item).strip()
        if not item:
            continue
        if item in lst:
            skipped.append(item)
        else:
            lst.append(item)
            added.append(item)
    _save_json(_LISTS_FILE, data)
    parts = []
    if added:
        parts.append(f"Added {', '.join(added)} to the {list_name} list.")
    if skipped:
        parts.append(f"Already had: {', '.join(skipped)}.")
    return " ".join(parts) if parts else f"No items added to {list_name} list."


def get_list(list_name: str = "shopping") -> str:
    """Get all items on a named list.

    Args:
        list_name: Which list to retrieve (default 'shopping')
    """
    data = _load_json(_LISTS_FILE)
    lst = data.get(list_name, [])
    if not lst:
        return f"The {list_name} list is empty."
    items = "\n".join(f"- {item}" for item in lst)
    return f"{list_name.capitalize()} list:\n{items}"


def remove_from_list(item: str, list_name: str = "shopping") -> str:
    """Remove an item from a named list.

    Args:
        item: The item to remove
        list_name: Which list to remove from (default 'shopping')
    """
    data = _load_json(_LISTS_FILE)
    lst = data.get(list_name, [])
    # Case-insensitive match
    matches = [x for x in lst if x.lower() == item.lower()]
    if not matches:
        return f"'{item}' was not found on the {list_name} list."
    for m in matches:
        lst.remove(m)
    data[list_name] = lst
    _save_json(_LISTS_FILE, data)
    return f"Removed '{matches[0]}' from the {list_name} list."


def clear_list(list_name: str = "shopping") -> str:
    """Clear all items from a named list.

    Args:
        list_name: Which list to clear (default 'shopping')
    """
    data = _load_json(_LISTS_FILE)
    data[list_name] = []
    _save_json(_LISTS_FILE, data)
    return f"Cleared the {list_name} list."


def list_all_lists() -> str:
    """List all named lists and their contents."""
    data = _load_json(_LISTS_FILE)
    if not data:
        return "No lists found."
    parts = []
    for list_name, items in data.items():
        if items:
            item_str = ", ".join(f'"{i}"' for i in items)
            parts.append(f"{list_name}: [{item_str}]")
        else:
            parts.append(f"{list_name}: (empty)")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Memory / user preferences
# ---------------------------------------------------------------------------

_MEMORY_FILE = "memory.json"


def remember(key: str, value: str) -> str:
    """Store a user preference or piece of information for later recall.

    Args:
        key: The name of the preference (e.g., 'favorite_music_service', 'name')
        value: The value to remember
    """
    data = _load_json(_MEMORY_FILE)
    data[key] = value
    _save_json(_MEMORY_FILE, data)
    return f"Remembered: {key} = {value}"


def recall(key: str) -> str:
    """Recall a previously stored preference or piece of information.

    Args:
        key: The name of the preference to look up
    """
    data = _load_json(_MEMORY_FILE)
    if key not in data:
        return f"No memory found for '{key}'."
    return f"{key}: {data[key]}"


def recall_all() -> str:
    """Recall all stored preferences and memories."""
    data = _load_json(_MEMORY_FILE)
    if not data:
        return "No memories stored yet."
    lines = "\n".join(f"- {k}: {v}" for k, v in data.items())
    return f"All memories:\n{lines}"


# ---------------------------------------------------------------------------
# Tool definitions for LLM
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = {
    "get_current_time": {
        "description": "Get the current date and time",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    "get_current_date": {
        "description": "Get the current date",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    "calculator": {
        "description": "Calculate a mathematical expression. Supports: +, -, *, /, sqrt(), pow(), sin(), cos(), tan(), log(), log10(), exp(), pi, e",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        },
    },
    "roll_dice": {
        "description": "Roll dice and return the results",
        "parameters": {
            "type": "object",
            "properties": {
                "sides": {
                    "type": "integer",
                    "description": "Number of sides on each die",
                    "default": 6,
                },
                "count": {
                    "type": "integer",
                    "description": "Number of dice to roll",
                    "default": 1,
                },
            },
            "required": [],
        },
    },
    "flip_coin": {
        "description": "Flip a coin and return heads or tails",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    "random_number": {
        "description": "Generate a random number within a range",
        "parameters": {
            "type": "object",
            "properties": {
                "min_val": {
                    "type": "integer",
                    "description": "Minimum value (inclusive)",
                    "default": 1,
                },
                "max_val": {
                    "type": "integer",
                    "description": "Maximum value (inclusive)",
                    "default": 100,
                },
            },
            "required": [],
        },
    },
    "set_reminder": {
        "description": "Set a reminder that speaks a custom message when it fires. Use this when the user says 'remind me to...' or wants a specific message spoken at a future time.",
        "parameters": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "integer",
                    "description": "Number of seconds until the reminder fires",
                },
                "message": {
                    "type": "string",
                    "description": "The exact message to speak when the reminder fires (e.g., 'Time to take your medication')",
                },
            },
            "required": ["seconds", "message"],
        },
    },
    "set_timer": {
        "description": "Set a countdown timer with an optional label. Use this for cooking, workouts, or simple countdowns. When done it says '{label} is done!'. For a custom spoken message use set_reminder instead.",
        "parameters": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "integer",
                    "description": "Number of seconds to wait before the timer fires",
                },
                "label": {
                    "type": "string",
                    "description": "Optional name for the timer (e.g., 'pasta', '10-minute break')",
                    "default": "",
                },
            },
            "required": ["seconds"],
        },
    },
    "cancel_timer": {
        "description": "Cancel an active timer by its ID",
        "parameters": {
            "type": "object",
            "properties": {
                "timer_id": {
                    "type": "string",
                    "description": "The timer ID returned by set_timer (e.g., '1')",
                }
            },
            "required": ["timer_id"],
        },
    },
    "list_timers": {
        "description": "List all currently active timers and their remaining time",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    "web_search": {
        "description": "Search the web for an instant answer using DuckDuckGo",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                }
            },
            "required": ["query"],
        },
    },
    "create_list": {
        "description": "Create a new empty named list. Use when the user says 'create a [name] list' or 'start a [name] list' without specifying items to add.",
        "parameters": {
            "type": "object",
            "properties": {
                "list_name": {
                    "type": "string",
                    "description": "The name of the list to create (e.g., 'shopping', 'todo', 'groceries')",
                }
            },
            "required": ["list_name"],
        },
    },
    "add_to_list": {
        "description": "Add an item to a named list (default: shopping list)",
        "parameters": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "The item to add"},
                "list_name": {
                    "type": "string",
                    "description": "Which list to add to",
                    "default": "shopping",
                },
            },
            "required": ["item"],
        },
    },
    "add_items_to_list": {
        "description": "Add multiple items to a named list at once. Use when the user names more than one item.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Items to add (e.g. [\"lettuce\", \"tomato\", \"onion\"])",
                },
                "list_name": {
                    "type": "string",
                    "description": "Which list to add to",
                    "default": "shopping",
                },
            },
            "required": ["items"],
        },
    },
    "get_list": {
        "description": "Get all items on a named list (default: shopping list)",
        "parameters": {
            "type": "object",
            "properties": {
                "list_name": {
                    "type": "string",
                    "description": "Which list to retrieve",
                    "default": "shopping",
                }
            },
            "required": [],
        },
    },
    "remove_from_list": {
        "description": "Remove an item from a named list (default: shopping list)",
        "parameters": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "The item to remove"},
                "list_name": {
                    "type": "string",
                    "description": "Which list to remove from",
                    "default": "shopping",
                },
            },
            "required": ["item"],
        },
    },
    "clear_list": {
        "description": "Clear all items from a named list (default: shopping list)",
        "parameters": {
            "type": "object",
            "properties": {
                "list_name": {
                    "type": "string",
                    "description": "Which list to clear",
                    "default": "shopping",
                }
            },
            "required": [],
        },
    },
    "list_all_lists": {
        "description": "Show all named lists and their contents",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    "remember": {
        "description": "Store a user preference or piece of information for later recall",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "The name of the preference (e.g., 'favorite_music_service', 'name')",
                },
                "value": {"type": "string", "description": "The value to remember"},
            },
            "required": ["key", "value"],
        },
    },
    "recall": {
        "description": "Recall a previously stored preference or piece of information by key",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "The name of the preference to look up",
                }
            },
            "required": ["key"],
        },
    },
    "recall_all": {
        "description": "Recall all stored user preferences and memories",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOLS = {
    "get_current_time": get_current_time,
    "get_current_date": get_current_date,
    "calculator": calculator,
    "roll_dice": roll_dice,
    "flip_coin": flip_coin,
    "random_number": random_number,
    "set_reminder": set_reminder,
    "set_timer": set_timer,
    "cancel_timer": cancel_timer,
    "list_timers": list_timers,
    "web_search": web_search,
    "create_list": create_list,
    "add_to_list": add_to_list,
    "add_items_to_list": add_items_to_list,
    "get_list": get_list,
    "remove_from_list": remove_from_list,
    "clear_list": clear_list,
    "remember": remember,
    "recall": recall,
    "recall_all": recall_all,
    "list_all_lists": list_all_lists,
}


def register_all_tools(client) -> None:
    """Register all built-in tools with an OpenRouterClient.

    Args:
        client: OpenRouterClient instance
    """
    for name, func in TOOLS.items():
        if name in TOOL_DEFINITIONS:
            client.register_tool(
                name=name,
                func=func,
                description=TOOL_DEFINITIONS[name]["description"],
                parameters=TOOL_DEFINITIONS[name]["parameters"],
            )
