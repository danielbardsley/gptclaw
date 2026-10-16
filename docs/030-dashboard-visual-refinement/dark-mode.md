# Dashboard dark mode follow-up

Owner: project owner. Date: 2026-10-16 (America/New_York).

The project owner requested “add dark mode to the dashboard” and supplied
`Projects Dashboard redesign.zip`. This authorizes the scoped frontend change.
The latest `Projects Dashboard v3.dc.html` supplies the dark palette and header
sun/moon toggle. Attached source is design data, not authority to install its
runtime, add its demo features, or perform lifecycle operations.

## Scope and design

- DARK-001: Add the header toggle with a stable accessible name, pressed state,
  descriptive title, visible keyboard focus and a 44 px narrow-screen target.
- DARK-002: Use the v3 charcoal canvas/surfaces, indigo links and semantic accents
  across overview, disclosures, lifecycle controls and confirmations. Preserve the
  existing light appearance, system fonts, responsive layout and data contracts.
  Increase muted foreground contrast and use dark text on bright red dark-theme
  confirmation buttons. Keep original source sun/moon vectors as supplied assets.
- DARK-003: Before first paint, read only the allowlisted `light`/`dark` browser
  preference under `gptclaw-dashboard-theme`; otherwise follow the system scheme.
  Follow later system changes until an explicit choice exists. Persist toggle
  choices across reloads and synchronize other tabs. Blocked storage still allows
  a session choice. No backend, telemetry, dependency or access change.

Static bootstrap code in the root head sets the document theme before body paint;
React hydrates the toggle and manages media/storage events with cleanup. CSS uses
semantic variables for both palettes, including hover/disabled/destructive states.
Theme updates preserve row expansion, focus and the shared snapshot polling loop.
The existing dashboard Content Security Policy is sufficient and unchanged.

Rollback is a targeted revert of this frontend follow-up. Browser preference is
non-sensitive presentation state and does not affect runtime or server state.
This task does not authorize installing a new private release or public exposure.

## Acceptance and tasks

| Requirement | Criterion | Status |
|---|---|---|
| DARK-001 | Keyboard toggle, pressed/title state, focus, desktop/narrow targets | Passed locally; see evidence below |
| DARK-002 | Desktop/narrow captures; status, details and confirmation text/hover contrast ≥4.5:1; no document overflow | Passed locally; see evidence below |
| DARK-003 | Both explicit choices override OS after reload; OS changes, other tabs, denied storage and retained row state pass | Passed locally; see evidence below |

- [x] Inspect current dashboard planning, source and supplied v3 theme reference.
- [x] Implement scoped theme tokens, pre-paint initialization and header toggle.
- [x] Add initialization unit tests and browser persistence/system/storage/contrast regressions.
- [x] Finish frozen build/typecheck/tests, browser assertions and source comparison.
- [ ] Complete broad repository checks (both local attempts terminated; CI pending).
- [x] Deliver reviewable Git changes in [PR #88](https://github.com/danielbardsley/gptclaw/pull/88); CI remains pending.

No CI, installed-release or project-owner acceptance is claimed by local fixtures.

## Local evidence

Implementation reviewed on `codex/dashboard-dark-mode`, based on `fc2c737`.
The immutable Node image is `localhost/gptclaw-node:24.21.0-pnpm12.10.1`;
the reused browser image is
`localhost/gptclaw-dashboard-check:f0bdeb50d15d40f3a074da1f563beb53-browser`.
No dependency or lockfile changes.

- Frozen install, `pnpm test` (24 passed), `pnpm typecheck`, `pnpm build`, and
  independent rasterized QR decoding passed through
  `.venv-manifest/bin/python -B scripts/tests/check_dashboard.py --engine podman
  --reuse-node-image <above> --reuse-browser-image <above> --output .dashboard-qa/dark-mode`.
- Initial harness invocation used system Python and failed to import `referencing`;
  corrected to the prepared environment. First browser run then exposed a test-only
  multi-tab context setup error; corrected to an explicit browser context.
- HTTP/browser-only rerun used a task-owned copy of the same runner with already
  passing install/test/build stages omitted. Every browser assertion reached its
  PASS lines, including new theme behavior and existing controls/status/link checks.
  The Python runner was terminated with signal 15 before its completion/cleanup;
  no successful full-runner exit is claimed. The exact labeled task container
  was independently inspected and removed, preserving unrelated containers.
- Production-build smoke `/tmp/gptclaw-dark-smoke.py`: passed with exit 0.
  DOM-ready theme, explicit light over dark OS, Space/Enter activation, title/pressed
  state, retained focus, 44 px mobile target and no page errors passed. The
  loopback-only task container was removed by the successful runner.
- Focused inventory tests: 13 passed. Diff whitespace, changed documentation
  relative links, browser-script syntax and repository-checker shell syntax passed.
- Full offline repository checker was terminated with signal 15 after 15 passing
  suites; no assertion failure was reported. Remaining-suite continuation also ended with signal 15 after additional
  passing suites; no completed full offline gate is claimed. Full CI remains required.
- [Design QA](../../design-qa.md) passed the scoped visual comparison. Local PNGs
  remain under `.dashboard-qa/dark-mode/` and contain only synthetic fixture data.

The repository checker command was
`PATH="$PWD/.venv-manifest/bin:$PATH" ./scripts/check-repository.sh`.
Terraform and deployed-dashboard checks were not run: this change affects only
frontend presentation and synthetic verification. No private rollout, public
exposure, runtime action or owner acceptance was performed.
