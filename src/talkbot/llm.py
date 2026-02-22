"""LLM provider abstraction with local llama.cpp and OpenRouter backends."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

from talkbot.openrouter import OpenRouterClient


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
        enable_thinking: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> None:
        self.model_path = model_path
        self.binary = binary
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.enable_thinking = enable_thinking
        self._llm = None
        self._use_python_backend = False

        if not Path(model_path).exists():
            raise LLMProviderError(
                f"Local model not found at '{model_path}'. "
                "Set TALKBOT_LOCAL_MODEL_PATH to a local GGUF path."
            )

        # Prefer python bindings (no external llama-cli dependency required).
        try:
            from llama_cpp import Llama  # type: ignore

            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                verbose=False,
            )
            self._use_python_backend = True
            return
        except Exception:
            self._llm = None
            self._use_python_backend = False

    def _messages_to_prompt(self, messages: list[dict]) -> str:
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
                if not self.enable_thinking and not content.startswith("/no_think"):
                    content = f"/no_think\n{content}"
                lines.append(f"User: {content}")
        lines.append("Assistant:")
        return "\n".join(lines)

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
                f"llama.cpp binary '{self.binary}' not found, and llama-cpp-python is unavailable. "
                "Install one of: `uv tool install talkbot --with llama-cpp-python` "
                "or system llama.cpp (`llama-cli`)."
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
        if self._use_python_backend and self._llm is not None:
            tokens = int(max_tokens or self.max_tokens)
            try:
                response = self._llm.create_chat_completion(
                    messages=messages,
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

        prompt = self._messages_to_prompt(messages)
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


def create_llm_client(
    *,
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    site_url: Optional[str] = None,
    site_name: Optional[str] = None,
    local_model_path: Optional[str] = None,
    llamacpp_bin: Optional[str] = None,
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
            return LocalLlamaCppClient(
                model_path=local_path,
                binary=llamacpp_bin or os.getenv("TALKBOT_LLAMACPP_BIN", "llama-cli"),
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

    raise LLMProviderError(
        f"Unknown provider '{provider}'. Expected one of: local, openrouter."
    )


def supports_tools(client) -> bool:
    """Return whether provider supports function/tool loop semantics."""
    return bool(getattr(client, "supports_tools", hasattr(client, "register_tool")))
