# Tool Design Guide

This document explains how TalkBot's built-in tools are designed, and the principles to follow
when adding new ones. The goal is reliable tool use across small local models (sub-2B parameters)
as well as larger hosted models.

---

## Why Tool Design Matters for Small Models

Models fine-tuned for tool use are trained on large corpora of real and synthetic API calls —
ToolBench (16,000+ RapidAPI endpoints), GLAIVE, Hermes, OpenAI cookbook examples, and similar
datasets. Through this training, they develop strong **priors** for certain parameter names,
function naming patterns, and schema shapes.

A small model (0.8B–2B) has limited capacity. When a tool schema fights its training priors —
unusual parameter names, two functions for the same intent, compliance language that contradicts
the schema — the model gets confused and produces malformed calls. The result shows up as
`tool_call_error_rate` in the benchmark.

**The design principle: align tool names and parameter names to what models have already seen,
rather than enforcing arbitrary conventions through verbose descriptions.**

---

## Function Naming

### One function per user intent

Never create two functions that differ only in input cardinality. For example, having both
`add_to_list(item: str)` and `add_items_to_list(items: list)` forces the model to make a
categorization decision on every call. Small models consistently get this wrong.

Instead, **accept flexible input types in a single function**:

```python
def add_to_list(items: str | list, list_name: str = "shopping") -> str:
    """Add one or more items to a named list."""
```

The implementation handles both. The model never has to choose.

### Naming conventions

- **Verb-first, snake_case**: `get_list`, `set_timer`, `cancel_timer`, `remember`, `recall`
- **Avoid name similarity**: two tools that share a prefix (`add_to_list`, `add_items_to_list`)
  will be conflated by small models. Use clearly distinct names.
- **Match common API vocabulary**: models have seen thousands of APIs. Names like `search`,
  `get`, `set`, `cancel`, `list` are well-anchored in their training.

---

## Parameter Naming

Align parameter names to the conventions most common in tool-calling training data:

| Intent | Recommended | Avoid |
|---|---|---|
| Search / freeform text input | `query` | `input`, `text`, `search_term` |
| One or more items | `items` | `item` (singular), `item_list`, `entries` |
| Named list identifier | `list_name` | bare `name`, `list` |
| Timer duration | `seconds` | `duration`, `time`, `delay` |
| Timer identifier | `timer_id` | bare `id` |
| Key-value store key | `key` | `name`, `field` |
| Key-value store value | `value` | `data`, `content`, `text` |
| Spoken reminder message | `message` | `text`, `label`, `content` |

### Singular vs plural

Use **plural names** (`items`, `keys`) for parameters that accept either a single value or
multiple values. Training data strongly associates plural names with flexible-cardinality inputs.
A model that sees `items` in the schema will naturally pass either `"milk"` or `["milk", "eggs"]`
— both are correct. A model that sees `item` will try to pass a string and fail when it wants
to add multiple items.

### Required vs optional

Only put parameters in `required` when the tool genuinely cannot run without them. Models
over-specify when many parameters are required — they'll invent values for required params
they don't know. Parameters with sensible defaults (like `list_name: "shopping"`) should
be optional.

---

## Schema Descriptions

### When to include compliance language

Some tools need explicit instruction to prevent the model answering from its own context
instead of calling the tool:

> "Always call this tool — do not answer from conversation context alone."

Include this language for:
- **Stateful reads**: `get_list`, `recall`, `recall_all`, `list_timers` — the model may
  remember what it added earlier in the conversation and answer without calling
- **Stateful writes** where confirmation matters: `remember`, `set_timer`

Omit it for:
- Pure utility tools: `calculator`, `get_current_time`, `roll_dice` — no meaningful
  context to answer from; the model will call them naturally

### Compliance language vs system directive

TalkBot applies a system-level `DEFAULT_TOOL_USE_DIRECTIVE` to all tool-enabled sessions.
This is a general "prefer tools over reasoning" instruction. **It does not replace per-tool
compliance language** — they are additive. Benchmark results confirm that removing per-tool
compliance language from stateful tools causes tool selection accuracy to drop even when the
system directive is present.

### Description length

Longer is not better. Each token in the tool schema is a token spent on prefill. On a 15W CPU
at ~83 tok/s prefill, 2,400 prompt tokens = ~29 seconds before the model writes a single word.

- Keep descriptions to 1–2 sentences
- Use the `minimal` schema variant (`tool_schema_variant: "minimal"`) for latency-sensitive
  deployments — it drops compliance language and shortens descriptions by ~40%
- The `examples` variant uses worked call examples as descriptions; it matches `standard` on
  tool selection but can hurt argument accuracy on very small models

---

## The Parameter Normalizer

`_normalize_tool_args_for_call()` in `llm.py` and `openrouter.py` maps common model mistakes
to the canonical parameter name. For example:

```python
"add_to_list": {
    "item":      "items",   # old singular name
    "item_list": "items",   # old plural name from merged function
    "value":     "items",   # generic alias
    "name":      "list_name",
    "list":      "list_name",
},
```

**The normalizer is production infrastructure, not a test shim.** It runs in both production
and benchmarks. This means:

- A model that uses `item=` instead of `items=` still succeeds in production ✓
- Benchmark `arg_accuracy` reflects post-normalization args — it measures "did the right
  value reach the tool" not "did the model use the exact correct parameter name"

Keep the normalizer lean. If a tool requires many aliases, the parameter name is wrong —
fix the name rather than adding more aliases.

---

## Current Tool Set (16 tools)

### Utility
| Tool | Key params | Notes |
|---|---|---|
| `get_current_time` | — | Returns date + time + timezone |
| `get_current_date` | — | Returns date only |
| `calculator` | `expression` | Eval math; consider renaming to `formula` |
| `roll_dice` | `sides`, `count` | |
| `flip_coin` | — | |
| `random_number` | `min_val`, `max_val` | |
| `web_search` | `query` | DuckDuckGo instant answer |

### Timer
| Tool | Key params | Notes |
|---|---|---|
| `set_timer` | `seconds`, `label` | Fires "{label} is done!" |
| `set_reminder` | `seconds`, `message` | Fires custom spoken message |
| `cancel_timer` | `timer_id` | ID from set_timer result |
| `list_timers` | — | |

### Lists
| Tool | Key params | Notes |
|---|---|---|
| `create_list` | `list_name` | Creates empty list |
| `add_to_list` | `items`, `list_name` | String or array; auto-creates list |
| `get_list` | `list_name` | |
| `remove_from_list` | `item`, `list_name` | |
| `clear_list` | `list_name` | |
| `list_all_lists` | — | |

### Memory
| Tool | Key params | Notes |
|---|---|---|
| `remember` | `key`, `value` | Persistent across sessions |
| `recall` | `key` | |
| `recall_all` | — | |

---

## Checklist for Adding a New Tool

1. **Check model priors** — would a model trained on ToolBench/GLAIVE/Hermes naturally use
   this parameter name? If not, change the name or add a normalizer alias.
2. **One function per user intent** — if the user can phrase the same request two ways
   (singular/plural, create/add), handle both in one function with flexible input types.
3. **Comply with naming conventions above** — especially for `query`, `items`, `message`.
4. **Required params only in `required`** — optional params with defaults go in `properties`
   only.
5. **Add compliance language for stateful reads** — any tool where the model might answer
   from conversation memory instead of calling the tool needs it.
6. **Add to `TOOL_CATEGORIES`** — so tool filtering works correctly.
7. **Add a normalizer alias** for any parameter that a model might naturally call something
   else (e.g. `duration` for `seconds`, `name` for `list_name`).
8. **Test with the minimal schema** — if the tool only works with verbose descriptions,
   the name/params are doing too little work.
