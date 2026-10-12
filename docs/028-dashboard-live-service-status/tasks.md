# TASKS-028: Dashboard live service status

- **Status:** Implementation authorized — work in progress
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

- [ ] T-005: Run meaningful provider projection/secret/mutation tests, deterministic
  clock and state tests, real timeout/coalescing load checks, frontend accessibility
  and relevant repository/stack gates. Inspect routes/UI for scope and starter demos
  if inherited; check diff/links. Record executed commands/outcomes. (AC-001–005)
- [ ] T-006: Deliver implementation PR with separate CI evidence; deploy through the
  reviewed private platform/provider path. Use task-owned synthetic single/group/DB
  targets for explicit CLI degradation/recovery acceptance and owner browser review.
  Verify rollback leaves inventory/lifecycle/data intact. Record per-criterion local,
  CI, live and owner evidence in acceptance.md; mark only DSH-002 Delivered after
  merge and acceptance. Clean up only owned fixtures without deleting existing data.
  (AC-001–005)

## Current handover

Implementation is authorized and local source integration is in progress. The
separate inventory foundation, status observation/store and link projection/UI
are now implemented in dependency order. Relevant offline and browser checks
have passed; final repository/CI results, installed-service/private-route evidence,
review/merge and owner acceptance remain pending. See the technical design for
exact implementation choices. No deployed completion is claimed.
