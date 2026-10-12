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

Only planning documents and roadmap/index references are prepared. Approval and all
implementation/CI/live/browser acceptance remain pending. These plans do not install
a service or change infrastructure. Next action: project owner reviews T-001; then
implement the inventory foundation before SPEC-028 and SPEC-029 integrations. Preserve
unrelated work and clean up only task-owned synthetic verification fixtures.

Implementation authorization is recorded in the specification. Exact packaging and
interface choices are being recorded in the design before rollout; no prior acceptance
result is implied.

Inventory source, socket API, accessible frontend and owned release/unit packaging are
implemented on the isolated branch. Local inventory (12), socket/worker (3), release
recovery (6), frontend boundary (2) tests passed; TypeScript and production build passed.
Live read-only scan found 13 valid projects. Real loopback HTTP and browser checks
passed for inventory rendering, read restrictions, keyboard navigation and error/recovery
states. The initial root-disk ENOSPC build failure was resolved by moving only this
task's worktree/build files to the project volume. Full repository checks passed. CI, service
rollout, private route/operator evidence and owner desktop acceptance remain pending.
