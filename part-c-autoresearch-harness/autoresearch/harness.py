"""End-to-end research orchestration and artifact generation."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any

from .planner import Planner
from .plugin import ExperimentPlugin, ExperimentResult


@dataclass(frozen=True)
class ResearchResult:
    best_experiment: ExperimentResult
    test_metric: float
    reproduction_delta: float
    completed_experiments: int
    output_directory: Path


class AutoresearchHarness:
    ARTIFACT_NAMES = {"events.jsonl", "experiments.json", "leaderboard.csv", "best_model.json", "report.md"}

    def __init__(
        self,
        plugin: ExperimentPlugin,
        planner: Planner,
        output_directory: Path,
        budget: int = 8,
        overwrite: bool = False,
    ) -> None:
        self.plugin = plugin
        self.planner = planner
        self.output_directory = output_directory
        self.budget = budget
        self.overwrite = overwrite
        self.events_path = output_directory / "events.jsonl"

    def run(self) -> ResearchResult:
        candidates = self.plugin.search_space()
        if not 1 <= self.budget <= len(candidates):
            raise ValueError(f"budget must be between 1 and {len(candidates)}")
        self._prepare_output()
        self._event("run_started", {
            "plugin": self.plugin.name,
            "planner": self.planner.name,
            "budget": self.budget,
            "objective": self.plugin.objective,
            "hypothesis": self.plugin.hypothesis,
        })
        selected = self.planner.select(candidates, self.budget, self.plugin.objective, self.plugin.hypothesis)
        self._validate_plan(selected)
        self._event("plan_created", {"experiments": [asdict(item) for item in selected]})

        results: list[ExperimentResult] = []
        failures: list[dict[str, str]] = []
        for config in selected:
            self._event("experiment_started", asdict(config))
            try:
                result = self.plugin.run_experiment(config)
            except Exception as exc:  # isolate one failed experiment from the research run
                failure = {"experiment_id": config.experiment_id, "error": str(exc)}
                failures.append(failure)
                self._event("experiment_failed", failure)
                continue
            if not math.isfinite(result.validation_metric) or not math.isfinite(result.train_metric):
                failure = {"experiment_id": config.experiment_id, "error": "non-finite metric"}
                failures.append(failure)
                self._event("experiment_failed", failure)
                continue
            results.append(result)
            self._event("experiment_completed", asdict(result))
        if not results:
            raise RuntimeError("All experiments failed; no model can be selected")

        reverse = not self.plugin.lower_is_better
        leaderboard = sorted(results, key=lambda result: result.validation_metric, reverse=reverse)
        best = leaderboard[0]
        best_config = next(item for item in selected if item.experiment_id == best.experiment_id)
        reproduced = self.plugin.run_experiment(best_config)
        reproduction_delta = abs(reproduced.validation_metric - best.validation_metric)
        test_metric = self.plugin.evaluate_test(best.model)
        gate = {
            "at_least_one_experiment": bool(results),
            "best_reproduced": reproduction_delta <= 1e-12,
            "test_metric_is_finite": math.isfinite(test_metric),
        }
        self._event("winner_selected", {
            "experiment_id": best.experiment_id,
            "validation_metric": best.validation_metric,
            "test_metric": test_metric,
            "reproduction_delta": reproduction_delta,
            "evidence_gate": gate,
        })
        self._write_artifacts(leaderboard, failures, best, test_metric, reproduction_delta, gate)
        self._event("run_completed", {"best_experiment": best.experiment_id, "evidence_gate_passed": all(gate.values())})
        return ResearchResult(best, test_metric, reproduction_delta, len(results), self.output_directory)

    def _prepare_output(self) -> None:
        self.output_directory.mkdir(parents=True, exist_ok=True)
        existing = [self.output_directory / name for name in self.ARTIFACT_NAMES if (self.output_directory / name).exists()]
        if existing and not self.overwrite:
            raise FileExistsError(f"Run already exists at {self.output_directory}; choose another --run-id or pass --overwrite")
        if self.overwrite:
            for path in existing:
                path.unlink()

    def _validate_plan(self, selected: list[Any]) -> None:
        if len(selected) != self.budget:
            raise ValueError(f"Planner selected {len(selected)} experiments for budget {self.budget}")
        identifiers = [item.experiment_id for item in selected]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Planner selected duplicate experiments")
        available = {item.experiment_id for item in self.plugin.search_space()}
        if any(identifier not in available for identifier in identifiers):
            raise ValueError("Planner selected an experiment outside the plugin search space")
        for config in selected:
            self.plugin.validate_config(config)

    def _event(self, event_type: str, data: dict[str, Any]) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "data": data,
        }
        with self.events_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, sort_keys=True) + "\n")

    def _write_artifacts(
        self,
        leaderboard: list[ExperimentResult],
        failures: list[dict[str, str]],
        best: ExperimentResult,
        test_metric: float,
        reproduction_delta: float,
        gate: dict[str, bool],
    ) -> None:
        experiments = {
            "plugin": self.plugin.name,
            "planner": self.planner.name,
            "objective": self.plugin.objective,
            "hypothesis": self.plugin.hypothesis,
            "metric": self.plugin.metric_name,
            "results": [asdict(result) for result in leaderboard],
            "failures": failures,
        }
        (self.output_directory / "experiments.json").write_text(
            json.dumps(experiments, indent=2, sort_keys=True), encoding="utf-8"
        )
        with (self.output_directory / "leaderboard.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["rank", "experiment_id", "degree", "ridge", "train_mse", "validation_mse"])
            for rank, result in enumerate(leaderboard, start=1):
                writer.writerow([
                    rank,
                    result.experiment_id,
                    result.parameters["degree"],
                    result.parameters["ridge"],
                    f"{result.train_metric:.10f}",
                    f"{result.validation_metric:.10f}",
                ])
        best_payload = {
            "experiment_id": best.experiment_id,
            "parameters": best.parameters,
            "model": best.model,
            "validation_metric": best.validation_metric,
            "test_metric": test_metric,
            "reproduction_delta": reproduction_delta,
            "evidence_gate": gate,
            "evidence_gate_passed": all(gate.values()),
        }
        (self.output_directory / "best_model.json").write_text(
            json.dumps(best_payload, indent=2, sort_keys=True), encoding="utf-8"
        )
        report = self._render_report(leaderboard, failures, best, test_metric, reproduction_delta, gate)
        (self.output_directory / "report.md").write_text(report, encoding="utf-8")

    def _render_report(
        self,
        leaderboard: list[ExperimentResult],
        failures: list[dict[str, str]],
        best: ExperimentResult,
        test_metric: float,
        reproduction_delta: float,
        gate: dict[str, bool],
    ) -> str:
        rows = "\n".join(
            f"| {rank} | {result.experiment_id} | {result.parameters['degree']} | {result.parameters['ridge']} | "
            f"{result.train_metric:.6f} | {result.validation_metric:.6f} |"
            for rank, result in enumerate(leaderboard, start=1)
        )
        gate_rows = "\n".join(f"- [{'x' if passed else ' '}] {name.replace('_', ' ')}" for name, passed in gate.items())
        return f"""# Autoresearch Report — {self.plugin.name}

## Objective

{self.plugin.objective}

## Hypothesis

{self.plugin.hypothesis}

## Method

Planner: `{self.planner.name}`. Budget: {self.budget} experiments. Selection metric: `{self.plugin.metric_name}` ({'lower' if self.plugin.lower_is_better else 'higher'} is better).

## Leaderboard

| Rank | Experiment | Degree | Ridge | Train MSE | Validation MSE |
|---:|---|---:|---:|---:|---:|
{rows}

## Selected model

- Experiment: `{best.experiment_id}`
- Parameters: `{json.dumps(best.parameters, sort_keys=True)}`
- Validation MSE: `{best.validation_metric:.6f}`
- Held-out test MSE: `{test_metric:.6f}`
- Reproduction delta: `{reproduction_delta:.12f}`
- Failed experiments: `{len(failures)}`

## Evidence gate

{gate_rows}

Overall: **{'PASS' if all(gate.values()) else 'FAIL'}**

## Conclusion

The winning configuration was selected only on validation performance and evaluated once on the held-out test split. The exact event stream, all candidates, and serialized coefficients are saved beside this report.
"""
