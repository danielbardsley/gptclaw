# TASKS-043 — Accessibility baseline

Status: Implementation authorized; verification and acceptance tracked below. Owner: Project owner.
Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md)

## Planning and authorization

- [x] P-01 — Inspect the catalogue, current source and related initiative records;
  capture observed baseline and dependencies in the specification.
- [x] P-02 — Draft requirements, measurable acceptance, design and ordered tasks
  for QLT-005; link the documentation index and mark the catalogue Draft.
- [x] P-03 — Project owner authorized implementation, reasonable scope decisions,
  tests and PR publication on 2026-10-21. Do not merge or deploy. Existing
  non-QLT capabilities are dependencies, not duplicate implementation tasks.

Selected implementation defaults: Use bundled pinned axe for web journeys, existing native semantic interaction tests, visible focus and reduced-motion conventions. Keep manual keyboard/assistive-technology/device acceptance distinct and pending until actually performed.

## Implementation

Start after P-03. Recheck current sources, guidance, version allocations and Git status
before edits. Follow the dependency order below, establishing trust and fixture
ownership before target operations. Where an interface is shared with another QLT
initiative, agree its version/capability contract before integration.

- [ ] T-01 — Audit starter journeys and implement semantics, focus behavior and negative interaction fixtures.
  Maps QLT-005-R01 to QLT-005-AC01; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-02 — Implement tokens/layout fixes and contrast/zoom/text/motion coverage.
  Maps QLT-005-R02 to QLT-005-AC02; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-03 — Integrate tools, fault fixtures and documented applicability/exclusion policy.
  Maps QLT-005-R03 to QLT-005-AC03; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-04 — Execute selected manual trials and record remaining platform gaps before baseline acceptance.
  Maps QLT-005-R04 to QLT-005-AC04; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-05 — Publish releases/guidance and document adoption and product-specific revalidation.
  Maps QLT-005-R05 to QLT-005-AC05; include the corresponding passing and
  failing acceptance scenarios before advancing.

## Verification and delivery

- [ ] T-06 — Run mapped focused tests, applicable generated-project gates and
  repository checks described in the design; record exact commands, revisions,
  results, skipped layers and limitations. Verify all QLT-005-AC01–AC05 with actual
  evidence; pending private/native/operator trials remain visibly pending.
- [ ] T-07 — Push the implementation branch and open a reviewable PR with sanitized
  evidence and known limitations. Do not merge, deploy or imply owner acceptance.

Merge, rollout and owner/device acceptance are downstream review actions excluded
from this implementation authorization, not tasks for the unattended run.

## Current handover

Completed: planning/source review and the three linked draft documents. No new
implementation, container execution, CI run, deployment or acceptance is claimed. All
implementation tasks remain unchecked. Existing supporting-slice results remain in their
original initiative acceptance records.

Next action: project owner reviews the proposed scope and decision; then an explicitly
authorized implementation task can proceed using this traceability. Shared QLT
dependencies can be implemented in slices, without claiming the full catalogue item
Delivered.