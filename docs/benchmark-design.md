# TalkBot Benchmark Design

## Overview

This document describes the design philosophy, evaluation methodology, and implementation
plan for TalkBot's conversation benchmark suite. It is intended as a living specification
that explains *why* each choice was made, so future contributors can understand the
trade-offs and extend the system with confidence.

TalkBot is voice-first: users speak, a small local model responds, and the response is
spoken aloud via TTS. This creates evaluation requirements that differ meaningfully from
standard LLM benchmarks — correctness matters, but so does whether the response sounds
natural when spoken, whether it works reliably across multiple runs, and whether a model
can sustain a coherent conversation over many turns on constrained hardware.

---

## Prior Art and Influences

### The Regex / Exact-Match Problem

The classic MMLU evaluation case study shows the danger of evaluation methodology
dominating scores. Three independent implementations of the same benchmark scored
LLaMA-65B as **0.637 / 0.637 / 0.488** — a 30% gap caused entirely by answer-extraction
differences, not model quality differences [1]. The same class of problem appears in
TalkBot's original benchmark: a response of `"I cannot cancel that timer"` fails a regex
expecting `r"can.t cancel"`, even though both mean the same thing when spoken aloud.

Regex-based response evaluation is appropriate when the match is structural (did a tool
get called? was an ID returned?). It is fragile for semantic correctness, where many
valid phrasings express the same intent.

### LLM-as-Judge

MT-Bench (2023) demonstrated that GPT-4 as judge achieves **85% agreement with human
experts**, matching the 81% human-human agreement baseline on the same questions [2].
MT-Bench uses an absolute 1–10 scale per turn, with reference-guided grading for
math and code to reduce judge failure rates from 70% to 15%.

WildBench (2024) refined this with task-specific checklists of 5–10 questions generated
per task type and pairwise GPT-4 scoring with a **K=500 character length penalty** to
suppress verbosity bias, achieving **0.98 Pearson correlation with human ratings** [3].

AlpacaEval introduced **length-controlled (LC) win rates** — using regression to control
for response length separately from response quality — improving human correlation from
0.94 to 0.98 [4].

The consistent finding across all three: LLM-as-judge substantially outperforms
regex/exact-match for open-ended response quality, at a cost measured in fractions of a
cent per evaluation.

### Tool Call Evaluation

The Berkeley Function Calling Leaderboard (BFCL) evaluates tool calls via **AST
(Abstract Syntax Tree) comparison** — parsing the generated function call into a syntax
tree and validating function name, required parameters, types, and values [5]. String
normalization (case-insensitive, whitespace/punctuation stripped) mitigates minor format
variation false negatives.

For multi-turn agentic tasks, τ-bench (2024) moves away from per-call matching entirely
toward **outcome-based evaluation**: the final database state is compared against an
annotated goal state [6]. This naturally handles semantic equivalence — two valid tool
call sequences that produce the same final state both succeed. τ-bench also introduces
the **pass^k metric**: running the same scenario k independent times and measuring the
fraction that succeed, which reveals reliability rather than just peak performance.

ToolBench / ToolEval uses ChatGPT as judge with majority voting (≥4 independent
judgments per solution), achieving **80.3% agreement with human annotators** on win
rate [7].

### Voice-Specific Evaluation

VoiceBench (2024) is the most directly relevant existing benchmark — described as "the
first benchmark designed to provide a multi-faceted evaluation of LLM-based voice
assistants" [8]. It evaluates *speech input understanding* (accent robustness, noise,
disfluencies) using GPT-4-as-judge on a 1–5 scale for open-ended QA. Crucially, it
measures a **"text-speech performance gap"** by comparing text-input vs. speech-input
performance to isolate ASR degradation from reasoning degradation.

However, VoiceBench does not evaluate *output quality for TTS synthesis* — whether the
model's text response is well-formed for spoken delivery. No existing benchmark measures
this dimension. TalkBot's TTS friction metrics fill this gap.

AudioBench (2024) found that audio LLMs are **more prompt-sensitive** than text LLMs,
motivating the use of multiple prompt templates per evaluation task [9]. A single prompt
template creates systematic false negatives when a slightly different phrasing would
have succeeded.

---

## Evaluation Dimensions

TalkBot's benchmark evaluates five distinct dimensions. Each has a primary method chosen
to match the nature of the claim being evaluated.

### 1. Tool Correctness (Structural)

**What it measures:** Did the model call the right tool with the right arguments?

**Method:** Structural matching against expected tool names and argument subsets, using
the existing `_evaluate_turn()` machinery. Argument normalization handles minor
format variations (e.g., `"10"` vs. `10`, `"ten seconds"` vs. `"10"`).

**Influenced by:** BFCL's AST evaluation with string normalization [5].

**Limitation:** Cannot detect functionally equivalent tool sequences that produce the
same outcome via different calls. Outcome-based evaluation (see Dimension 5) addresses
this for multi-turn scenarios.

### 2. Response Correctness (Semantic)

**What it measures:** Did the model answer correctly, even if phrased differently than
expected?

**Method:** LLM judge (see §LLM Judge Design below) scoring on a 1–5 scale:
- 5 — Fully correct, complete, appropriately concise
- 4 — Correct with minor omission or unnecessary detail
- 3 — Partially correct; key information present but incomplete
- 2 — Mostly incorrect; contains one accurate element
- 1 — Incorrect or irrelevant

Regex/contains checks remain available for scenarios where the match is structural
(exact ID, specific number, specific phrase that must appear verbatim).

**Influenced by:** MT-Bench absolute scoring [2], WildBench checklist approach [3].

### 3. TTS Spoken Quality (Novel)

**What it measures:** Is the response appropriate for spoken delivery — free of
markdown, underscore identifiers, code blocks, and other TTS-hostile tokens?

This dimension has two components:

**3a. TTS Friction Score (deterministic):** Count of TTS-hostile token patterns
remaining in the response after any normalization. Categories:
- Markdown: code fences, code spans, bold/italic markers, headers, bullet markers
- Identifier underscores: `snake_case` tokens that would be read as "snake underscore case"
- Symbol clusters: `%`, `$N`, `@`, raw URLs
- Code-like constructs: `key=value`, JSON fragments

A response with friction score 0 is clean for TTS. A higher score indicates how much
normalization was needed.

**3b. Spoken Naturalness (LLM judge):** Even a markdown-free response can sound
unnatural — over-formal, list-like in cadence, using jargon. The LLM judge scores
spoken naturalness separately from correctness on a 1–5 scale.

**TTS-style directive experiment:** A key hypothesis is that a system prompt directive
like *"Respond in natural spoken English. Never use markdown, bullet points, headers, or
technical identifiers with underscores — say 'cancel the timer' not cancel_timer"*
reduces TTS friction score significantly. The benchmark measures `friction(without
directive)` vs. `friction(with directive)` to quantify this. If the directive reduces
friction by >80%, normalization becomes a safety net rather than a primary mechanism.

**Influenced by:** VoiceBench's spoken quality framing [8]; identified gap in existing
benchmarks.

### 4. Reliability (pass^k)

**What it measures:** Does the model succeed consistently, or only sometimes?

**Method:** Each scenario is run k independent times with temperature > 0. The
**pass rate** = `successes / k` is reported alongside a reliability band:

| Band | Pass Rate | Interpretation |
|------|-----------|----------------|
| High | ≥ 0.80 | Reliable; suitable for production |
| Medium | 0.40–0.79 | Inconsistent; may frustrate users |
| Low | < 0.40 | Unreliable; not ready |

Default k=3 for routine runs; k=5 for scenarios tagged `high_variability` (recovery,
error handling, ambiguous input). Temperature is fixed at 0.3 for pass^k runs to
introduce realistic variation without maximizing randomness.

The pass^k metric was motivated by τ-bench's finding that GPT-4o achieves <25% pass^8
on retail customer service tasks — demonstrating that single-run benchmarks can
dramatically overstate model reliability [6].

**Reporting:** Both `pass_rate` (continuous) and `passed` (boolean, pass_rate ≥ 0.67)
are reported so existing dashboards remain comparable.

### 5. Conversation Endurance

**What it measures:** Can the model sustain a coherent, contextually aware conversation
over many turns? At what turn count does quality degrade?

**Method:** Long-form scenarios (15–30 turns) with:
- **Context recall checks:** Later turns ask about information established in early turns
  (e.g., "what was the first timer I set?"). LLM judge evaluates recall accuracy.
- **Latency growth tracking:** Per-turn latency is recorded; a latency growth rate
  (ms/turn) reveals whether context accumulation creates superlinear slowdown on SBCs.
- **Quality degradation rate:** LLM judge scores per turn; a declining trend indicates
  context window pressure or model confusion.
- **Failure mode detection:** Repetition, refusal, contradiction, hallucinated tool
  calls, and context abandonment are scored as categorical failures.

**Why this matters for SBCs:** A Raspberry Pi or similar SBC running a quantized 0.8B
model has strict memory limits. Context accumulation may cause OOM errors, swapping, or
inference slowdown before any semantic degradation appears. Endurance scenarios surface
this hardware-model interaction that single-turn benchmarks miss entirely.

**Target turn counts by model size:**

| Model Size | Target Turns | Rationale |
|------------|-------------|-----------|
| 0.5B–1B Q8 | 10–15 | Practical Pi 4 limit |
| 1B–3B Q4 | 15–20 | Pi 5 / M-series Mac |
| 7B+ | 20–30 | Workstation / cloud |

---

## LLM Judge Design

### Model Selection

**Default judge: `google/gemini-2.5-flash-lite` via OpenRouter**

Rationale:
- **Cost:** ~$0.10/1M input, ~$0.40/1M output. A full 50-scenario × k=3 benchmark with
  ~700 token judge prompts costs roughly **$0.03–$0.05 per run** — negligible.
- **Stability:** Gemini 2.5 is a current-generation model family; less likely to be
  deprecated than older flash variants. Paid tier avoids the rate-limiting that affects
  free-tier models, which has been a practical problem on overnight Pi runs.
- **Capability:** Sufficient for structured JSON rubric scoring and semantic equivalence
  judgment. Gemini Flash models are well-calibrated for instruction-following tasks.
- **Latency:** Network round-trip from a Pi to OpenRouter is the dominant cost; model
  speed within that is fast enough to not bottleneck overnight runs.

The judge model is a configurable parameter (`--judge-model`) so it can be overridden
without code changes.

### Judge Prompt Design

Influenced by WildBench's checklist approach [3] and MT-Bench's reference-guided
grading [2], each judge call includes:

1. **Task context:** The conversation history up to and including the evaluated turn
2. **Scoring rubric:** A task-type-specific checklist (3–5 yes/no questions) plus
   holistic 1–5 scores for correctness and spoken quality
3. **Anti-bias instructions:** Explicit instruction not to favor longer responses;
   a response that answers correctly in one sentence scores higher than a verbose
   equivalent (reversing the verbosity bias documented in MT-Bench [2])
4. **Output format:** Strict JSON — prevents free-text that requires secondary parsing

Example rubric for a timer scenario:
```json
{
  "checklist": {
    "timer_acknowledged": "Did the response confirm the timer was set/cancelled?",
    "duration_mentioned": "Did the response state the timer duration or ID?",
    "no_tool_jargon": "Did the response avoid technical identifiers like set_timer?",
    "spoken_natural": "Would this response sound natural if read aloud?"
  },
  "scores": {
    "correctness": "1-5",
    "spoken_quality": "1-5"
  },
  "reasoning": "one sentence"
}
```

### Bias Mitigations

- **Length penalty:** Responses >400 characters longer than a reference answer are
  flagged; the judge is instructed to treat verbosity as a defect, not a virtue.
  Adapted from WildBench's K=500 threshold [3].
- **No self-reference:** The judge prompt never names the model being evaluated, to
  avoid any model-family bias.
- **Structured output only:** Free-text judge reasoning is captured but not scored;
  only the numeric fields feed into pass/fail.

### Cost Guard

To prevent runaway costs on misconfigured runs, the benchmark runner enforces:
- `--max-judge-calls N` (default: 500 per run)
- Estimated cost is printed before any judge calls begin
- Dry-run mode (`--judge-dry-run`) substitutes a local heuristic scorer for
  development and CI

---

## TTS Normalization Strategy

### Two-layer approach

**Layer 1 — System prompt directive (primary):**
A TTS-style directive in the system prompt instructs the model to respond in natural
spoken English from the start. When effective, this eliminates TTS-hostile tokens before
they are generated, which is always better than cleaning them up after.

**Layer 2 — `normalize_for_tts()` (safety net):**
Even with a good directive, models occasionally produce markdown — especially under
few-shot examples, tool call results, or long conversation pressure. The normalization
function catches and removes these artifacts before TTS synthesis.

### What normalization handles (deterministic)

- Markdown: code fences, inline code, bold/italic, headers, bullets, numbered lists,
  horizontal rules
- Underscore identifiers: `cancel_timer` → "cancel timer" (iterative, handles chains)
- Label IDs: `Timer ID: 3` → "Timer 3"

### What normalization cannot handle (requires judge)

- Unnatural sentence cadence (reads like a bullet list even without bullets)
- Over-formal register ("I shall proceed to cancel the aforementioned timer")
- Jargon that isn't underscore-formatted (`API`, `JSON`, `HTTP 200`)
- Numbers that need spoken form (`14:32` → "2:32 PM", `15%` → "fifteen percent")
  — Phase 2 normalization, not yet implemented

### Benchmark experiment: directive effectiveness

Each benchmark profile can be run with and without the TTS directive to measure the
delta in TTS friction scores. This answers: *how much work is the directive doing vs.
the normalization?* If the directive reduces friction by >80%, normalization is
confirmed as a safety net. If <50%, the directive wording needs improvement.

---

## Scenario Types

| Type | Description | Typical Turns | Key Metrics |
|------|-------------|---------------|-------------|
| `functional` | Single-capability test (set timer, add to list) | 2–4 | Tool correctness, response correctness |
| `recovery` | Error, retry, and correction flows | 4–8 | Reliability (pass^k), semantic correctness |
| `multi_tool` | Sequences requiring multiple tool types | 5–10 | Tool correctness, context recall |
| `endurance` | Long conversation with recall checks | 15–30 | Quality degradation, latency growth |
| `tts_quality` | Responses evaluated for spoken naturalness | 2–4 | TTS friction score, spoken quality |
| `adversarial` | Ambiguous or contradictory user input | 3–6 | Refusal detection, graceful handling |

---

## Hardware Targets

Benchmarks are designed to run on:

| Platform | Notes |
|----------|-------|
| Raspberry Pi 4 (4GB) | Baseline SBC; quantized 0.5B–1B models via llama.cpp |
| Raspberry Pi 5 (8GB) | Higher capability SBC; up to 3B Q4 |
| Apple Silicon (M-series) | Development baseline; Metal acceleration |
| x86 Linux workstation | CI baseline; CPU inference |

Endurance scenarios flag hardware-specific failure modes: OOM, swap thrashing,
thermal throttling (Pi). Per-turn latency is reported with hardware metadata so
results are comparable across platforms.

---

## References

[1] Gao et al. "A Note on MMLU Implementations." Hugging Face Blog, 2023.
    https://huggingface.co/blog/open-llm-leaderboard-mmlu

[2] Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena."
    arXiv:2306.05685, 2023.
    https://arxiv.org/abs/2306.05685

[3] Lin & Chen. "WildBench: Benchmarking LLMs with Challenging Tasks from Real Users
    in the Wild." arXiv:2406.04770, 2024.
    https://arxiv.org/abs/2406.04770

[4] Li et al. "AlpacaEval: An Automatic Evaluator of Instruction-following Models."
    https://tatsu-lab.github.io/alpaca_eval/

[5] Yan et al. "Berkeley Function-Calling Leaderboard."
    https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html

[6] Yao et al. "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World
    Domains." arXiv:2406.12045, 2024.
    https://arxiv.org/abs/2406.12045

[7] Qin et al. "ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world
    APIs." arXiv:2307.16789, 2023.
    https://arxiv.org/abs/2307.16789

[8] Chen et al. "VoiceBench: Benchmarking LLM-Based Voice Assistants."
    arXiv:2410.17196, 2024.
    https://arxiv.org/abs/2410.17196

[9] Wang et al. "AudioBench: A Universal Benchmark for Audio Large Language Models."
    arXiv:2406.16020, 2024.
    https://arxiv.org/abs/2406.16020
