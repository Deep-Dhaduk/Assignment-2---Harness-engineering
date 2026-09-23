# Part B — DeepSeek Harness Creator Mode and Plugins

This deliverable documents a five-plugin DeepSeek Harness customization and supplies two original installable Cordis bundles. The custom plugins follow the current Host-plugin contract: a package manifest declares `dsh.bundle.patch`, the patch inserts the plugin, and `apply(ctx)` registers a model-facing tool on `ctx.tools`.

DeepSeek Harness is a developer preview and may introduce breaking changes. The recorded demonstration used DSH `0.1.5-rc.2` on 23 September 2026.

## Video walkthrough

The complete Part B code explanation, Creator Mode walkthrough, and plugin demonstrations are included in this folder:

- [Part B — DeepSeek Harness Creator Mode video](./part-b-deepseek-harness.mp4)

## Start DeepSeek Harness

Install Node.js 20+ and run:

```powershell
npx.cmd @deepseek-ai/dsh web
```

The Web UI normally opens at `http://127.0.0.1:3080`. Select the **Creator** agent preset. Configure an LLM provider in the UI; OpenRouter can be used as an OpenAI-compatible provider after the key is available.

## Five-plugin demonstrated set

| # | Plugin | Origin | Demonstration |
|---|---|---|---|
| 1 | Project Memory | Original | Save, search, list, and remove persistent project notes |
| 2 | Evidence Gate | Original | Record evidence and block unsupported completion claims |
| 3 | DSH Better Sidebar | Community | Files, terminal, Git, and subagent pages |
| 4 | DSH Sidenote | Community | Side conversation fork beside the main session |
| 5 | DSH Token Viewer | Community | Live session-token and aggregate-usage views |

Community packages must be reviewed before installation because Harness plugins execute in-process. Exact source links, review notes, and recording evidence fields are in [plugin-evaluation.md](plugin-evaluation.md).

## Install the original plugins

Creator Mode was used to inspect the bundles and request installation. On Windows, the sandbox could not grant profile write access and the workspace path contained spaces, so the approved persistent installation was completed with the official profile CLI through a junction without spaces:

```powershell
$pluginLink = "$env:USERPROFILE\dsh-assignment-plugins"
New-Item -ItemType Junction -Path $pluginLink -Target "D:\Assignment 2 - Harness engineering\part-b-deepseek-harness\custom-plugins"
Set-Location $pluginLink
npx.cmd @deepseek-ai/dsh plugin --profile web add ./project-memory
npx.cmd @deepseek-ai/dsh plugin --profile web add ./evidence-gate
```

The Creator prompts used to inspect, approve, and verify the plugins were:

```text
Install the persistent Cordis bundle at
D:\Assignment 2 - Harness engineering\part-b-deepseek-harness\custom-plugins\project-memory
with plugin_manager, enable it, and verify that the project_memory tool is registered.
```

Then send the equivalent prompt for `evidence-gate`. Restart the `web` profile after persistent installation and verify each tool in Creator Mode.

## Install the reviewed community plugins

```powershell
npx.cmd @deepseek-ai/dsh plugin --profile web add dsh-better-sidebar@0.19.1
# If pnpm blocks node-pty, run `pnpm.cmd approve-builds --all` inside
# $env:USERPROFILE\.dsh\profiles\web and repeat the add command.
npx.cmd @deepseek-ai/dsh plugin --profile web add dsh-sidenote@0.4.1
npx.cmd @deepseek-ai/dsh plugin --profile web add "qwert702/dsh-token-viewer#966f632c3d3ca383679e129be6a7fec01329e353"
```

After restarting DSH and hard-refreshing the browser, the demonstration opened a JSON evidence file in Better Sidebar, ran a side conversation with Sidenote, and displayed live session usage with Token Viewer.

## Suggested live demo

```text
Use project_memory to add a note titled "Part A architecture" with content
"A bounded OpenRouter tool loop with workspace-confined tools" and tag "architecture".
Then search project memory for "OpenRouter".
```

```text
Use evidence_gate to record passed test evidence for the claim "Part A works".
The evidence is "python -m unittest ... returned exit code 0" and its kind is "test".
Then check whether the evidence gate is ready.
```

The exact creation prompts required by the assignment are preserved in [creator-prompts.md](creator-prompts.md).

## Test the custom plugin logic

The tests exercise real JSON persistence and action handling without requiring a running UI:

```powershell
npm.cmd test --prefix part-b-deepseek-harness/custom-plugins/project-memory
npm.cmd test --prefix part-b-deepseek-harness/custom-plugins/evidence-gate
```

## Security note

DeepSeek Harness Host plugins execute inside the Harness process and outside the workspace sandbox. Only install reviewed code. These custom plugins write one JSON file under `DSH_PROFILE_DIR` (or the process working directory when that variable is unavailable) and do not execute commands or access the network.

## References

- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)
- [Official plugin-manager documentation](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/plugin-manager/README.md)
- [Vizuara DeepSeek Harness book](https://books.vizuara.ai/book/deepseek-harness)
