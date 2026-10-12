# SPEC-028: Dashboard live service status

- **Status:** Approved for implementation — implementation and acceptance in progress
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Primary feature:** DSH-002
- **Design:** [TDD-028](technical-design.md) · **Tasks:** [TASKS-028](tasks.md)
- **Dependencies:** [Inventory foundation](../027-dashboard-project-inventory/spec.md), [runtime operation](../008-runtime-operation-skill/spec.md), [multi-service runtime](../025-multi-service-projects/spec.md), [database lifecycle](../026-development-databases/spec.md)

## Outcome and authorization

Let the project owner distinguish a ready application from stopped, starting, failed,
degraded or unobservable projects, and inspect each declared component's health,
uptime, restart count and last observed status change from the private dashboard.
The view must remain honest when the collector or runtime provider is unavailable.

The October 12 request authorizes this separate specification/design/task set and
planning PR. Implementation is now authorized; installation, deployment and acceptance remain pending.
This initiative extends the read-only inventory; it does not authorize runtime actions.

## Scope and existing readiness

Include live overall/component state, readiness health, current-run uptime, defined
restart counts, observation timestamps and last observed state-change time for supported
manifest schemas 1–4. Cover web, API and PostgreSQL components where declared. Keep a
supported project visible when it has never been started or its provider is unhealthy.

Current `scripts/private_apps.py:status` and `scripts/project_groups.py:status` return
sanitized lifecycle/health and route information; groups include component state.
They do not provide uptime, restart count or durable status-change history. Provider
ownership checks must remain authoritative. `gptclawctl db status` includes broader
backup/recovery data and is not an appropriate wholesale dashboard payload. Reuse
reviewed provider health observation, including its existing credential handling,
without forwarding database credentials, SQL diagnostics or raw inspection output.

DSH-001 is a dependency, not installed capability. New provider observation fields
must be additive/versioned and preserve existing CLI/lifecycle behavior. This feature
adds current runtime facts and bounded in-memory observation, not a telemetry store.

Exclude start/stop/restart buttons, auto-repair, alerting, notifications, logs, resource
charts, build/backup/cost status, Git state, public exposure and production targets.
Do not claim full DSH-005, DSH-009, DSH-011 or DSH-014 delivery. SPEC-029 owns links.

## Requirements

### STS-001 — Observed overall and component state

Join status only to an unambiguous validated inventory root/ID. Preserve overall state
and one entry per declared component; normalize reviewed provider values into documented
ready, stopped, starting, failed, degraded or unknown states. Preserve a separate
provider-state field where needed, including unpublished and recovery-required states.
An active process does not prove readiness or publication. Distinguish healthy,
unhealthy, unknown and not-applicable health. A healthy group requires all required
components ready and the provider's publication/operation conditions satisfied.

Unsupported, conflicted or unavailable targets show unknown/unavailable; never map a
read failure to stopped or healthy. Only a supported target with a successful observation
can be described as stopped, including a positively established never-started target.

### STS-002 — Defined runtime timing and restart semantics

For owned active components, show uptime since the observed current container/process
start, resetting when that instance changes. Report runtime-observed restart count for
that container instance, explicitly labeled as such; zero is a valid measured value.
User/systemd restarts that replace the instance do not accumulate into this count.
For stopped components, uptime is not applicable. Missing counters/timestamps are
unavailable with a reason, never silently zero. Validate data and detect clock anomalies.

Show last observed overall/component status change using collector observation time.
Initial observation is labeled “First observed”; a collector restart or observation gap
must not create an invented actual transition time. A transition seen after a gap is
labeled “Change detected”, with the preceding observation time if available. No durable
history or claim of exact unseen transition timing is required.

### STS-003 — Bounded refresh and explicit freshness

Collect asynchronously with finite per-project timeouts, concurrency and output bounds.
Coalesce browser requests; no separate runtime process/probe storm per browser or tab.
Healthy fixtures become visible within 15 seconds of a provider-observable transition
under the documented supported load. Each result carries its own observation time and
freshness. After 30 seconds without a successful observation, show stale/unknown and
last successful time; an unavailable component cannot inherit a sibling's timestamp.

One blocked target must not hide other results or stall inventory. Cached status may
remain visible with a stale label. Collector loss/recovery and provider incompatibility
produce actionable fixed diagnostics, without automatic repair or credential escalation.

### STS-004 — Safe read-only provider boundary

Use only reviewed observation operations and ownership-verified runtime resources.
Allowlist projected fields and finite runtime inspection queries. Browser input selects
an inventory row key, never a unit name, container ID, root path, probe URL or command.
No project commands, hooks, runtime creation/deletion, unit writes, route changes or
provider reconciliation mutation occurs from status reads. Any collector state is
limited to bounded memory; review any existing helper side effects before reuse.

Health probes use the validated existing runtime-owned local target and existing
credential-safe readiness handling, with bounded requests and no redirects/proxies.
No arbitrary network destination is accepted. Never forward raw Podman/systemd
inspection, environment values, mounts, database credentials, token-bearing operation
receipts, raw errors or log output. Apply SPEC-027's private host/origin/read boundary.

### STS-005 — Clear and accessible status presentation

Provide overall status in the inventory and component details on selection. Use text
labels alongside icons/colors, disclose timing/counter semantics and show freshness,
partial failures and operation-in-progress state. Preserve useful inventory when
runtime observation is down. Keyboard users can open and read component details.

## Acceptance criteria

| ID | Observable result and evidence needed | Requirement IDs |
|---|---|---|
| AC-001 | Synthetic provider tests cover supported single web/API and schema-3/4 groups: never-started, stopped, starting, ready, unpublished, failed, busy, degraded and DB recovery conditions; missing/conflicting resources and unavailable providers never report healthy or stopped falsely. | STS-001 |
| AC-002 | Controlled owned-instance tests show uptime progression/reset, measured zero/nonzero restart counts, stopped and unsupported metrics, clock anomalies, first observation and transitions across gaps/collector restarts with truthful labels. | STS-002 |
| AC-003 | With 20 synthetic projects, four component observations per project maximum and two clients, healthy transitions appear within 15 seconds; a hung project times out, stale values are labeled by 30 seconds, repeated clients share collection and other rows remain responsive. | STS-003 |
| AC-004 | Mutation/execution spies and synthetic-secret fixtures prove observation invokes only allowed reads/probes, verifies ownership, rejects arbitrary targets and emits allowlisted output without secrets. Inventory/HTTP boundary tests continue to pass. | STS-001/004 |
| AC-005 | Live acceptance on a task-owned synthetic single-service app and web/API/DB group verifies displayed health/component state, timing semantics and freshness against provider observations. Explicit CLI test operations create stopped/degraded/recovered scenarios; dashboard reads never cause those actions. Owner browser and keyboard checks pass; acceptance records local/CI/live/owner results separately. | STS-001/002/003/005 |

## Dependencies and decisions

Implement after SPEC-027's identity, private service and observation interface are
reviewed and delivered. Extend provider observations only after inspecting the installed
version/capabilities; do not read unsupported receipt schemas speculatively. The project
owner reviews the proposed current-instance restart and last-observed-transition semantics
with this scope. These are useful measured values, not cumulative incident telemetry.
Implementation records exact provider fields and polling budgets in the companion design.
Use synthetic fixtures and separately scoped private acceptance targets; preserve all
existing application data. Status remains useful without SPEC-029 links.

## Implementation authorization

On October 12 the project owner instructed: “In order implement the specs for
DSH-001, DSH-002 and DSH-003. Finish once all acceptance criteria have been met.”
This approves the specified scope and defaults and authorizes implementation and
necessary reversible private runtime verification. Existing operator, review/merge,
public-exposure and production gates remain in force. Acceptance is still unproven.
