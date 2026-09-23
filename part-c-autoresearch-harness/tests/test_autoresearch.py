from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

PART_C = Path(__file__).parents[1]
sys.path.insert(0, str(PART_C))

from autoresearch.harness import AutoresearchHarness
from autoresearch.planner import HeuristicPlanner
from autoresearch.plugin import ExperimentConfig
from autoresearch.plugins import SyntheticRegressionPlugin


class PluginTests(unittest.TestCase):
    def test_dataset_is_reproducible(self) -> None:
        first = SyntheticRegressionPlugin(seed=7)
        second = SyntheticRegressionPlugin(seed=7)
        self.assertEqual(first.train, second.train)

    def test_quadratic_improves_linear_baseline(self) -> None:
        plugin = SyntheticRegressionPlugin()
        linear = plugin.run_experiment(ExperimentConfig("linear", {"degree": 1, "ridge": 0.0}))
        quadratic = plugin.run_experiment(ExperimentConfig("quadratic", {"degree": 2, "ridge": 0.0}))
        self.assertLess(quadratic.validation_metric, linear.validation_metric)

    def test_invalid_configuration_is_rejected(self) -> None:
        plugin = SyntheticRegressionPlugin()
        with self.assertRaises(ValueError):
            plugin.validate_config(ExperimentConfig("bad", {"degree": 99, "ridge": 0.0}))


class HarnessTests(unittest.TestCase):
    def test_end_to_end_run_writes_evidence_and_reproduces(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            harness = AutoresearchHarness(
                SyntheticRegressionPlugin(), HeuristicPlanner(), output, budget=8
            )
            result = harness.run()
            self.assertEqual(result.completed_experiments, 8)
            self.assertLessEqual(result.reproduction_delta, 1e-12)
            for name in AutoresearchHarness.ARTIFACT_NAMES:
                self.assertTrue((output / name).is_file(), name)
            best = json.loads((output / "best_model.json").read_text(encoding="utf-8"))
            self.assertTrue(best["evidence_gate_passed"])
            events = (output / "events.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(json.loads(events[0])["type"], "run_started")
            self.assertEqual(json.loads(events[-1])["type"], "run_completed")

    def test_existing_run_requires_explicit_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            AutoresearchHarness(SyntheticRegressionPlugin(), HeuristicPlanner(), output, budget=1).run()
            with self.assertRaises(FileExistsError):
                AutoresearchHarness(SyntheticRegressionPlugin(), HeuristicPlanner(), output, budget=1).run()


if __name__ == "__main__":
    unittest.main()
