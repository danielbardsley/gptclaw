# ACCEPTANCE-027: Private dashboard project inventory

- **Status:** In progress — local, container and browser evidence; CI/private operator/owner gates pending
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-027](spec.md) · **Design:** [TDD-027](technical-design.md) · **Tasks:** [TASKS-027](tasks.md)
- **Source:** isolated `codex/dashboard-specs` worktree; inventory increment prepared for [PR #69](https://github.com/danielbardsley/gptclaw/pull/69)

## Criterion mapping

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | Passed locally | Four synthetic schema topologies appear once in deterministic order; group children/non-projects excluded; duplicate IDs lose target bindings. Live read-only scan found 13 valid distinct project rows. |
| AC-002 | Passed locally | Synthetic valid/missing/invalid/stale metadata and file-presence fixtures retain manifest identity and honest fields; provider unavailable/unsupported remains separate from health; input declarations are not rewritten. |
| AC-003 | Passed locally | Unsafe paths, symlinks, hardlinks, FIFO, malformed/oversized/unreadable manifests, directory replacement, scan/time/output/diagnostic bounds and synthetic-secret projection tests pass. Discovery execution/network spies pass; pinned validation includes group paths. |
| AC-004 | Pending | Actual loopback production frontend runs rootlessly as forge with only standalone/static assets and the collector socket mounted. HTTP checks return 405 for mutations, 400 for arbitrary parameters and 403 for foreign Host/Origin. Operator creation of the absent approved `/srv/forge/platform` base, owned user-service rollout, exact private Serve route/Funnel-off evidence and owner tailnet desktop access remain. |
| AC-005 | Pending final environment | Browser checks pass for semantic inventory table, keyboard skip navigation, escaped names, metadata gaps, empty/partial/stale/outage/recovery states. Full offline repository gate passes. CI and owner/live acceptance are still pending and are not inferred from local results. |

## Executed verification

From the isolated worktree on the project volume:

- `/srv/forge/projects/gptclaw/.venv-manifest/bin/python -B scripts/tests/test_project_manifest.py`: 27 existing tests passed after the additive pinned-directory validator change.
- Same interpreter, `scripts/tests/test_dashboard_inventory.py`: 12 tests passed.
- Same interpreter, `scripts/tests/test_dashboard_collector.py`: 4 tests passed.
- Same interpreter, `scripts/tests/test_dashboard_install.py`: 7 release/socket ownership and recovery tests passed; all fixtures are isolated, with host commands mocked.
- Pinned rootless Node 24.21.0 / pnpm 12.10.1 container: frozen install, three HTTP-boundary tests, `pnpm typecheck` and `pnpm build` passed.
- `PATH=/srv/forge/projects/gptclaw/.venv-manifest/bin:$PATH ./scripts/check-repository.sh`: full offline repository gate passed, including all existing suites and registered dashboard tests.
- `bash -n scripts/check-repository.sh`, dashboard Python parsing and `git diff --check`: passed. Relative links in all three planning sets and the platform/runbook documentation passed.
- Actual production frontend on `127.0.0.1:18201` connected to the task-owned collector; real HTTP checks passed and the pinned Playwright 1.64.0 browser ran `scripts/tests/dashboard-browser.cjs` successfully. Its screenshot is task-owned ignored verification output, not committed project data.

The initial build hit root-volume ENOSPC after successful compilation/type checks.
Only this task's worktree/build assets moved to the project volume; the subsequent
production build passed. Synthetic fixture/assertion failures were corrected and
rerun; the real browser run passed. The portable CI-equivalent `scripts/tests/check_dashboard.py` also passed after
shortening its task-owned socket path to fit the Unix-socket limit; it exercised frozen
install, tests, type generation/typecheck, production build, four synthetic topologies,
real HTTP restrictions and all browser scenarios. No Terraform change or local apply ran.

## Remaining delivery and acceptance

Record the committed inventory revision, exact CI result and installed release/image/
provider identity. Roll out only the owned dashboard units through the reviewed
manager, verify restart/rollback and private listeners/mounts, then complete the scoped
operator Serve step from the [runbook](../../runbooks/manage-dashboard.md). The owner
must open the actual dashboard in a tailnet desktop browser. Merge and final per-criterion
acceptance remain pending; DSH-001 is not Delivered. Preserve all project data, existing
services/routes and unknown configuration. DSH-002 and DSH-003 are separately authorized
and follow this inventory foundation; this record claims no status/link acceptance.

Live release preparation initially refused Podman's unprefixed image ID; normalization
and a regression test now pass. The subsequent attempt identified an operational
prerequisite: the approved platform directory is absent and forge lacks write access
to its parent. The CLI now reports `operator-required` for that exact directory. No
privilege/parent-permission workaround, AWS mutation or partial service install ran.

At inventory head `3d8a3bb`, existing private-app and both Terraform CI workflows
passed. The new dashboard workflow passed offline tests/install/frontend build but
failed its fresh browser-image build because Docker requires an explicit Containerfile
path (local Podman reuse had masked that difference). The helper now supplies the
exact recipe path; a fresh-image portable rerun and new CI result are required.

The fresh pinned browser-image build and portable exact frontend/socket/HTTP/browser
gate passed after the explicit Containerfile correction. A further boundary regression
allows legitimate top-level navigation from an external link while continuing to deny
cross-origin API data reads; three frontend tests and actual HTTP checks pass. Partial
scans retain earlier rows with a visible stale metadata label and remove their active
target bindings; a fourth collector test covers partial-to-complete recovery. Final
CI results on this corrected inventory head remain pending.
