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
| AC-002 | Partial local coverage | Synthetic tests and isolated real-container single/group runs verify pause ordering/same-instance resume, build-before-replace, stopped rebuild retention and failure preservation. Deployed systemd/publication and remaining interruption scenarios still require acceptance. |
| AC-003 | Partial local coverage | Web restart preserves API identity; selected DB primitive preserves its generation/credential epoch and leaves app instances untouched; dependent health failure does not cascade. Actual persistent records, route recovery and Metro/backend isolation require runtime evidence. |
| AC-004 | Partial local coverage | Thirteen isolated controller tests and frontend boundary tests cover sessions/CSRF/Origin, strict JSON/unknown fields, typed actions, duplicate/replayed/expired/changed intents, capacity and socket rejection. Full browser/socket integration and deployed restricted mounts remain to verify. |
| AC-005 | Partial local coverage | Synthetic tests retain a durable guard/journal after timeout, prevent a second writer, reconcile without replay, handle lost acceptance/idempotency and preserve unknown results across controller restart. Worker-death/storage-error/native reconciliation scenarios remain to complete. |
| AC-006 | Automated browser checks passed; owner pending | Frozen frontend unit/typecheck/build and the full synthetic browser run passed, including viewport/focus/results/contrast, lost-response recovery, scoped confirmation and unchanged metrics. Actual owner comparison, keyboard and zoom acceptance remain pending. |
| AC-007 | In progress | Offline gate and browser verification underway. Final-head CI, authorized private rollout, owned fixture acceptance, rollback, project-owner acceptance and merged delivery remain pending. |

## Local checks observed so far

- `scripts/tests/test_project_groups.py`: 16 existing group tests passed after initial lifecycle extension.
- `scripts/tests/test_project_controls.py`: 20 focused tests passed, including generated-output swaps, SIGKILL guard/reconciliation, Metro running-start no-op/short-lease stop, fixed absolute expiry/backend isolation, stable intent identity across observation refresh and refusal of false protocol readiness. An additional focused partial-pause test passed: a timeout after freezing WEB retains the guard, blocks Resume until reconciliation, reports mixed pause state, and allows an explicit Stop to unfreeze before stopping without replacing instances. The full gate will include all 21 tests.
- `scripts/tests/test_dashboard_controls.py`: 13 isolated controller tests passed, including admission-time storage failure recovery and refusal of delayed reconciled workers.
- `scripts/tests/test_dashboard_install.py`: 11 release/ownership/rollback tests passed, including older stable-provider refusal before any service change while reads remain available.
- Frozen `pnpm install` in the existing rootless Node image passed with the repository lockfile and pinned pnpm 12.10.1.
- Frontend tests: 21 passed (including a real Unix-socket frontend boundary and stalled-controller/healthy-inventory regression); route type generation/TypeScript and production build passed in the existing pinned rootless environment.
- The first attempted frontend test used a container with network disabled before dependencies existed. It failed fetching dependencies; only that exact task-owned container was stopped after command/network/mount verification. The subsequent explicit frozen setup succeeded. No host packages were installed.
- The first browser run failed in the newly added synthetic test block because it ran before the shared layout fixture was initialized. This was a test placement error; it was moved after baseline browser scenarios. A corrected full run passed, including confirmation/cancel/focus, lost-response recovery without replay, scope/busy/generation checks and responsive captures. It also exposed and verified fixes for browser wall-clock skew and focus return before React enabled the initiating button. Subsequent semantic/freshness refinements need the final rerun.

An intermediate full `./scripts/check-repository.sh` run completed successfully: 874 cases across 46 unittest suites, plus the shell/source invariants. This is intermediate working-tree evidence; later refinements still need the final gate.

The local native single-service harness passed start/no-op, same-instance pause/resume, component restart, running rebuild, stop and stopped rebuild against real rootless containers. The web/API group also passed whole-project restart, web/API restarts, same-instance pause/resume, running/stopped rebuild and unrelated-peer instance/readiness isolation. Real generated ephemeral notes survived a web restart and were lost on the explicitly warned API restart. The API/DB run passed start/no-op, DB/API/project restarts, running/stopped rebuild, synthetic record retention and unrelated-peer identity/readiness isolation. Its database restart retained the exact active volume generation and credential epoch while the API instance continued; application rebuild retained the DB instance. All three runs removed their owned aliases/containers/networks. Their systemd/Serve interface is a test adapter; this is not deployed systemd/private acceptance. Actual managed Metro and web/API/DB acceptance remain pending.

The first native harness attempts refused a wrong catalogue ID, then failed cold isolated toolchain construction before an app started. The harness was corrected to the released `fastify` ID and to reverify/reuse existing matching images. Failed task-owned source/receipt stages remain ignored and private until scoped cleanup.

The full final frontend/browser rerun passed after a project-header assertion was
scoped to the project table: accessible service headers legitimately add their own
row headers. Captures are in ignored `.dashboard-qa/dsh009-final/` at
1440/1280/768/390 px, with 720 CSS px exercising desktop 200% layout reflow.
This does not substitute for actual owner browser zoom acceptance.

## Review and staged rollout proposal

Implementation draft [PR #86](https://github.com/danielbardsley/gptclaw/pull/86)
includes the planning package from #85. Initial dashboard CI failed only at the
browser project-header assertion described above; the corrected final-head CI
still needs to pass. No CI success is inferred from the local result.

The currently active dashboard is release
`355073098b3f810379b1e3a90f0e8a71edb74b3caf1fd98e7e44acf2e9a915de`:
status and links enabled, controls absent; both owned services were observed active.
The stable installed CLI reports 1.14.0; the implementation provider is 1.15.0.
Immutable assets have been staged, without activation, for:

- Controls candidate: `7cfb24c6b8069d4b9024138fa6e31c9498d4be4cf33b41d418ca3da6e2bbbb7e`.
- Compatible read-only rollback: `7af4d32fdd57fc494a13b208084938aaaca0f80e9c266ecf59084eb9253e5349`.

After final verification and separate private rollout approval, use the frozen
candidate provider to start an explicitly owned disposable fixture and upgrade the
verified stable launcher/ingress first. This briefly restarts the shared loopback
router; it must preserve all project processes and private Serve handlers. Then
activate the candidate dashboard, observe its three owned services and restricted
mounts, and run acceptance only against specifically owned synthetic fixtures.
For rollback, disable new submissions, let active operations finish, explicitly
reconcile unknown outcomes and resume/stop paused fixtures as intended, then activate
the compatible read-only release. Preserve runtime data and operation evidence.
Detailed commands and refusal conditions are in the dashboard runbook. These are
proposed effects, not executed rollout evidence or new authorization.

Final repository/native/CI verification is not yet claimed passed. Generated check logs/captures stay in
ignored task output; no credentials, environment dumps, source payloads or database
contents are retained in this evidence. Existing user services/data have not been
mutated for acceptance. No private rollout or owner acceptance has occurred.
