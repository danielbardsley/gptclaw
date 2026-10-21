# TASKS-042 — Preview smoke tests

Status: Draft plan; implementation and acceptance pending. Owner: Project owner.
Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md)

## Planning and authorization

- [x] P-01 — Inspect the catalogue, current source and related initiative records;
  capture observed baseline and dependencies in the specification.
- [x] P-02 — Draft requirements, measurable acceptance, design and ordered tasks
  for QLT-004; link the documentation index and mark the catalogue Draft.
- [ ] P-03 — Project owner reviews the proposed decision below, approves the
  specification and separately authorizes the selected implementation scope.
  This planning request already authorizes P-01/P-02; it grants no runtime action.

Project owner confirms the initial application journey and private acceptance target
before execution. Proposed default checks are read-only; writing journeys require a
named disposable synthetic dataset.

## Implementation

Start after P-03. Recheck current sources, guidance, version allocations and Git status
before edits. Follow the dependency order below, establishing trust and fixture
ownership before target operations. Where an interface is shared with another QLT
initiative, agree its version/capability contract before integration.

- [ ] T-01 — Implement trusted target resolution and identity/redirect rejection fixtures.
  Maps QLT-004-R01 to QLT-004-AC01; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-04 — Implement read-only defaults, explicit write scope and interruption-safe fixture cleanup.
  Maps QLT-004-R04 to QLT-004-AC04; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-02 — Build profiles and asset/prefix/health/journey fault scenarios.
  Maps QLT-004-R02 to QLT-004-AC02; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-03 — Integrate update hooks, generation checks, cancellation and race/timeout tests.
  Maps QLT-004-R03 to QLT-004-AC03; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-05 — Add reporting, redaction and separate private-client/native acceptance procedures.
  Maps QLT-004-R05 to QLT-004-AC05; include the corresponding passing and
  failing acceptance scenarios before advancing.

## Verification and delivery

- [ ] T-06 — Run mapped focused tests, applicable generated-project gates and
  repository checks described in the design; record exact commands, revisions,
  results, skipped layers and limitations. Verify all QLT-004-AC01–AC05 with actual
  evidence; pending private/native/operator trials remain visibly pending.
- [ ] T-07 — Open/review the implementation PR, observe final-code CI, merge via
  the repository workflow, and complete separately authorized rollout and owner
  acceptance where applicable. Add sanitized criterion-by-criterion acceptance
  evidence, update index/catalogue according to actual state, and clean up only
  owned fixtures. A plan or CI-only result cannot establish runtime acceptance.

## Current handover

Completed: planning/source review and the three linked draft documents. No new
implementation, container execution, CI run, deployment or acceptance is claimed. All
implementation tasks remain unchecked. Existing supporting-slice results remain in their
original initiative acceptance records.

Next action: project owner reviews the proposed scope and decision; then an explicitly
authorized implementation task can proceed using this traceability. Shared QLT
dependencies can be implemented in slices, without claiming the full catalogue item
Delivered.