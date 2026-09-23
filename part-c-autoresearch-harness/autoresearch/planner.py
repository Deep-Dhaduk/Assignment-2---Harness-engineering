"""Deterministic and OpenRouter-assisted bounded experiment planners."""

from __future__ import annotations

import json
import os
from typing import Protocol
from urllib.request import Request, urlopen

from .plugin import ExperimentConfig


class Planner(Protocol):
    name: str
    def select(self, candidates: list[ExperimentConfig], budget: int, objective: str, hypothesis: str) -> list[ExperimentConfig]: ...


class HeuristicPlanner:
    name = "deterministic-heuristic"

    def select(self, candidates: list[ExperimentConfig], budget: int, objective: str, hypothesis: str) -> list[ExperimentConfig]:
        del objective, hypothesis
        # First cover every degree at low regularization, then fill nearby ridge variants.
        ordered = sorted(candidates, key=lambda item: (
            0 if float(item.parameters["ridge"]) == 0.0 else 1,
            int(item.parameters["degree"]),
            float(item.parameters["ridge"]),
        ))
        return ordered[:budget]


class OpenRouterPlanner:
    name = "openrouter-coding-assistant"

    def __init__(self, api_key: str, model: str = "openrouter/free", base_url: str = "https://openrouter.ai/api/v1") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def select(self, candidates: list[ExperimentConfig], budget: int, objective: str, hypothesis: str) -> list[ExperimentConfig]:
        catalog = [{"id": item.experiment_id, **item.parameters} for item in candidates]
        prompt = (
            "You are planning bounded ML experiments. Select a diverse, hypothesis-driven sequence "
            f"of exactly {budget} unique IDs from the catalog. Return only a JSON array of ID strings. "
            f"Objective: {objective}\nHypothesis: {hypothesis}\nCatalog: {json.dumps(catalog)}"
        )
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "temperature": 0}
        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        with urlopen(request, timeout=90) as response:
            message = json.loads(response.read().decode("utf-8"))["choices"][0]["message"]["content"]
        start, end = message.find("["), message.rfind("]")
        selected_ids = json.loads(message[start:end + 1])
        by_id = {item.experiment_id: item for item in candidates}
        if not isinstance(selected_ids, list) or len(selected_ids) != budget or len(set(selected_ids)) != budget:
            raise ValueError("Planner did not return the required number of unique experiment IDs")
        if any(identifier not in by_id for identifier in selected_ids):
            raise ValueError("Planner returned an ID outside the validated search space")
        return [by_id[identifier] for identifier in selected_ids]


def planner_from_environment(mode: str) -> Planner:
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    placeholder = key.lower() in {"", "replace-with-your-openrouter-key"}
    if mode == "heuristic" or (mode == "auto" and placeholder):
        return HeuristicPlanner()
    if placeholder:
        raise ValueError("OPENROUTER_API_KEY is required when --planner openrouter is selected")
    return OpenRouterPlanner(
        key,
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )
