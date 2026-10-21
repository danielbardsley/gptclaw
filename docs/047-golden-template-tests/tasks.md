# TASKS-047 — Golden-template tests

Status: Draft plan; implementation and acceptance pending. Owner: Project owner.
Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md)

## Planning and authorization

- [x] P-01 — Inspect the catalogue, current source and related initiative records;
  capture observed baseline and dependencies in the specification.
- [x] P-02 — Draft requirements, measurable acceptance, design and ordered tasks
  for QLT-009; link the documentation index and mark the catalogue Draft.
- [ ] P-03 — Project owner reviews the proposed decision below, approves the
  specification and separately authorizes the selected implementation scope.
  This planning request already authorizes P-01/P-02; it grants no runtime action.

Project owner reviews the exact-release support matrix and explicit retirement policy
before any currently supported release is excluded. New releases must pass before
catalogue adoption; no moving latest selector or arbitrary target deletion is proposed.

## Implementation

Start after P-03. Recheck current sources, guidance, version allocations and Git status
before edits. Follow the dependency order below, establishing trust and fixture
ownership before target operations. Where an interface is shared with another QLT
initiative, agree its version/capability contract before integration.

- [ ] T-01 — Implement matrix enumeration, capability classification and missing-release tests.
  Maps QLT-009-R01 to QLT-009-AC01; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-03 — Implement fixture receipts, ownership guards, interruption recovery and sentinel-preservation tests.
  Maps QLT-009-R03 to QLT-009-AC03; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-02 — Integrate existing checkers and fill generate/quality/lifecycle/data/mobile matrix gaps.
  Maps QLT-009-R02 to QLT-009-AC02; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-04 — Add event/change-selection rules, schedule/manual gates, caching and bounded parallelism.
  Maps QLT-009-R04 to QLT-009-AC04; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-05 — Implement report/redaction/quarantine checks and record matrix acceptance plus adoption guidance.
  Maps QLT-009-R05 to QLT-009-AC05; include the corresponding passing and
  failing acceptance scenarios before advancing.

## Verification and delivery

- [ ] T-06 — Run mapped focused tests, applicable generated-project gates and
  repository checks described in the design; record exact commands, revisions,
  results, skipped layers and limitations. Verify all QLT-009-AC01–AC05 with actual
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