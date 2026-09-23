"""CLI wiring for the autoresearch harness."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .harness import AutoresearchHarness
from .planner import planner_from_environment
from .plugins import SyntheticRegressionPlugin


def load_repo_env(start: Path) -> None:
    for directory in (start.resolve(), *start.resolve().parents):
        candidate = directory / ".env"
        if not candidate.is_file():
            continue
        for raw_line in candidate.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the custom ML autoresearch harness")
    parser.add_argument("--run-id", default="run", help="Artifact directory name")
    parser.add_argument("--budget", type=int, default=8, help="Number of experiments, 1-12")
    parser.add_argument("--planner", choices=["auto", "heuristic", "openrouter"], default="auto")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, help="Artifact root directory")
    parser.add_argument("--overwrite", action="store_true", help="Replace known artifacts in this run directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_repo_env(Path.cwd())
    if not args.run_id or any(character in args.run_id for character in '<>:"/\\|?*'):
        raise SystemExit("--run-id must be a valid single directory name")
    planner = planner_from_environment(args.planner)
    plugin = SyntheticRegressionPlugin(seed=args.seed)
    output_root = args.output or Path(__file__).parents[1] / "artifacts"
    harness = AutoresearchHarness(
        plugin=plugin,
        planner=planner,
        output_directory=output_root / args.run_id,
        budget=args.budget,
        overwrite=args.overwrite,
    )
    result = harness.run()
    print(f"Completed {result.completed_experiments} experiments using {planner.name}.")
    print(f"Best: {result.best_experiment.experiment_id} {result.best_experiment.parameters}")
    print(f"Validation MSE: {result.best_experiment.validation_metric:.6f}")
    print(f"Test MSE: {result.test_metric:.6f}")
    print(f"Artifacts: {result.output_directory.resolve()}")
    return 0
