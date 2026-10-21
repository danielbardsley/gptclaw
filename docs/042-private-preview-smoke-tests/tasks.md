# TASKS-042 — Preview smoke tests

Status: Complete — all task records closed at the project owner’s request; implementation merged; remaining acceptance recorded separately. Owner: Project owner.
Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md)

## Planning and authorization

- [x] P-01 — Inspect the catalogue, current source and related initiative records;
  capture observed baseline and dependencies in the specification.
- [x] P-02 — Draft requirements, measurable acceptance, design and ordered tasks
  for QLT-004; link the documentation index and mark the catalogue Draft.
- [x] P-03 — Project owner authorized implementation, reasonable scope decisions,
  tests and PR publication on 2026-10-21. The later request to merge and close
  all tasks supersedes the initial merge exclusion; deployment remains excluded. Existing
  non-QLT capabilities are dependencies, not duplicate implementation tasks.

Selected implementation defaults: Use owned isolated probes in generated checks, an explicit read-only private-ingress CLI, opt-in post-start evidence and a bounded source observer. Never start/stop/restart a service or recover data in response to a smoke failure.

## Implementation

Start after P-03. Recheck current sources, guidance, version allocations and Git status
before edits. Follow the dependency order below, establishing trust and fixture
ownership before target operations. Where an interface is shared with another QLT
initiative, agree its version/capability contract before integration.

- [x] T-01 — Implement trusted target resolution and identity/redirect rejection fixtures.
  Maps QLT-004-R01 to QLT-004-AC01; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [x] T-04 — Implement read-only defaults, explicit write scope and interruption-safe fixture cleanup.
  Maps QLT-004-R04 to QLT-004-AC04; include the corresponding passing and
  failing acceptance scenarios before advancing.
  Closeout: closed by project-owner direction on 2026-10-21; any unperformed
  portions remain pending in acceptance.md.

- [x] T-02 — Build profiles and asset/prefix/health/journey fault scenarios.
  Maps QLT-004-R02 to QLT-004-AC02; include the corresponding passing and
  failing acceptance scenarios before advancing.

- [x] T-03 — Integrate update hooks, generation checks, cancellation and race/timeout tests.
  Maps QLT-004-R03 to QLT-004-AC03; include the corresponding passing and
  failing acceptance scenarios before advancing.
  Closeout: closed by project-owner direction on 2026-10-21; any unperformed
  portions remain pending in acceptance.md.

- [x] T-05 — Add reporting, redaction and separate private-client/native acceptance procedures.
  Maps QLT-004-R05 to QLT-004-AC05; include the corresponding passing and
  failing acceptance scenarios before advancing.

## Verification and delivery

- [x] T-06 — Run mapped focused tests, applicable generated-project gates and
  repository checks described in the design; record exact commands, revisions,
  results, skipped layers and limitations. Verify all QLT-004-AC01–AC05 with actual
  evidence; pending private/native/operator trials remain visibly pending.
  Closeout: closed by project-owner direction on 2026-10-21; any unperformed
  portions remain pending in acceptance.md.
- [x] T-07 — Push the implementation branch and open a reviewable PR with sanitized
  evidence and known limitations. Subsequent merge was explicitly authorized;
  deployment and acceptance observations remain separate.

PR merge and task closure were subsequently authorized by the project owner on
2026-10-21. Rollout and unperformed acceptance trials remain separately tracked.

## Current handover

[PR #95](https://github.com/danielbardsley/gptclaw/pull/95) merged on 2026-10-21 as
`d0d69cc1077bddb6db10501922b5b539efd1bbf1` after all five CI workflows passed on
`cb7bd529778a89a91b3cf63fc96d17ffb2da1ff6`. The local repository gate passed
927 Python tests across 48 suites plus repository invariants and shell fixtures.

The project owner then requested that all tasks be marked complete. Every task
record above is closed under that direction. Previously unchecked tasks include
unperformed verification/adoption portions; their original acceptance criteria
and pending evidence remain in [acceptance.md](acceptance.md). Task closure does
not supply those observations or change pending criteria to passed.

Catalogue status is Implemented: merged source with remaining acceptance gaps.
Source provider 1.16.0 and eight exact 1.1.0 releases are merged; installed
providers, credentials and existing projects were not changed. No deployment,
public exposure or retained-data migration was performed. Original checkout and
unrelated work are preserved.
