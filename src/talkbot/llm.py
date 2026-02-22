"""LLM provider abstraction with local llama.cpp and OpenRouter backends."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Optional

import httpx
from talkbot.openrouter import OpenRouterClient
from talkbot.thinking import NO_THINK_INSTRUCTION


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider cannot be initialized or used."""


class LocalLlamaCppClient:
    """Non-server local client using llama.cpp CLI."""

    supports_tools = False
    provider_name = "local"

    def __init__(
        self,
        *,
        model_path: str,
        binary: str = "llama-cli",
        n_ctx: int = 2048,
        enable_thinking: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> None:
        self.model_path = model_path
        self.binary = binary
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.enable_thinking = enable_thinking
        self.n_ctx = int(n_ctx)
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
                    content = f"/no_think\n{content}"
            prepared.append({"role": role, "content": content})

        if not self.enable_thinking and not has_system:
            prepared.insert(0, {"role": "system", "content": NO_THINK_INSTRUCTION})
        return prepared

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
        ]
        try:
            proc = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
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

        return proc.stdout.strip()

    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
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
            content = (
                response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            return {"choices": [{"message": {"content": content}}]}

        prompt = self._messages_to_prompt(prepared_messages)
        content = self._run_prompt(prompt, max_tokens=max_tokens)
        return {"choices": [{"message": {"content": content}}]}

    def simple_chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        return self.chat_completion(messages)["choices"][0]["message"]["content"]

    def chat_with_system_tools(
        self, message: str, system_prompt: Optional[str] = None
    ) -> str:
        # Local backend currently has no native tools loop; fallback to normal chat.
        return self.simple_chat(message, system_prompt=system_prompt)

    def chat_with_tools(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_tool_calls: int = 10,
    ) -> str:
        del max_tool_calls
        response = self.chat_completion(
            messages, temperature=temperature, max_tokens=max_tokens
        )
        return response["choices"][0]["message"].get("content", "")

    def register_tool(self, *args, **kwargs) -> None:
        # Supported for compatibility; no-op in local mode.
        del args, kwargs

    def close(self) -> None:
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
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
        self.model = model
        self.base_url = self._normalize_base_url(base_url)
        self.api_key = api_key or os.getenv("TALKBOT_LOCAL_SERVER_API_KEY")
        self.enable_thinking = enable_thinking
        self.client = httpx.Client(timeout=timeout)

        self.tools: dict[str, Callable] = {}
        self.tool_definitions: list[dict] = []

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
            elif role == "user" and not self.enable_thinking:
                if not content.startswith("/no_think"):
                    content = f"/no_think\n{content}"
            prepared.append({"role": role, "content": content})
        if not self.enable_thinking and not has_system:
            prepared.insert(0, {"role": "system", "content": NO_THINK_INSTRUCTION})
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
        temperature: float = 0.7,
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
            return response.json()
        except httpx.HTTPError as e:
            raise LLMProviderError(f"Local server request failed: {e}") from e

    def chat_with_tools(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_tool_calls: int = 10,
    ) -> str:
        if not self.tools:
            response = self.chat_completion(messages, temperature, max_tokens)
            return response["choices"][0]["message"].get("content", "")

        current_messages = messages.copy()
        tool_call_count = 0
        executed_tool_summaries: list[str] = []
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
                    return response["choices"][0]["message"].get("content", "")
                response = self.chat_completion(
                    current_messages, temperature, max_tokens, include_tools=False
                )
                return response["choices"][0]["message"].get("content", "")
            message = response["choices"][0]["message"]
            tool_calls = message.get("tool_calls") or self._extract_tag_tool_calls(
                message.get("content", "")
            )
            if not tool_calls:
                return message.get("content", "")

            current_messages.append(message)
            for tool_call in tool_calls:
                tool_call_count += 1
                function_name = tool_call["function"]["name"]
                try:
                    function_args = json.loads(tool_call["function"]["arguments"])
                except Exception:
                    function_args = {}
                if function_name in self.tools:
                    try:
                        result = self.tools[function_name](**function_args)
                    except Exception as e:
                        result = f"Error executing {function_name}: {e}"
                else:
                    result = f"Error: Tool {function_name} not found"
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

        response = self.chat_completion(
            current_messages, temperature, max_tokens, include_tools=False
        )
        return response["choices"][0]["message"].get("content", "")

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
        return response["choices"][0]["message"].get("content", "")

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
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
):
    """Create provider-specific LLM client."""
    provider = (provider or "local").strip().lower()
    if provider == "local":
        local_path = local_model_path or os.getenv("TALKBOT_LOCAL_MODEL_PATH")
        if not local_path:
            default_path = Path("models/default.gguf")
            if default_path.exists():
                local_path = str(default_path)
        if local_path:
            try:
                n_ctx = int(os.getenv("TALKBOT_LOCAL_N_CTX", "2048"))
            except ValueError:
                n_ctx = 2048
            n_ctx = max(512, n_ctx)
            return LocalLlamaCppClient(
                model_path=local_path,
                binary=llamacpp_bin or os.getenv("TALKBOT_LLAMACPP_BIN", "llama-cli"),
                n_ctx=n_ctx,
                enable_thinking=enable_thinking,
            )
        raise LLMProviderError(
            "Local provider selected but TALKBOT_LOCAL_MODEL_PATH is not set. "
            "Project default is ./models/default.gguf."
        )

    if provider == "openrouter":
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
        server_model = (os.getenv("TALKBOT_LOCAL_SERVER_MODEL") or "").strip()
        if not server_model:
            local_path = local_model_path or os.getenv("TALKBOT_LOCAL_MODEL_PATH", "")
            server_model = local_path.strip() or model
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
