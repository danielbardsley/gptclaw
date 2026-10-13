# TASKS-028: Dashboard live service status

- **Status:** Delivered and accepted
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-028](spec.md) · **Design:** [TDD-028](technical-design.md)

## Planning and authorization

- [x] T-000: Inspect current single/group status, owned resource checks and database
  readiness boundaries; draft DSH-002 with inventory dependency and measurable criteria.
  Planning requested October 12; no runtime action or implementation performed.
- [x] T-001: Project owner approves scope/design and authorizes implementation.
  Confirm current-instance counter/observed-change semantics and supported load.
  Require SPEC-027's reviewed inventory/private interface before integration;
  record exact provider observation version and side-effect-free read contract.

## Dependency-ordered implementation

- [x] T-002: Add reviewed additive provider observation capability and safe field
  projection for all supported single/group/DB topologies. Define every state mapping,
  ownership refusal, start-time/counter availability reason and probe deadline; preserve
  existing CLI/lifecycle behavior. (STS-001/002/004; AC-001/002/004)
- [x] T-003: After T-002 and inventory identity, implement bounded pooled collection,
  per-component snapshots, coalescing, timeouts and observed-transition memory.
  Cover stale thresholds, collector loss, instance replacement and identity conflicts.
  (STS-001/002/003/004; AC-001/002/003/004)
- [x] T-004: Add inventory status badges and accessible component details with textual
  state, busy/failure/freshness and documented uptime/restart/transition labels.
  Keep inventory available without runtime observations. (STS-005; AC-005)

## Verification and delivery

- [x] T-005: Run meaningful provider projection/secret/mutation tests, deterministic
  clock and state tests, real timeout/coalescing load checks, frontend accessibility
  and relevant repository/stack gates. Inspect routes/UI for scope and starter demos
  if inherited; check diff/links. Record executed commands/outcomes. (AC-001–005)
- [x] T-006: Deliver implementation PR with separate CI evidence; deploy through the
  reviewed private platform/provider path. Use task-owned synthetic single/group/DB
  targets for explicit CLI degradation/recovery acceptance and owner browser review.
  Verify rollback leaves inventory/lifecycle/data intact. Record per-criterion local,
  CI, live and owner evidence in acceptance.md; mark only DSH-002 Delivered after
  merge and acceptance. Clean up only owned fixtures without deleting existing data.
  (AC-001–005)

## Current handover

Implementation, local checks, all four CI workflows, private rollout and owner
acceptance passed. Inventory, status and links were activated in order. Exact
release/provider/image provenance and per-criterion evidence are in acceptance.md.
Owner-reported group timeouts were corrected through trusted validation reuse,
one fixed authenticated DB readiness query and a documented finite four-second
project deadline; the actual 20-project default-budget test still finishes under
15 seconds. Clean live degradation/recovery completed in 9.62/14.96 seconds.

PR #69 is merged after final-head CI and the owner's explicit merge approval.
The approved initial DSH-001/002/003 scope is Delivered.
Existing applications/data, private access and unrelated handlers remain intact.
The three named synthetic runtimes are stopped; their source/data is retained. Logs/preview integrations await their separate prerequisites, and
the owner deferred visual cleanup.
