"""Built-in tools for the talking bot."""

import datetime
import json
import math
import random
from typing import Any


def get_current_time() -> str:
    """Get the current date and time."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_current_date() -> str:
    """Get the current date."""
    return datetime.date.today().isoformat()


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

    try:
        # Only allow basic math operations
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


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


# Tool definitions for LLM
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
}


# Tool registry
TOOLS = {
    "get_current_time": get_current_time,
    "get_current_date": get_current_date,
    "calculator": calculator,
    "roll_dice": roll_dice,
    "flip_coin": flip_coin,
    "random_number": random_number,
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
