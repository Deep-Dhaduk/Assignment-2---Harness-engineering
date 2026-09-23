# Evidence Gate

An original DeepSeek Harness Host plugin that registers `evidence_gate`. It stores claims and test/file/metric/citation/demo evidence in `assignment-evidence-gate.json` under `DSH_PROFILE_DIR`.

`check` returns `ready: true` only when at least one claim exists and every recorded claim has a passing evidence item. Failed evidence remains visible for auditability.

The plugin has no install scripts, runtime dependencies, network calls, or command execution. Install this directory as a bundle from Creator Mode with `plugin_manager`.
