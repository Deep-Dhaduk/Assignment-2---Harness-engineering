"""Workspace-scoped tools exposed to the coding model."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any, Callable


class ToolError(ValueError):
    """A safe, model-readable tool failure."""


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[[dict[str, Any]], dict[str, Any]]

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class WorkspaceTools:
    ALLOWED_PROGRAMS = {"python", "python3", "py", "pytest", "git", "node", "npm", "npm.cmd"}
    BLOCKED_GIT_SUBCOMMANDS = {"clean", "reset", "checkout", "restore", "rebase", "push", "commit"}

    def __init__(self, workspace: Path, max_output_chars: int = 20_000) -> None:
        self.workspace = workspace.resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.max_output_chars = max_output_chars
        self._tools = self._build_tools()

    @property
    def schemas(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(name)
        if not tool:
            raise ToolError(f"Unknown tool: {name}")
        if not isinstance(arguments, dict):
            raise ToolError("Tool arguments must be a JSON object")
        return tool.handler(arguments)

    def _resolve(self, raw_path: str) -> Path:
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ToolError("path must be a non-empty string")
        candidate = (self.workspace / raw_path).resolve()
        try:
            candidate.relative_to(self.workspace)
        except ValueError as exc:
            raise ToolError(f"Path escapes workspace: {raw_path}") from exc
        return candidate

    def _truncate(self, text: str) -> tuple[str, bool]:
        if len(text) <= self.max_output_chars:
            return text, False
        return text[: self.max_output_chars] + "\n...[truncated]", True

    def _list_files(self, args: dict[str, Any]) -> dict[str, Any]:
        base = self._resolve(str(args.get("path", ".")))
        if not base.is_dir():
            raise ToolError(f"Not a directory: {args.get('path', '.')}")
        files: list[str] = []
        for item in sorted(base.rglob("*")):
            if any(part in {".git", ".venv", "node_modules", "__pycache__"} for part in item.parts):
                continue
            files.append(item.relative_to(self.workspace).as_posix() + ("/" if item.is_dir() else ""))
            if len(files) >= 500:
                break
        return {"files": files, "limited": len(files) >= 500}

    def _read_file(self, args: dict[str, Any]) -> dict[str, Any]:
        path = self._resolve(str(args.get("path", "")))
        if not path.is_file():
            raise ToolError(f"File does not exist: {args.get('path')}")
        content, truncated = self._truncate(path.read_text(encoding="utf-8", errors="replace"))
        return {"path": path.relative_to(self.workspace).as_posix(), "content": content, "truncated": truncated}

    def _write_file(self, args: dict[str, Any]) -> dict[str, Any]:
        path = self._resolve(str(args.get("path", "")))
        content = args.get("content")
        if not isinstance(content, str):
            raise ToolError("content must be a string")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return {"path": path.relative_to(self.workspace).as_posix(), "bytes": len(content.encode("utf-8"))}

    def _run_command(self, args: dict[str, Any]) -> dict[str, Any]:
        program = args.get("program")
        arguments = args.get("arguments", [])
        if program not in self.ALLOWED_PROGRAMS:
            raise ToolError(f"Program is not allowlisted: {program}")
        if not isinstance(arguments, list) or not all(isinstance(value, str) for value in arguments):
            raise ToolError("arguments must be an array of strings")
        if program == "git" and arguments and arguments[0].lower() in self.BLOCKED_GIT_SUBCOMMANDS:
            raise ToolError(f"Git subcommand is blocked: {arguments[0]}")
        try:
            completed = subprocess.run(
                [program, *arguments],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30,
                shell=False,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ToolError(f"Command could not run: {exc}") from exc
        stdout, out_truncated = self._truncate(completed.stdout)
        stderr, err_truncated = self._truncate(completed.stderr)
        return {
            "exit_code": completed.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "truncated": out_truncated or err_truncated,
        }

    def _build_tools(self) -> dict[str, Tool]:
        object_schema = {"type": "object", "additionalProperties": False}
        tools = [
            Tool("list_files", "List files below a workspace directory.", {
                **object_schema,
                "properties": {"path": {"type": "string", "description": "Relative directory; defaults to ."}},
            }, self._list_files),
            Tool("read_file", "Read a UTF-8 text file inside the workspace.", {
                **object_schema,
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            }, self._read_file),
            Tool("write_file", "Create or replace a UTF-8 text file inside the workspace.", {
                **object_schema,
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            }, self._write_file),
            Tool("run_command", "Run an allowlisted program without a shell in the workspace.", {
                **object_schema,
                "properties": {
                    "program": {"type": "string", "enum": sorted(self.ALLOWED_PROGRAMS)},
                    "arguments": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["program", "arguments"],
            }, self._run_command),
        ]
        return {tool.name: tool for tool in tools}


def encode_tool_result(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
