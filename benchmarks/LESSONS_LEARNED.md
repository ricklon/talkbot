# Benchmark Lessons Learned

Accumulated from benchmark runs on this repo. Each entry records what we
observed, what we changed, and what the data confirmed. Ordered newest-first.

---

## 2026-02-27 — Pipeline benchmark: Mistral [TOOL_CALLS] in OpenRouter prompt-tool path

### Mistral models ignore XML tool tag instruction and emit [TOOL_CALLS] regardless

**Observation:** `mistral-small-3.1-24b-instruct` via OpenRouter was classified by
the preflight check as not supporting native tools (`_native_tools_supported=False`),
so `chat_with_tools` routed to `_chat_with_prompt_tools`. That path injects a system
prompt instructing the model to use `<tool_call>{...}</tool_call>` XML tags. The model
ignored this and emitted `[TOOL_CALLS][{"name": "get_current_time", "arguments": {}}]`
in its native Mistral format anyway. `_extract_prompt_tool_call` only parsed XML tags,
so the tool was never dispatched and the raw `[TOOL_CALLS]` string was returned —
which TTS would speak aloud verbatim.

**Fix:** Added `_extract_bracket_tool_calls()` static method to `OpenRouterClient`
(same logic as `LocalServerClient`) and wired it as a fallback in both
`_chat_with_prompt_tools` (after XML extraction fails) and `_chat_with_native_tools`
(after `message.get("tool_calls")` is empty). For the native path, synthetic
`tool_calls` are injected into the assistant message so tool response `tool_call_id`
references remain valid.

**Lesson:** When a model is routed through the prompt-tool fallback path, it may still
emit its fine-tuned native tool format regardless of prompt instructions. Always add
bracket/native format extraction as a fallback in the prompt path — not just in the
native path. The two extraction paths must stay in sync.

**Benchmark result:** mistral-small-3.1-24b-instruct via pipeline benchmark:
- Before fix: 8/12 answers correct, 3/5 tool calls correct
- After fix: 10/12 answers correct, 5/5 tool calls correct

---

## 2026-02-27 — Schema variants and tool profile experiments

### Schema descriptions are invisible to local small models

**Observation:** Running qwen3-1.7b-q4_k_m against three description variants
(minimal / standard / examples) produced identical results: 60% success,
73% tool selection, 100% arg accuracy in every run.

**Lesson:** Local models ≤2B parameters have behavior baked into their weights
from fine-tuning. The tool schema description is part of the prompt, but these
models do not use it to decide *how* to call a tool or *whether* to call one.
Enriching descriptions for them is wasted tokens.

**Implication:** For local small models, the only levers are (a) the system
prompt, (b) intent routing that bypasses the model entirely, and (c) the tool
name itself if the model was fine-tuned on similar function names.

---

### Compliance language outperforms worked examples for capable remote models

**Observation:** ministral-3b-2512 via OpenRouter:
- `minimal` descriptions (no guidance): 60% success
- `standard` (enriched + "always call this tool"): 70% success  (+10%)
- `examples` (worked examples only): 60% success

**Lesson:** The `"always call this tool — do not answer from context"` compliance
instruction is worth more than worked expression examples alone. Examples help
with *how* to format arguments; compliance language drives *whether* the model
calls the tool at all. You need both, but compliance language is the primary
lever for Cluster B failures (capable models answering without tools).

---

### Removing noise tools from small local models can hurt, not help

**Observation:** qwen3-1.7b-llm with 15 tools (noise removed) scored 50% vs
70% with the full 17-tool schema. It newly failed `list_multistep_packing` and
`memory_persistent_strict` — scenarios it had previously passed.

**Lesson:** Small local models may rely on the full schema as a kind of
"grounding context." Removing tools they don't use still perturbs their
routing behavior in unexpected ways. Schema trimming is not universally
beneficial — it is model-specific and must be tested, not assumed.

---

### Removing a single decoy tool fixed a specific routing failure

**Observation:** qwen3-8b-intent with `set_reminder` removed scored 70% vs
60% with the full tool set. `cross_tool_mix` (turn 3: "add to my reminders
list") now passes because `add_to_list` is the only plausible tool.

**Lesson:** When a model has two semantically similar tools (`set_reminder` and
`add_to_list` both accept text and relate to "reminders"), it may route to the
wrong one. Removing the decoy is the most direct fix when the decoy is rarely
legitimately needed. This is the "schema clutter causes misdispatch" pattern.

---

### Core-only tool filters fail if tested scenarios need the removed tools

**Observation:** ollama-llama3.2-3b with only 6 core tools (timer + utility)
saw tool_selection_accuracy drop from 77% to 50% because list/memory scenarios
had no tools to call.

**Lesson:** Tool filter design must account for what scenarios will be run.
Profiling a model's "reliable tools" only makes sense if you also know which
tasks you will ask it to perform. A restricted profile that removes tools tested
in the benchmark is a self-defeating experiment.

---

## 2026-02-27 — v3-schemas run: enriched tool descriptions

### "Always call this tool" drove gemini-2.5-flash-lite from 60% → 100%

**Observation:** After adding compliance language to get_current_time,
get_current_date, remember, recall, and get_list, gemini-2.5-flash-lite
jumped from 60% to 100% success and 86% → 100% tool selection accuracy.

**Lesson:** Gemini-family models are highly instruction-following. They read
tool descriptions carefully and act on explicit instructions within them.
`"Always call this tool when the user asks X — never answer from training data"`
is a direct, reliable lever for this model family.

---

### Expression examples in calculator description helped remote models, not local

**Observation:** After adding `"Examples: '0.15 * 47', '7.05 / 3'"` to the
calculator expression parameter description, all remote models already passing
continued to pass. qwen3-1.7b continued to output `calculate_percent_of_amount`
regardless.

**Lesson:** Remote models already know `calculator(expression=str)` from RLHF.
The examples are a backstop for edge cases. For local models that invent their
own function names, no amount of schema enrichment helps — they need explicit
few-shot examples in the *system prompt*, not in the schema.

---

### Memory key underscore format guidance reduced haiku-4-5 arg failures

**Observation:** Adding `"lowercase_underscore, e.g. 'favorite_color'"` to the
`remember` key parameter description brought claude-haiku-4-5 arg_accuracy from
75% → 100% by guiding it to use consistent key format across remember/recall.

**Lesson:** When a tool depends on *consistent* values across multiple calls
(memory keys, list names), the parameter description must explicitly say so.
`"Use this exact key when calling recall later"` prevents the space-vs-underscore
inconsistency that broke haiku's cross-turn memory lookup.

---

## 2026-02-27 — v3-fixed run: test assertion fixes

### Recovery scenario regex must cover all natural refusal phrasings

**Observation:** gemini-2.5-pro responded "I can't find a timer with the ID 99"
and failed the recovery scenario. The regex had `couldn't find` but not
`can't find`.

**Lesson:** Refusal/error responses have many natural phrasings. Test regex
patterns should cover: `can't`, `cannot`, `couldn't`, `unable to`, `there is no`,
`not found`, `doesn't exist`. When adding a new recovery scenario, enumerate at
least 5 phrasings before writing the regex.

---

### Memory key format assertions must not enforce a specific format

**Observation:** Both claude-haiku-4-5 and gemini-2.5-pro used `"favorite color"`
(space) as a memory key. haiku was internally consistent (stored and recalled
with the same key, got correct answer) but failed the test's `args_contains`
check for `"favorite_color"` (underscore).

**Lesson:** When testing argument *values* that have no schema-enforced format,
check the value stored (e.g. `"blue"`) not the key format. Reserve format
checking for cases where the schema explicitly constrains it.

---

### Case sensitivity in response_contains causes false failures for capable models

**Observation:** claude-sonnet-4-6 failed `list_basics` because it responded
"**Grocery**: milk" but `response_contains: ["grocery"]` is case-sensitive.
Earlier, ministral-3b capitalized "Atlas" failing the `memory_context_pressure`
check for "atlas".

**Lesson:** Always use `response_regex: "(?i)pattern"` instead of
`response_contains` for any string that a model might reasonably capitalize.
Proper nouns, list names, and stored values are all at risk. The `(?i)` flag
costs nothing and prevents entire categories of false failures.

---

## 2026-02-27 — v3 run: local tool dispatch (Mistral [TOOL_CALLS] format)

### Mistral-family models via Ollama emit [TOOL_CALLS] as plain text

**Observation:** mistral-nemo:latest via Ollama scored 10% tool selection.
Inspection showed it was outputting `[TOOL_CALLS][{"name": "...", "arguments":
{...}}]` as plain text in the content field rather than structured `tool_calls`
API objects. OpenRouter normalizes this; Ollama passes it through raw.

**Fix:** Added `_extract_bracket_tool_calls()` to `LocalServerClient` in llm.py,
inserted in the fallback chain after XML tag extraction.

**Lesson:** When routing a model family through a different inference server,
verify the tool call wire format. The same model can produce different formats
depending on whether it goes through OpenRouter (normalized) or Ollama (raw).
Always test tool dispatch end-to-end, not just capability in isolation.

---

## 2026-02-27 — v3 run: intent routing regex false positive

### Recall regex matched math queries, routing calculator to memory

**Observation:** qwen3-1.7b in INTENT mode and qwen3-8b INTENT mode both routed
"What is 15 percent of 47 dollars?" to `recall(key="15_percent_of_47_dollars")`.
The recall regex `[a-z0-9_ ]{2,40}` included digits, matching the full math
expression as a memory key.

**Fix:** Removed digits from recall key character class: `[a-z_ ]{2,40}`.
Memory keys are alphanumeric-with-underscores, never purely numeric, and never
contain math expressions.

**Lesson:** Intent routing regexes must be written defensively. Overly broad
character classes in capture groups will match inputs they were never designed
for. After writing a routing regex, manually test it against the full scenario
corpus to find false positives before running a benchmark.

---

## 2026-02-27 — v3 run: scenario design

### utility_time_date: tool order matters when one tool's result embeds another's

**Observation:** `get_current_time` returns `"2026-02-27 10:35:42 EST"` which
embeds the date. When the scenario asked "What time is it?" first, models
correctly answered "What's the date?" from the prior turn's result without
calling `get_current_date`. 62% failure rate, all false fails.

**Fix:** Swap order — ask date first (`get_current_date` returns date only),
then ask time.

**Lesson:** When two tools return overlapping information, the scenario order
determines whether the second tool is actually needed. Design scenarios so that
each turn's expected tool call cannot be satisfied by a previous turn's result.

---

## 2026-02-27 — Benchmark architecture

### Token budget: full schema consumes 78% of ctx=2048

**Observation:** The 17-tool schema is ~1,595 tokens. At ctx=2048 (qwen3-1.7b
default), schema + system prompt leaves ~250 tokens for conversation history
and model output combined.

**Implication:** Multi-turn scenario failures for local models may be caused by
context overflow, not model capability. The core-13 schema (noise tools removed)
is ~968 tokens (47%). Category-based tool search can drop this to 244-411 tokens
(12-20%) with zero latency cost.

---

### Three failure clusters describe most tool-use failures

**Cluster A — "Invents tool names":** Model tries to use tools but calls names
not in the schema (e.g. `calculate_percent_of_amount`). Caused by weight-level
fine-tuning on different function signatures. Schema enrichment does not fix
this. Fix: system prompt few-shot examples showing the exact tool name, or
intent routing.

**Cluster B — "Answers from context":** Capable model bypasses tool call when
it can answer from conversation history or training knowledge. Compliance
language in tool description (`"Always call this tool — never answer from
context"`) is the primary fix. Affects all smart models for time/date/memory.

**Cluster C — "Calls tool with wrong args":** Model knows the tool name but
passes malformed arguments (JSON schema blob as expression string; space in
key instead of underscore). Fix: worked examples + format constraints in
parameter description.

---

### Never-called tools split into two categories

**Category 1 — Not tested, correctly skipped:** `roll_dice`, `flip_coin`,
`random_number`, `web_search`, `remove_from_list`, `clear_list`. No benchmark
scenario requires them; models correctly do not call them. These are schema
weight with no benchmark signal.

**Category 2 — Expected but actively bypassed:** `recall_all`. The
`memory_context_pressure` scenario expects it, but all 11 models bypassed it
by answering from context. This is a Cluster B failure masquerading as a
never-called tool. Fix: add compliance language to `recall_all` description.

---

### Remote vs local model schema responsiveness

| Model type | Responds to description changes | Primary lever |
|---|---|---|
| Local ≤2B (qwen3-1.7b) | No | Intent routing, system prompt |
| Local 8B (qwen3-8b) | Minimal | Intent routing, tool filter |
| Ollama 3B (llama3.2) | Partial | Tool name recognition |
| Remote 3B (ministral) | Yes — compliance language | Description compliance clause |
| Remote frontier (gemini, claude) | Yes — highly responsive | Any schema improvement |
