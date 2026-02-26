import json
import os

import pytest
import httpx

from talkbot.openrouter import OpenRouterClient


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeHttpClient:
    def __init__(self):
        self.calls = []

    def post(self, url, headers, json):
        self.calls.append({"url": url, "headers": headers, "json": json})
        return FakeResponse({"choices": [{"message": {"content": "ok"}}]})

    def close(self):
        return None


@pytest.fixture(autouse=True)
def _disable_openrouter_tool_preflight(monkeypatch):
    monkeypatch.setenv("TALKBOT_OPENROUTER_TOOL_PREFLIGHT", "0")
    monkeypatch.delenv("TALKBOT_OPENROUTER_TOOL_TRANSPORT", raising=False)


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ValueError):
        OpenRouterClient(api_key=None)


def test_get_headers_include_defaults():
    client = OpenRouterClient(api_key="k")
    headers = client._get_headers()

    assert headers["Authorization"] == "Bearer k"
    assert headers["Content-Type"] == "application/json"
    assert "X-Title" in headers


def test_chat_completion_posts_expected_payload():
    client = OpenRouterClient(api_key="k", model="m")
    fake_http = FakeHttpClient()
    client.client = fake_http
    client.register_tool("echo", lambda text: text, "Echo", {"type": "object"})

    result = client.chat_completion(
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.2,
        max_tokens=20,
    )

    sent = fake_http.calls[0]
    assert sent["url"].endswith("/chat/completions")
    assert sent["json"]["model"] == "m"
    assert sent["json"]["temperature"] == 0.2
    assert sent["json"]["max_tokens"] == 20
    assert sent["json"]["tool_choice"] == "auto"
    assert len(sent["json"]["tools"]) == 1
    assert result["choices"][0]["message"]["content"] == "ok"


def test_chat_with_tools_executes_call_and_returns_followup(monkeypatch):
    client = OpenRouterClient(api_key="k")
    client.register_tool(
        "add", lambda a, b: str(a + b), "Add", {"type": "object", "properties": {}}
    )

    responses = iter(
        [
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "function": {
                                        "name": "add",
                                        "arguments": json.dumps({"a": 2, "b": 3}),
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
            {"choices": [{"message": {"role": "assistant", "content": "done"}}]},
        ]
    )

    captured = []

    def fake_chat_completion(messages, temperature=0.7, max_tokens=None, stream=False):
        captured.append(messages)
        return next(responses)

    monkeypatch.setattr(client, "chat_completion", fake_chat_completion)

    output = client.chat_with_tools([{"role": "user", "content": "sum"}])

    assert output == "done"
    tool_msg = captured[1][-1]
    assert tool_msg["role"] == "tool"
    assert tool_msg["name"] == "add"
    assert tool_msg["content"] == "5"


def test_chat_with_tools_without_registered_tools(monkeypatch):
    client = OpenRouterClient(api_key="k")

    monkeypatch.setattr(
        client,
        "chat_completion",
        lambda *_args, **_kwargs: {
            "choices": [{"message": {"content": "plain response"}}]
        },
    )

    assert client.chat_with_tools([{"role": "user", "content": "hello"}]) == "plain response"


def test_chat_with_tools_handles_empty_choices(monkeypatch):
    client = OpenRouterClient(api_key="k")

    monkeypatch.setattr(client, "chat_completion", lambda *_args, **_kwargs: {"choices": []})

    assert client.chat_with_tools([{"role": "user", "content": "hello"}]) == ""


def test_chat_with_tools_prompt_transport_executes_tool(monkeypatch):
    monkeypatch.setenv("TALKBOT_OPENROUTER_TOOL_TRANSPORT", "prompt")
    client = OpenRouterClient(api_key="k")
    client.register_tool(
        "add", lambda a, b: str(a + b), "Add", {"type": "object", "properties": {}}
    )

    responses = iter(
        [
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": '<tool_call>{"name":"add","arguments":{"a":2,"b":3}}</tool_call>',
                        }
                    }
                ],
                "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
            },
            {
                "choices": [{"message": {"role": "assistant", "content": "5"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
            },
        ]
    )

    monkeypatch.setattr(
        client,
        "_request_completion",
        lambda **_kwargs: next(responses),
    )

    output = client.chat_with_tools([{"role": "user", "content": "sum"}])
    assert output == "5"


def test_chat_with_tools_falls_back_to_prompt_on_native_unsupported(monkeypatch):
    client = OpenRouterClient(api_key="k")
    client.register_tool("echo", lambda text: text, "Echo", {"type": "object"})

    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    response = httpx.Response(
        404,
        request=request,
        text='{"error":{"message":"No endpoints found that support tool use"}}',
    )
    error = httpx.HTTPStatusError(
        "No endpoints found that support tool use",
        request=request,
        response=response,
    )

    monkeypatch.setattr(client, "_chat_with_native_tools", lambda *_args, **_kwargs: (_ for _ in ()).throw(error))
    monkeypatch.setattr(client, "_chat_with_prompt_tools", lambda *_args, **_kwargs: "fallback-ok")

    assert client.chat_with_tools([{"role": "user", "content": "hello"}]) == "fallback-ok"


def test_chat_with_tools_native_mode_does_not_fallback_on_unsupported(monkeypatch):
    monkeypatch.setenv("TALKBOT_OPENROUTER_TOOL_TRANSPORT", "native")
    client = OpenRouterClient(api_key="k")
    client.register_tool("echo", lambda text: text, "Echo", {"type": "object"})

    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    response = httpx.Response(
        404,
        request=request,
        text='{"error":{"message":"No endpoints found that support tool use"}}',
    )
    error = httpx.HTTPStatusError(
        "No endpoints found that support tool use",
        request=request,
        response=response,
    )

    monkeypatch.setattr(
        client,
        "_chat_with_native_tools",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    monkeypatch.setattr(client, "_chat_with_prompt_tools", lambda *_args, **_kwargs: "fallback-ok")

    with pytest.raises(httpx.HTTPStatusError):
        client.chat_with_tools([{"role": "user", "content": "hello"}])


def test_chat_with_tools_native_mode_preflight_rejects_unsupported(monkeypatch):
    monkeypatch.setenv("TALKBOT_OPENROUTER_TOOL_TRANSPORT", "native")
    monkeypatch.setenv("TALKBOT_OPENROUTER_TOOL_PREFLIGHT", "1")
    client = OpenRouterClient(api_key="k")
    client.register_tool("echo", lambda text: text, "Echo", {"type": "object"})
    monkeypatch.setattr(client, "_detect_native_tool_support", lambda: False)

    with pytest.raises(RuntimeError, match="does not advertise native tool calling"):
        client.chat_with_tools([{"role": "user", "content": "hello"}])
