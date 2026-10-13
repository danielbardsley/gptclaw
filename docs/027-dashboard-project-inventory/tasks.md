# TASKS-027: Dashboard project inventory

- **Status:** Implementation authorized — work in progress
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-027](spec.md) · **Design:** [TDD-027](technical-design.md)

## Planning and authorization

- [x] T-000: Read roadmap, manifest/provider interfaces and current hosting guidance;
  draft separate DSH-001 specification, design and acceptance mapping. Planning
  requested October 12; no implementation, runtime installation or deployment ran.
- [x] T-001: Project owner reviews scope/design and authorizes implementation.
  Settle source/release ownership, platform path, stack, route and operator boundary;
  record exact unit/socket contracts, versioned metadata/response shapes and budgets.

## Dependency-ordered implementation

- [x] T-002: Build the bounded immediate-directory inventory adapter using complete
  validation and safe lookup. Add metadata/presence projection, duplicate-ID refusal,
  provider-support detection, row keys and synthetic failure/bounds/secret fixtures.
  No repository commands or network discovery. (INV-001/002/003; AC-001/002/003)
- [x] T-003: After T-002, add the versioned typed read/socket interface and rootless
  frontend. Implement semantic inventory, safe text rendering, timestamps and empty,
  stale, partial and unavailable states; enforce method/host/origin/path bounds.
  (INV-002/003/004/005; AC-002/003/004/005)
- [x] T-004: Prepare pinned platform packaging, owned service lifecycle and private
  route runbook with rollback; verify current installed-provider/toolchain parity.
  Review any required operator/IaC change before installation. Preserve `/projects/`,
  unknown units and all unrelated routes. (INV-004; AC-004)

## Verification and delivery

- [x] T-005: Remove starter-only demos if adapting a starter; inspect actual routes/UI
  against scope and retain justified health/security support. Run meaningful fixture,
  API and accessibility tests, appropriate repository/stack checks, diff and relative
  links. Record exact local commands/outcomes and limitations. (All INV; AC-001–005)
- [ ] T-006: Deliver reviewed implementation PR and record CI separately. Roll out
  through the reviewed private platform path, verify identity/listeners/mounts/Serve,
  and obtain owner desktop-browser inventory acceptance. Exercise collector failure
  and rollback without affecting project runtimes/data. Create acceptance.md with
  per-criterion evidence; mark DSH-001 Delivered only after merge and acceptance.
  Do not mark broader PRJ-007/UI/degraded-mode features delivered. (AC-001–005)

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
