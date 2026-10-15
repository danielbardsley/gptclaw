# TDD-037: Typed dashboard lifecycle operations

- **Status:** Approved for implementation — work in progress
- **Owner:** Project owner
- **Date:** 2026-10-15 (America/New_York)
- **Specification:** [SPEC-037](spec.md) · **Tasks:** [TASKS-037](tasks.md)
- **Visual target:** [Reference mapping](reference.md)

## Existing behavior and proposed architecture

`platform/dashboard/app/ProjectRow.tsx` owns expansion; `StatusPanel.tsx` and
`MetroPanel.tsx` render observed components. `lib/boundary.ts`/`proxy.ts` permit
GET/HEAD on specific paths. `lib/collector.ts` reads `/v1/snapshot` over the owned
Unix socket. `scripts/dashboard_collector.py` refreshes bounded observations;
browser reads do not execute project commands. `scripts/manage_dashboard.py`
installs immutable collector/frontend releases; the frontend receives only assets
and the socket directory. Keep those observation and mount boundaries.

`scripts/gptclawctl.py` dispatches project lifecycle to `private_apps.py`,
`project_groups.py` and mobile modules; `project_groups.restart` currently stops
and starts the entire group under its outer lock. Component build/log/quality
selection is not an independent lifecycle contract. PostgreSQL lifecycle and
persistent receipts are in `project_database.py`. Metro has separate owned session,
transport/expiry and recovery contracts. No implementation exists merely because
an action appears in the reference.

Add an owned host controller alongside the collector, with a separate Unix socket
in the already restricted socket directory, an independent finite systemd user
service and immutable provider code. The collector remains read-only. Next.js
forwards typed requests to this controller; it never executes a host shell or
receives the project directory, secrets or Podman socket. Version and hash the new
service/socket/feature configuration in the existing release descriptor. Reuse
owned install/drift/rollback checks; do not grant sudo, new AWS rights or Serve
administration. Socket protection is against accidental exposure, not hostile
code executing as forge.

## Provider contract and capabilities

Introduce an additive versioned lifecycle capability/intent/result contract shared
by CLI and controller. The provider is the source of eligibility; the browser only
renders it. Keep current flags and no-component behavior compatible. Proposed CLI
surface, to be implemented and advertised in the next reviewed provider version:

- `restart --project-root <root> --component web|api|db|metro` for declared eligible components.
- Project `rebuild`, `pause`, `resume` actions with `--project-root`.
- Internal typed preflight/execute/reconcile functions used by the controller and CLI.

These are proposals, not commands to run against the current installation. Freeze
the exact provider/toolchain through existing version sources and release metadata;
do not invent a pin. Capability inspection reports contract version, action/target
pairs, enabled status/reason, manifest digest, binding/runtime generation, busy/paused
state, data-risk category and affected/dependent components. Unknown versions disable
controls. Never infer capability from `runtime_support: supported` alone.

Use an additive snapshot schema for control availability and a bounded sanitized
recent-operation projection, merged by the existing Next.js snapshot endpoint through a second fixed read-only
controller snapshot request (never dispatch). The collector retains its read-only contract. Controller loss makes controls unavailable without
invalidating independent inventory/status/link reads. Preserve accepted
inventory/status/link fields and their semantics. Sensitive canonical roots and
internal unit/container/volume identities stay in the host controller. Opaque row
keys are selectors, not authorization: bind them independently to current validated
inventory plus exact canonical root/ID and safe directory identity. The controller
revalidates against bounded safe discovery and provider ownership at intent and
execution time; stale collector data cannot grant control. Lock/recheck against
concurrent rename, manifest/source handoff and runtime replacement. Source task
worktrees retain their existing no-runtime policy.

## Operation protocol and browser boundary

Proposed exact frontend routes (trailing-slash equivalents allowed), all no-store:

| Method/path | Shape and behavior |
|---|---|
| POST `/dashboard/api/control-intents/` | Strict JSON `{schema_version:1, project_key, action, component:null|enum}` plus CSRF proof. Return short-lived single-use intent ID, exact display target/impact, generation and expiry. Preflight performs no runtime mutation. |
| POST `/dashboard/api/operations/` | Strict JSON `{schema_version:1, intent_id, idempotency_key}` plus CSRF proof. Atomically consume/revalidate intent and persist operation before dispatch; 202 with operation ID, or typed refusal. |
| GET `/dashboard/api/operations/<opaque-id>/` | Bounded sanitized status only; unknown IDs disclose no target details. Never starts/retries a worker. |
| GET `/dashboard/api/control-session/` | Obtain a short-lived CSRF token paired with a Secure, HttpOnly, SameSite=Strict, dashboard-path cookie. No CORS; exact same-origin fetch checks; no runtime side effects. |

Mirror allowlisted typed paths on controller schema 1; no generic proxy target.
Do not broaden all POSTs or change the read-method rule globally. Origin is mandatory
and exact for mutations; validate configured HTTPS origin and Host, reject foreign
or missing Origin, cross-site Fetch Metadata, non-JSON, unexpected query/path forms
and unknown fields. Check CSRF token/session binding server-side before intent or
submission. Start/Resume use the same intent flow, submitted after explicit click;
interrupting actions wait for the inline Confirm button. A canceled/expired intent
cannot execute. Replayed intent with the same idempotency key returns its original
operation; a different key or changed payload is a conflict, not a second action.
Use a client-generated cryptographically random fixed-format operation ID as the
idempotency key, persisted before submission. The same ID addresses the status read
after a lost acceptance response; an unrecognized ID never causes execution. Reject
an existing ID bound to a different target/intent rather than reassigning it.

Bound request bodies to 8 KiB, action/component strings to enums and opaque IDs to
fixed format. Limit to 64 outstanding intents, 60-second intent TTL, four active
operations globally and one per project; return a visible retryable busy/capacity
refusal, not an unbounded queue. Bound session issuance and retained sessions as
well. An intent never accepts paths, argv, environment, unit names or URLs. Use the
existing configured dashboard origin, no forwarded-header-derived authority. These
numbers are proposed implementation defaults to be verified in TASK-037-002/005.

Tailnet dashboard access remains the trust population. Session/CSRF is request
integrity, not individual user authentication or a new identity system. Record
initiator as dashboard or CLI, not a fabricated personal identity. If separate
viewer/operator roles are later required, that is a separate access-policy change.

## Lifecycle algorithms and locking

All adapters use the existing project outer lock and established DB/Metro ownership
locks, in documented project-before-component order. Controller preflight does not
reserve the runtime indefinitely. Submission records acceptance first; the worker
acquires locks, repeats preconditions and records running before any side effect.
CLI direct mutations participate in the same locks/operation guard; the controller
cannot provide serialization by locking only its own requests. Coordinate with
source-handoff guards, DB reset/migrate/restore operations and existing busy receipts.
A durable active-operation guard blocks conflicting writes after controller death
until reconciliation, even after OS locks are released.

### Project operations

Use current declared dependency order (DB before API before web, when present),
reverse for shutdown. Keep Metro lifecycle confined to its project. Whole-project
restart retains existing semantics; do not silently include a mobile binding's backend.

Rebuild first validates source/manifest/toolchain/lockfile fingerprints and builds
application artifacts using existing bounded jobs. No dependency upgrades or lockfile
rewrite. Record prior active components and intended artifact identities. Before
replacement, recheck fingerprints/target and ownership; changed inputs invalidate
execution rather than replacing from a different checkout. Database images/volumes
are not build targets. Retain the prior owned artifacts and receipts for explicit
recovery. Replace only the active application set in dependency order; a stopped
project remains stopped after build. Readiness failure records actual partial state,
withdraws unsafe publication and offers explicit recovery. Do not automatically run
downgrade migrations or attempt data rollback. A source/artifact restore is explicit
and cannot overwrite intervening source edits.

For eligible stateless profiles, implement bounded owned container freeze/unfreeze
through typed provider functions, not shell text. Pause withdraws publication,
freezes consumers then dependencies, and persists per-component stage/identity.
Resume unfreezes dependencies then consumers, checks readiness and republishes.
Mixed failure reports partial/unknown with preserved identities; reconcile actual
freeze state before a retry. Existing health checks/observation must recognize pause
without treating a deliberately frozen runtime as ready or auto-repairing it.
Stop explicitly unfreezes as required for graceful owned shutdown. Refuse rebuild
and restart on paused profiles. Preserve start-time/restart counters from provider
observations, not a demo timer. Pause is initially ineligible for any DB-bearing
project and Metro; this avoids inventing database quiescence or lease extension.

### Component restart

Resolve only declared component identities under the group lock. Require a known
active unpaused selected runtime and ready required dependencies. Persist a component
restart stage without changing sibling runtime ownership or deleting the group network.
Gracefully stop and replace the selected runtime using its existing prepared artifact,
ports, configuration and volume contract. Recheck instance generation before stop.
A single-service project uses the same primitive; optional `--component` never changes
legacy whole-project restart behavior.

Web restart preserves API/DB process IDs. API restart preserves web/DB, including the
expected ephemeral in-memory data warning. DB restart uses the existing DB graceful
stop/start with the same owned persistent volume, leaving API/web processes running.
Withdraw readiness-gated affected routes during the interruption and re-observe
all dependencies/dependants afterward. Restore only verified healthy routes. If the
API cannot reconnect, record degraded and suggest a separate explicit API restart;
never cascade it. DB restart is refused during backup/reset/migration/rotation/restore
or ambiguous volume/owner state; DB-specific locks remain authoritative.

Metro restart delegates to its owned lifecycle, requires current explicit transport
and session authorization and never changes a binding/backend. Reuse its generation
and expiry refusal; do not renew authorization, extend TTL, change transport or
reconfigure routes as a side effect of clicking Restart.

## Durable operations, observations and failure

Store controller-owned versioned JSON operation records under the owned platform
state directory, mode 0700/0600, safe no-symlink opens and atomic replace/fsync.
Records contain operation/idempotency/intent IDs, binding and input digests, selected
scope, affected components, stage timestamps, before/after owned generations,
provider version, result and fixed sanitized reasons. Store no credential values,
request cookies/CSRF proofs, arbitrary output, database records or source contents.
Provider-private recovery metadata stays outside public responses. Public projections
expose only project/component labels, operation IDs, stages and fixed reasons.

Persist acceptance/idempotency mapping before dispatch, running before mutation,
component-stage receipts around each side effect and terminal result after bounded
post-observation. A record write failure before acceptance causes no dispatch; a
failure after side effects leaves recoverable unknown evidence and blocks further
writes. On startup or orphan detection, compare operation stages with actual owned
resource identities and provider receipts. Never automatically rerun a nonterminal
operation. Resolve success only from confirmed effects and readiness; otherwise
record failed/unknown with an inspect/reconcile path. Lost HTTP responses and browser
reload query the existing operation ID/idempotency mapping and do not resubmit intent.

Apply finite per-adapter stage deadlines derived from existing provider commands;
document exact values before implementation acceptance. Killing an HTTP request
never kills an operation. A deadline expiry does not prove the container action
stopped: mark unknown, reap only owned workers, reconcile native operations before
unlocking conflicting writes. No arbitrary browser cancel for accepted mutations.

Retain terminal records/idempotency mappings for seven days, with a 1000-record/10 MiB
budget; never prune active/unknown records. Prune eligible expired terminal records
only. If safe pruning cannot satisfy the budget, refuse new mutations with an explicit
storage-capacity reason while keeping reads available. Expired operation IDs return
unavailable/expired, not success. Recent UI shows at most five records per project,
with retention text; this is bounded operation evidence, not a general event timeline.

Keep shared snapshot polling. Poll operation status only while an operation is active,
with bounded backoff; detach on unmount and recover via recent records after reload.
After terminal result request a fresh observation through bounded controller scheduling;
no generic force-scan endpoint. Display “operation completed; health observation pending”
until actual fresh state arrives. Never optimistically flip status/link/uptime/restart
values. Existing collector freshness remains independent of operation completion.

## Frontend presentation

Add a control panel inside `ProjectRow` above metadata/destination panels; integrate
component metrics with `StatusPanel`/`MetroPanel` so no accepted field is lost or
rendered inconsistently twice. Use [reference.md](reference.md) for arrangement.
Project toolbar has visible scope and six named verbs; components have Restart only.
Keep unsupported verbs disabled with readable reasons, stale/busy constraints, inline
impact/confirmation, real stage/result and bounded Recent strip. Preserve disclosure
state, focused target and confirmation identity across refresh. Invalidate confirmation
on changed binding/generation/expiry; never silently retarget an open confirmation.

Use semantic buttons/regions and live polite announcements, logical keyboard order,
Cancel/focus return and visible target descriptions. Stack at narrow widths, meet the
specified touch/contrast/zoom targets and use indeterminate reduced-motion-safe busy
presentation. Keep existing local fonts/packages and tokens; no bundled reference runtime.

## Planned changes

| File/component | Planned responsibility | Requirements |
|---|---|---|
| `scripts/gptclawctl.py`, `private_apps.py`, `project_groups.py`, `project_database.py`, Metro modules | Versioned capability/preflight, component restart, rebuild, eligible pause/resume, shared locking/receipts/recovery | CTL-001/002/003/006 |
| Proposed `scripts/dashboard_controls.py` and isolated tests | Typed host controller, identity binding, intent/idempotency/state/worker limits and reconciliation | CTL-001/005/006 |
| `scripts/dashboard_collector.py` and observation modules | Additive capability/paused projection and real post-action observations without writes on reads | CTL-001/002/006/007 |
| `platform/dashboard/lib/boundary.ts`, `proxy.ts`, proposed control helpers/API routes | Exact write-path checks, CSRF/session/JSON/schema limits and typed socket forwarding | CTL-005/006 |
| `app/ProjectRow.tsx`, component panels, proposed control panel, `app/globals.css` | Reference layout, confirmations, eligibility, operation results, responsive/focus behavior | CTL-004/006 |
| `scripts/manage_dashboard.py`, provider release descriptors/tests, operations runbooks | Default-off owned controller deployment, contract compatibility, read-only rollback and recovery | CTL-007 |
| Existing focused Python/frontend/browser suites plus new behavior tests | Isolation, hostile input, concurrency, interruption, readiness and visual/accessibility evidence | CTL-001–007 |

Names for new modules/routes are proposed. Keep their schemas explicit and independently
testable; no framework migration, generic command bus or new infrastructure dependency.

## Verification, rollout and rollback

Local checks use synthetic disposable owned projects and isolated operation directories.
Test component replacement identities and persistent record retention, not just returned
labels. Cover every capability profile, concurrency with direct CLI and DB/source actions,
worker death between receipt stages, CSRF/replay/changed-binding attacks, offline storage
errors and old/new contract compatibility. Stub native adapters for failure injection;
real owned containers are required separately for lifecycle/readiness/pause tests.

Run `git diff --check`, `git diff --cached --check`, `./scripts/check-repository.sh`
with the prepared manifest environment, changed-shell syntax checks and focused suites.
Use the existing pinned rootless Node/browser workflow for frozen install, frontend tests,
typecheck/build and browser regression/captures. Do not install host packages. Require
final-head applicable CI; no Terraform checks are needed unless IaC actually changes.

Private rollout is a later separately authorized action: activate reviewed provider
first, then a controls-disabled compatible dashboard/controller release; prove read-only
regressions and default-off behavior before enabling the frozen controls flag. Use
only task-owned synthetic web/API/group/DB/Metro fixtures, verify sibling instance IDs,
records and unrelated routes, then owner desktop/narrow/keyboard/zoom acceptance.
Record commands/revisions and local/CI/live/owner results separately in acceptance.md.
No actual production/project data is required. Clean up only proven owned fixtures.

Rollback first disables submissions, drains or explicitly reconciles active/unknown
operations, preserves evidence and returns any deliberately paused fixture to its prior
reviewed state where safe. Restore compatible immutable read-only dashboard/provider
versions; refuse a provider downgrade that cannot interpret active receipts/paused state.
Do not stop projects, remove volumes/routes, discard receipts or overwrite source merely
to roll back controls. A feature flag can disable writes while recovery remains available.

## Traceability and review decisions

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| CTL-001 | Versioned provider capabilities, bound preflight and exact targets | TASK-037-002/003/005 | AC-001/004 |
| CTL-002 | Group orchestration, rebuild artifact boundary and stateless freeze state | TASK-037-002/004 | AC-002 |
| CTL-003 | Selected-runtime replacement, DB volume retention and Metro isolation | TASK-037-003 | AC-003 |
| CTL-004 | Reference panel, inline consent and accessible actual results | TASK-037-006/007 | AC-006 |
| CTL-005 | Exact origin/method/schema/CSRF and restricted socket controller | TASK-037-005/007 | AC-001/004/006 |
| CTL-006 | Shared locks, durable idempotency, stages and reconciliation | TASK-037-003/004/005/007 | AC-002/003/005/006 |
| CTL-007 | Default-off versioned release, compatibility and recovery-first rollback | TASK-037-008/009 | AC-001/005/007 |

Project owner reviews this concrete proposal, including stateless-only pause/resume,
rebuild preserving a stopped project, current tailnet access population and seven-day
result retention. These are proposed defaults, not claims of approval or installed
capability. Implementation was authorized October 15; rollout and owner acceptance remain separate evidence gates.
