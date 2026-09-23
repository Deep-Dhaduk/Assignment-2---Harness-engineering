"""Stable plugin contract between research orchestration and ML domains."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str
    parameters: dict[str, int | float | str]


@dataclass(frozen=True)
class ExperimentResult:
    experiment_id: str
    parameters: dict[str, int | float | str]
    validation_metric: float
    train_metric: float
    model: dict[str, Any]
    observations: str


class ExperimentPlugin(Protocol):
    name: str
    objective: str
    hypothesis: str
    metric_name: str
    lower_is_better: bool

    def search_space(self) -> list[ExperimentConfig]: ...
    def run_experiment(self, config: ExperimentConfig) -> ExperimentResult: ...
    def evaluate_test(self, model: dict[str, Any]) -> float: ...
    def validate_config(self, config: ExperimentConfig) -> None: ...
