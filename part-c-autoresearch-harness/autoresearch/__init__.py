"""A bounded, reproducible machine-learning autoresearch harness."""

from .harness import AutoresearchHarness, ResearchResult
from .plugin import ExperimentConfig, ExperimentPlugin, ExperimentResult

__all__ = ["AutoresearchHarness", "ResearchResult", "ExperimentConfig", "ExperimentPlugin", "ExperimentResult"]
