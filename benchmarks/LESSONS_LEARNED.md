# Benchmark Lessons Learned

Accumulated from benchmark runs on this repo. Each entry records what we
observed, what we changed, and what the data confirmed. Ordered newest-first.

---

## 2026-03-10 — Endurance scenarios: repeated store bypass (Cluster B on write operations)

### All endurance scenarios score 0% — not context overflow

**Observation:** Running 5 endurance scenarios (10–30 turns) against all four
qwen3.5 M3 Max profiles produced 0% success across the board. Initial hypothesis
was context overflow (ctx=4096), but token counts at failure points were
2600–2700 tokens — well within the 4096 window.

**Actual cause:** The model calls `remember` / `add_to_list` / `set_timer`
correctly on the first 1–2 invocations, then bypasses subsequent calls to the
same tool. On turn 3 of `deep_endurance_session`:

- prompt_tokens: 2632, completion_tokens: **12**
- tool_calls: **[]**
- assertion: `"Missing expected tool call: ['remember']"`
- response: *"I've saved your project name as 'Falcon'."*

The model generates 12 tokens, no tool call, and confidently moves on. It
learned from the conversation context that calling `remember` works, so it
shortcuts the mechanism and pretends to store without actually calling.

This is **Cluster B ("answers from context") on write operations**, not just
recall. The pattern triggers earlier than expected (turn 3, not turn 20+)
when the same tool is called repeatedly in sequence.

**Affected scenarios:** All five endurance scenarios, all four qwen3.5 profiles
(0.8b Q8_0 LLM/Intent, 0.8b Q4_K_M, 2b Q4_K_M). Failure is at the write
operations, not the recall assertions.

**Note on context-bypass at late recall turns:** This is distinct from the
late-turn context-bypass documented in `deep_endurance_session.json` (turns
25–27), where the model correctly answers from context without calling recall
tools. That pattern is expected and acceptable — the information is already
in context. The *store* bypass is not acceptable: the tool must be called
to persist data across sessions.

**Fix options (not yet tested):**
1. Add compliance language to `remember`, `add_to_list`, and `set_timer`
   descriptions: `"Always call this tool — even if you have already called it
   recently. Every call stores new data. Do not acknowledge without calling."`
2. Redesign endurance scenarios to interleave different tools between repeated
   calls of the same tool (reduces the "I've already done this" pattern).
3. Both: compliance language is the primary lever; interleaving reduces surface area.

**Evidence that compliance language works:** In `validated-20260227-v3-schemas`,
adding `"Always call this tool — never answer from context"` to `get_current_time`
and `remember` drove gemini-2.5-flash-lite from 60% → 100% success. The same
mechanism should suppress write-operation bypass.

**Research findings (2026-03-10):** This pattern is documented in the academic
literature and practitioner writing, though it has no single canonical name.
Key sources:

- **BFCL V4 (ICML 2025)**: confirms multi-turn tool count consistency is a
  distinct failure mode from single-turn accuracy; small models systematically
  under-call after initial success
- **BUTTON (ICLR 2025, arXiv:2410.12952)**: identifies the root cause as sparse
  multi-turn tool training data; most function-calling fine-tune datasets are
  single-turn, so models never learn that the same tool may be needed N times
- **MemTool (arXiv:2507.21428)**: frames it as "implicit few-shot learning from
  conversation history" — prior `[user → tool call → result → confirmation]`
  quads teach the model to shortcut by emitting confirmation without the call
- **Qwen model card**: explicitly states "it is not guaranteed that the model
  generation will always follow the protocol even with proper prompting" and
  acknowledges qwen3.5-0.8B is more prone to anomalous generation; recommends
  Qwen-Agent (deterministic dispatch wrapper) for production tool use
- **Sohaib Ahmed (practitioner blog)**: documented the identical pattern in
  Qwen 2.5 Coder 1.5B — correct on first call, manual shortcut on subsequent

**Ranked fixes for sub-2B local models:**
1. **Dynamic tool set reduction + `tool_choice: "required"`**: Detect intent,
   send only the relevant tool, force a call. Mechanical guarantee — no
   persuasion. llama-server supports `tool_choice: "required"`.
   TalkBot's intent routing (TALKBOT_LOCAL_DIRECT_TOOL_ROUTING=1) is the
   current equivalent and is already the recommended architecture for these models.
2. **Strip natural-language confirmations from history**: Store raw tool-role
   messages, not the model's "I've remembered X" summaries. Removes the
   implicit few-shot bypass examples from context.
3. **Compliance language in tool descriptions**: Works marginally for capable
   remote models; negligible for sub-2B local models (confirmed by experiment).

**Conclusion for TalkBot:** Intent routing (deterministic dispatch) is the
correct and documented solution for this model class. The endurance scenarios
expose this architectural split — LLM mode fails at repeated store operations;
Intent mode is the production recommendation for sub-2B models.

**Intent routing endurance results (2026-03-10):** Re-ran all 5 endurance
scenarios with LLM vs Intent routing side-by-side. **Both scored 0% success.**
Tool selection accuracy: LLM 60.2%, Intent 59.1%. No meaningful difference.

**Why intent routing doesn't help here:** Intent routing intercepts tool calls
that the model *requests*. When the model makes **zero tool calls** (verbally
hallucinating "I've remembered X" while `tool_calls=[]`), there is nothing to
intercept. The failure is upstream of routing — the model never emits a tool
call request in the first place.

Observed directly: turns like `t3 tools=[] | "I've remembered that the project
is called Falcon."` produce 12-token completions with no tool call. The model
shortcuts the call-execute-confirm loop to just the confirm step.

**Cascade effect confirmed:** Skipped writes propagate downstream. When
`add_to_list` is bypassed at turn 20, the list stays empty. A subsequent
`get_list` at turn 23 returns nothing, and the assertion `"tasks list contains
test|code|deploy"` fails — even though `get_list` was called correctly.

**What actually needs to happen:**
- `tool_choice: "required"` forces a tool call JSON to be emitted. llama-server
  supports this. Without it, the model can return plain text with no call.
- Dynamic tool set: send only the one tool the intent router already identified.
  Eliminates ambiguity about which tool to call.
- Together: intent detection → single-tool schema + `tool_choice: "required"` →
  model *must* emit a tool call → arguments are extracted and executed.

This is a benchmark/infrastructure gap, not a model capability gap. The
endurance scenarios expose it most clearly because repeated same-tool calls
amplify the bypass pattern.

**Status (2026-03-11 — RESOLVED):** Implemented `tool_choice: "required"` +
single-tool schema in `LocalServerClient` (commit 3b83c3d, issue #44 closed).

Results after fix (M3 Max, qwen3.5-0.8b Q8_0):
- Endurance overall: **0% → 60%** (3/5 scenarios pass_k met)
- Timer Sequence: **100%** (15/15, pass_k satisfied)
- Memory Recall: **100%** (10/10)
- Long Mixed 30 turns: **30/30 turns passing** (pass_k accumulating)
- Core canonical suite: **90% maintained** — intent leads leaderboard

**Key implementation insight:** Only WRITE tools are forced (`remember`,
`add_to_list`, `set_timer`, `create_list`, `clear_list`, `remove_from_list`).
Keyed read tools (`get_list`, `recall`) are excluded from forcing because the
model generates consistent `list_name` / `key` args from context in LLM mode,
but may produce mismatched names when isolated to a single forced schema.
Stateless reads (`get_current_time`, `get_current_date`, `flip_coin`, etc.)
are safely forced because they require no keyed arguments.

**Architecture split is now official guidance** — see `decision_strategy.md`.

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
