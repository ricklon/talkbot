"""OpenRouter API client for the talking bot with tool support."""

import json
import os
from typing import Any, Callable, Optional

import httpx


class OpenRouterClient:
    """Client for interacting with OpenRouter API with tool support."""

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
        temperature: float = 0.7,
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
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        # Add tools if registered
        if self.tool_definitions:
            payload["tools"] = self.tool_definitions
            payload["tool_choice"] = "auto"

        response = self.client.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self._get_headers(),
            json=payload,
        )
        response.raise_for_status()

        return response.json()

    def chat_with_tools(
        self,
        messages: list[dict],
        temperature: float = 0.7,
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
            return response["choices"][0]["message"]["content"]

        tool_call_count = 0
        current_messages = messages.copy()

        while tool_call_count < max_tool_calls:
            response = self.chat_completion(current_messages, temperature, max_tokens)
            message = response["choices"][0]["message"]

            # Check if the model wants to call tools
            tool_calls = message.get("tool_calls")
            if not tool_calls:
                # No tool calls, return the content
                return message.get("content", "")

            # Add assistant message to conversation
            current_messages.append(message)

            # Execute tool calls
            for tool_call in tool_calls:
                tool_call_count += 1
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                if function_name in self.tools:
                    try:
                        result = self.tools[function_name](**function_args)
                    except Exception as e:
                        result = f"Error executing {function_name}: {str(e)}"
                else:
                    result = f"Error: Tool {function_name} not found"

                # Add tool response
                current_messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    }
                )

        # Max tool calls reached, get final response
        response = self.chat_completion(current_messages, temperature, max_tokens)
        return response["choices"][0]["message"].get("content", "")

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

        return self.chat_completion(messages)["choices"][0]["message"]["content"]

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

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
