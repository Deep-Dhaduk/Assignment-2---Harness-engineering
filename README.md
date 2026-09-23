# Assignment 2 — Harness Engineering

This repository contains all three deliverables for the harness-engineering assignment:

1. **Part A — OpenRouter coding harness:** a coding agent built from scratch with a bounded tool loop, safe workspace tools, transcript logging, offline demo mode, and live OpenRouter support.
2. **Part B — DeepSeek Harness customization:** five demonstrated plugins, including two original, installable Cordis/DeepSeek Harness plugins (`project-memory` and `evidence-gate`).
3. **Part C — ML autoresearch harness:** a plugin-driven, end-to-end experiment loop that plans, trains, evaluates, ranks, reproduces, and reports ML experiments.

No API key is committed. Parts A and C both support deterministic offline demonstrations, while an OpenRouter key enables their live model paths.

## Quick start

Requirements: Python 3.11+ and Node.js 20+.

```powershell
Copy-Item .env.example .env

# Part A: deterministic demo of the complete agent/tool loop
python part-a-openrouter-harness/run.py --demo

# Part A: live request after adding OPENROUTER_API_KEY to .env
python part-a-openrouter-harness/run.py "Create a Python file named hello.py and test it"

# Part B: test the two original plugin implementations
npm.cmd test --prefix part-b-deepseek-harness/custom-plugins/project-memory
npm.cmd test --prefix part-b-deepseek-harness/custom-plugins/evidence-gate

# Part C: execute the complete autoresearch workflow offline
python part-c-autoresearch-harness/run.py --run-id my-demo --budget 8

# Run every automated test
python -m unittest discover -s part-a-openrouter-harness/tests -v
python -m unittest discover -s part-c-autoresearch-harness/tests -v
```

## Repository map

```text
.
├── part-a-openrouter-harness/       # coding agent built from scratch
├── part-b-deepseek-harness/         # DSH setup, plugin plan, two custom plugins
├── part-c-autoresearch-harness/     # end-to-end custom ML research harness
├── docs/                            # architecture, traceability, video scripts
├── .env.example                     # safe configuration template
└── .github/workflows/tests.yml      # repeatable CI verification
```

## Submission evidence

- [Requirements traceability](docs/requirements-traceability.md)
- [Architecture](docs/architecture.md)
- [Part A video walkthrough](part-a-openrouter-harness/part-a-openrouter-harness.mp4)
- [Part B video walkthrough](part-b-deepseek-harness/part-b-deepseek-harness.mp4)
- [Part C video walkthrough](part-c-autoresearch-harness/part-c-autoresearch-harness.mp4)
- [Part A documentation](part-a-openrouter-harness/README.md)
- [Part B documentation](part-b-deepseek-harness/README.md)
- [Part C documentation](part-c-autoresearch-harness/README.md)

The three walkthrough videos are stored with their corresponding deliverables.

## Academic integrity and security

The implementations are original assignment code. Upstream projects are cited in the relevant READMEs and were used to understand public interfaces, not copied as submissions. Never commit `.env`, API keys, DeepSeek profile data, or private experiment data.
