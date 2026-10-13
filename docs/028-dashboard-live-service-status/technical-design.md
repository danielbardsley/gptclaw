# TDD-028: Owned runtime observation and status snapshots

- **Status:** Implemented on feature branch — final validation and rollout pending
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-028](spec.md) · **Tasks:** [TASKS-028](tasks.md)

## Interfaces and approach

Extend the trusted Python collector and typed read protocol from
[TDD-027](../027-dashboard-project-inventory/technical-design.md). Inventory snapshots
remain independent of status collection; a failed runtime never removes a validated
project row. Resolve opaque row keys to revalidated root/ID internally, refuse duplicate
IDs, and verify ownership/root binding before inspecting a service or container.

Use a reviewed additive observation function in the versioned provider, rather than
copying lifecycle logic into the frontend. Current source responsibilities are
`scripts/private_apps.py:status`/`inspect_service` and
`scripts/project_groups.py:status`. Inspect helper behavior and installed parity before
reuse. Avoid wholesale `db status`, raw `podman inspect`, systemd property dumps or
receipt serialization. Database health must reuse reviewed secret-safe readiness and
ownership checks; it must not issue credentials to the browser or initialize a database.
The dashboard does not call start/stop/restart or invoke project manifest commands.

Proposed provider additions expose an observation-schema capability and narrow timing
fields sourced from ownership-verified runtime inspection: current instance identity,
start time and runtime restart count. Restrict systemd/Podman queries to exact selected
owned resources, cap captured output, sanitize errors and validate JSON before field
projection. Any required unit/process timing fallback has its own labeled semantics;
do not substitute a systemd restart counter for the container-instance count. No
restart counters or clocks are inferred from stale lifecycle receipts.

## Data contract and state mapping

Proposed status result includes response version, opaque row key, supported/provider
version, overall lifecycle/health, operation-busy flag, observed/last-success times,
freshness and component records. Each component record includes its declared name,
normalized/provider state, health, observation time, uptime seconds or a reason,
instance restart count or a reason, and last-observed-change information. Instance
identity remains collector-internal; do not expose runtime ownership tokens or raw
container metadata. Missing values carry typed reasons such as unavailable,
not-applicable, unsupported, ownership-conflict or clock-anomaly.

Document a complete mapping for every supported provider state before implementation.
Preserve ready/stopped/starting/failed/degraded distinctions, unpublished and interrupted
operations, and schema-4 recovery requirements. Overall healthy requires all declared
components ready plus publication/operation conditions. Do not derive group success
from an empty component set. A missing resource with an inconsistent owned receipt is
a diagnostic, not automatically “never started”. Carry per-component failures even
when the project observation is otherwise partially useful.

Keep an in-memory transition map keyed by root/ID/component and observed instance.
Record first observation separately. Update last-observed-change only when a successful
state/health/operation-busy tuple changes; repeated identical polls do not reset it.
After collection gaps, mark newly detected transitions as observed after a gap rather
than exact event times. Reset history when project identity changes or the collector
restarts. No project or runtime receipt writes and no persistent history are needed.

## Scheduling and failure bounds

Proposed supported-load target is 20 projects. Poll every five seconds, with at most
four project observations concurrently and a four-second deadline per project; kill
and reap owned observation workers on timeout so a stuck helper cannot occupy the
queue forever. A round of 20 entirely blocked projects is bounded to 80 seconds plus scheduling
on a single-worker host (40 seconds on this two-CPU host); healthy supported-load
fixtures with one blocked target must still meet the 15-second visibility criterion;
prove the SPEC-028 15-second freshness target with the synthetic load test. Bound
per-project results to 64 KiB and the status response to 1 MiB. A round never overlaps
itself; browser clients share the same snapshots. Health request timeouts must fit
inside the project deadline, including groups and credential-safe DB readiness.
If existing helper bounds cannot fit, revise the reviewed adapter rather than dropping
required ownership/readiness checks.

Keep one latest successful observation per project/component. Mark stale at 30 seconds,
retain its timestamp and diagnostic, and replace it only after a valid successful read.
Limit history to the bounded inventory (maximum 256 rows); evict entries removed by a
successful scan, never a partial failed scan. Above the 20-project performance target,
show collection capacity/partial status honestly and record measured latency; no
unbounded process creation or silent universal freshness promise. The collector
never caches secret material in transition/snapshot state.

## Frontend and verification

Add textual status badges and a keyboard-accessible component panel to the inventory.
Show observation age, “First observed”/“Change detected”, current-run uptime and
“Container-instance restarts”. Include a concise explanation that replacement resets
the instance counter. Operation-busy and unavailable diagnostics remain visible.
Status panel failures do not block inventory rendering or link metadata.

Test provider projection/ownership, exact state mappings, counters/timestamp bounds,
probe behavior and no mutation using synthetic adapters. Use deterministic clocks for
clock jumps, transition gaps and stale thresholds; exercise real worker timeouts and
coalescing under the specified 20-project load. Secret fixtures and capture spies cover
stdout/stderr/API/cache boundaries. Run appropriate provider/repository and frontend
checks after implementation; record actual commands rather than proposed successes.

After reviewed rollout, compare a task-owned synthetic single service and managed
web/API/DB group against provider output. Generate degradation/recovery through explicit
reviewed CLI acceptance operations, not dashboard actions. Record deployment revision,
provider capability, observation times, listener/privacy checks and owner browser
acceptance. Preserve existing data and never run destructive DB reset for status tests.

## Components, rollout and traceability

| Requirement | Component/mechanism | Tasks | Acceptance |
|---|---|---|---|
| STS-001 | Provider observation projection and complete state mapping | T-002/003 | AC-001/004/005 |
| STS-002 | Owned instance metrics and in-memory observed transitions | T-002/003 | AC-002/005 |
| STS-003 | Bounded worker pool, snapshots and stale threshold | T-003/005 | AC-003/005 |
| STS-004 | Fixed read adapter, ownership checks, secret-safe probes | T-002/003/005 | AC-004 |
| STS-005 | Inventory badges and accessible component panel | T-004/005/006 | AC-005 |

Roll out as an additive provider/collector/frontend increment after inventory works.
An older provider returns unsupported timing/status capability explicitly. Roll back
the dashboard increment and additive provider projection through reviewed releases;
retain existing lifecycle compatibility and project data. Inventory remains usable
when status is disabled. The project owner reviews semantics and load target; the
implementation author records exact fields, capability version and measured deadlines
before live rollout. No infrastructure or production dependency is required by this plan.

## Recorded implementation

Provider 1.9.0 adds `gptclawctl observe --project-root` and advertises observation
schema 1; existing `status` behavior remains compatible. The observer checks
root/ID/inode binding, unit/container ownership and readiness, and projects only
timing, state, health and publication fields. Its scoped read adapter deduplicates
native queries, requests only fixed container inspection fields, refuses native
mutations and receipt writes, and compares trusted bootstrap bytes without
publishing a provider snapshot. Independent group component reads use at most
three threads inside one project worker; a failed component retains useful siblings.

The collector uses a clean Python forkserver with the known tooling path preloaded
once, then restores its parent environment. This avoids repeated library startup
inside the four-second per-project deadline and never forks the multithreaded HTTP
process directly. Up to four project workers (bounded by available CPUs), a 20-project rotating window, 64 KiB per
result and five-second collection scheduling remain bounded; hung workers and
their owned process groups are killed/reaped. `dashboard_status.py` stores no more
than 256 project entries and records only in-memory transitions. Per-component
failure does not inherit a sibling's timestamp. Unsupported/future capabilities
remain unavailable and stale status withdraws publication.

`manage_dashboard.py prepare/start --with-status` records an opt-in status feature
in the immutable release descriptor and starts the collector with `--status`.
Inventory remains usable with this feature off. The Next.js status column and
keyboard-accessible component panel show current/last-known state, busy operations,
current-run uptime, container-instance restart counts and observed-change semantics.
Browser elapsed time also ages status when the last fetched observation is old.
No lifecycle controls, logs, telemetry database or project dataset mutation is added.

## Live budget correction

Owner desktop acceptance exposed repeated group timeouts on the two-CPU host.
The original two-second budget was too short for concurrent ownership checks,
authenticated DB readiness and HTTP probes. Exact-byte trusted schema meta-checks
are now reused (every manifest is still fully validated); the clean forkserver
preloads all four validators. DB readiness uses one fixed authenticated revision
query; HTTP readiness is bounded to 500 ms, and docs capability to 250 ms. Ordinary
lifecycle helpers are restored after each observation and keep their own bounds.

Project observations now have a finite four-second deadline. This is a budget
correction, not acceptance by hiding failures: the real 20-project worker test
uses this actual default, includes a hung target/coalesced readers, and must finish
within 15 seconds. Whole-worker process-group termination, ownership validation,
64 KiB results, 30-second stale threshold and 20-project rotating windows remain.
All-blocked workloads can exceed the supported healthy-load latency; their rows
remain explicitly unavailable/stale. Record actual deployed group refresh and
degradation/recovery measurements separately.
