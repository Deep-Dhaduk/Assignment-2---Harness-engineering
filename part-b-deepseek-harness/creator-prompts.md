# Creator Mode Prompts

These prompts document how the two original plugins were specified and provide reproducible evidence for the assignment.

## Prompt 1 — Project Memory

```text
Create a persistent Host-only Cordis bundle named @assignment/project-memory for DeepSeek Harness.
It must register one model-facing tool named project_memory with add, list, search, and remove actions.
Store notes as JSON inside DSH_PROFILE_DIR, validate all user input, never execute shell commands,
and return a concise text rendering plus structured JSON. Include package.json, cordis.patch.yml,
index.js, isolated storage logic, a README, and Node tests. Make the bundle installable by Creator
Mode's plugin_manager without a build step.
```

## Prompt 2 — Evidence Gate

```text
Create a persistent Host-only Cordis bundle named @assignment/evidence-gate for DeepSeek Harness.
It must register an evidence_gate tool that records evidence for claims, lists evidence, and checks
whether every recorded claim has at least one passing item. Evidence kinds are test, file, metric,
citation, and demo; statuses are passed and failed. Persist JSON under DSH_PROFILE_DIR, do not use
the network or shell, and return a ready boolean with counts. Include a manifest, bundle patch,
Host plugin, isolated storage logic, README, and Node tests with no build step.
```

## Installation prompt

```text
Inspect this local bundle, install it with plugin_manager install_bundle, enable it in the current
profile, report the activation outcome, and verify its tool registration:
<ABSOLUTE_PLUGIN_DIRECTORY>
```

## Agent-preset customization prompt

```text
Create a preset named Assignment Researcher based on Standard. Keep filesystem and shell tools,
enable project_memory and evidence_gate, and add a system instruction requiring evidence_gate
to be ready before claiming an implementation is complete. Do not alter the Standard preset.
```
