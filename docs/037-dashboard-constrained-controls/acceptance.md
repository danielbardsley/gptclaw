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
| AC-001 | Partial automated coverage | Provider capability/refusal tests and final-head dashboard CI cover supported profiles, invalid actions/components, changed source, lock conflicts and older stable-provider refusal. Actual managed Metro and deployed release compatibility remain pending. |
| AC-002 | Partial local coverage | Synthetic tests and isolated real-container single/group runs verify pause ordering/same-instance resume, build-before-replace, stopped rebuild retention and failure preservation. Deployed systemd/publication and remaining interruption scenarios still require acceptance. |
| AC-003 | Partial runtime coverage | Real-container WEB restart preserved API identity/data; API/DB restarts and rebuilds preserved synthetic persistent records, the active volume and credential epoch. Dependent health failure tests do not cascade. Deployed route recovery and actual Metro/backend isolation remain pending. |
| AC-004 | Partial local coverage | Thirteen isolated controller tests and frontend boundary tests cover sessions/CSRF/Origin, strict JSON/unknown fields, typed actions, duplicate/replayed/expired/changed intents, capacity and socket rejection. Full browser/socket integration and deployed restricted mounts remain to verify. |
| AC-005 | Partial automated coverage | Tests cover SIGKILL, timeouts, admission/storage failures, partial pause, retained guards, retry exclusion, explicit reconciliation without replay, lost acceptance/idempotency and controller restart. Deployed interruption/recovery scenarios remain pending. |
| AC-006 | Automated browser checks passed; owner pending | Frozen frontend unit/typecheck/build and the full synthetic browser run passed, including viewport/focus/results/contrast, lost-response recovery, scoped confirmation and unchanged metrics. Actual owner comparison, keyboard and zoom acceptance remain pending. |
| AC-007 | In progress | All four CI workflows passed at revision 7e295de; the local gate passed 882 cases/46 suites and all five non-Metro native profile runs passed. The later frontend JSON transport correction passed local frontend/browser checks and needs its publication/CI checkpoint. Private rollout is approved; execution, managed-fixture acceptance, rollback, project-owner acceptance and merge remain pending. |

## Local checks observed so far

- `scripts/tests/test_project_groups.py`: 16 existing group tests passed after initial lifecycle extension.
- `scripts/tests/test_project_controls.py`: 20 focused tests and an additional focused partial-pause test passed locally; the complete 21-test suite passed in final-head dashboard CI. Coverage includes generated-output swaps, SIGKILL guard/reconciliation, Metro running-start no-op/short-lease stop, fixed absolute expiry/backend isolation, stable intent identity across observation refresh and refusal of false protocol readiness. A timeout after freezing WEB retains the guard, blocks Resume until reconciliation, reports mixed pause state, and allows an explicit Stop to unfreeze before stopping without replacing instances.
- `scripts/tests/test_dashboard_controls.py`: 13 isolated controller tests passed, including admission-time storage failure recovery and refusal of delayed reconciled workers.
- `scripts/tests/test_dashboard_install.py`: 11 release/ownership/rollback tests passed, including older stable-provider refusal before any service change while reads remain available.
- Frozen `pnpm install` in the existing rootless Node image passed with the repository lockfile and pinned pnpm 12.10.1.
- Frontend tests: 21 passed (including a real Unix-socket frontend boundary and stalled-controller/healthy-inventory regression); route type generation/TypeScript and production build passed in the existing pinned rootless environment.
- The first attempted frontend test used a container with network disabled before dependencies existed. It failed fetching dependencies; only that exact task-owned container was stopped after command/network/mount verification. The subsequent explicit frozen setup succeeded. No host packages were installed.
- The first browser run failed in the newly added synthetic test block because it ran before the shared layout fixture was initialized. This was a test placement error; it was moved after baseline browser scenarios. Corrected full local and CI runs passed, including confirmation/cancel/focus, lost-response recovery without replay, scope/busy/generation checks, responsive captures and subsequent semantic/freshness refinements. The checks also exposed and verified fixes for browser wall-clock skew and focus return before React enabled the initiating button.

An intermediate full `./scripts/check-repository.sh` run completed successfully: 874 cases across 46 unittest suites, plus the shell/source invariants.

The later local gate ended with signal 143 during the worktree suite, before a
terminal test summary; completed suites had reported no failure. Its handle was
terminal and no child test processes remained before replacement. A bounded
replacement completed against `7e295ded15215dedd06a61c21a2fb5303e2dbccd`, with
task-owned log/result metadata under `/tmp/dsh009-repository-final-7e295de/`.
It passed with exit 0: 882 cases across 46 suites plus the repository invariants.
The interrupted attempt itself is not a passing gate. Later edits change only
frontend transport, optional native verification and documentation; Python provider
code remains identical to this passing checkpoint.

The local native single-API harness passed start/no-op, same-instance pause/resume, component restart, running rebuild, stop and stopped rebuild against real rootless containers. The web/API group also passed whole-project restart, web/API restarts, same-instance pause/resume, running/stopped rebuild and unrelated-peer instance/readiness isolation. Real generated ephemeral notes survived a web restart and were lost on the explicitly warned API restart. The API/DB run passed start/no-op, DB/API/project restarts, running/stopped rebuild, synthetic record retention and unrelated-peer identity/readiness isolation. Its database restart retained the exact active volume generation and credential epoch while the API instance continued; application rebuild retained the DB instance. Additional single-WEB and WEB/API/DB runs passed applicable lifecycle actions, running/stopped rebuild and retention/isolation; the persistent group also refused Pause/Resume without instance changes and retained both app siblings during DB restart. All five runs removed their owned aliases/containers/networks and successful fixture trees. Their systemd/Serve interface is a test adapter; this is not deployed systemd/private acceptance. Managed runtime acceptance remains pending.

The first native harness attempts refused a wrong catalogue ID, then failed cold isolated toolchain construction before an app started. The harness was corrected to the released `fastify` ID and to reverify/reuse existing matching images. Failed task-owned source/receipt stages remain ignored and private until scoped cleanup.

The full final frontend/browser rerun passed after a project-header assertion was
scoped to the project table: accessible service headers legitimately add their own
row headers. Captures are in ignored `.dashboard-qa/dsh009-final/` at
1440/1280/768/390 px, with 720 CSS px exercising desktop 200% layout reflow.
This does not substitute for actual owner browser zoom acceptance.

Before activation, a new transport regression reproduced that parsing/reserializing
at the frontend erased duplicate keys before the controller could reject them
(unexpected HTTP 200 versus expected 400 in the Unix-socket fixture). The frontend
now forwards the original bounded bytes; duplicate-key, malformed and invalid-UTF8
inputs reach the strict authoritative parser unchanged. The complete frozen local
frontend tests (21), typecheck, production build, HTTP/socket and browser checks
passed after this correction. No new dependency or request route was introduced.

## Review and staged rollout proposal

Implementation draft [PR #86](https://github.com/danielbardsley/gptclaw/pull/86)
includes the planning package from #85. Initial dashboard CI failed only at the
browser project-header assertion described above. At revision
`7e295ded15215dedd06a61c21a2fb5303e2dbccd`, corrected
[dashboard CI #100](https://github.com/danielbardsley/gptclaw/actions/runs/38797555283)
and [application CI #203](https://github.com/danielbardsley/gptclaw/actions/runs/38797555161)
passed. Dashboard logs explicitly record 21 lifecycle tests, 13 controller tests,
11 installer tests, and full frontend/browser acceptance.
[Development-host CI #302](https://github.com/danielbardsley/gptclaw/actions/runs/38797555071)
and [federation CI #206](https://github.com/danielbardsley/gptclaw/actions/runs/38797555227)
also passed at that revision. These were PR quality checks, not infrastructure
apply or runtime deployment evidence. Subsequent frontend transport, optional
native-harness and documentation edits need their publication/CI checkpoint.

The pre-rollout dashboard was release
`355073098b3f810379b1e3a90f0e8a71edb74b3caf1fd98e7e44acf2e9a915de`:
status and links enabled, controls absent; both owned services were observed active.
The stable installed CLI reports 1.14.0; the implementation provider is 1.15.0.
Immutable assets have been staged, without activation, for:

- Controls candidate: `90520b389e487fcce01110e8e13c58f58bfed5ab2e3cce378215fdf99b8ced04`.
- Compatible read-only rollback: `ee3bb086e44d04aac9505f623dfc625207ccdce385363e0d766a700635745b31`.

These replace the earlier unactivated 7cfb24c6/7af4d32f candidates after the
frontend transport correction. Both retain the same frozen provider
`c91b4a26c7909e75d3fbe451c1784f5b09d8730c86c62bdc0a0e8a3fcdcef206`.

The project owner explicitly approved private rollout and fixture acceptance after
the remaining checks pass, including disposable single/group/DB fixtures and the
retained synthetic Metro fixtures `mob001-accept-one` and `mob001-accept-two`.
Read-only inspection found both named canonical checkouts clean on their existing
Metro contract branches. Their old sessions are expired/stopped; acceptance will
use fresh finite sessions through the reviewed provider, without extending an old
lease. Readback found the named fixtures' 8443/8444 listeners absent; the existing
443 dashboard/projects and separate 8445 handler remain intact, with Funnel off.
The [exact operator handoff](operator-plan.md) prepares scoped additions/removal
through the existing operator path; no Tailscale mutation has been executed.

After final verification, use the frozen
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

### First approved private activation and route correction

All four workflows passed on `8cb6e0aee4329eef92d8fa7505d5e71502c8ac72`:
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38803942019),
[application](https://github.com/danielbardsley/gptclaw/actions/runs/38803942009),
[development host](https://github.com/danielbardsley/gptclaw/actions/runs/38803941881)
and [federation](https://github.com/danielbardsley/gptclaw/actions/runs/38803941933).
The application workflow's first mobile job timed out downloading pnpm during
bootstrap; rerunning only that failed job at the same revision passed. No project
test failed in that attempt and no package pin changed.

After those checks, the approved disposable API peer started through provider
1.15.0. The owned stable launcher/ingress upgraded to the exact frozen provider.
Candidate `90520b38…` activated with all three services active; real private HTTPS
snapshot and secure session requests passed. All ten pre-existing managed
container IDs/states and the Serve baseline digest remained unchanged.

The first dashboard intent was refused before operation admission: Next removes
`/dashboard` from the request URL before invoking an application route handler.
The additional handler boundary had required the public path and returned 405.
New writes were disabled through the reviewed manager. The correction restores
only the selected handler's exact internal path before validation; query, malformed
path, origin, cookie, CSRF and body checks remain enforced. The new regression
sends a POST through the actual production Next server and Unix socket to a
non-mutating controller stub. Frozen frontend tests (21), typecheck, build,
real HTTP/socket and full synthetic browser acceptance passed after correction.
The first harness rerun required its old read-only method test to supply valid
write headers now that controls are enabled; the second complete run passed.
Corrected immutable assets are staged; their publication/CI and activation are
pending. No successful dashboard lifecycle operation is claimed yet.

Both named Metro fixtures now have fresh finite running sessions and verified
loopback protocol observations. Their private routes remain pending the existing
SSM operator's exact handoff; this does not establish private Metro readiness.
Fresh API/DB initialization retained a blocked allocation receipt when API
preparation used an unselected image. Diagnosis identified the supported
component dependency-install prerequisite; preparation and same-ID initialization
recovery are in progress. No reset, source change or data deletion was used.

Live lifecycle/rollback acceptance, final corrected-head CI, owner desktop/mobile
acceptance and review/merge remain pending. Generated logs/captures stay in ignored
task output; no credentials, environment dumps, source payloads or database
contents are retained in this evidence. Existing user services/data have not been
mutated for acceptance.


### Live capability timing correction

The corrected Next release `0cf6e4b…` activated with status/links/controls enabled.
Real private intent admission passed. All ten negative HTTPS checks passed with
unchanged peer identity: missing/foreign Origin, missing cookie/CSRF, duplicate
keys, invalid UTF-8, malformed JSON, extra command field, command component and
oversized body. Start operation `52bdd143687d437da29760fdd4c2d80d` and ready Start
no-op `81ebd3a69920420fbd99fc68f14a9620` both completed successfully through the
actual controller/systemd/rootless path. The following Pause intent was refused
before admission because capability inspection exceeded its four-second budget.

Read-only timing on the actual two-CPU host reproduced four concurrent isolated
capability reads taking 4.92–5.84 seconds, despite a single direct read taking 1.65
seconds. The UI cache consequently reported unavailable capabilities for valid
running projects. New writes were disabled again while correcting that read
budget to eight seconds for cache collection and submission preflight. The
regression covers valid six-second reads and continued fail-closed timeout
handling; no lifecycle deadline, worker count or service resource limit changes.
Fourteen focused controller tests pass. Corrected staging/live evidence and
final corrected-head CI remain pending.

Both fresh persistent fixture databases now initialized successfully through the
reviewed dependency/install and database interfaces. The first retained its exact
initialization operation ID `519d8c208d11441db73f4e5881776b76` throughout recovery;
no reallocation, reset or credential inspection was used. The required setup is
API component dependency preparation before initial database migration. Named
Metro sessions remain finite and protocol-ready, with private routes pending the
existing operator; their backends and all unrelated services are preserved.


The first eight-second release preserved the running peer and API instances, but
another Pause intent was refused before admission. Service counters showed no OOM,
restart or memory-limit event. Further read-only inspection found cache entries
aging while the entire collection window completed. Collection now uses two
background readers and publishes each completed row immediately, with a two-second
rest between windows. This preserves finite reads and fail-closed preflight while
avoiding delay behind an unrelated project. A blocked-reader regression verifies
that the healthy row becomes visible before the slow reader completes. Live
reverification and final-head checks remain pending; no Pause success is claimed.
