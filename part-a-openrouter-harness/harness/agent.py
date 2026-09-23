"""The model/tool execution loop—the core of the harness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .client import ModelClient
from .tools import ToolError, WorkspaceTools, encode_tool_result


SYSTEM_PROMPT = """You are a careful coding agent operating inside one workspace.
Inspect existing files before changing them. Use tools for every filesystem or execution action.
Prefer small, verifiable changes. Run relevant tests. Never claim a command succeeded unless its
tool result shows exit_code 0. Finish with a concise summary of changes and verification."""


@dataclass(frozen=True)
class AgentResult:
    answer: str
    steps: int
    messages: list[dict[str, Any]]


class Agent:
    def __init__(self, client: ModelClient, tools: WorkspaceTools, max_steps: int = 12) -> None:
        self.client = client
        self.tools = tools
        self.max_steps = max_steps

    def run(self, task: str) -> AgentResult:
        if not task.strip():
            raise ValueError("task must not be empty")
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task.strip()},
        ]
        for step in range(1, self.max_steps + 1):
            assistant = self.client.complete(messages, self.tools.schemas)
            normalized = self._normalize_assistant(assistant)
            messages.append(normalized)
            calls = normalized.get("tool_calls") or []
            if not calls:
                answer = normalized.get("content") or "The model stopped without a final message."
                return AgentResult(answer=answer, steps=step, messages=messages)
            for call in calls:
                result = self._execute_call(call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.get("id", "missing-id"),
                    "name": call.get("function", {}).get("name", "unknown"),
                    "content": encode_tool_result(result),
                })
        raise RuntimeError(f"Agent exceeded maximum step count ({self.max_steps})")

    def save_artifact(self, result: AgentResult, path: Path, task: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "task": task,
            "steps": result.steps,
            "answer": result.answer,
            "messages": result.messages,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def _execute_call(self, call: dict[str, Any]) -> dict[str, Any]:
        function = call.get("function") or {}
        name = function.get("name", "")
        try:
            arguments = json.loads(function.get("arguments") or "{}")
            value = self.tools.execute(name, arguments)
            return {"ok": True, "value": value}
        except (json.JSONDecodeError, ToolError, TypeError, ValueError, OSError) as exc:
            return {"ok": False, "error": str(exc)}

    @staticmethod
    def _normalize_assistant(message: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(message, dict):
            raise RuntimeError("Model response message must be an object")
        normalized: dict[str, Any] = {"role": "assistant", "content": message.get("content")}
        if message.get("tool_calls"):
            normalized["tool_calls"] = message["tool_calls"]
        return normalized
