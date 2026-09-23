"""Command-line interface for the coding harness."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .agent import Agent
from .client import OpenRouterClient, ScriptedDemoClient
from .config import Settings
from .tools import WorkspaceTools


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Part A coding harness")
    parser.add_argument("task", nargs="?", help="Coding task for the agent")
    parser.add_argument("--demo", action="store_true", help="Run deterministic offline demonstration")
    parser.add_argument("--workspace", type=Path, help="Agent workspace")
    parser.add_argument("--model", help="OpenRouter model slug")
    parser.add_argument("--max-steps", type=int, help="Maximum model iterations")
    parser.add_argument("--artifact", type=Path, help="JSON trajectory output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.from_environment(Path.cwd())
    task = args.task or ("Create hello.py, inspect it, and run it." if args.demo else "")
    if not task:
        raise SystemExit("Provide a task, or pass --demo.")
    if args.demo:
        client = ScriptedDemoClient()
        workspace = (args.workspace or Path(__file__).parents[1] / "demo-workspace").resolve()
    else:
        if not settings.api_key:
            raise SystemExit("OPENROUTER_API_KEY is missing. Add it to .env or run with --demo.")
        client = OpenRouterClient(
            api_key=settings.api_key,
            model=args.model or settings.model,
            base_url=settings.base_url,
            timeout_seconds=settings.timeout_seconds,
        )
        workspace = (args.workspace or Path.cwd()).resolve()
    tools = WorkspaceTools(workspace, max_output_chars=settings.max_output_chars)
    agent = Agent(client, tools, max_steps=args.max_steps or settings.max_steps)
    result = agent.run(task)
    artifact = args.artifact or (
        Path(__file__).parents[1] / "artifacts" / f"trajectory-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    )
    agent.save_artifact(result, artifact, task)
    print(f"\nAgent completed in {result.steps} step(s).")
    print(result.answer)
    print(f"Trajectory: {artifact.resolve()}")
    return 0
