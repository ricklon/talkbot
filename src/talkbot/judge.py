"""LLM-as-judge evaluation module for TalkBot benchmarks.

Calls an OpenRouter model to score benchmark turn quality on two dimensions:
  - correctness (1–5): did the response answer the user correctly?
  - spoken_quality (1–5): is the response natural for TTS, free of markdown/jargon?

Default judge model: google/gemini-2.5-flash-lite
  - Paid tier (no rate-limit surprises on overnight Pi runs)
  - Current-generation Gemini family (low deprecation risk)
  - ~$0.10/1M input, ~$0.40/1M output → ~$0.03–0.05 per full benchmark run

Dry-run mode substitutes a heuristic TTS-friction scorer so tests and CI
can exercise the full evaluation pipeline without any API calls or costs.

Design influenced by:
  - MT-Bench: absolute 1–10 scale, reference-guided grading [arXiv:2306.05685]
  - WildBench: task-type checklists, anti-verbosity instruction [arXiv:2406.04770]
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any

import httpx

DEFAULT_JUDGE_MODEL = "google/gemini-2.5-flash-lite"
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Per-tag rubric checklists. First matching tag wins; "default" is the fallback.
# Checklist items are yes/no questions that guide the judge toward task-specific criteria.
_RUBRICS: dict[str, list[str]] = {
    "timer": [
        "Did the response acknowledge the timer action (set, cancelled, or listed)?",
        "Did the response mention the relevant timer duration or ID when appropriate?",
        "Did the response avoid technical identifiers like set_timer or cancel_timer?",
        "Is the response appropriately brief for a voice assistant?",
    ],
    "list": [
        "Did the response confirm the list action (add, remove, get, or clear)?",
        "Did the response mention the list name or item when relevant?",
        "Is the response clear and natural when spoken aloud?",
    ],
    "memory": [
        "Did the response confirm what was remembered or recalled?",
        "Is the recalled information consistent with prior turns?",
        "Is the response natural and conversational in tone?",
    ],
    "recovery": [
        "Did the response handle the error or unexpected situation gracefully?",
        "Did the response offer a helpful correction or alternative?",
        "Is the tone calm and helpful, not robotic or excessively apologetic?",
    ],
    "math": [
        "Is the numeric answer correct?",
        "Is the answer stated clearly without unnecessary steps?",
        "Would the answer sound natural if read aloud?",
    ],
    "default": [
        "Does the response correctly address the user's request?",
        "Is the response appropriately concise for a voice assistant?",
        "Is the response natural when spoken aloud — no markdown, no jargon?",
    ],
}


@dataclass
class JudgeConfig:
    """Configuration for the LLM judge."""

    model: str = DEFAULT_JUDGE_MODEL
    api_key: str | None = None
    max_calls: int = 500
    dry_run: bool = False
    timeout: float = 30.0


@dataclass
class JudgeResult:
    """Result of a single LLM judge evaluation."""

    correctness: float          # 1–5
    spoken_quality: float       # 1–5
    checklist: dict[str, bool]  # rubric question index → pass/fail
    reasoning: str
    tokens_used: int = 0
    error: str | None = None

    @property
    def has_error(self) -> bool:
        return self.error is not None

    @property
    def avg_score(self) -> float:
        """Average of correctness and spoken_quality; 0.0 if errored."""
        if self.has_error:
            return 0.0
        return round((self.correctness + self.spoken_quality) / 2.0, 2)


class LLMJudge:
    """Evaluates benchmark turns by calling an OpenRouter LLM judge.

    Usage::

        config = JudgeConfig(model="google/gemini-2.5-flash-lite")
        with LLMJudge(config) as judge:
            result = judge.evaluate_turn(
                user="Set a timer for 5 minutes",
                response="Sure! I've set a timer for 5 minutes.",
                history=[],
                tags=["timer"],
            )
            print(result.correctness, result.spoken_quality)
    """

    def __init__(self, config: JudgeConfig) -> None:
        self.config = config
        self._calls_made = 0
        self._client: httpx.Client | None = None
        if not config.dry_run:
            self._client = httpx.Client(timeout=config.timeout)

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "LLMJudge":
        return self

    def __exit__(self, *_: Any) -> bool:
        self.close()
        return False

    @property
    def calls_made(self) -> int:
        return self._calls_made

    @property
    def calls_remaining(self) -> int:
        return max(0, self.config.max_calls - self._calls_made)

    def _api_key(self) -> str:
        key = self.config.api_key or os.getenv("OPENROUTER_API_KEY", "")
        if not key:
            raise RuntimeError(
                "No OpenRouter API key. Set OPENROUTER_API_KEY or pass --judge-api-key."
            )
        return key

    def _select_rubric(self, tags: list[str]) -> list[str]:
        for tag in tags:
            if tag in _RUBRICS:
                return _RUBRICS[tag]
        return _RUBRICS["default"]

    def _build_prompt(
        self,
        *,
        user: str,
        response: str,
        history: list[dict[str, str]],
        tags: list[str],
    ) -> str:
        rubric_items = self._select_rubric(tags)
        rubric_lines = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(rubric_items))

        # Include up to 6 prior messages for context, truncated to 200 chars each
        context_str = ""
        if len(history) > 2:
            prior = [m for m in history if m.get("role") != "system"][-6:]
            lines = [f"  [{m['role']}]: {str(m.get('content', ''))[:200]}" for m in prior]
            context_str = "\nConversation context (recent turns):\n" + "\n".join(lines) + "\n"

        checklist_keys = ", ".join(f'"{i + 1}": true_or_false' for i in range(len(rubric_items)))

        return f"""You are evaluating a voice assistant response. Be concise and strict.
{context_str}
User said: {user!r}
Assistant responded: {response!r}

Answer each checklist question with true or false:
{rubric_lines}

Then provide:
- correctness: integer 1-5
  5 = fully correct and complete
  4 = correct with minor omission
  3 = partially correct
  2 = mostly wrong, one accurate element
  1 = incorrect or irrelevant
- spoken_quality: integer 1-5
  5 = natural spoken English, no markdown or jargon
  4 = mostly natural, minor awkwardness
  3 = passable but some unnatural phrasing
  2 = contains markdown symbols or underscore_identifiers
  1 = heavy markdown, code blocks, or technical jargon throughout

IMPORTANT: Do NOT reward verbosity. A short correct answer scores higher than a long one.
Any response containing **bold**, `code`, ## headers, or - bullet points scores spoken_quality <= 2.
Any response containing underscore_identifiers like set_timer scores spoken_quality <= 3.

Respond with ONLY valid JSON, no other text:
{{"checklist": {{{checklist_keys}}}, "correctness": 1_to_5, "spoken_quality": 1_to_5, "reasoning": "one sentence"}}"""

    def _dry_run_evaluate(self, *, response: str, tags: list[str]) -> JudgeResult:
        """Heuristic scorer for dry-run mode. No API calls."""
        # Import the already-compiled regexes from text_utils to avoid duplication
        from talkbot.text_utils import (
            _MD_BOLD_ITALIC_RE,
            _MD_BULLET_RE,
            _MD_CODE_FENCE_RE,
            _MD_CODE_SPAN_RE,
            _MD_HEADER_RE,
            _MD_NUMBERED_RE,
            _UNDERSCORE_ID_RE,
        )

        friction = 0
        friction += len(_MD_CODE_FENCE_RE.findall(response))
        friction += len(_MD_CODE_SPAN_RE.findall(response))
        friction += len(_MD_BOLD_ITALIC_RE.findall(response))
        friction += len(_MD_HEADER_RE.findall(response))
        friction += len(_MD_BULLET_RE.findall(response))
        friction += len(_MD_NUMBERED_RE.findall(response))
        friction += len(_UNDERSCORE_ID_RE.findall(response))

        spoken_quality = max(1.0, 5.0 - float(friction))
        correctness = 3.0  # neutral — can't assess correctness without calling a model

        rubric_items = self._select_rubric(tags)
        checklist = {str(i + 1): True for i in range(len(rubric_items))}

        return JudgeResult(
            correctness=correctness,
            spoken_quality=spoken_quality,
            checklist=checklist,
            reasoning="[dry-run] heuristic score based on TTS friction count",
            tokens_used=0,
        )

    def evaluate_turn(
        self,
        *,
        user: str,
        response: str,
        history: list[dict[str, str]],
        tags: list[str],
    ) -> JudgeResult:
        """Evaluate a single conversation turn.

        Returns a JudgeResult. On API error or call-limit, returns a result
        with ``error`` set so callers can distinguish scored vs. skipped turns.
        """
        if self._calls_made >= self.config.max_calls:
            return JudgeResult(
                correctness=0.0,
                spoken_quality=0.0,
                checklist={},
                reasoning="[skipped] judge call limit reached",
                error="call_limit_reached",
            )

        self._calls_made += 1

        if self.config.dry_run:
            return self._dry_run_evaluate(response=response, tags=tags)

        prompt = self._build_prompt(
            user=user,
            response=response,
            history=history,
            tags=tags,
        )

        try:
            assert self._client is not None
            resp = self._client.post(
                f"{_OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key()}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/ricklon/talkbot",
                    "X-Title": "TalkBot Benchmark Judge",
                },
                json={
                    "model": self.config.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                    "max_tokens": 256,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            usage = data.get("usage") or {}
            tokens_used = int(usage.get("total_tokens", 0))
            content = data["choices"][0]["message"]["content"].strip()

            # Strip markdown code fences if model wraps the JSON
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)

            parsed = json.loads(content)
            checklist = {
                str(k): bool(v) for k, v in parsed.get("checklist", {}).items()
            }
            return JudgeResult(
                correctness=float(parsed.get("correctness", 3)),
                spoken_quality=float(parsed.get("spoken_quality", 3)),
                checklist=checklist,
                reasoning=str(parsed.get("reasoning", "")),
                tokens_used=tokens_used,
            )

        except Exception as exc:
            return JudgeResult(
                correctness=0.0,
                spoken_quality=0.0,
                checklist={},
                reasoning="",
                error=str(exc),
            )


def estimate_judge_cost(
    scenario_count: int,
    avg_turns: float = 3.0,
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    avg_prompt_tokens: int = 700,
    avg_response_tokens: int = 150,
) -> dict[str, Any]:
    """Estimate OpenRouter cost for a judged benchmark run.

    Returns a dict with token counts and estimated USD cost.
    Pricing is approximate and may not reflect current OpenRouter rates.
    """
    # Approximate pricing per 1M tokens (input/output)
    _PRICING: dict[str, tuple[float, float]] = {
        "google/gemini-2.5-flash-lite": (0.10, 0.40),
        "google/gemini-2.0-flash-lite-001": (0.075, 0.30),
        "google/gemini-2.0-flash-001": (0.10, 0.40),
        "meta-llama/llama-3.3-70b-instruct": (0.10, 0.32),
        "meta-llama/llama-3.3-70b-instruct:free": (0.0, 0.0),
        "openai/gpt-4o-mini": (0.15, 0.60),
    }
    input_per_m, output_per_m = _PRICING.get(model, (0.10, 0.40))

    total_calls = int(scenario_count * avg_turns)
    total_input = total_calls * avg_prompt_tokens
    total_output = total_calls * avg_response_tokens
    cost_usd = (total_input / 1_000_000 * input_per_m) + (
        total_output / 1_000_000 * output_per_m
    )

    return {
        "model": model,
        "judge_calls": total_calls,
        "input_tokens": total_input,
        "output_tokens": total_output,
        "estimated_cost_usd": round(cost_usd, 4),
        "input_rate_per_1m": input_per_m,
        "output_rate_per_1m": output_per_m,
    }
