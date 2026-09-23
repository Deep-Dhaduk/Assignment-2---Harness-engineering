"""A deterministic polynomial-regression research domain."""

from __future__ import annotations

import random
from typing import Any

from ..math_utils import fit_polynomial, mean_squared_error
from ..plugin import ExperimentConfig, ExperimentResult


class SyntheticRegressionPlugin:
    name = "synthetic-polynomial-regression"
    objective = "Minimize held-out mean squared error on a noisy nonlinear regression problem."
    hypothesis = "A quadratic model will improve on the linear baseline without the variance of higher degrees."
    metric_name = "mean_squared_error"
    lower_is_better = True

    def __init__(self, seed: int = 2026) -> None:
        self.seed = seed
        points = self._make_dataset(seed)
        self.train = points[:70]
        self.validation = points[70:95]
        self.test = points[95:120]

    @staticmethod
    def _make_dataset(seed: int) -> list[tuple[float, float]]:
        rng = random.Random(seed)
        points: list[tuple[float, float]] = []
        for index in range(120):
            x = -3.0 + 6.0 * index / 119
            noise = rng.gauss(0.0, 0.35)
            y = 1.5 + 2.8 * x - 0.7 * x * x + noise
            points.append((x, y))
        rng.shuffle(points)
        return points

    def search_space(self) -> list[ExperimentConfig]:
        candidates: list[ExperimentConfig] = []
        number = 1
        for degree in (1, 2, 3, 4):
            for ridge in (0.0, 0.01, 0.1):
                candidates.append(ExperimentConfig(
                    experiment_id=f"exp-{number:02d}",
                    parameters={"degree": degree, "ridge": ridge},
                ))
                number += 1
        return candidates

    def validate_config(self, config: ExperimentConfig) -> None:
        degree = config.parameters.get("degree")
        ridge = config.parameters.get("ridge")
        if not isinstance(degree, int) or degree not in {1, 2, 3, 4}:
            raise ValueError("degree must be one of 1, 2, 3, or 4")
        if not isinstance(ridge, (int, float)) or float(ridge) not in {0.0, 0.01, 0.1}:
            raise ValueError("ridge must be one of 0.0, 0.01, or 0.1")

    def run_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        self.validate_config(config)
        degree = int(config.parameters["degree"])
        ridge = float(config.parameters["ridge"])
        train_x, train_y = map(list, zip(*self.train))
        validation_x, validation_y = map(list, zip(*self.validation))
        coefficients = fit_polynomial(train_x, train_y, degree, ridge)
        train_mse = mean_squared_error(coefficients, train_x, train_y)
        validation_mse = mean_squared_error(coefficients, validation_x, validation_y)
        return ExperimentResult(
            experiment_id=config.experiment_id,
            parameters=dict(config.parameters),
            validation_metric=validation_mse,
            train_metric=train_mse,
            model={"type": "polynomial_regression", "degree": degree, "ridge": ridge, "coefficients": coefficients},
            observations=f"degree={degree}, ridge={ridge:g}, validation MSE={validation_mse:.6f}",
        )

    def evaluate_test(self, model: dict[str, Any]) -> float:
        test_x, test_y = map(list, zip(*self.test))
        return mean_squared_error(list(model["coefficients"]), test_x, test_y)
