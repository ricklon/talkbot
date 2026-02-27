"""Built-in tools for the talking bot."""

import datetime
import json
import math
import os
import random
import re
import threading
import time
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data directory for persistent storage
# ---------------------------------------------------------------------------

def _data_dir() -> Path:
    configured = os.getenv("TALKBOT_DATA_DIR", "").strip()
    d = Path(configured).expanduser() if configured else (Path.home() / ".talkbot")
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


def time_until(target: str) -> str:
    """Calculate how long until a target time and return a natural language duration.

    Args:
        target: Natural language time description (e.g. "tomorrow at 10am", "3pm", "10:30")
    """
    now = datetime.datetime.now().astimezone()
    target_lower = target.lower().strip()

    base_date = (now.date() + datetime.timedelta(days=1)) if "tomorrow" in target_lower else now.date()

    time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", target_lower)
    if not time_match:
        return f"Could not parse a time from: {target}"

    hour = int(time_match.group(1))
    minute = int(time_match.group(2) or 0)
    meridiem = time_match.group(3)

    if meridiem == "pm" and hour != 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0

    target_dt = datetime.datetime.combine(base_date, datetime.time(hour, minute)).astimezone()

    if base_date == now.date() and target_dt <= now:
        target_dt += datetime.timedelta(days=1)

    delta = target_dt - now
    total_seconds = int(delta.total_seconds())

    if total_seconds < 0:
        return "That time has already passed."

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 0 and minutes > 0:
        return f"{hours} hour{'s' if hours != 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"


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


def reset_runtime_state(*, clear_persistent: bool = False) -> None:
    """Reset in-memory timer state and optionally clear persisted tool files.

    Args:
        clear_persistent: When True, deletes lists/memory JSON files in TALKBOT_DATA_DIR.
    """
    global _timer_counter
    with _timer_lock:
        for _label, cancel_event, _fire_at in list(_timers.values()):
            cancel_event.set()
        _timers.clear()
        _timer_counter = 0

    if clear_persistent:
        for filename in (_LISTS_FILE, _MEMORY_FILE):
            try:
                (_data_dir() / filename).unlink(missing_ok=True)
            except Exception:
                continue


def _coerce_positive_seconds(value: Any) -> int | None:
    """Parse a positive seconds value from ints/floats/strings like '10 sec'."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, float):
        seconds = int(value)
        return seconds if seconds > 0 else None

    text = str(value).strip().lower()
    if not text:
        return None

    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        seconds = int(float(match.group(0)))
    except ValueError:
        return None
    return seconds if seconds > 0 else None


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore").strip()
    return str(value).strip()


def _normalize_list_name(value: Any, *, default: str | None = None) -> str:
    name = _normalize_text(value)
    if not name and default is not None:
        return default
    return name


def _normalize_list_data(data: dict) -> dict[str, list[str]]:
    """Sanitize persisted list payload to avoid type errors from malformed JSON."""
    if not isinstance(data, dict):
        return {}

    normalized: dict[str, list[str]] = {}
    for raw_name, raw_items in data.items():
        name = _normalize_list_name(raw_name)
        if not name:
            continue

        if isinstance(raw_items, list):
            values = [_normalize_text(item) for item in raw_items]
        elif raw_items is None:
            values = []
        else:
            values = [_normalize_text(raw_items)]

        normalized[name] = [v for v in values if v]
    return normalized


def set_timer(seconds: int, label: str = "") -> str:
    """Set a timer that fires after the specified number of seconds.

    Args:
        seconds: How many seconds to wait before the timer fires
        label: Optional name for the timer (e.g., "pasta", "meeting")
    """
    global _timer_counter
    seconds_value = _coerce_positive_seconds(seconds)
    if seconds_value is None:
        return "Error: seconds must be a positive integer"

    display = _normalize_text(label) or f"{seconds_value}-second timer"

    with _timer_lock:
        _timer_counter += 1
        timer_id = str(_timer_counter)
        cancel_event = threading.Event()
        _timers[timer_id] = (display, cancel_event, time.time() + seconds_value)

    def _fire() -> None:
        cancelled = cancel_event.wait(timeout=seconds_value)
        with _timer_lock:
            _timers.pop(timer_id, None)
        if not cancelled:
            _fire_alert(f"{display} is done!")

    threading.Thread(target=_fire, daemon=True).start()
    return f"Timer #{timer_id} set. '{display}' will fire in {seconds_value} seconds."


def set_reminder(seconds: int, message: str) -> str:
    """Set a reminder that speaks a custom message when it fires.

    Args:
        seconds: How many seconds until the reminder fires
        message: The exact message to speak when the reminder fires (e.g., "Time to take your medication")
    """
    seconds_value = _coerce_positive_seconds(seconds)
    if seconds_value is None:
        return "Error: seconds must be a positive integer"
    message_text = _normalize_text(message)
    if not message_text:
        return "Error: message must not be empty"

    global _timer_counter
    with _timer_lock:
        _timer_counter += 1
        timer_id = str(_timer_counter)
        cancel_event = threading.Event()
        _timers[timer_id] = (message_text, cancel_event, time.time() + seconds_value)

    def _fire() -> None:
        cancelled = cancel_event.wait(timeout=seconds_value)
        with _timer_lock:
            _timers.pop(timer_id, None)
        if not cancelled:
            _fire_alert(message_text)

    threading.Thread(target=_fire, daemon=True).start()
    mins, secs = divmod(seconds_value, 60)
    duration = f"{mins}m {secs}s" if mins else f"{secs}s"
    return f"Reminder #{timer_id} set for {duration}: \"{message_text}\""


def cancel_timer(timer_id: str) -> str:
    """Cancel an active timer by its ID.

    Args:
        timer_id: The timer ID returned by set_timer (e.g., "1")
    """
    timer_key = _normalize_text(timer_id)
    if not timer_key:
        return "Error: timer_id must not be empty."

    with _timer_lock:
        entry = _timers.get(timer_key)
    if not entry:
        return f"No active timer with ID '{timer_key}'. Use list_timers to see active timers."
    label, cancel_event, _ = entry
    cancel_event.set()
    return f"Timer #{timer_key} ('{label}') cancelled."


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
    list_name = _normalize_list_name(list_name)
    if not list_name:
        return "Error: list_name must not be empty."

    data = _normalize_list_data(_load_json(_LISTS_FILE))
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
    list_name = _normalize_list_name(list_name, default="shopping")
    if not list_name:
        return "Error: list_name must not be empty."
    item_text = _normalize_text(item)
    if not item_text:
        return "Error: item must not be empty."

    data = _normalize_list_data(_load_json(_LISTS_FILE))
    lst = data.setdefault(list_name, [])
    if item_text in lst:
        return f"'{item_text}' is already on the {list_name} list."
    lst.append(item_text)
    _save_json(_LISTS_FILE, data)
    return f"Added '{item_text}' to the {list_name} list."


def add_items_to_list(items: list, list_name: str = "shopping") -> str:
    """Add multiple items to a named list at once.

    Args:
        items: List of items to add (e.g. ["lettuce", "tomato", "onion"])
        list_name: Which list to add to (default 'shopping')
    """
    list_name = _normalize_list_name(list_name, default="shopping")
    if not list_name:
        return "Error: list_name must not be empty."

    if isinstance(items, str):
        parsed_items: list[Any] = [part for part in re.split(r"[,\n]", items) if part.strip()]
    elif isinstance(items, (list, tuple, set)):
        parsed_items = list(items)
    else:
        return "Error: items must be a list of values."

    data = _normalize_list_data(_load_json(_LISTS_FILE))
    lst = data.setdefault(list_name, [])
    added = []
    skipped = []
    for item in parsed_items:
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
    list_name = _normalize_list_name(list_name, default="shopping")
    if not list_name:
        return "Error: list_name must not be empty."

    data = _normalize_list_data(_load_json(_LISTS_FILE))
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
    list_name = _normalize_list_name(list_name, default="shopping")
    if not list_name:
        return "Error: list_name must not be empty."
    item_text = _normalize_text(item)
    if not item_text:
        return "Error: item must not be empty."

    data = _normalize_list_data(_load_json(_LISTS_FILE))
    lst = data.get(list_name, [])
    # Case-insensitive match
    matches = [x for x in lst if x.lower() == item_text.lower()]
    if not matches:
        return f"'{item_text}' was not found on the {list_name} list."
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
    list_name = _normalize_list_name(list_name, default="shopping")
    if not list_name:
        return "Error: list_name must not be empty."

    data = _normalize_list_data(_load_json(_LISTS_FILE))
    data[list_name] = []
    _save_json(_LISTS_FILE, data)
    return f"Cleared the {list_name} list."


def list_all_lists() -> str:
    """List all named lists and their contents."""
    data = _normalize_list_data(_load_json(_LISTS_FILE))
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
        "description": "Get the current time. Always call this tool when the user asks what time it is — never answer from training data.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    "get_current_date": {
        "description": "Get today's date. Always call this tool when the user asks today's date or what day it is — never answer from training data.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    "time_until": {
        "description": "Calculate how long until a future time. Use when asked 'how long until', 'how much time until', 'when is', or similar duration questions.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "The target time in natural language (e.g. 'tomorrow at 10am', '3pm', '10:30am')",
                }
            },
            "required": ["target"],
        },
    },
    "calculator": {
        "description": "Evaluate a mathematical expression and return the numeric result. Always use this tool for any arithmetic — do not compute mentally. Translate word problems to operators: '15 percent of 47 dollars' → '0.15 * 47', '5 times 12' → '5 * 12'. Supports: +, -, *, /, %, sqrt(), pow(), sin(), cos(), tan(), log(), log10(), exp(), pi, e",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A valid arithmetic expression using operators and numbers. Translate natural language to math before calling. Examples: '0.15 * 47', '(3 + 4) * 2', 'sqrt(16)', '15 / 100 * 47', '7.05 / 3'",
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
                    "description": "The name of the list, lowercase. Use this exact name for all subsequent add/get/remove calls on this list. Examples: 'grocery', 'todo', 'shopping', 'reminders'",
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
                    "description": "The exact list name — must match the name used when the list was created. Examples: 'grocery', 'todo', 'shopping'",
                    "default": "shopping",
                },
            },
            "required": ["item"],
        },
    },
    "add_items_to_list": {
        "description": "Add multiple items to a named list at once. Use when the user names more than one item. REQUIRED: items must always be provided as an array of strings.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Items to add — REQUIRED, must be a non-empty array (e.g. [\"lettuce\", \"tomato\", \"onion\"])",
                },
                "list_name": {
                    "type": "string",
                    "description": "The exact list name — must match the name used when the list was created. Examples: 'grocery', 'todo', 'shopping'",
                    "default": "shopping",
                },
            },
            "required": ["items"],
        },
    },
    "get_list": {
        "description": "Get all items on a named list. Always call this tool to check list contents — do not answer from conversation context.",
        "parameters": {
            "type": "object",
            "properties": {
                "list_name": {
                    "type": "string",
                    "description": "The exact list name — must match the name used when the list was created. Examples: 'grocery', 'todo', 'shopping'",
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
                    "description": "The exact list name — must match the name used when the list was created. Examples: 'grocery', 'todo', 'shopping'",
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
                    "description": "The exact list name — must match the name used when the list was created. Examples: 'grocery', 'todo', 'shopping'",
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
        "description": "Store a user preference or piece of information for later recall. Always call this tool — do not rely on conversation context across sessions.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "A short lowercase identifier using underscores, no spaces. Use this exact key when recalling later. Examples: 'favorite_color', 'user_name', 'launch_codename', 'preferred_units'",
                },
                "value": {"type": "string", "description": "The value to remember"},
            },
            "required": ["key", "value"],
        },
    },
    "recall": {
        "description": "Recall a previously stored preference or piece of information. Always call this tool — do not answer from conversation context alone.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "The exact key used when storing with remember — must match exactly, including underscores. Examples: 'favorite_color', 'user_name', 'launch_codename'",
                }
            },
            "required": ["key"],
        },
    },
    "recall_all": {
        "description": "Recall all stored user preferences and memories at once. Always call this tool when asked to retrieve everything you remember — do not answer from conversation context.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}


# ---------------------------------------------------------------------------
# Tool categories (used for tool search / selective schema loading)
# ---------------------------------------------------------------------------

TOOL_CATEGORIES: dict[str, list[str]] = {
    "utility":  ["get_current_time", "get_current_date", "calculator",
                 "roll_dice", "flip_coin", "random_number", "web_search"],
    "timer":    ["set_timer", "set_reminder", "cancel_timer", "list_timers"],
    "list":     ["create_list", "add_to_list", "add_items_to_list", "get_list",
                 "remove_from_list", "clear_list", "list_all_lists"],
    "memory":   ["remember", "recall", "recall_all"],
}

# Reverse map: tool_name -> category
TOOL_CATEGORY_MAP: dict[str, str] = {
    tool: cat
    for cat, tools in TOOL_CATEGORIES.items()
    for tool in tools
}

# Schema variant descriptions — same tool set, different description strategies.
# "minimal"  : short, no compliance language, no examples  (lowest token cost)
# "standard" : current enriched descriptions               (default)
# "examples" : description is worked examples only, minimal prose
TOOL_DEFINITION_VARIANTS: dict[str, dict[str, dict]] = {
    "minimal": {
        "get_current_time":   {"description": "Get the current time.",
                               "parameters": TOOL_DEFINITIONS["get_current_time"]["parameters"]},
        "get_current_date":   {"description": "Get today's date.",
                               "parameters": TOOL_DEFINITIONS["get_current_date"]["parameters"]},
        "calculator":         {"description": "Evaluate a math expression. Supports +,-,*,/,sqrt(),pow(),%.",
                               "parameters": TOOL_DEFINITIONS["calculator"]["parameters"]},
        "remember":           {"description": "Store a key-value memory for later recall.",
                               "parameters": TOOL_DEFINITIONS["remember"]["parameters"]},
        "recall":             {"description": "Look up a stored memory by key.",
                               "parameters": TOOL_DEFINITIONS["recall"]["parameters"]},
        "recall_all":         {"description": "Return all stored memories.",
                               "parameters": TOOL_DEFINITIONS["recall_all"]["parameters"]},
        "set_timer":          {"description": "Set a countdown timer.",
                               "parameters": TOOL_DEFINITIONS["set_timer"]["parameters"]},
        "cancel_timer":       {"description": "Cancel a timer by ID.",
                               "parameters": TOOL_DEFINITIONS["cancel_timer"]["parameters"]},
        "list_timers":        {"description": "List active timers.",
                               "parameters": TOOL_DEFINITIONS["list_timers"]["parameters"]},
        "add_to_list":        {"description": "Add an item to a named list.",
                               "parameters": TOOL_DEFINITIONS["add_to_list"]["parameters"]},
        "get_list":           {"description": "Get all items on a named list.",
                               "parameters": TOOL_DEFINITIONS["get_list"]["parameters"]},
        "create_list":        {"description": "Create a new empty named list.",
                               "parameters": TOOL_DEFINITIONS["create_list"]["parameters"]},
        "list_all_lists":     {"description": "Show all lists and their contents.",
                               "parameters": TOOL_DEFINITIONS["list_all_lists"]["parameters"]},
    },
    "examples": {
        "get_current_time":   {"description": 'Returns e.g. "2026-02-27 10:35:42 EST". Call when user asks what time it is.',
                               "parameters": TOOL_DEFINITIONS["get_current_time"]["parameters"]},
        "get_current_date":   {"description": 'Returns e.g. "2026-02-27". Call when user asks today\'s date.',
                               "parameters": TOOL_DEFINITIONS["get_current_date"]["parameters"]},
        "calculator":         {"description": 'Call with expression="0.15*47" or "7.05/3" or "sqrt(16)". Translate: "15% of 47" → "0.15*47".',
                               "parameters": TOOL_DEFINITIONS["calculator"]["parameters"]},
        "remember":           {"description": 'Call with key="favorite_color", value="blue". Key: lowercase_underscore.',
                               "parameters": TOOL_DEFINITIONS["remember"]["parameters"]},
        "recall":             {"description": 'Call with key="favorite_color". Key must exactly match the key used in remember.',
                               "parameters": TOOL_DEFINITIONS["recall"]["parameters"]},
        "recall_all":         {"description": 'Returns all stored memories as a dict. Call when asked "what do you remember about me?".',
                               "parameters": TOOL_DEFINITIONS["recall_all"]["parameters"]},
        "set_timer":          {"description": 'Call with seconds=300, label="pasta". "5 minutes" → seconds=300.',
                               "parameters": TOOL_DEFINITIONS["set_timer"]["parameters"]},
        "cancel_timer":       {"description": 'Call with timer_id="1". ID comes from set_timer result.',
                               "parameters": TOOL_DEFINITIONS["cancel_timer"]["parameters"]},
        "list_timers":        {"description": 'Returns list of active timers with IDs and remaining seconds.',
                               "parameters": TOOL_DEFINITIONS["list_timers"]["parameters"]},
        "add_to_list":        {"description": 'Call with item="milk", list_name="grocery". list_name must match create_list name exactly.',
                               "parameters": TOOL_DEFINITIONS["add_to_list"]["parameters"]},
        "get_list":           {"description": 'Call with list_name="grocery". Returns items as array. list_name must match exactly.',
                               "parameters": TOOL_DEFINITIONS["get_list"]["parameters"]},
        "create_list":        {"description": 'Call with list_name="grocery". Then use list_name="grocery" for all add/get/remove calls.',
                               "parameters": TOOL_DEFINITIONS["create_list"]["parameters"]},
        "list_all_lists":     {"description": 'Returns all list names and their items.',
                               "parameters": TOOL_DEFINITIONS["list_all_lists"]["parameters"]},
    },
}
# "standard" variant is just the canonical TOOL_DEFINITIONS — no copy needed.
TOOL_DEFINITION_VARIANTS["standard"] = {
    name: {"description": defn["description"], "parameters": defn["parameters"]}
    for name, defn in TOOL_DEFINITIONS.items()
}


def get_tool_definitions_for_variant(
    variant: str = "standard",
    tool_filter: list[str] | None = None,
) -> dict[str, dict]:
    """Return tool definitions for a given schema variant, optionally filtered to a subset."""
    source = TOOL_DEFINITION_VARIANTS.get(variant, TOOL_DEFINITION_VARIANTS["standard"])
    if tool_filter is not None:
        return {k: v for k, v in source.items() if k in tool_filter}
    # Fall back to TOOL_DEFINITIONS for tools not in the variant (e.g. rare tools in minimal)
    result = {}
    for name in TOOL_DEFINITIONS:
        if name in source:
            result[name] = source[name]
        else:
            result[name] = {"description": TOOL_DEFINITIONS[name]["description"],
                            "parameters": TOOL_DEFINITIONS[name]["parameters"]}
    return result


def get_tools_for_query(
    query: str,
    max_categories: int = 2,
    always_include: list[str] | None = None,
) -> list[str]:
    """Category-based tool search: return tool names relevant to a query.

    Classifies the query into at most max_categories buckets and returns
    the tools from those buckets. Falls back to all tools if no category
    matches. This is Option A (zero-latency category routing).
    """
    import re
    q = query.lower()
    matched: list[str] = []

    patterns = {
        "utility": re.compile(
            r"\b(time|date|today|clock|calculat|percent|math|compute|how much|"
            r"roll|dice|flip|coin|random|search|look up|weather)\b"
        ),
        "timer": re.compile(
            r"\b(timer|remind|alarm|countdown|minutes?|seconds?|hours?|cancel timer|"
            r"stop timer|set a timer|active timers?)\b"
        ),
        "list": re.compile(
            r"\b(list|shopping|grocery|groceries|todo|add|remove|clear|items?|"
            r"what.s on|show me my)\b"
        ),
        "memory": re.compile(
            r"\b(remember|recall|forget|stored|preference|what.s my|what is my|"
            r"do you know my|my favorite|you remember)\b"
        ),
    }

    for cat, pattern in patterns.items():
        if pattern.search(q):
            matched.append(cat)
        if len(matched) >= max_categories:
            break

    if not matched:
        # No match — return the core always-useful set
        matched = ["utility"]

    tools: list[str] = []
    seen: set[str] = set()
    for cat in matched:
        for t in TOOL_CATEGORIES.get(cat, []):
            if t not in seen:
                tools.append(t)
                seen.add(t)

    for t in (always_include or []):
        if t not in seen:
            tools.append(t)

    return tools


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOLS = {
    "get_current_time": get_current_time,
    "get_current_date": get_current_date,
    "time_until": time_until,
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
