# TASKS-030: Dashboard visual refinement

- **Status:** Approved for implementation — work in progress
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-030](spec.md) · **Design:** [TDD-030](technical-design.md)
- **Reference:** [Mapping and captures](reference.md)

## Planning and authorization

- [x] T-000: Inspect repository/index/catalogue, delivered dashboard contracts and
  current frontend; measure existing read-only layout and draft the planning set.
  Planning requested October 12; no product implementation/service change ran.
- [x] T-001: Inspect/render the supplied HTML offline, record its digest/captures
  and observed pattern, and define the supported adaptation and explicit omissions.
  The attachment resolves the original unavailable URL. Table/full-width inline details,
  local token direction and complete component metrics are proposed concretely.
  Reference captures are planning evidence, not implementation acceptance. (VIS-001)
- [x] T-002: Project owner reviews this concrete spec/design and explicitly authorizes
  implementation/private rollout. Record new scope approval separately from prior
  delivered DSH-001/002/003 authorization and from review/merge/acceptance.
  (VIS-001–006; AC-001–006)

## Dependency-ordered implementation

- [x] T-003: After T-002, implement the reference-derived shell/tokens, managed tile,
  freshness toolbar and compact semantic table with stable full-width disclosure.
  Retain metadata/order/row identity; adapt narrow screens, long values and snapshot
  failures. Omit search/filter/rescan and extra aggregate counters. (VIS-001/VIS-002/VIS-003/VIS-005/VIS-006;
  AC-001/AC-002/AC-004/AC-005)
- [x] T-004: Adapt actual component details and destinations to bordered panels and
  compact pills. Preserve all counters/timing/freshness, state vocabulary, accessible
  reasons, safe anchors and repository independence. Keep refresh focus/open state and
  link activation independent of disclosure. No reference adapter/mock data/logs/preview
  capability is introduced. (VIS-003/VIS-004/VIS-005/VIS-006; AC-003/AC-004/AC-005)

## Verification and delivery

- [x] T-005: Run meaningful synthetic layout/keyboard/contrast/bounds and existing
  status/link/security/expiry/shared-read checks; inspect the actual screen and routes
  against supported scope. Remove/avoid all demo controls/data/runtime from the supplied
  design while retaining health/private-read support. Run frontend tests/types/build and
  applicable repository/diff/link gates. Record deterministic reference comparisons,
  viewport/zoom evidence and executed commands separately from deployment/owner acceptance.
  (AC-001–005)
- [ ] T-006: Deliver the authorized implementation through the PR workflow; roll out
  through the owned private release manager and verify route/identity and owner design,
  group/details/destination acceptance. Exercise owned release rollback; record all
  criterion evidence in acceptance.md. Mark only DSH-015 Delivered after merge/acceptance.
  Clean up only task fixtures and retain data. Broader history/search/logs/previews/UI
  foundation remain separate. (AC-006)

## Current handover

The compact semantic overview, full-width detail panels/component region and
responsive styling are implemented. Existing polling, freshness, destination
validation and private request boundary are reused; unsupported reference controls
and data are absent. Frozen install, seven frontend tests, typecheck/build and the
real HTTP/browser gate passed. Browser checks cover six-row density, responsive
bounds, keyboard/focus preservation, counters/freshness, expiry and contrast.
The extended all-state browser checks and full repository gate passed; all four
implementation CI workflows passed. Private rollout, actual HTTPS/group/navigation
checks and owned old/new release rollback passed. Owner comparison/zoom acceptance
and final review/merge remain. See acceptance.md for exact evidence.

## Implementation authorization

The project owner instructed “implement the spec” on October 12. This approves
SPEC-030 and its documented supported-only adaptation and authorizes implementation
and necessary reversible private rollout/verification through the owned dashboard
release path. Review/merge and actual owner acceptance remain separate delivery gates.
