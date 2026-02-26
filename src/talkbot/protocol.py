"""Protocol definitions for TalkBot LLM clients."""

from typing import Any, Callable, Optional, Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for LLM clients indicating support for tools and unified chat methods."""

    supports_tools: bool
    provider_name: str
    last_usage: dict[str, Any]

    def register_tool(
        self, name: str, func: Callable[..., Any], description: str, parameters: dict[str, Any]
    ) -> None:
        """Register a tool/function that the LLM can call."""
        ...

    def clear_tools(self) -> None:
        """Clear all registered tools."""
        ...

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Send a basic chat completion request without executing tools."""
        ...

    def simple_chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Send a simple chat message (no tool execution)."""
        ...

    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_tool_calls: int = 10,
    ) -> str:
        """Chat with automatic tool execution."""
        ...

    def chat_with_system_tools(
        self, message: str, system_prompt: Optional[str] = None
    ) -> str:
        """Chat with system tools enabled."""
        ...

    def close(self) -> None:
        """Close the client and clean up resources."""
        ...

    def __enter__(self) -> "LLMClient":
        ...

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        ...
