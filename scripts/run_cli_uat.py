#!/usr/bin/env python3
"""End-to-end CLI UAT runner for TalkBot.

Exercises the real `talkbot` CLI entrypoints with the main user journeys:
- ask the time
- ask for information
- remember and recall something
- make and read a grocery list
- set a timer and wait for the alert
- hold an extended conversation

By default this script isolates data in a temporary directory so it does not
pollute the user's normal `~/.talkbot` memory/lists. Pass `--data-dir` to keep
or inspect the persisted state.
"""

from __future__ import annotations

import argparse
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path


DEFAULT_LOCAL_SERVER_MODEL = "qwen3.5-0.8b-q8_0.gguf"
DEFAULT_LOCAL_SERVER_URL = "http://127.0.0.1:8000/v1"


@dataclass
class ScenarioResult:
    name: str
    passed: bool
    details: str


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", default="local_server", choices=["local", "local_server", "openrouter"])
    parser.add_argument("--model", default=DEFAULT_LOCAL_SERVER_MODEL)
    parser.add_argument("--local-server-url", default=DEFAULT_LOCAL_SERVER_URL)
    parser.add_argument("--backend", default=os.getenv("TALKBOT_DEFAULT_TTS_BACKEND", "kittentts"))
    parser.add_argument("--speak", action="store_true", help="Enable TTS so you can hear the responses.")
    parser.add_argument("--api-key", default=os.getenv("OPENROUTER_API_KEY", ""))
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Persistent tool data directory. Defaults to a temporary isolated directory.",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Keep the temporary data directory when the script exits.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Per-command timeout in seconds (default: 120).",
    )
    return parser.parse_args(argv)


def _base_env(args: argparse.Namespace, data_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = str(Path.cwd() / ".uv-cache")
    env["TALKBOT_DATA_DIR"] = str(data_dir)
    env["TALKBOT_LOCAL_DIRECT_TOOL_ROUTING"] = "1"
    if args.api_key:
        env["OPENROUTER_API_KEY"] = args.api_key
    return env


def _base_cmd(args: argparse.Namespace) -> list[str]:
    return [
        "uv",
        "run",
        "talkbot",
        "--provider",
        args.provider,
        "--model",
        args.model,
        "--local-server-url",
        args.local_server_url,
    ]


def _chat_cmd(args: argparse.Namespace, prompt: str) -> list[str]:
    cmd = _base_cmd(args) + ["chat", prompt, "--tools"]
    if not args.speak:
        cmd.append("--no-speak")
    else:
        cmd.extend(["--backend", args.backend])
    return cmd


def _run_chat(args: argparse.Namespace, env: dict[str, str], prompt: str) -> tuple[bool, str]:
    proc = subprocess.run(
        _chat_cmd(args, prompt),
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        timeout=args.timeout,
    )
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output


class InteractiveSession:
    def __init__(self, cmd: list[str], env: dict[str, str], timeout: int) -> None:
        self.proc = subprocess.Popen(
            cmd,
            cwd=Path.cwd(),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self.timeout = timeout
        self._lines: list[str] = []
        self._queue: queue.Queue[str] = queue.Queue()
        self._reader = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader.start()

    def _read_stdout(self) -> None:
        assert self.proc.stdout is not None
        for line in self.proc.stdout:
            clean = line.rstrip("\n")
            self._lines.append(clean)
            self._queue.put(clean)

    def send_line(self, text: str) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(text + "\n")
        self.proc.stdin.flush()

    def wait_for(self, pattern: str, *, timeout: int | None = None) -> bool:
        compiled = re.compile(pattern)
        deadline = time.time() + (timeout or self.timeout)
        while time.time() < deadline:
            try:
                line = self._queue.get(timeout=0.5)
            except queue.Empty:
                if self.proc.poll() is not None:
                    break
                continue
            if compiled.search(line):
                return True
        return any(compiled.search(line) for line in self._lines)

    def finish(self) -> tuple[int, str]:
        if self.proc.stdin and not self.proc.stdin.closed:
            try:
                self.proc.stdin.close()
            except Exception:
                pass
        try:
            code = self.proc.wait(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            code = self.proc.wait(timeout=5)
        self._reader.join(timeout=1)
        return code, "\n".join(self._lines)


def _say_cmd(args: argparse.Namespace) -> list[str]:
    cmd = _base_cmd(args) + ["say", "--tools"]
    if args.speak:
        cmd.extend(["--backend", args.backend])
    else:
        cmd.extend(["--backend", args.backend, "--volume", "0"])
    return cmd


def _scenario_time(args: argparse.Namespace, env: dict[str, str]) -> ScenarioResult:
    ok, output = _run_chat(args, env, "What time is it?")
    passed = ok and "AI:" in output and re.search(r"\b\d{2}:\d{2}:\d{2}\b", output) is not None
    return ScenarioResult("Ask Time", passed, output)


def _scenario_information(args: argparse.Namespace, env: dict[str, str]) -> ScenarioResult:
    ok, output = _run_chat(args, env, "What is 15 percent of 47 dollars?")
    passed = ok and "AI:" in output and "7.05" in output
    return ScenarioResult("Ask Information", passed, output)


def _scenario_memory(args: argparse.Namespace, env: dict[str, str]) -> ScenarioResult:
    ok_store, store_output = _run_chat(args, env, "Remember that my project codename is Falcon.")
    ok_recall, recall_output = _run_chat(args, env, "What did you remember about my project codename?")
    passed = ok_store and ok_recall and "project_codename" in recall_output and "falcon" in recall_output.lower()
    return ScenarioResult("Remember Something", passed, store_output + "\n---\n" + recall_output)


def _scenario_list(args: argparse.Namespace, env: dict[str, str]) -> ScenarioResult:
    ok_make, make_output = _run_chat(args, env, "Create a grocery list and add milk.")
    ok_read, read_output = _run_chat(args, env, "What is on my grocery list?")
    passed = ok_make and ok_read and "milk" in read_output.lower()
    return ScenarioResult("Make And Read Grocery List", passed, make_output + "\n---\n" + read_output)


def _scenario_timer(args: argparse.Namespace, env: dict[str, str]) -> ScenarioResult:
    cmd = _say_cmd(args)
    session = InteractiveSession(cmd, env, timeout=args.timeout)
    session.wait_for(r"Interactive mode started", timeout=10)
    session.send_line("Set a timer for 3 seconds.")
    saw_ack = session.wait_for(r"Timer #|fire in 3 seconds|AI:", timeout=30)
    saw_alert = session.wait_for(r"\[TIMER\].*done|is done!", timeout=15)
    session.send_line("exit")
    code, output = session.finish()
    passed = saw_ack and saw_alert
    if code != 0:
        output = f"[exit_code={code}]\n{output}"
    return ScenarioResult("Set Timer", passed, output)


def _scenario_extended_conversation(args: argparse.Namespace, env: dict[str, str]) -> ScenarioResult:
    cmd = _say_cmd(args)
    session = InteractiveSession(cmd, env, timeout=args.timeout)
    session.wait_for(r"Interactive mode started", timeout=10)
    prompts = [
        "Remember that my launch codename is Atlas.",
        "Create a grocery list and add eggs.",
        "What is on my grocery list?",
        "What did you remember about my launch codename?",
        "What time is it?",
        "exit",
    ]
    for prompt in prompts:
        session.send_line(prompt)
        time.sleep(0.5)
    code, output = session.finish()
    passed = (
        code == 0
        and "eggs" in output.lower()
        and "launch_codename: atlas" in output.lower()
        and re.search(r"\b\d{2}:\d{2}:\d{2}\b", output) is not None
    )
    return ScenarioResult("Extended Conversation", passed, output)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if args.data_dir:
        data_dir = Path(args.data_dir).expanduser()
        data_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = tempfile.TemporaryDirectory(prefix="talkbot-uat-")
        data_dir = Path(temp_dir.name)

    env = _base_env(args, data_dir)

    print("CLI UAT")
    print("=======")
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model}")
    print(f"Server: {args.local_server_url}")
    print(f"Data dir: {data_dir}")
    print(f"Speak: {'on' if args.speak else 'off'}")
    print()

    scenarios = [
        _scenario_time,
        _scenario_information,
        _scenario_memory,
        _scenario_list,
        _scenario_timer,
        _scenario_extended_conversation,
    ]

    results: list[ScenarioResult] = []
    for scenario in scenarios:
        result = scenario(args, env)
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}")
        print(result.details)
        print()

    failed = [r for r in results if not r.passed]
    print("Summary")
    print("=======")
    print(f"Passed: {len(results) - len(failed)}/{len(results)}")
    if failed:
        print("Failed scenarios:")
        for result in failed:
            print(f"- {result.name}")
    else:
        print("All CLI UAT scenarios passed.")

    if temp_dir is not None and not args.keep_data:
        temp_dir.cleanup()

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
