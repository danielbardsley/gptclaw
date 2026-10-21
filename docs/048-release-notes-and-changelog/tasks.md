# TASKS-048 — Release notes and changelog

Status: Implementation authorized; verification and acceptance tracked below. Owner: Project owner.
Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md)

## Planning and authorization

- [x] P-01 — Inspect the catalogue, current source and related initiative records;
  capture observed baseline and dependencies in the specification.
- [x] P-02 — Draft requirements, measurable acceptance, design and ordered tasks
  for QLT-010; link the documentation index and mark the catalogue Draft.
- [x] P-03 — Project owner authorized implementation, reasonable scope decisions,
  tests and PR publication on 2026-10-21. Do not merge or deploy. Existing
  non-QLT capabilities are dependencies, not duplicate implementation tasks.

Selected implementation defaults: Implement an optional local draft generator using immutable Git ranges and reviewed acceptance ledgers. Preserve manual drafts, flag unaccepted changes, and never tag, merge, promote or publish releases.

## Implementation

Start after P-03. Recheck current sources, guidance, version allocations and Git status
before edits. Follow the dependency order below, establishing trust and fixture
ownership before target operations. Where an interface is shared with another QLT
initiative, agree its version/capability contract before integration.

- [x] T-01 — Implement validated range selection, provenance and malformed/moving-range fixtures.
  Maps QLT-010-R01 to QLT-010-AC01; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [x] T-04 — Add sanitization, idempotence, instruction-as-data and manual-edit preservation tests.
  Maps QLT-010-R04 to QLT-010-AC04; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [x] T-02 — Implement acceptance mapping and unsupported/contradictory-claim tests.
  Maps QLT-010-R02 to QLT-010-AC02; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [ ] T-03 — Implement notes formatting and review examples for compatibility, migration and limitations.
  Maps QLT-010-R03 to QLT-010-AC03; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [x] T-05 — Document opt-in adoption, review/publication handoff and correction/rollback procedure.
  Maps QLT-010-R05 to QLT-010-AC05; include the corresponding passing and
  failing acceptance scenarios before advancing.

## Verification and delivery

- [ ] T-06 — Run mapped focused tests, applicable generated-project gates and
  repository checks described in the design; record exact commands, revisions,
  results, skipped layers and limitations. Verify all QLT-010-AC01–AC05 with actual
  evidence; pending private/native/operator trials remain visibly pending.
- [x] T-07 — Push the implementation branch and open a reviewable PR with sanitized
  evidence and known limitations. Do not merge, deploy or imply owner acceptance.

Merge, rollout and owner/device acceptance are downstream review actions excluded
from this implementation authorization, not tasks for the unattended run.

## Current handover

Implementation is pushed in [draft PR #95](https://github.com/danielbardsley/gptclaw/pull/95).
Eight new exact quality-enabled starter releases pass the local and CI matrix.
The source provider is 1.16.0; installed providers were not changed. See
[acceptance evidence](acceptance.md) for every original criterion, passing layers
and remaining trials. Unchecked tasks include partial automated/adoption/manual
scenarios, not an absent implementation. They must not be marked complete merely
because the happy-path matrix passed. Catalogue state remains In review.

The project owner reviews and decides subsequent adoption/acceptance. Merge and
deployment were expressly excluded and have not been performed. Original workspace
changes are preserved in their original checkout; implementation uses an isolated
feature worktree. No user assistance was needed for the executed tests.
