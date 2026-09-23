# Part A — OpenRouter Coding Harness From Scratch

This is a small coding-agent harness implemented directly with Python's standard library. It does not use LangChain, Pydantic AI, or an agent SDK. The implementation exposes tools to an OpenRouter model, executes requested tools locally, returns results, and repeats until the model produces a final answer.

## Video walkthrough

The complete Part A code explanation and execution demonstration is included in this folder:

- [Part A — OpenRouter Coding Harness video](./part-a-openrouter-harness.mp4)

## Features

- OpenRouter Chat Completions API with `openrouter/free` by default.
- OpenAI-compatible function/tool calling.
- Multiple tool calls per model response.
- Workspace-confined file listing, reading, and writing.
- A command runner with an executable allowlist and no shell expansion.
- Maximum-step and output-size limits.
- JSON transcript artifacts for audit and replay.
- A deterministic offline model for demonstrations and automated tests.
- Zero runtime dependencies outside Python 3.11+.

## Run offline first

From the repository root:

```powershell
python part-a-openrouter-harness/run.py --demo
```

The demo asks the scripted model to create `hello.py`, read it, execute it, and finish. It exercises the same agent loop and tools used by the live model.

## Run with OpenRouter

Copy `.env.example` to `.env`, add your key, and run:

```powershell
python part-a-openrouter-harness/run.py "Create calculator.py with add and subtract functions, then test it"
```

Optional flags:

```text
--workspace PATH   directory the agent may access (default: current directory)
--model MODEL      override OPENROUTER_MODEL
--max-steps N      bound model/tool iterations
--artifact PATH    save the JSON trajectory at a chosen path
--demo             use the offline scripted model
```

## Agent loop

```text
task + tool schemas → model → tool calls? ── no ─→ final answer
                              │
                             yes
                              ↓
                    validate and execute tools
                              ↓
                    append results to history
                              └──────────────→ model
```

The model proposes tool calls; it never directly touches the computer. `Agent.run()` owns execution, validation, logging, and the stopping condition.

## Safety boundaries

- File paths are resolved and rejected when they escape the selected workspace.
- File reads and command output are truncated to configured limits.
- Commands are passed as argument arrays with `shell=False`.
- Only `python`, `py`, `pytest`, `git`, `node`, and npm executables are permitted.
- Dangerous Git subcommands are rejected.
- The loop stops after `HARNESS_MAX_STEPS`.

This is an educational local harness, not a hardened multi-tenant sandbox. Run it only in a disposable project and review changes before committing.

## Tests

```powershell
python -m unittest discover -s part-a-openrouter-harness/tests -v
```

## References

- [OpenRouter quickstart](https://openrouter.ai/docs/quickstart)
- [OpenRouter tool calling](https://openrouter.ai/docs/guides/features/tool-calling)
- [Simple Coding Harness](https://github.com/dlmastery/simple-coding-harness) — assignment reference only
- [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) — conceptual reference
