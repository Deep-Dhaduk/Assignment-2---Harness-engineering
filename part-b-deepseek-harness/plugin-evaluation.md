# Five-Plugin Evaluation and Demo Record

Do not claim that a community plugin is installed until the corresponding Creator Mode result and visible behavior have been recorded.

| Plugin | Source | Why selected | Demo evidence to capture |
|---|---|---|---|
| Project Memory | `custom-plugins/project-memory` | Original persistent second brain | Tool call, saved note, successful search |
| Evidence Gate | `custom-plugins/evidence-gate` | Original completion-quality gate | Record evidence, check returns `ready: true` |
| Better Sidebar | https://github.com/omdsh-dev/DSH-better-sidebar | Adds useful project navigation surfaces | Visible sidebar and one registered page |
| Sidenote | https://github.com/g-yixuan/dsh-sidenote | Keeps branch questions beside the main conversation | Open `/side` and run one side prompt |
| Token Viewer | https://github.com/qwert702/dsh-token-viewer | Read-only session usage evidence | Show the token strip and usage details |

## Review checklist for every third-party plugin

- [ ] Read its README, license, manifest, install scripts, and requested permissions.
- [ ] Pin the exact version or commit used in the video.
- [ ] Check that the release supports the installed DeepSeek Harness version.
- [ ] Do not install unexpected build scripts without understanding them.
- [ ] Capture the Plugin Manager activation result.
- [ ] Demonstrate visible or model-facing functionality.
- [ ] Record failures honestly rather than describing registration as successful execution.

## Recording log

This table records the completed local demonstration.

| Plugin | Version/commit | Installed | Demonstrated | Notes |
|---|---|---:|---:|---|
| Project Memory | 1.0.0 local | Yes | Yes | Added and searched the Part A architecture note |
| Evidence Gate | 1.0.0 local | Yes | Yes | Claim supported; `ready=true` |
| Better Sidebar | 0.19.1 | Yes | Yes | Opened `assignment-evidence-gate.json` in Files |
| Sidenote | 0.4.1 | Yes | Yes | Opened and used a side conversation |
| Token Viewer | 0.2.1, commit `966f632c3d3ca383679e129be6a7fec01329e353` | Yes | Yes | Displayed session token usage |

An attempted `dsh-reminder` GitHub install was removed after its checkout lacked the declared compiled `lib/index.js`; it is not counted as an installed or demonstrated plugin.
