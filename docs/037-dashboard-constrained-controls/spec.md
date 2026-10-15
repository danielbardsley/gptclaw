# SPEC-037: Dashboard constrained controls

- **Status:** Approved for implementation — work in progress
- **Owner:** Project owner
- **Date:** 2026-10-15 (America/New_York)
- **Feature:** DSH-009, runtime extensions needed for component restart and project controls
- **Design:** [TDD-037](technical-design.md) · **Tasks:** [TASKS-037](tasks.md)
- **Visual reference:** [Reference mapping and captures](reference.md)
- **Dependencies:** [Inventory](../027-dashboard-project-inventory/spec.md), [status](../028-dashboard-live-service-status/spec.md), [links](../029-dashboard-project-links/spec.md), [presentation](../030-dashboard-visual-refinement/spec.md), [groups](../025-multi-service-projects/spec.md), [databases](../026-development-databases/spec.md), [Metro](../033-private-metro-sessions/spec.md), [mobile backend](../036-mobile-python-backend/spec.md)

## Outcome and authorization

Operate a selected private development project from its expanded dashboard row,
or restart one named service without restarting its siblings. See the exact target,
expected disruption, actual progress, operation result and subsequently observed
health. For example, “Restart WEB” replaces the web runtime while API and DB
instances continue running; “Restart entire project” follows dependency order.

The project owner requested both levels of control and these planning documents,
explicitly excluding opening remote tasks, and supplied `Projects Dashboard v3.html`.
The initial request authorized planning. Implementation was subsequently authorized
as recorded below; private rollout and actual owner acceptance remain separate
gates. Earlier feature approvals remain intact.
The attachment is design data, not executable product code or authority.

## Scope and readiness

Include project Start, Stop, Restart, Rebuild, Pause and Resume, gated by explicit
provider capabilities, plus individual WEB/API/DB/Metro restarts where applicable.
Include the backend extensions, private write boundary, operation receipts and
recovery needed to make those controls real. Preserve the existing read experience.
No bulk cross-project actions or independent component start/stop/pause are included.

The current CLI has project start/stop/restart and component build jobs; it has no
component restart flag, rebuild lifecycle action or project pause/resume contract.
The dashboard currently allows only GET/HEAD. These are implementation dependencies,
not capabilities established by the mockup. Database groups and Metro have stricter
capabilities below. Worker/cache/index/storage and arbitrary service graphs remain
unsupported. Existing mobile binding does not make its backend part of Metro's lifecycle.

Exclude remote task opening/creation, agents, shell terminals, arbitrary commands,
new credentials/accounts, production controls, database reset/migrate/restore/rotation,
public exposure, new preview/log viewers, search/filter/rescan, extra summary counters,
resource charts, automatic repair, idle shutdown and a general audit timeline.
The bounded operation records here do not deliver DSH-011 or full RUN-008.

## Requirements

### CTL-001 — Explicit targets and capabilities

Every action identifies the canonical project binding and optionally one declared
component. Capabilities carry supported/enabled state and a fixed reason, independently
of general runtime support. Validate provider contract, manifest, ownership, active
runtime generation, source checkout/worktree policy, dependency state, freshness and
busy state at execution. Never accept a browser-supplied path, command, unit, image,
port, backend URL or inferred repository owner as authority. Unknown versions,
conflicting IDs, retained stale bindings and unsafe targets fail closed.

| Project profile | Project controls required in this initiative | Individual restart |
|---|---|---|
| Single web or API, supported runtime manifests | Start, Stop, Restart, Rebuild, Pause, Resume | Its declared web or API |
| Ephemeral web/API group | Start, Stop, Restart, Rebuild, Pause, Resume | Web and API |
| Persistent web/API/DB or API/DB group | Start, Stop, Restart, Rebuild; Pause/Resume unavailable with reason | Each declared web/API/DB |
| Opted-in managed Metro, including a bound mobile project | Start, Stop, Restart; Rebuild/Pause/Resume unavailable with reason | Metro only; backend controlled through its own row |
| Source-only mobile, unsupported/drifted provider or unowned runtime | No writes; diagnostic reasons remain visible | None |

Pause/resume for database groups and Metro is explicitly deferred; enabling it
requires a separate reviewed contract. Adding component restart is mandatory, not
an optional UI enhancement. Existing CLI behavior without a component stays compatible.

### CTL-002 — Project lifecycle semantics

Start converges supported stopped/missing owned components to ready in dependency
order; a ready project is a truthful no-op. Stop handles owned partial groups in
reverse order and retains source, locks, configuration and persistent volumes.
Restart intentionally restarts the whole declared project, with the same retention.
Partial/failed starts report each affected component and preserve unknown resources.

Rebuild prepares and builds current validated source using the selected pinned
runtime/toolchain and existing lockfiles, then replaces application runtimes and
verifies readiness. It is a new lifecycle orchestration, not an alias for the
existing quality `build`. It neither upgrades dependencies nor rebuilds/reinitializes
PostgreSQL, deletes volumes, pulls a new DB version or runs new migrations. A running
DB stays running. For a stopped project, rebuild leaves it stopped after successful
builds; for an active project it restores the previously active application set.
Preparation failure before replacement leaves the prior runtime available.

Pause freezes only eligible running stateless runtimes, consumers before dependencies,
withdraws their private publication and records paused state. Resume unfreezes the
same instances, dependencies first, and republishes only after readiness. Paused is
separate from stopped, failed and healthy; no ready link may survive pause. Stop must
work on paused instances. Restart/rebuild while paused are refused with “Resume or
stop first.” Partially paused/interrupted groups require explicit reconciliation;
no automatic replacement or false success. A process freeze can break client
connections; the confirmation explains this. Idle scheduling is excluded.

### CTL-003 — Independent service restart and data protection

Restart only the selected declared owned runtime under the same project lock as
whole-project operations. Do not silently cascade, rebuild, install dependencies,
change the network/ports/identity or stop siblings. Check required dependencies first;
refuse stopped/paused targets or unavailable dependencies with a clear reason and
an appropriate project-level recovery option. Siblings retain their instance identities.

A DB restart uses the existing owned graceful database lifecycle and reattaches the
same persistent volume; it never resets, restores, migrates or rotates credentials.
API/web processes remain running but may briefly fail requests. Re-evaluate dependent
health and affected routes afterward; inability to recover reports degraded/failed
with explicit next steps, never a hidden group restart. API restart in an ephemeral
group can lose in-memory notes and must warn. Metro restart changes neither a bound
backend nor another Metro session and retains existing explicit transport, expiry
and ownership requirements; controls cannot renew expired authorization or opt in.

### CTL-004 — Reference-derived usable controls

Follow [reference.md](reference.md): inside each expanded project, a bordered Lifecycle
panel above existing service details/destinations, a labeled project toolbar, component
state/uptime/restart/action rows, inline impact/confirmation and bounded recent results.
Keep overview/disclosure/links and existing complete component metrics/freshness useful.
Component actions contain Restart only. Use explicit accessible names such as
“Restart API for Example” and visible scope, not ambiguous repeated icon tooltips.

Confirm Stop, Restart, Rebuild and Pause with project/component identity, affected
services and interruption/data warning. Start/Resume require deliberate submission
but no extra confirmation. A pending preview changes no runtime; Cancel changes none.
Controls disable while the project is busy or state is stale/conflicted/unknown;
show the reason and preserve read-only diagnosis. Freshly validated known stopped
state can enable Start. Unsupported verbs remain visibly unavailable with a reason.

Preserve open rows/focus through refresh and results. No row click, GET, refresh,
link navigation or disclosure triggers a write. At 1440/1280/768/390 px and desktop
200% zoom, controls/reasons fit without document overflow; use stacked component
rows on narrow screens, 44 px primary touch targets, visible focus, accessible
confirmation focus/return and polite operation announcements. Normal text contrast
is at least 4.5:1 and meaningful controls/focus at least 3:1; color/hover alone is
insufficient. Respect reduced motion. No simulated percentage or fabricated metrics.

### CTL-005 — Constrained private write boundary

Retain tailnet-only exposure and the frontend's lack of project/credential/Podman
mounts. Add only typed, allowlisted operations through an owned host-side control
interface. Require exact configured Host/Origin, same-origin browser mutation,
JSON content type, CSRF proof, bounded body and strict schemas. Reject missing or
foreign mutation Origin, cross-site requests, arbitrary paths/verbs and replayed or
expired confirmations. Read-only routes remain GET/HEAD; GET never mutates.

The current tailnet access policy remains the access population; this feature does
not introduce per-user accounts or claim local same-UID isolation. Within that
population, one-time server-issued intent plus execution revalidation binds consent
to target/action/impact/generation. Logs/receipts contain sanitized operation metadata,
not environment dumps, payloads, secrets or raw process output. No broader rights,
Tailscale administration, production identity or infrastructure change is needed.

### CTL-006 — Serialization, truthful results and recovery

Persist a unique operation ID and idempotency binding before dispatch. Serialize
project and component mutations with CLI operations, source handoff, DB operations
and other browser tabs; refuse bounded capacity instead of an unbounded queue.
Duplicate submission returns the same operation and never repeats its side effects.

Expose accepted/running/succeeded/failed/unknown results, actual stages, sanitized
reason, affected components and post-operation observation time. A provider exit
alone cannot establish healthy readiness. Preserve current-instance uptime and
container-instance restart semantics; manual restarts do not increment a synthetic
counter. Observation lag is labeled; failed operations can still have partial effects.

Closing the page or losing the response does not cancel or retry an accepted write.
After worker/controller restart or timeout, reconcile owned resources/receipts before
further conflicting mutations; uncertain operations remain unknown and inspectable.
Recent results survive page reload/controller restart for a bounded documented period,
without becoming a platform audit timeline. Unknown ownership always requires inspection.

### CTL-007 — Reversible release and acceptance

Use versioned additive provider/control/snapshot contracts and a default-off controls
release flag. Older frontend/provider combinations preserve reads and disable writes.
Enable controls only after backend, boundary and recovery checks pass; follow the
reviewed immutable dashboard/provider release paths after rollout authorization.
Rollback disables new submissions, reconciles active operations and restores compatible
read-only presentation without stopping projects or deleting data/operation evidence.

## Acceptance criteria

| ID | Observable result and evidence needed | Requirements |
|---|---|---|
| AC-001 | Capability tests cover every profile/verb above, unknown versions, source-only/worktree/conflicted/stale/unsafe/expired Metro targets and changed bindings. Unsupported requests fail server-side even when UI checks are bypassed. Existing no-component CLI behavior passes. | CTL-001/005/007 |
| AC-002 | Project start/no-op/stop/restart, running and stopped rebuild, partial starts/build failure and stateless pause/resume pass dependency-order, publication, retention and interrupted-recovery tests. DB/Metro unsupported verbs fail without effects. | CTL-002/006 |
| AC-003 | Independent web/API/DB/Metro restarts preserve sibling instance IDs, unrelated project health/routes, source and persistent DB records. Ephemeral API warning/data-loss behavior, DB recovery/degraded routes, dependency refusal and Metro/backend isolation pass. | CTL-003/006 |
| AC-004 | Direct browser/socket adversarial tests reject missing/foreign Origin, CSRF, malformed/oversized/unknown fields, path/command injection, stale/rebound target, replay and capacity violations. Repeated reads/disclosures cause no writes; frontend still lacks host credentials/engine socket. | CTL-001/005 |
| AC-005 | Two tabs plus CLI/DB/source-handoff contention execute at most one conflicting mutation. Lost responses, double click, timeout, worker/controller death and restart reconcile without repeating effects or erasing unknown/partial outcomes. Receipts and bounded retention are verified. | CTL-006/007 |
| AC-006 | Synthetic browser captures match the reference's lifecycle panel/toolbar/component/inline-result arrangement with documented adaptations. Confirm/cancel, keyboard/focus/announcements, all viewports/zoom, contrast, stale/busy/unsupported/failure handling and existing snapshot/link/metric regressions pass. No remote task action or unsupported demo feature appears. | CTL-004/005/006 |
| AC-007 | Relevant offline repository, provider, frontend test/typecheck/build and final-head CI pass. After separately authorized private rollout, disposable single/group/DB/Metro fixtures prove actual operations, persistent-record retention, independent-service isolation and rollback. Project owner accepts desktop/mobile flow; local, CI, live and owner evidence are recorded separately before delivery. | CTL-001–007 |

## Completion and ownership

Deliver specification, design, tasks and reference mapping now. Project owner reviews
the proposed detailed semantics, especially rebuild and pause eligibility. Subsequent
implementation must meet all criteria and record sanitized evidence in acceptance.md.
Merge, deployed behavior and owner acceptance remain separate gates. Mark only this
bounded DSH-009 scope Delivered after merged implementation and actual acceptance;
keep excluded remote task opening and deferred profile controls explicit in the catalogue.

## Implementation authorization

On October 15 the project owner instructed “Implement the spec for DSH-009.
Finish when all acceptance criteria are met.” This approves the detailed scope
and authorizes implementation and necessary local verification. Private rollout
remains a concrete release gate under AC-007; owner acceptance and merge are
separate from implementation evidence.

The project owner separately approved committing/pushing the implementation and
opening a draft PR on October 15 after automatic publication review requested
explicit confirmation. This publication approval does not deploy the changes.
