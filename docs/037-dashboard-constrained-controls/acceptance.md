# SPEC-037 acceptance evidence

- **Status:** Implementation in progress; acceptance incomplete
- **Owner:** Project owner
- **Date:** 2026-10-15 (America/New_York)
- **Specification:** [SPEC-037](spec.md) · **Design:** [TDD-037](technical-design.md) · **Tasks:** [TASKS-037](tasks.md)
- **Branch:** `codex/dsh-009-controls`

The project owner authorized implementation and completion against the acceptance
criteria October 15. This record separates synthetic local evidence from actual
runtime, CI, private rollout and owner acceptance. No criterion is established by
planned commands or by the supplied visual reference.

| Criterion | Current disposition | Evidence / remaining work |
|---|---|---|
| AC-001 | Partial local coverage | Provider capability matrix and refusal tests cover supported profiles, invalid actions/components, changed source and lock conflicts. Real Metro/old-provider/unsafe-target and release compatibility evidence still needs completion. |
| AC-002 | Partial local coverage | Synthetic native-engine tests verify pause ordering/same-instance resume, build-before-replace, stopped rebuild retention and failure preservation. Actual staged-output publication, native pause/rebuild and interruption scenarios remain. |
| AC-003 | Partial local coverage | Web restart preserves API identity; selected DB primitive preserves its generation/credential epoch and leaves app instances untouched; dependent health failure does not cascade. Actual persistent records, route recovery and Metro/backend isolation require runtime evidence. |
| AC-004 | Partial local coverage | Thirteen isolated controller tests and frontend boundary tests cover sessions/CSRF/Origin, strict JSON/unknown fields, typed actions, duplicate/replayed/expired/changed intents, capacity and socket rejection. Full browser/socket integration and deployed restricted mounts remain to verify. |
| AC-005 | Partial local coverage | Synthetic tests retain a durable guard/journal after timeout, prevent a second writer, reconcile without replay, handle lost acceptance/idempotency and preserve unknown results across controller restart. Worker-death/storage-error/native reconciliation scenarios remain to complete. |
| AC-006 | Pending browser acceptance | Frontend unit/typecheck/build passes; reference-derived panel and scoped confirmations implemented. Initial browser run exposed a test fixture initialization error; corrected placement is under verification. Final viewport/focus/results/contrast and owner comparison remain pending. |
| AC-007 | In progress | Offline gate and browser verification underway. Final-head CI, authorized private rollout, owned fixture acceptance, rollback, project-owner acceptance and merged delivery remain pending. |

## Local checks observed so far

- `scripts/tests/test_project_groups.py`: 16 existing group tests passed after initial lifecycle extension.
- `scripts/tests/test_project_controls.py`: 16 focused tests passed, including generated-output swaps and SIGKILL guard/reconciliation behavior. Subsequent Metro preflight refinements remain under verification.
- `scripts/tests/test_dashboard_controls.py`: 13 isolated controller tests passed, including admission-time storage failure recovery and refusal of delayed reconciled workers.
- `scripts/tests/test_dashboard_install.py`: 10 release/ownership/rollback tests passed.
- Frozen `pnpm install` in the existing rootless Node image passed with the repository lockfile and pinned pnpm 12.10.1.
- Frontend tests: 21 passed (including a real Unix-socket frontend boundary and stalled-controller/healthy-inventory regression); route type generation/TypeScript and production build passed in the existing pinned rootless environment.
- The first attempted frontend test used a container with network disabled before dependencies existed. It failed fetching dependencies; only that exact task-owned container was stopped after command/network/mount verification. The subsequent explicit frozen setup succeeded. No host packages were installed.
- The first browser run failed in the newly added synthetic test block because it ran before the shared layout fixture was initialized. This was a test placement error; it was moved after baseline browser scenarios. A corrected full run passed, including confirmation/cancel/focus, lost-response recovery without replay, scope/busy/generation checks and responsive captures. It also exposed and verified fixes for browser wall-clock skew and focus return before React enabled the initiating button. Subsequent semantic/freshness refinements need the final rerun.

An intermediate full `./scripts/check-repository.sh` run completed successfully: 874 cases across 46 unittest suites, plus the shell/source invariants. This is intermediate working-tree evidence; later refinements still need the final gate.

The local native single-service harness passed start/no-op, same-instance pause/resume, component restart, running rebuild, stop and stopped rebuild against real rootless containers. It reused matching verified toolchain images and removed its task-owned aliases/containers/networks. Its systemd/Serve interface is a test adapter; it is not deployed systemd/private acceptance. Web/API group and database native checks remain in progress.

The first native harness attempts refused a wrong catalogue ID, then failed cold isolated toolchain construction before an app started. The harness was corrected to the released `fastify` ID and to reverify/reuse existing matching images. Failed task-owned source/receipt stages remain ignored and private until scoped cleanup.

Final verification is not yet claimed passed. Generated check logs/captures stay in
ignored task output; no credentials, environment dumps, source payloads or database
contents are retained in this evidence. Existing user services/data have not been
mutated for acceptance. No private rollout or owner acceptance has occurred.
