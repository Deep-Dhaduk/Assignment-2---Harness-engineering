# Architecture

## Part A — Coding harness

```text
CLI
 │ loads task, workspace, configuration
 ▼
Agent loop ────────► ModelClient
 │                    ├─ OpenRouterClient (live)
 │                    └─ ScriptedDemoClient (offline/test)
 │ assistant tool calls
 ▼
WorkspaceTools
 ├─ list_files
 ├─ read_file
 ├─ write_file
 └─ run_command (allowlist, no shell)
 │
 └─ tool results ───► message history ───► next model step

Every message and tool result ───► trajectory JSON
```

The model is a planner, not an executor. Only the harness can invoke tools. Path confinement, command allowlisting, response truncation, and maximum steps bound execution.

## Part B — DeepSeek Harness plugins

```text
Creator Mode / profile
          │ plugin_manager install_bundle
          ▼
package.json ──► dsh.bundle.patch ──► Host plugin apply(ctx)
                                              │
                                      ctx.tools.register(...)
                                      ┌───────┴────────┐
                                      ▼                ▼
                              project_memory     evidence_gate
                                      │                │
                                      └──── JSON in DSH_PROFILE_DIR
```

Both custom plugins are Host-only Cordis bundles with no build step or dependencies. The action logic is kept separate from Harness registration so persistence behavior can be tested without a running UI.

## Part C — Autoresearch harness

```text
Objective + hypothesis
          ▼
Planner ──► validated, budget-bounded experiment plan
          ▼
AutoresearchHarness ──► ExperimentPlugin.run_experiment(...)
          │                         │
          │                         ├─ deterministic data
          │                         ├─ train polynomial model
          │                         └─ validation MSE
          ▼
Leaderboard ──► reproduce winner ──► held-out test evaluation
          ▼
Evidence gate ──► model + report + CSV + JSON + event stream
```

The planner may be heuristic or OpenRouter-assisted. In either mode it can only select IDs from the plugin's prevalidated search space. The orchestration layer owns budgets, errors, audit events, selection, reproduction, and reporting; the plugin owns the ML domain.
