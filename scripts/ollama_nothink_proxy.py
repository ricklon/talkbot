#!/usr/bin/env python3
"""
Minimal proxy: OpenAI-compatible /v1/chat/completions  →  ollama /api/chat with think:false

Usage:
    uv run python scripts/ollama_nothink_proxy.py [--port 11435] [--ollama http://127.0.0.1:11434]

Then benchmark against http://127.0.0.1:11435/v1 instead of http://127.0.0.1:11434/v1.

Why: ollama 0.17.x ignores chat_template_kwargs/enable_thinking in the OpenAI endpoint.
The native /api/chat endpoint supports think:false which properly disables CoT generation.
"""

from __future__ import annotations

import argparse
import json
import logging
import socketserver
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ollama-proxy")

OLLAMA_URL = "http://127.0.0.1:11434"


def _post_json(url: str, data: dict, timeout: int = 600) -> dict:
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _openai_to_ollama_messages(messages: list[dict]) -> list[dict]:
    """Convert OpenAI message format to ollama native format.
    Strips /no_think wrappers injected by LocalServerClient (they're not needed here)."""
    out = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "") or ""
        # Strip /no_think wrappers that LocalServerClient injects around user messages
        if role == "user":
            content = content.replace("/no_think\n", "").replace("\n/no_think", "").strip()
        # Strip system messages that are purely /no_think or NO_THINK_INSTRUCTION
        if role == "system" and content.strip() in {
            "/no_think",
            "Respond directly with concise final answers. Do not include chain-of-thought or <think> tags.",
        }:
            continue
        tool_calls = m.get("tool_calls")
        entry: dict[str, Any] = {"role": role, "content": content}
        if tool_calls:
            # Convert OpenAI tool call format to ollama native
            native_calls = []
            for tc in tool_calls:
                fn = tc.get("function", {})
                args = fn.get("arguments", "{}")
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}
                native_calls.append({
                    "id": tc.get("id", ""),
                    "function": {"name": fn.get("name", ""), "arguments": args},
                })
            entry["tool_calls"] = native_calls
        # Tool result messages
        if role == "tool":
            entry["role"] = "tool"
            entry["content"] = content
        out.append(entry)
    return out


def _ollama_to_openai_response(ollama_resp: dict, model: str, req_id: str) -> dict:
    """Convert ollama /api/chat response to OpenAI chat.completion format."""
    msg = ollama_resp.get("message", {})
    content = msg.get("content", "") or ""
    tool_calls_raw = msg.get("tool_calls") or []

    # Convert tool calls: ollama arguments is dict, OpenAI expects JSON string
    openai_tool_calls = []
    for i, tc in enumerate(tool_calls_raw):
        fn = tc.get("function", {})
        args = fn.get("arguments", {})
        if isinstance(args, dict):
            args = json.dumps(args)
        openai_tool_calls.append({
            "id": tc.get("id", f"call_{i}"),
            "type": "function",
            "function": {
                "name": fn.get("name", ""),
                "arguments": args,
            },
        })

    finish_reason = "stop"
    if tool_calls_raw:
        finish_reason = "tool_calls"
    elif ollama_resp.get("done_reason") == "length":
        finish_reason = "length"

    choice_msg: dict[str, Any] = {"role": "assistant", "content": content}
    if openai_tool_calls:
        choice_msg["tool_calls"] = openai_tool_calls

    prompt_eval = ollama_resp.get("prompt_eval_count", 0)
    eval_count = ollama_resp.get("eval_count", 0)
    # Timing durations are in nanoseconds; convert to ms for downstream consumers.
    prompt_eval_ms = round((ollama_resp.get("prompt_eval_duration") or 0) / 1e6, 1)
    gen_ms = round((ollama_resp.get("eval_duration") or 0) / 1e6, 1)

    return {
        "id": req_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": choice_msg,
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": prompt_eval,
            "completion_tokens": eval_count,
            "total_tokens": prompt_eval + eval_count,
            "x_prompt_eval_ms": prompt_eval_ms,
            "x_gen_ms": gen_ms,
        },
    }


def handle_chat_completions(body: dict) -> dict:
    model = body.get("model", "")
    messages = body.get("messages", [])
    temperature = body.get("temperature", 0.3)
    max_tokens = body.get("max_tokens")
    tools = body.get("tools")

    ollama_payload: dict[str, Any] = {
        "model": model,
        "messages": _openai_to_ollama_messages(messages),
        "think": False,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if max_tokens:
        ollama_payload["options"]["num_predict"] = int(max_tokens)
    if tools:
        ollama_payload["tools"] = tools  # format is already compatible

    req_id = f"chatcmpl-proxy-{int(time.time() * 1000)}"
    ollama_resp = _post_json(f"{OLLAMA_URL}/api/chat", ollama_payload)
    return _ollama_to_openai_response(ollama_resp, model, req_id)


def handle_models() -> dict:
    """Proxy /v1/models to ollama /api/tags."""
    req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    models = [
        {
            "id": m["name"],
            "object": "model",
            "created": 0,
            "owned_by": "ollama",
        }
        for m in data.get("models", [])
    ]
    return {"object": "list", "data": models}


class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # suppress default access log
        pass

    def _send_json(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/v1/models", "/v1/models/"):
            try:
                self._send_json(200, handle_models())
            except Exception as e:
                self._send_json(502, {"error": str(e)})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode())
        except json.JSONDecodeError as e:
            self._send_json(400, {"error": f"bad json: {e}"})
            return

        if self.path in ("/v1/chat/completions", "/v1/chat/completions/"):
            t0 = time.time()
            try:
                result = handle_chat_completions(body)
                elapsed = time.time() - t0
                log.info(
                    "model=%s tokens=%s elapsed=%.1fs",
                    body.get("model"),
                    result.get("usage", {}).get("completion_tokens"),
                    elapsed,
                )
                self._send_json(200, result)
            except urllib.error.URLError as e:
                log.error("ollama connection error: %s", e)
                self._send_json(502, {"error": f"ollama unavailable: {e}"})
            except Exception as e:
                log.error("proxy error: %s", e, exc_info=True)
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": f"path not handled: {self.path}"})


def main():
    global OLLAMA_URL

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=11435, help="Port to listen on (default: 11435)")
    parser.add_argument("--ollama", default="http://127.0.0.1:11434", help="Ollama base URL")
    args = parser.parse_args()

    OLLAMA_URL = args.ollama.rstrip("/")

    # Verify ollama is reachable
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=5):
            pass
        log.info("ollama at %s is reachable", OLLAMA_URL)
    except Exception as e:
        log.error("Cannot reach ollama at %s: %s", OLLAMA_URL, e)
        sys.exit(1)

    class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
        """Bounded thread pool so aborted runs leave at most max_workers zombie threads."""
        daemon_threads = True

        def __init__(self, server_address, RequestHandlerClass, max_workers: int = 4):
            super().__init__(server_address, RequestHandlerClass)
            self._executor = ThreadPoolExecutor(max_workers=max_workers)

        def process_request(self, request, client_address):
            self._executor.submit(self.process_request_thread, request, client_address)

    server = ThreadedHTTPServer(("127.0.0.1", args.port), ProxyHandler)
    log.info(
        "Proxy listening on http://127.0.0.1:%d/v1  →  %s (think:false)",
        args.port,
        OLLAMA_URL,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down proxy")


if __name__ == "__main__":
    main()
