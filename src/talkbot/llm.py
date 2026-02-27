"""LLM provider abstraction with local llama.cpp and OpenRouter backends."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import difflib
import inspect
from pathlib import Path
from typing import Any, Callable, Optional

import httpx
from talkbot.openrouter import OpenRouterClient
from talkbot.thinking import NO_THINK_INSTRUCTION
from talkbot.protocol import LLMClient


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider cannot be initialized or used."""


def _response_message(response: dict[str, Any]) -> dict[str, Any]:
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict):
                return message
    return {}


def _response_content(response: dict[str, Any]) -> str:
    message = _response_message(response)
    content = message.get("content")
    if content is not None:
        return content if isinstance(content, str) else str(content)

    error = response.get("error")
    if isinstance(error, dict):
        detail = error.get("message") or error.get("code") or str(error)
        return f"Error: {detail}"
    if error:
        return f"Error: {error}"
    return ""


def _normalize_tool_args_for_call(function_name: str, function_args: Any) -> dict[str, Any]:
    """Normalize common alias parameters produced by smaller models."""
    if not isinstance(function_args, dict):
        return {}

    args = dict(function_args)
    if function_name == "roll_dice":
        if "count" not in args and "dice" in args:
            args["count"] = args.get("dice")
        if "sides" not in args:
            if "face" in args:
                args["sides"] = args.get("face")
            elif "faces" in args:
                args["sides"] = args.get("faces")
        args.pop("dice", None)
        args.pop("face", None)
        args.pop("faces", None)

    alias_map: dict[str, dict[str, str]] = {
        "set_timer": {
            "duration": "seconds",
            "time": "seconds",
            "secs": "seconds",
            "sec": "seconds",
            "delay": "seconds",
        },
        "set_reminder": {
            "duration": "seconds",
            "time": "seconds",
            "secs": "seconds",
            "sec": "seconds",
            "text": "message",
            "label": "message",
        },
        "cancel_timer": {
            "id": "timer_id",
            "timer": "timer_id",
            "timerid": "timer_id",
        },
        "create_list": {"name": "list_name", "list": "list_name"},
        "get_list": {"name": "list_name", "list": "list_name"},
        "clear_list": {"name": "list_name", "list": "list_name"},
        "add_to_list": {"name": "list_name", "list": "list_name", "value": "item"},
        "add_items_to_list": {"name": "list_name", "list": "list_name"},
        "remove_from_list": {"name": "list_name", "list": "list_name", "value": "item"},
        "remember": {"name": "key", "field": "key", "text": "value"},
        "recall": {"name": "key", "field": "key"},
    }

    for alias, canonical in alias_map.get(function_name, {}).items():
        if alias in args and canonical not in args:
            args[canonical] = args[alias]
    # Remove alias keys once canonical key is populated so duplicate calls
    # with different alias spellings dedupe to the same call signature.
    for alias, canonical in alias_map.get(function_name, {}).items():
        if canonical in args and alias in args:
            args.pop(alias, None)
    return args


def _extract_remember_intent(text: str) -> tuple[str, str] | None:
    candidate = str(text or "").strip()
    if not candidate:
        return None
    match = re.search(
        r"\b(?:remember|store|save)(?:\s+that)?\s+(?:my\s+)?([a-z0-9_ ]{2,40}?)\s+is\s+(.+)$",
        candidate,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    key = match.group(1).strip().lower().replace(" ", "_")
    value = match.group(2).strip().strip(".!?")
    if not key or not value:
        return None
    return key, value


def _rewrite_tool_call_for_user_intent(
    function_name: str,
    function_args: dict[str, Any],
    user_text: str,
) -> tuple[str, dict[str, Any]]:
    """Fix common wrong-tool calls based on explicit current-turn user intent."""
    remember = _extract_remember_intent(user_text)
    if remember and function_name in {"recall", "recall_all"}:
        key, value = remember
        return "remember", {"key": key, "value": value}
    return function_name, dict(function_args)


def _latest_user_text(messages: list[dict[str, Any]]) -> str:
    for message in reversed(messages):
        if str(message.get("role", "")).strip().lower() == "user":
            return str(message.get("content", "")).strip()
    return ""


def _filter_tool_args_for_callable(func: Callable[..., Any], args: dict[str, Any]) -> dict[str, Any]:
    """Drop kwargs that the target callable does not accept."""
    if not isinstance(args, dict):
        return {}
    try:
        signature = inspect.signature(func)
    except Exception:
        return dict(args)

    accepts_var_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    if accepts_var_kwargs:
        return dict(args)

    allowed = {
        name
        for name, parameter in signature.parameters.items()
        if parameter.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    }
    return {key: value for key, value in args.items() if key in allowed}


class LocalLlamaCppClient:
    """Non-server local client using llama.cpp CLI."""

    supports_tools = True
    provider_name = "local"

    def __init__(
        self,
        *,
        model_path: str,
        binary: str = "llama-cli",
        n_ctx: int = 2048,
        enable_thinking: bool = False,
        temperature: float = 0.3,
        max_tokens: int = 512,
        direct_tool_routing: Optional[bool] = None,
    ) -> None:
        import datetime as _dt
        _now = _dt.datetime.now().astimezone()
        self._launch_time_context = (
            f"Current date and time: {_now.strftime('%A, %B %d, %Y %I:%M %p')} "
            f"{_now.strftime('%Z')} (UTC{_now.strftime('%z')[:3]}:{_now.strftime('%z')[3:]})"
        )
        self.model_path = model_path
        self.binary = binary
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.enable_thinking = enable_thinking
        self.n_ctx = int(n_ctx)
        self.last_usage: dict = {}
        self.tools: dict[str, Callable] = {}
        self.tool_definitions: list[dict] = []
        if direct_tool_routing is None:
            self.direct_tool_routing = os.getenv("TALKBOT_LOCAL_DIRECT_TOOL_ROUTING", "0").strip().lower() in {"1", "true", "yes", "on"}
        else:
            self.direct_tool_routing = direct_tool_routing
        self._llm = None
        self._use_python_backend = False
        self._requested_binary = binary

        if not Path(model_path).exists():
            raise LLMProviderError(
                f"Local model not found at '{model_path}'. "
                "Set TALKBOT_LOCAL_MODEL_PATH to a local GGUF path."
            )

        resolved_bin = self._resolve_binary(binary)
        if resolved_bin:
            self.binary = resolved_bin

        # Prefer python bindings (no external llama-cli dependency required).
        try:
            from llama_cpp import Llama  # type: ignore

            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                verbose=False,
            )
            self._use_python_backend = True
            return
        except Exception:
            self._llm = None
            self._use_python_backend = False

    @staticmethod
    def _resolve_binary(binary: str) -> Optional[str]:
        """Resolve a llama.cpp executable from PATH or common aliases."""
        candidates: list[str] = []
        for candidate in (binary, "llama-cli", "llama"):
            if candidate and candidate not in candidates:
                candidates.append(candidate)
        for candidate in candidates:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
        return None

    def _messages_to_prompt(self, messages: list[dict]) -> str:
        messages = self._prepare_messages(messages)
        lines = []
        for m in messages:
            role = str(m.get("role", "user")).strip().lower()
            content = str(m.get("content", "")).strip()
            if not content:
                continue
            if role == "system":
                lines.append(f"System: {content}")
            elif role == "assistant":
                lines.append(f"Assistant: {content}")
            else:
                lines.append(f"User: {content}")
        lines.append("Assistant:")
        return "\n".join(lines)

    def _with_tool_guidance(self, messages: list[dict]) -> list[dict]:
        """Inject deterministic tool-call instructions for text-only local models."""
        tool_names = sorted(self.tools.keys())
        if not tool_names:
            return messages
        guidance = (
            "Tool mode is enabled.\n"
            "When a tool can help, choose the best tool and call it.\n"
            "For memory/list/timer requests, always call tools first.\n"
            "Do not answer memory/list/timer questions from chat memory alone.\n"
            "For tool calls, output ONLY a single Python-style function call with named args "
            "and no extra text.\n"
            "After tool results are available, answer the user using those results.\n"
            "Examples:\n"
            "- get_current_time()\n"
            "- set_timer(seconds=10)\n"
            "- cancel_timer(timer_id=\"1\")\n"
            "- create_list(list_name=\"grocery\")\n"
            "- add_to_list(item=\"milk\", list_name=\"grocery\")\n"
            "- list_all_lists()\n"
            "- remember(key=\"favorite_color\", value=\"blue\")\n"
            "- recall(key=\"favorite_color\")\n"
            "If no tool fits, answer normally in one short sentence.\n"
            f"Available tools: {', '.join(tool_names)}"
        )
        return [{"role": "system", "content": guidance}] + list(messages)

    def _prepare_messages(self, messages: list[dict]) -> list[dict]:
        """Normalize messages so thinking behavior is consistent across backends."""
        prepared: list[dict] = []
        has_system = False
        for m in messages:
            role = str(m.get("role", "user")).strip().lower()
            content = str(m.get("content", "")).strip()
            if not content:
                continue
            if role == "system":
                has_system = True
            elif role == "user" and not self.enable_thinking:
                if not content.startswith("/no_think"):
                    content = f"/no_think\n{content}\n/no_think"
            prepared.append({"role": role, "content": content})
        if not self.enable_thinking and not has_system:
            prepared.insert(0, {"role": "system", "content": NO_THINK_INSTRUCTION})
        return prepared

    @staticmethod
    def _clean_output(text: str) -> str:
        """Strip ANSI escape codes, <think>...</think> blocks, and llama.cpp noise from output."""
        import re as _re
        text = _re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", text)
        # Remove closed think blocks
        text = _re.sub(r"<think>.*?</think>", "", text, flags=_re.DOTALL)
        # Remove unclosed think block (EOF before closing tag)
        text = _re.sub(r"<think>.*", "", text, flags=_re.DOTALL)
        # Remove llama.cpp interactive-mode noise lines
        text = _re.sub(r"^[>\s]*EOF by user\s*$", "", text, flags=_re.MULTILINE)
        return text.strip()

    def _run_prompt(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        tokens = int(max_tokens or self.max_tokens)
        cmd = [
            self.binary,
            "-m",
            self.model_path,
            "-p",
            prompt,
            "-n",
            str(tokens),
            "--temp",
            str(self.temperature),
            "--no-display-prompt",
            "--no-conversation",
            "--single-turn",
        ]
        try:
            proc = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            )
        except FileNotFoundError as e:
            raise LLMProviderError(
                f"llama.cpp binary '{self._requested_binary}' not found (also tried common aliases), "
                "and llama-cpp-python is unavailable. Set TALKBOT_LLAMACPP_BIN to the executable path, "
                "or install one of: `uv tool install talkbot --with llama-cpp-python` "
                "or system llama.cpp (`llama-cli` / `llama`)."
            ) from e
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else ""
            raise LLMProviderError(
                f"Local llama.cpp generation failed{': ' + stderr if stderr else ''}"
            ) from e

        return self._clean_output(proc.stdout)

    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> dict:
        del stream
        prepared_messages = self._prepare_messages(messages)
        if self._use_python_backend and self._llm is not None:
            tokens = int(max_tokens or self.max_tokens)
            try:
                response = self._llm.create_chat_completion(
                    messages=prepared_messages,
                    temperature=float(temperature),
                    max_tokens=tokens,
                )
            except Exception as e:
                raise LLMProviderError(
                    f"Local llama-cpp-python generation failed: {e}"
                ) from e
            content = _response_content(response)
            content = self._clean_output(content)
            self.last_usage = response.get("usage") or {}
            return {"choices": [{"message": {"content": content}}], "usage": self.last_usage}

        prompt = self._messages_to_prompt(prepared_messages)
        content = self._run_prompt(prompt, max_tokens=max_tokens)
        self.last_usage = {}
        return {"choices": [{"message": {"content": content}}]}

    def simple_chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        augmented = (
            f"{self._launch_time_context}\n\n{system_prompt}"
            if system_prompt
            else self._launch_time_context
        )
        messages: list[dict] = [
            {"role": "system", "content": augmented},
            {"role": "user", "content": message},
        ]
        return _response_content(self.chat_completion(messages))

    def chat_with_system_tools(
        self, message: str, system_prompt: Optional[str] = None
    ) -> str:
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        return self.chat_with_tools(messages)

    def chat_with_tools(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        max_tool_calls: int = 10,
    ) -> str:
        if not self.tools:
            response = self.chat_completion(messages, temperature=temperature, max_tokens=max_tokens)
            return _response_content(response)

        current_messages = self._with_tool_guidance(messages)
        latest_user_text = _latest_user_text(messages)
        tool_call_count = 0
        executed_tool_summaries: list[str] = []
        executed_call_results: dict[str, str] = {}

        # Fast-path common spoken intents before asking model to format a tool call.
        direct_calls = self._direct_tool_calls_from_user(messages) if self.direct_tool_routing else []
        if direct_calls:
            for tool_call in direct_calls:
                function_name = tool_call["function"]["name"]
                try:
                    function_args = json.loads(tool_call["function"]["arguments"])
                except Exception:
                    function_args = {}
                function_name, function_args = _rewrite_tool_call_for_user_intent(
                    function_name,
                    function_args,
                    latest_user_text,
                )
                function_args = _normalize_tool_args_for_call(function_name, function_args)
                if function_name in self.tools:
                    tool_func = self.tools[function_name]
                    function_args = _filter_tool_args_for_callable(tool_func, function_args)
                    try:
                        result = tool_func(**function_args)
                    except Exception as e:
                        result = f"Error executing {function_name}: {e}"
                else:
                    result = f"Error: Tool {function_name} not found"
                executed_tool_summaries.append(f"{function_name}({function_args}) -> {result}")
            return "\n".join(s.split(" -> ", 1)[-1] for s in executed_tool_summaries)

        while tool_call_count < max_tool_calls:
            response = self.chat_completion(current_messages, temperature=temperature, max_tokens=max_tokens)
            content = self._clean_output(_response_content(response))
            tool_calls = self._extract_tag_tool_calls(content)

            if not tool_calls:
                tool_calls = self._extract_python_style_tool_calls(content)
            if not tool_calls:
                tool_calls = self._resolve_tool_like_text(content)
            if not tool_calls:
                if executed_tool_summaries:
                    return "\n".join(s.split(" -> ", 1)[-1] for s in executed_tool_summaries)
                return content

            # Keep model transcript so the next turn can see what it attempted.
            current_messages.append({"role": "assistant", "content": content})

            any_new_calls = False
            for tool_call in tool_calls:
                tool_call_count += 1
                function_name = tool_call["function"]["name"]
                try:
                    function_args = json.loads(tool_call["function"]["arguments"])
                except Exception:
                    function_args = {}
                function_name, function_args = _rewrite_tool_call_for_user_intent(
                    function_name,
                    function_args,
                    latest_user_text,
                )
                function_args = _normalize_tool_args_for_call(function_name, function_args)
                tool_func: Callable[..., Any] | None = None
                if function_name in self.tools:
                    tool_func = self.tools[function_name]
                    function_args = _filter_tool_args_for_callable(tool_func, function_args)
                call_key = f"{function_name}|{json.dumps(function_args, sort_keys=True)}"
                if call_key in executed_call_results:
                    current_messages.append(
                        {
                            "role": "tool",
                            "name": function_name,
                            "content": executed_call_results[call_key],
                        }
                    )
                    continue
                any_new_calls = True
                if function_name in self.tools:
                    try:
                        result = tool_func(**function_args) if tool_func is not None else ""
                    except Exception as e:
                        result = f"Error executing {function_name}: {e}"
                else:
                    result = f"Error: Tool {function_name} not found"
                executed_call_results[call_key] = str(result)
                executed_tool_summaries.append(f"{function_name}({function_args}) -> {result}")
                current_messages.append(
                    {
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    }
                )

            if not any_new_calls:
                break

        if executed_tool_summaries:
            # Keep post-tool response deterministic in local mode: return tool results
            # directly instead of asking the model to paraphrase again.
            return "\n".join(s.split(" -> ", 1)[-1] for s in executed_tool_summaries)
        response = self.chat_completion(current_messages, temperature=temperature, max_tokens=max_tokens)
        return _response_content(response).strip()

    def register_tool(
        self, name: str, func: Callable, description: str, parameters: dict
    ) -> None:
        del description, parameters
        self.tools[name] = func

    def clear_tools(self) -> None:
        self.tools.clear()
        self.tool_definitions.clear()

    def _extract_python_style_tool_calls(self, content: str) -> list[dict]:
        """Fallback for models that output tool calls as Python-style calls: name(k='v', ...)."""
        if not content:
            return []
        tool_calls: list[dict] = []
        pattern = re.compile(r"\b(\w+)\s*\(([^)]*)\)")
        for idx, match in enumerate(pattern.finditer(content)):
            name = match.group(1)
            if name not in self.tools:
                continue
            args_str = match.group(2).strip()
            args: dict = {}
            for kv in re.finditer(
                r'(\w+)\s*=\s*(?:"([^"]*?)"|\'([^\']*?)\'|([\w.+-]+))', args_str
            ):
                key = kv.group(1)
                val: object = (
                    kv.group(2) if kv.group(2) is not None
                    else kv.group(3) if kv.group(3) is not None
                    else kv.group(4) or ""
                )
                try:
                    val = int(val)  # type: ignore[arg-type]
                except (ValueError, TypeError):
                    try:
                        val = float(val)  # type: ignore[arg-type]
                    except (ValueError, TypeError):
                        pass
                args[key] = val
            tool_calls.append(
                {
                    "id": f"pyfunc-{idx}",
                    "function": {"name": name, "arguments": json.dumps(args)},
                }
            )
        return tool_calls

    @staticmethod
    def _extract_tag_tool_calls(content: str) -> list[dict]:
        """Fallback parser for models that emit <tool_call>{...}</tool_call> text."""
        if not content:
            return []
        matches = re.findall(
            r"<tool_call>\s*(\{.*?\})\s*</tool_call>", content, flags=re.DOTALL
        )
        tool_calls: list[dict] = []
        for idx, block in enumerate(matches):
            try:
                payload = json.loads(block)
            except Exception:
                continue
            name = str(payload.get("name", "")).strip()
            args = payload.get("arguments", {})
            if not name:
                continue
            if not isinstance(args, dict):
                args = {}
            tool_calls.append(
                {
                    "id": f"text-tool-{idx}",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(args),
                    },
                }
            )
        return tool_calls

    def _resolve_tool_like_text(self, content: str) -> list[dict]:
        """Best-effort map for short tool-like model outputs."""
        text = (content or "").strip()
        if not text:
            return []
        line = text.splitlines()[0].strip().strip("`").strip()
        line = line.rstrip(".;:")
        compact = re.sub(r"[^a-z0-9_()]+", "", line.lower())
        if not compact:
            return []

        # Exact bare function name (with or without empty parens).
        bare = compact.rstrip("()")
        if bare in self.tools and compact in (bare, f"{bare}()"):
            return [{"id": f"plain-{bare}-0", "function": {"name": bare, "arguments": "{}"}}]

        # Heuristic aliases for common tool intents.
        lowered = line.lower()
        if re.search(r"\b(list|show)\s+timers?\b|\bactive\s+timers?\b", lowered):
            return [{"id": "alias-timers-0", "function": {"name": "list_timers", "arguments": "{}"}}]
        if "list timer" in lowered or "active timer" in lowered:
            return [{"id": "alias-timers-0", "function": {"name": "list_timers", "arguments": "{}"}}]
        cancel_match = re.search(r"cancel\s+timer\s+#?(\d+)", lowered)
        if cancel_match:
            return [
                {
                    "id": "alias-cancel-timer-0",
                    "function": {
                        "name": "cancel_timer",
                        "arguments": json.dumps({"timer_id": cancel_match.group(1)}),
                    },
                }
            ]
        remember_match = re.search(
            r"\bremember(?:\s+that)?\s+(?:my\s+)?([a-z0-9_ ]{2,40}?)\s+is\s+(.+)$",
            lowered,
        )
        if remember_match:
            key = remember_match.group(1).strip().replace(" ", "_")
            value = remember_match.group(2).strip().strip(".!?")
            if key and value:
                return [
                    {
                        "id": "alias-remember-0",
                        "function": {
                            "name": "remember",
                            "arguments": json.dumps({"key": key, "value": value}),
                        },
                    }
                ]
        recall_match = re.search(
            r"\b(?:what\s+is|recall)\s+(?:my\s+)?([a-z0-9_ ]{2,40})\??$",
            lowered,
        )
        if recall_match:
            key = recall_match.group(1).strip().replace(" ", "_")
            if key:
                return [
                    {
                        "id": "alias-recall-0",
                        "function": {
                            "name": "recall",
                            "arguments": json.dumps({"key": key}),
                        },
                    }
                ]
        if re.search(r"\bwhat\s+time\b|\bcurrent\s+time\b|\btime\s+is\s+it\b", lowered):
            return [{"id": "alias-time-0", "function": {"name": "get_current_time", "arguments": "{}"}}]
        if re.search(r"\bwhat\s+date\b|\bcurrent\s+date\b|\btoday'?s\s+date\b", lowered):
            return [{"id": "alias-date-0", "function": {"name": "get_current_date", "arguments": "{}"}}]
        if re.search(r"\bcoin\b", lowered):
            return [{"id": "alias-coin-0", "function": {"name": "flip_coin", "arguments": "{}"}}]
        if "list" in lowered and "all" in lowered:
            return [{"id": "alias-lists-0", "function": {"name": "list_all_lists", "arguments": "{}"}}]
        timer_match = re.search(
            r"(?:set\s+)?(?:a\s+)?timer(?:\s+for)?\s+(\d+)\s*(?:s|sec|secs|second|seconds)\b",
            lowered,
        )
        if timer_match:
            return [
                {
                    "id": "alias-set-timer-0",
                    "function": {
                        "name": "set_timer",
                        "arguments": json.dumps({"seconds": int(timer_match.group(1))}),
                    },
                }
            ]

        # Dice-like aliases: rolled_d20_total, d20, 2d20, etc.
        if "roll" in lowered or re.search(r"\d+d\d+|d\d+", lowered):
            count = 1
            sides = 6
            m = re.search(r"(\d+)\s*d\s*(\d+)", lowered)
            if m:
                count, sides = int(m.group(1)), int(m.group(2))
            else:
                m2 = re.search(r"\bd\s*(\d+)\b", lowered)
                if m2:
                    sides = int(m2.group(1))
            return [
                {
                    "id": "alias-dice-0",
                    "function": {
                        "name": "roll_dice",
                        "arguments": json.dumps({"sides": sides, "count": count}),
                    },
                }
            ]

        # Fuzzy tool-name fallback for token-like hallucinations.
        names = list(self.tools.keys())
        if names and len(compact) <= 40:
            guess = difflib.get_close_matches(bare, names, n=1, cutoff=0.6)
            if guess:
                return [
                    {
                        "id": f"fuzzy-{guess[0]}-0",
                        "function": {"name": guess[0], "arguments": "{}"},
                    }
                ]
        return []

    def _direct_tool_calls_from_user(self, messages: list[dict]) -> list[dict]:
        """Deterministic intent routing for common voice utterances."""
        if not messages:
            return []
        user_text = ""
        for m in reversed(messages):
            if str(m.get("role", "")).strip().lower() == "user":
                user_text = str(m.get("content", "")).strip().lower()
                break
        if not user_text:
            return []

        if "what time" in user_text or "current time" in user_text:
            return [{"id": "direct-time-0", "function": {"name": "get_current_time", "arguments": "{}"}}]
        if "what date" in user_text or "current date" in user_text:
            return [{"id": "direct-date-0", "function": {"name": "get_current_date", "arguments": "{}"}}]
        if "flip a coin" in user_text or "coin flip" in user_text:
            return [{"id": "direct-coin-0", "function": {"name": "flip_coin", "arguments": "{}"}}]
        if "what lists do you have" in user_text or "list all lists" in user_text:
            return [{"id": "direct-lists-0", "function": {"name": "list_all_lists", "arguments": "{}"}}]
        if "list timers" in user_text or "active timers" in user_text:
            return [{"id": "direct-timers-0", "function": {"name": "list_timers", "arguments": "{}"}}]
        remember_match = re.search(
            r"\bremember(?:\s+that)?\s+(?:my\s+)?([a-z0-9_ ]{2,40}?)\s+is\s+(.+)$",
            user_text,
        )
        if remember_match:
            key = remember_match.group(1).strip().replace(" ", "_")
            value = remember_match.group(2).strip().strip(".!?")
            if key and value:
                return [
                    {
                        "id": "direct-remember-0",
                        "function": {
                            "name": "remember",
                            "arguments": json.dumps({"key": key, "value": value}),
                        },
                    }
                ]
        recall_match = re.search(
            r"\b(?:what\s+is|recall)\s+(?:my\s+)?([a-z0-9_ ]{2,40})\??$",
            user_text,
        )
        if recall_match:
            key = recall_match.group(1).strip().replace(" ", "_")
            if key:
                return [
                    {
                        "id": "direct-recall-0",
                        "function": {
                            "name": "recall",
                            "arguments": json.dumps({"key": key}),
                        },
                    }
                ]
        cancel_match = re.search(r"cancel\s+timer\s+#?(\d+)", user_text)
        if cancel_match:
            return [
                {
                    "id": "direct-cancel-timer-0",
                    "function": {
                        "name": "cancel_timer",
                        "arguments": json.dumps({"timer_id": cancel_match.group(1)}),
                    },
                }
            ]
        timer_match = re.search(
            r"(?:set\s+)?(?:a\s+)?timer(?:\s+for)?\s+(\d+)\s*(?:s|sec|secs|second|seconds)\b",
            user_text,
        )
        if timer_match:
            return [
                {
                    "id": "direct-set-timer-0",
                    "function": {
                        "name": "set_timer",
                        "arguments": json.dumps({"seconds": int(timer_match.group(1))}),
                    },
                }
            ]

        dm = re.search(r"\b(\d+)\s*d\s*(\d+)(?:s)?\b", user_text)
        if dm:
            count = int(dm.group(1))
            sides = int(dm.group(2))
            return [
                {
                    "id": "direct-dice-0",
                    "function": {
                        "name": "roll_dice",
                        "arguments": json.dumps({"sides": sides, "count": count}),
                    },
                }
            ]
        return []

    def close(self) -> None:
        return None

    def __enter__(self) -> "LocalLlamaCppClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        self.close()
        return False


class LocalServerClient:
    """OpenAI-compatible local server client (e.g. llama-server)."""

    supports_tools = True
    provider_name = "local_server"

    def __init__(
        self,
        *,
        model: str,
        base_url: str,
        api_key: Optional[str] = None,
        enable_thinking: bool = False,
        timeout: float = 60.0,
    ) -> None:
        import datetime as _dt
        _now = _dt.datetime.now().astimezone()
        self._launch_time_context = (
            f"Current date and time: {_now.strftime('%A, %B %d, %Y %I:%M %p')} "
            f"{_now.strftime('%Z')}"
        )
        self.model = model
        self.base_url = self._normalize_base_url(base_url)
        self.api_key = api_key or os.getenv("TALKBOT_LOCAL_SERVER_API_KEY")
        self.enable_thinking = enable_thinking
        self.client = httpx.Client(timeout=timeout)

        self.tools: dict[str, Callable] = {}
        self.tool_definitions: list[dict] = []
        self.last_usage: dict = {}

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        url = (base_url or "").strip().rstrip("/")
        if not url:
            raise LLMProviderError(
                "Local server URL is empty. Set TALKBOT_LOCAL_SERVER_URL."
            )
        if not url.endswith("/v1"):
            url = f"{url}/v1"
        return url

    def _prepare_messages(self, messages: list[dict]) -> list[dict]:
        prepared: list[dict] = []
        has_system = False
        for m in messages:
            role = str(m.get("role", "user")).strip().lower()
            content = str(m.get("content", "")).strip()
            if not content:
                continue
            if role == "system":
                has_system = True
                # Prepend current date/time so model doesn't guess from training data
                content = f"{self._launch_time_context}\n\n{content}"
            elif role == "user" and not self.enable_thinking:
                if not content.startswith("/no_think"):
                    content = f"/no_think\n{content}\n/no_think"
            prepared.append({"role": role, "content": content})
        if not self.enable_thinking and not has_system:
            prepared.insert(0, {"role": "system", "content": f"{self._launch_time_context}\n\n{NO_THINK_INSTRUCTION}"})
        return prepared

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def register_tool(
        self, name: str, func: Callable, description: str, parameters: dict
    ) -> None:
        self.tools[name] = func
        self.tool_definitions.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            }
        )

    def clear_tools(self) -> None:
        self.tools.clear()
        self.tool_definitions.clear()

    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        include_tools: bool = True,
    ) -> dict:
        payload: dict = {
            "model": self.model,
            "messages": self._prepare_messages(messages),
            "temperature": temperature,
            "stream": stream,
        }
        if not self.enable_thinking:
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        if max_tokens:
            payload["max_tokens"] = int(max_tokens)
        if include_tools and self.tool_definitions:
            payload["tools"] = self.tool_definitions
            payload["tool_choice"] = "auto"

        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            self.last_usage = data.get("usage") or {}
            return data
        except httpx.HTTPError as e:
            raise LLMProviderError(f"Local server request failed: {e}") from e

    def chat_with_tools(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        max_tool_calls: int = 10,
    ) -> str:
        if not self.tools:
            response = self.chat_completion(messages, temperature, max_tokens)
            return _response_content(response)

        current_messages = messages.copy()
        tool_call_count = 0
        executed_tool_summaries: list[str] = []
        executed_call_results: dict[str, str] = {}  # call_key -> result (dedup)
        while tool_call_count < max_tool_calls:
            try:
                response = self.chat_completion(current_messages, temperature, max_tokens)
            except LLMProviderError:
                if executed_tool_summaries:
                    fallback_messages = [
                        m for m in current_messages if m.get("role") != "tool"
                    ]
                    fallback_messages.append(
                        {
                            "role": "user",
                            "content": "Use these tool results to answer:\n"
                            + "\n".join(executed_tool_summaries),
                        }
                    )
                    response = self.chat_completion(
                        fallback_messages,
                        temperature,
                        max_tokens,
                        include_tools=False,
                    )
                    return _response_content(response)
                response = self.chat_completion(
                    current_messages, temperature, max_tokens, include_tools=False
                )
                return _response_content(response)
            message = _response_message(response)
            if not message:
                return _response_content(response)
            content = _response_content(response)
            tool_calls = message.get("tool_calls") or self._extract_tag_tool_calls(content)
            # Fallback: bare tool name (e.g. "list_timers" or "list_timers()")
            if not tool_calls:
                name_candidate = content.strip().rstrip("()")
                if name_candidate in self.tools and content.strip() in (
                    name_candidate, f"{name_candidate}()"
                ):
                    tool_calls = [
                        {
                            "id": f"plain-{name_candidate}-0",
                            "function": {"name": name_candidate, "arguments": "{}"},
                        }
                    ]
            # Fallback: Python-style call syntax (e.g. add_to_list(item="x", list_name="y"))
            if not tool_calls:
                tool_calls = self._extract_python_style_tool_calls(content)
            if not tool_calls:
                return message.get("content", "")

            current_messages.append(message)
            any_new_calls = False
            for tool_call in tool_calls:
                tool_call_count += 1
                function_name = tool_call["function"]["name"]
                try:
                    function_args = json.loads(tool_call["function"]["arguments"])
                except Exception:
                    function_args = {}
                function_args = _normalize_tool_args_for_call(function_name, function_args)
                call_key = f"{function_name}|{json.dumps(function_args, sort_keys=True)}"
                if call_key in executed_call_results:
                    # Duplicate — replay original result to keep history valid, don't re-execute
                    current_messages.append(
                        {
                            "tool_call_id": tool_call["id"],
                            "role": "tool",
                            "name": function_name,
                            "content": executed_call_results[call_key],
                        }
                    )
                    continue
                any_new_calls = True
                if function_name in self.tools:
                    try:
                        result = self.tools[function_name](**function_args)
                    except Exception as e:
                        result = f"Error executing {function_name}: {e}"
                else:
                    result = f"Error: Tool {function_name} not found"
                executed_call_results[call_key] = str(result)
                executed_tool_summaries.append(
                    f"{function_name}({function_args}) -> {result}"
                )
                current_messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    }
                )
            if not any_new_calls:
                # Every call in this batch was a duplicate — stop looping
                break

        response = self.chat_completion(
            current_messages, temperature, max_tokens, include_tools=False
        )
        final_text = _response_content(response).strip()
        # If the model still outputs a tool-call pattern (can't escape it), return
        # the accumulated tool results instead of the raw function-call text.
        if executed_tool_summaries and (
            self._extract_python_style_tool_calls(final_text)
            or final_text.strip().rstrip("()") in self.tools
        ):
            return "\n".join(s.split(" -> ", 1)[-1] for s in executed_tool_summaries)
        return final_text

    def _extract_python_style_tool_calls(self, content: str) -> list[dict]:
        """Fallback for models that output tool calls as Python-style calls: name(k="v", ...)."""
        if not content:
            return []
        tool_calls: list[dict] = []
        # Match: known_tool_name(arg=val, ...)
        pattern = re.compile(r'\b(\w+)\s*\(([^)]*)\)')
        for idx, match in enumerate(pattern.finditer(content)):
            name = match.group(1)
            if name not in self.tools:
                continue
            args_str = match.group(2).strip()
            args: dict = {}
            for kv in re.finditer(
                r'(\w+)\s*=\s*(?:"([^"]*?)"|\'([^\']*?)\'|([\w.+-]+))', args_str
            ):
                key = kv.group(1)
                val: object = (
                    kv.group(2) if kv.group(2) is not None
                    else kv.group(3) if kv.group(3) is not None
                    else kv.group(4) or ""
                )
                try:
                    val = int(val)  # type: ignore[arg-type]
                except (ValueError, TypeError):
                    try:
                        val = float(val)  # type: ignore[arg-type]
                    except (ValueError, TypeError):
                        pass
                args[key] = val
            tool_calls.append({
                "id": f"pyfunc-{idx}",
                "function": {"name": name, "arguments": json.dumps(args)},
            })
        return tool_calls

    @staticmethod
    def _extract_tag_tool_calls(content: str) -> list[dict]:
        """Fallback parser for models that emit <tool_call>{...}</tool_call> text."""
        if not content:
            return []
        matches = re.findall(
            r"<tool_call>\s*(\{.*?\})\s*</tool_call>", content, flags=re.DOTALL
        )
        tool_calls: list[dict] = []
        for idx, block in enumerate(matches):
            try:
                payload = json.loads(block)
            except Exception:
                continue
            name = str(payload.get("name", "")).strip()
            args = payload.get("arguments", {})
            if not name:
                continue
            if not isinstance(args, dict):
                args = {}
            tool_calls.append(
                {
                    "id": f"text-tool-{idx}",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(args),
                    },
                }
            )
        return tool_calls

    def simple_chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        response = self.chat_completion(messages)
        return _response_content(response)

    def chat_with_system_tools(
        self, message: str, system_prompt: Optional[str] = None
    ) -> str:
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        return self.chat_with_tools(messages)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "LocalServerClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        self.close()
        return False


def create_llm_client(
    *,
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    site_url: Optional[str] = None,
    site_name: Optional[str] = None,
    local_model_path: Optional[str] = None,
    llamacpp_bin: Optional[str] = None,
    local_server_url: Optional[str] = None,
    local_server_api_key: Optional[str] = None,
    enable_thinking: bool = False,
) -> LLMClient:
    """Create provider-specific LLM client."""
    provider = (provider or "local").strip().lower()
    if provider == "local":
        local_path = local_model_path or os.getenv("TALKBOT_LOCAL_MODEL_PATH")
        if not local_path:
            default_path = Path("models/default.gguf")
            if default_path.exists():
                local_path = str(default_path)
        if local_path:
            _path_lower = local_path.lower()
            _env_n_ctx = os.getenv("TALKBOT_LOCAL_N_CTX", "").strip()
            if _env_n_ctx:
                try:
                    n_ctx = max(512, int(_env_n_ctx))
                except ValueError:
                    n_ctx = 2048
            else:
                # Auto-select based on model size detected from path.
                # Benchmark sweep: qwen3-1.7b peaks at 2048, qwen3-8b at 4096.
                if any(t in _path_lower for t in ("8b", "13b", "14b", "32b", "70b")):
                    n_ctx = 4096
                else:
                    n_ctx = 2048
            _env_routing = os.getenv("TALKBOT_LOCAL_DIRECT_TOOL_ROUTING", "").strip()
            if _env_routing:
                _direct_routing: Optional[bool] = _env_routing.lower() in {"1", "true", "yes", "on"}
            else:
                # Benchmark A/B: intent routing helps 8b+ models (+14% success),
                # hurts small models like 1.7b (-14%). Auto-select by size.
                _direct_routing = any(t in _path_lower for t in ("8b", "13b", "14b", "32b", "70b"))
            return LocalLlamaCppClient(
                model_path=local_path,
                binary=llamacpp_bin or os.getenv("TALKBOT_LLAMACPP_BIN", "llama-cli"),
                n_ctx=n_ctx,
                enable_thinking=enable_thinking,
                direct_tool_routing=_direct_routing,
            )
        raise LLMProviderError(
            "Local provider selected but TALKBOT_LOCAL_MODEL_PATH is not set. "
            "Project default is ./models/default.gguf."
        )

    if provider == "openrouter":
        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise LLMProviderError(
                "OpenRouter provider selected but OPENROUTER_API_KEY is not set."
            )
        client = OpenRouterClient(
            api_key=api_key, model=model, site_url=site_url, site_name=site_name
        )
        client.provider_name = "openrouter"
        client.supports_tools = True
        return client

    if provider == "local_server":
        server_url = (
            local_server_url
            or os.getenv("TALKBOT_LOCAL_SERVER_URL")
            or "http://127.0.0.1:8000/v1"
        )
        # Explicit model param wins (GUI selection); fall back to env var, then local path
        server_model = model or (os.getenv("TALKBOT_LOCAL_SERVER_MODEL") or "").strip()
        if not server_model:
            local_path = local_model_path or os.getenv("TALKBOT_LOCAL_MODEL_PATH", "")
            server_model = local_path.strip()
        return LocalServerClient(
            model=server_model,
            base_url=server_url,
            api_key=local_server_api_key,
            enable_thinking=enable_thinking,
        )

    raise LLMProviderError(
        f"Unknown provider '{provider}'. Expected one of: local, local_server, openrouter."
    )


def supports_tools(client) -> bool:
    """Return whether provider supports function/tool loop semantics."""
    return bool(getattr(client, "supports_tools", hasattr(client, "register_tool")))
