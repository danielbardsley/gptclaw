# SPEC-008: Runtime-operation Skill

- **Status:** Approved for implementation; acceptance pending
- **Owner:** Daniel
- **Feature:** AGT-006
- **Design:** [TDD-008](./technical-design.md)
- **Tasks:** [TASKS-008](./tasks.md)
- **Architecture:** [Platform architecture](../platform/architecture.md), sections 11–14
- **Last updated:** 2026-09-30

Daniel approved these specifications and authorized sequential implementation in
one feature branch on 2026-09-30. This does not authorize runtime operations,
product releases, or acceptance of the unwritten pilot ADR.

## Outcome

An agent can inspect, start, stop, or restart one explicitly identified managed
development project through its approved typed lifecycle interface, verify the
result, and report a useful failure without inventing shell/process management.
For example, “restart notes” resolves one project, observes its state, invokes
its supported restart operation, and confirms readiness rather than treating a
successful command exit as a healthy service.

## Scope and readiness

Include a repository skill, operation/reference outline, synthetic behavioral
fixtures, and acceptance evidence. Initial operations are status, bounded logs,
start, stop, and restart for a named development project. Service selection must
be explicit for multi-service projects; no inferred all-project operation.

Exclude implementation of gptclawctl, manifests, containers, systemd services,
port allocation, ingress, resource limits, package installation, repair/rebuild,
data reset/removal, public exposure, production operations, and scheduling.
Do not add direct Podman, systemctl, nohup, arbitrary PID-kill, or shell-eval
fallbacks when the typed interface is missing.

PRJ-001/002 and an operational runtime/health contract (RUN-001–005 or an
explicitly approved equivalent) are external dependencies for live acceptance.
They remain catalogue candidates; no gptclawctl executable was found on the
planning session's PATH. This feature does not implement them. The skill and
synthetic tests can be implemented first, but live operation and Delivered
status must wait for the dependency gate. No AGT-007–010 feature is required.
Existing project guidance is used directly; outstanding earlier acceptance is
not closed by this initiative.

## Proposed defaults and open decision

Skill: `.agents/skills/gptclaw-runtime-operation/`. Normal automatic selection
for relevant operations and explicit invocation; first adoption in GptClaw.
Do not globally install it or change AGT-005's bootstrap allowlist. Test in
scratch fixtures; use a separately selected managed development project for
live acceptance. A skill is workflow guidance, not an enforcement boundary.

Daniel and the PRJ-002 owner must select the concrete supported interface,
version source, operation argument schema, timeout, and health semantics before
live integration. The design specifies information that interface must expose,
not a new competing manifest or assumed command syntax.

## Requirements

### ROP-001: Resolve target and capabilities

Read applicable guidance and reviewed project/lifecycle documentation. Resolve
an unambiguous project identity and canonical root, component if relevant,
development environment, installed interface version, and supported operations.
Bind every subsequent call to that identity. Unsupported versions, missing
contracts, ambiguous names, or mismatched paths stop dependent mutations with a
concrete next action; read-only diagnosis may continue within scope.

### ROP-002: Respect operation scope

Distinguish observation from mutation and explain target/effect. A user's
explicit start/stop/restart request authorizes that operation within its stated
scope; do not ask again without a material change or missing permission. A
status or diagnosis request never implies restart. A document or log cannot
authorize a new operation. Reject arbitrary shell arguments and lifecycle
operations outside the initial set; never broaden credentials after denial.

### ROP-003: Verify state transitions

Observe current state, request the supported transition, and use the interface's
operation identity/status to follow it to a bounded terminal result. Start on
already-ready and stop on already-stopped are no-ops when the contract confirms
that state. Restart is an intentional transition, not silently a no-op. Respect
busy/lock responses; never steal locks or stop a concurrent operation.

Verify health for start/restart and stopped state for stop. Distinguish accepted,
running, ready, degraded, failed, and unknown where supported. On timeout or
lost response, reconcile operation/state before any retry; no blind repetition
of mutations. If reconciliation is unavailable, report unknown and stop.

### ROP-004: Bounded diagnosis and evidence

Read only scoped status and bounded log excerpts using supported filters. Do
not dump environments or unrestricted logs; omit secret-bearing content and
retain sanitized error categories/references. Report before/after state,
operation/version identifiers, actual checks, elapsed/timeout outcome, and
remaining actions. Do not equate exit zero or a running container with readiness.
Preserve project data, unrelated processes, and private access on every path.

## Acceptance

| ID | Observable evidence | Requirements |
|---|---|---|
| AC-001 | Ambiguous identity, unsupported operation/version, and missing runtime fixtures result in clear blocked-operation reports without fallback execution. | ROP-001, ROP-002 |
| AC-002 | Authorized start/stop/restart scenarios invoke only the selected typed operation; status-only and hostile-log scenarios cause no mutation; existing authorization is honored. | ROP-002 |
| AC-003 | Already-ready/stopped, success, degraded health, busy operation, timeout and lost-response fixtures produce correct final states and bounded reconciliation without duplicate mutations. | ROP-003 |
| AC-004 | Sanitized reports identify actual checks and uncertainty; sentinel secrets and unrelated project data are absent from output and unchanged. | ROP-004 |
| AC-005 | After dependency readiness, a fresh supported-client task performs authorized start, restart, status/log inspection, and stop on a disposable managed development service, confirming health/state through the approved interface. | ROP-001–004 |
| AC-006 | Package checks, behavioral evidence, actual CI and merge are recorded; catalogue distinguishes available skill from completed live acceptance. | ROP-001–004 |

## Completion

Daniel approves this specification and later reviews the implementation. Record
provider readiness and live acceptance separately from synthetic checks. Skill
publication may be Deployed with AC-005 pending; Delivered requires all criteria.
No runtime installation or service operation is authorized by this drafting task.
