# Part C — Custom ML Autoresearch Harness

This is an original, plugin-driven ML research harness. It takes a research objective, builds an experiment plan, executes bounded experiments, evaluates a held-out metric, ranks candidates, reproduces the winner, saves the best model, and writes a Markdown report plus an append-only event trajectory.

The included `SyntheticRegressionPlugin` is deliberately dependency-free so the complete workflow runs offline on any Python 3.11+ installation. It searches polynomial model degree and ridge regularization against a deterministic noisy dataset.

## Video walkthrough

The complete Part C code explanation and end-to-end autoresearch demonstration are included in this folder:

- [Part C — Custom ML Autoresearch Harness video](./part-c-autoresearch-harness.mp4)

## End-to-end run

```powershell
python part-c-autoresearch-harness/run.py --run-id my-demo --budget 8
```

Generated under `artifacts/my-demo/`:

```text
events.jsonl       append-only research trajectory
experiments.json   complete structured results
leaderboard.csv    candidates sorted by validation MSE
best_model.json    selected model parameters and test score
report.md          objective, hypothesis, results, and conclusion
```

The committed `artifacts/demo/` directory is evidence from a deterministic reference run.

## Optional coding-assistant planning

By default, `--planner auto` uses OpenRouter if `OPENROUTER_API_KEY` is available and otherwise uses the deterministic heuristic planner. The model can only select from the plugin's validated search space; it cannot execute code or invent unbounded configurations.

```powershell
python part-c-autoresearch-harness/run.py --run-id llm-demo --budget 8 --planner openrouter
```

The offline path is a real autoresearch run—not fabricated output. Only the proposal policy changes when an LLM is enabled; training, measurement, ranking, evidence, and artifacts stay deterministic and auditable.

## Harness/plugin separation

The harness owns:

- budgets and stopping;
- planning and validation;
- append-only event logging;
- error isolation;
- leaderboard selection;
- winner reproduction;
- evidence gates and reporting.

The ML plugin owns:

- the research objective and hypothesis;
- dataset creation;
- allowed experiment configurations;
- model training and evaluation;
- model serialization.

Implement `ExperimentPlugin` to attach another ML domain without changing the harness loop.

## Tests

```powershell
python -m unittest discover -s part-c-autoresearch-harness/tests -v
```

Tests verify deterministic data, parameter validation, model quality, experiment ranking, reproduction, and required artifacts.

## References

- [WecoAI awesome-autoresearch](https://github.com/WecoAI/awesome-autoresearch)
- [Harness Engineering](https://harnessengineering.vizuara.ai/)
- [Agent Harness overview](https://vizuaraai.github.io/vizuara-ai-daily/agent-harness/)

These references informed the harness boundaries. The experiment engine and plugin contract here are original implementations.
