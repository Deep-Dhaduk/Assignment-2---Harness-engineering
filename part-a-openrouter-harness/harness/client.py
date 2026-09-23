"""Model clients implementing the narrow interface consumed by the agent loop."""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ModelClient(Protocol):
    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]: ...


@dataclass
class OpenRouterClient:
    api_key: str
    model: str
    base_url: str = "https://openrouter.ai/api/v1"
    timeout_seconds: int = 90
    retries: int = 2

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "parallel_tool_calls": True,
        }
        request = Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Deep-Dhaduk/Assignment-2---Harness-engineering",
                "X-OpenRouter-Title": "Assignment 2 Harness Engineering",
            },
        )
        for attempt in range(self.retries + 1):
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    data = json.loads(response.read().decode("utf-8"))
                return data["choices"][0]["message"]
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:2000]
                if exc.code not in {429, 500, 502, 503, 504} or attempt == self.retries:
                    raise RuntimeError(f"OpenRouter HTTP {exc.code}: {detail}") from exc
            except (URLError, TimeoutError) as exc:
                if attempt == self.retries:
                    raise RuntimeError(f"OpenRouter request failed: {exc}") from exc
            time.sleep(2**attempt)
        raise AssertionError("retry loop exited unexpectedly")


class ScriptedDemoClient:
    """Deterministic local model used to prove the real tool loop without a key."""

    def __init__(self) -> None:
        self.step = 0

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        del messages, tools
        script = [
            self._call("demo-call-1", "write_file", {"path": "hello.py", "content": "print('Hello from the harness!')\n"}),
            self._call("demo-call-2", "read_file", {"path": "hello.py"}),
            self._call("demo-call-3", "run_command", {"program": "python", "arguments": ["hello.py"]}),
            {"role": "assistant", "content": "Created, inspected, and executed hello.py successfully."},
        ]
        response = script[min(self.step, len(script) - 1)]
        self.step += 1
        return response

    def _call(self, call_id: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": call_id,
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(arguments)},
            }],
        }
