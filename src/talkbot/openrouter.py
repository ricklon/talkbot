"""OpenRouter API client for the talking bot with tool support."""

import json
import os
import re
from typing import Any, Callable, Optional

import httpx

from talkbot.protocol import LLMClient


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
    if not isinstance(function_args, dict):
        return {}
    args = dict(function_args)
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
    for alias, canonical in alias_map.get(function_name, {}).items():
        if canonical in args and alias in args:
            args.pop(alias, None)
    return args


_MODEL_TOOL_SUPPORT_CACHE: dict[str, bool] = {}


class OpenRouterClient:
    """Client for interacting with OpenRouter API with tool support."""

    supports_tools: bool = True
    provider_name: str = "openrouter"

    BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = "openai/gpt-3.5-turbo"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
    ):
        """Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key. If not provided, reads from OPENROUTER_API_KEY env var.
            model: Model to use for completions. Defaults to gpt-3.5-turbo.
            site_url: Your site's URL for OpenRouter rankings.
            site_name: Your site's name for OpenRouter rankings.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
            )

        self.model = model
        self.site_url = site_url or os.getenv("OPENROUTER_SITE_URL", "")
        self.site_name = site_name or os.getenv("OPENROUTER_SITE_NAME", "TalkBot")
        self.client = httpx.Client(timeout=60.0)

        # Tool registry
        self.tools: dict[str, Callable] = {}
        self.tool_definitions: list[dict] = []
        self.last_usage: dict = {}
        self._native_tools_supported: Optional[bool] = None

    def register_tool(
        self, name: str, func: Callable, description: str, parameters: dict
    ) -> None:
        """Register a tool/function that the LLM can call.

        Args:
            name: Tool name (must be unique)
            func: Function to call
            description: Description of what the tool does
            parameters: JSON Schema for parameters
        """
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
        """Clear all registered tools."""
        self.tools.clear()
        self.tool_definitions.clear()

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
        }
        return {k: v for k, v in headers.items() if v}

    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> dict:
        """Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens to generate.
            stream: Whether to stream the response.

        Returns:
            The full API response dictionary.
        """
        return self._request_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            include_tools=True,
        )

    def _request_completion(
        self,
        *,
        messages: list[dict],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool,
        include_tools: bool,
    ) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if include_tools and self.tool_definitions:
            payload["tools"] = self.tool_definitions
            payload["tool_choice"] = "auto"
        response = self.client.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self._get_headers(),
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        self.last_usage = data.get("usage") or {}
        return data

    @staticmethod
    def _tool_transport_mode() -> str:
        raw = os.getenv("TALKBOT_OPENROUTER_TOOL_TRANSPORT", "auto").strip().lower()
        if raw in {"prompt", "prompt_xml", "xml"}:
            return "prompt"
        if raw in {"native", "openai"}:
            return "native"
        return "auto"

    @staticmethod
    def _tool_prefight_enabled() -> bool:
        raw = os.getenv("TALKBOT_OPENROUTER_TOOL_PREFLIGHT", "1").strip().lower()
        return raw in {"1", "true", "yes", "on"}

    def _detect_native_tool_support(self) -> Optional[bool]:
        model_key = str(self.model or "").strip()
        if not model_key:
            return None
        if model_key in _MODEL_TOOL_SUPPORT_CACHE:
            return _MODEL_TOOL_SUPPORT_CACHE[model_key]
        try:
            response = self.client.get(
                f"{self.BASE_URL}/models",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            payload = response.json()
            models = payload.get("data")
            if not isinstance(models, list):
                return None
            wanted = {
                model_key.lower(),
                model_key.split(":")[0].lower(),
            }
            for entry in models:
                if not isinstance(entry, dict):
                    continue
                entry_id = str(entry.get("id") or "").lower()
                canonical = str(entry.get("canonical_slug") or "").lower()
                if entry_id not in wanted and canonical not in wanted:
                    continue
                supported = entry.get("supported_parameters")
                if not isinstance(supported, list):
                    return None
                support_set = {str(item).strip().lower() for item in supported}
                supports = "tools" in support_set and "tool_choice" in support_set
                _MODEL_TOOL_SUPPORT_CACHE[model_key] = supports
                return supports
        except Exception:
            return None
        return None

    def _should_use_prompt_tool_transport(self) -> bool:
        mode = self._tool_transport_mode()
        if mode == "prompt":
            return True
        if mode == "native":
            return False
        if self._native_tools_supported is False:
            return True
        if self._tool_prefight_enabled():
            support = self._detect_native_tool_support()
            if support is False:
                self._native_tools_supported = False
                return True
            if support is True:
                self._native_tools_supported = True
        return False

    @staticmethod
    def _is_native_tool_unsupported_error(exc: Exception) -> bool:
        if not isinstance(exc, httpx.HTTPStatusError):
            return False
        response = exc.response
        if response is None:
            return False
        if response.status_code not in {400, 404}:
            return False
        body = response.text.lower()
        if "no endpoints found that support tool use" in body:
            return True
        if "support tool use" in body and "endpoint" in body:
            return True
        if "tool_choice" in body and "unsupported" in body:
            return True
        return False

    def _tool_catalog_for_prompt(self) -> str:
        tools_payload = []
        for entry in self.tool_definitions:
            function = entry.get("function") if isinstance(entry, dict) else None
            if not isinstance(function, dict):
                continue
            tools_payload.append(
                {
                    "name": function.get("name"),
                    "description": function.get("description"),
                    "parameters": function.get("parameters"),
                }
            )
        return json.dumps(tools_payload, ensure_ascii=True)

    def _prompt_tool_instruction(self) -> str:
        return (
            "Native tool calling is unavailable for this model route.\n"
            "Use XML tool tags exactly when a tool is needed:\n"
            "<tool_call>{\"name\":\"TOOL_NAME\",\"arguments\":{...}}</tool_call>\n"
            "After receiving a <tool_response> message, answer the user normally.\n"
            "If no tool is needed, answer normally with no tool tag.\n"
            f"Available tools: {self._tool_catalog_for_prompt()}"
        )

    @staticmethod
    def _extract_prompt_tool_call(content: str) -> Optional[dict[str, Any]]:
        text = str(content or "")
        match = re.search(r"<tool_call>\s*(.*?)\s*</tool_call>", text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return None
        payload = match.group(1).strip()
        if payload.startswith("```"):
            payload = payload.strip("`")
            payload = payload.replace("json", "", 1).strip()
        try:
            data = json.loads(payload)
        except Exception:
            return None
        if not isinstance(data, dict):
            return None
        function_name = str(data.get("name") or "").strip()
        args = data.get("arguments")
        if not function_name:
            return None
        if not isinstance(args, dict):
            args = {}
        return {"name": function_name, "arguments": args}

    def _chat_with_prompt_tools(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: Optional[int],
        max_tool_calls: int,
    ) -> str:
        current_messages = [{"role": "system", "content": self._prompt_tool_instruction()}]
        current_messages.extend(messages)
        tool_calls = 0
        while tool_calls < max_tool_calls:
            response = self._request_completion(
                messages=current_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                include_tools=False,
            )
            content = _response_content(response)
            parsed = self._extract_prompt_tool_call(content)
            if not parsed:
                # Mistral-family models may ignore the XML prompt and emit [TOOL_CALLS] anyway.
                bracket = self._extract_bracket_tool_calls(content)
                if bracket:
                    tc = bracket[0]
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except Exception:
                        args = {}
                    parsed = {"name": tc["function"]["name"], "arguments": args}
            if not parsed:
                return content

            function_name = parsed["name"]
            function_args = _normalize_tool_args_for_call(function_name, parsed["arguments"])
            if function_name in self.tools:
                try:
                    result = self.tools[function_name](**function_args)
                except Exception as exc:
                    result = f"Error executing {function_name}: {exc}"
            else:
                result = f"Error: Tool {function_name} not found"

            tool_calls += 1
            current_messages.append({"role": "assistant", "content": content})
            tool_payload = {
                "name": function_name,
                "arguments": function_args,
                "result": str(result),
            }
            current_messages.append(
                {
                    "role": "user",
                    "content": f"<tool_response>{json.dumps(tool_payload, ensure_ascii=True)}</tool_response>",
                }
            )

        response = self._request_completion(
            messages=current_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            include_tools=False,
        )
        return _response_content(response)

    @staticmethod
    def _extract_bracket_tool_calls(content: str) -> list[dict]:
        """Fallback for Mistral-family models that emit [TOOL_CALLS] as plain text content.

        OpenRouter usually normalizes this, but some model routes pass it through raw.
        Handles: [TOOL_CALLS][{...}]  and  [TOOL_CALLS] [{...}, ...]
        """
        if not content or "[TOOL_CALLS]" not in content:
            return []
        tool_calls: list[dict] = []
        decoder = json.JSONDecoder()
        for idx, match in enumerate(re.finditer(r"\[TOOL_CALLS\]\s*", content)):
            remainder = content[match.end():]
            if not remainder or remainder[0] not in ("[", "{"):
                continue
            try:
                obj, _ = decoder.raw_decode(remainder)
            except (json.JSONDecodeError, ValueError):
                continue
            calls = obj if isinstance(obj, list) else [obj]
            for call_idx, call in enumerate(calls):
                if not isinstance(call, dict):
                    continue
                name = str(call.get("name", "")).strip()
                if not name:
                    continue
                args = call.get("arguments", {})
                if not isinstance(args, dict):
                    args = {}
                tool_calls.append({
                    "id": f"bracket-{idx}-{call_idx}",
                    "function": {"name": name, "arguments": json.dumps(args)},
                })
        return tool_calls

    def _chat_with_native_tools(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: Optional[int],
        max_tool_calls: int,
    ) -> str:
        tool_call_count = 0
        current_messages = messages.copy()

        while tool_call_count < max_tool_calls:
            response = self.chat_completion(current_messages, temperature, max_tokens)
            message = _response_message(response)
            if not message:
                return _response_content(response)

            content = _response_content(response)
            native_tool_calls = message.get("tool_calls")
            bracket_tool_calls = self._extract_bracket_tool_calls(content) if not native_tool_calls else []
            tool_calls = native_tool_calls or bracket_tool_calls
            if not tool_calls:
                return content

            # If tool calls came from bracket extraction (not native API), inject them
            # into the message so tool response messages have valid tool_call_id refs.
            if bracket_tool_calls:
                message = dict(message)
                message["tool_calls"] = [
                    {"id": tc["id"], "type": "function", "function": tc["function"]}
                    for tc in bracket_tool_calls
                ]
            current_messages.append(message)
            for tool_call in tool_calls:
                tool_call_count += 1
                function_name = tool_call["function"]["name"]
                try:
                    function_args = json.loads(tool_call["function"]["arguments"])
                except Exception:
                    function_args = {}
                function_args = _normalize_tool_args_for_call(function_name, function_args)

                if function_name in self.tools:
                    try:
                        result = self.tools[function_name](**function_args)
                    except Exception as exc:
                        result = f"Error executing {function_name}: {str(exc)}"
                else:
                    result = f"Error: Tool {function_name} not found"

                current_messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    }
                )

        response = self.chat_completion(current_messages, temperature, max_tokens)
        return _response_content(response)

    def chat_with_tools(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        max_tool_calls: int = 10,
    ) -> str:
        """Chat with automatic tool execution.

        Args:
            messages: List of message dicts.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            max_tool_calls: Maximum number of tool call iterations.

        Returns:
            The final response text.
        """
        if not self.tools:
            # No tools registered, do simple completion
            response = self.chat_completion(messages, temperature, max_tokens)
            return _response_content(response)
        mode = self._tool_transport_mode()
        if mode == "native" and self._tool_prefight_enabled():
            support = self._detect_native_tool_support()
            if support is False:
                raise RuntimeError(
                    "OpenRouter model route does not advertise native tool calling "
                    "(tools/tool_choice). Set TALKBOT_OPENROUTER_TOOL_TRANSPORT=prompt "
                    "to allow prompt-tool fallback."
                )
        if self._should_use_prompt_tool_transport():
            return self._chat_with_prompt_tools(messages, temperature, max_tokens, max_tool_calls)
        try:
            return self._chat_with_native_tools(messages, temperature, max_tokens, max_tool_calls)
        except Exception as exc:
            if self._is_native_tool_unsupported_error(exc):
                self._native_tools_supported = False
                if mode == "auto":
                    return self._chat_with_prompt_tools(
                        messages,
                        temperature,
                        max_tokens,
                        max_tool_calls,
                    )
            raise

    def simple_chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Send a simple chat message.

        Args:
            message: The user's message.
            system_prompt: Optional system prompt to set context.

        Returns:
            The AI's response.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        return _response_content(self.chat_completion(messages))

    def chat_with_system_tools(
        self, message: str, system_prompt: Optional[str] = None
    ) -> str:
        """Chat with system tools enabled.

        Args:
            message: The user's message.
            system_prompt: Optional system prompt.

        Returns:
            The AI's response with tool execution.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        return self.chat_with_tools(messages)

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self) -> "OpenRouterClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Context manager exit."""
        self.close()
        return False
