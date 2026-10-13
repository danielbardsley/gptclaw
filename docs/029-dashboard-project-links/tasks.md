# TASKS-029: Dashboard project links

- **Status:** Implementation authorized — work in progress
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-029](spec.md) · **Design:** [TDD-029](technical-design.md)

## Planning and authorization

- [x] T-000: Read current private route/status and single/group API prefix contracts;
  draft DSH-003 with explicit missing log-viewer/preview-registry prerequisites.
  Planning requested October 12; no service, exposure or implementation change ran.
- [x] T-001: Project owner approves staged scope/design and authorizes implementation.
  Require reviewed SPEC-027 identity/hosting and SPEC-028 publication/freshness contracts;
  settle route-descriptor version, URL policy and initial integration acceptance limits.

## Dependency-ordered implementation

- [x] T-002: Add reviewed read-only route capability descriptor for owned single/group
  targets; document exact supported app/docs paths and unsupported/conflicted behavior.
  Do not forward operator commands or infer publication from Serve URL alone.
  (LNK-001/004; AC-001/004)
- [x] T-003: Project typed app/docs/repository links with canonical validation, independent
  metadata/status freshness and unavailable reasons. Implement accessible navigation
  and safe external tabs with no backend URL fetches. (LNK-001/002/004/005; AC-001/002/004/005)
- [x] T-004: Add capability-gated logs destination and display-only preview adapter
  contracts; keep absent live prerequisites unavailable. Cover active/expired/revoked,
  stale, wrong-project/forbidden endpoints and elapsed-time expiry with synthetic
  fixtures. No logs handler, preview provisioning or Funnel action. (LNK-002/003/005; AC-002/003)

## Verification and delivery

- [x] T-005: Run meaningful destination/security/clock/freshness/capability tests,
  mutation/network/secret capture spies, keyboard checks and relevant stack/repository
  gates. Inspect UI/routes for scoped behavior and starter-only demos if inherited;
  check diff and relative links. Record exact local outcomes. (AC-001–005)
- [ ] T-006: Deliver implementation PR and record CI separately; roll out privately
  and obtain owner browser acceptance for task-owned web/API/group links and recorded
  repository destinations. Verify outage/unavailable states and rollback without route
  or exposure changes. Record per-criterion local/CI/live/owner evidence in acceptance.md.
  After merge and initial acceptance mark the delivered DSH-003 slice accurately, with
  live log-viewer/preview integrations pending their prerequisites. (AC-001–005)
- [ ] T-007: When independently accepted DSH-006/NET-108 prerequisites exist and their
  integration scope is authorized, replace the unavailable adapters with reviewed
  reads and record actual logs/active-preview navigation evidence. Do not claim full
  live integration from synthetic fixtures or initial-slice acceptance. (LNK-002/003; AC-002/003/005)

## Current handover

Implementation, local checks, all four CI workflows, private rollout and owner
acceptance passed. Inventory, status and links were activated in order. Exact
release/provider/image provenance and per-criterion evidence are in acceptance.md.
Owner-reported group timeouts were corrected through trusted validation reuse,
one fixed authenticated DB readiness query and a documented finite four-second
project deadline; the actual 20-project default-budget test still finishes under
15 seconds. Clean live degradation/recovery completed in 9.62/14.96 seconds.

Review/merge of PR #69 remains. No catalogue feature is Delivered before merge.
Existing applications/data, private access and unrelated handlers remain intact.
Synthetic source/data is retained; only owned fixtures may be stopped after
verification. Logs/preview integrations await their separate prerequisites, and
the owner deferred visual cleanup.
