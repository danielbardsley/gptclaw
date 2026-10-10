# TASKS-021: Versioned template catalogue

- **Status:** Delivered — initial web slice merged and accepted
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-021](spec.md) · **Design:** [TDD-021](technical-design.md)

## Planning and authorization

- [x] T-000: Inspect current roadmap, template creation, provider marker/bundle and
  accepted dependency/toolchain contracts; draft the initial PRJ-003 web-entry
  specification/design/tasks. Daniel requested planning; no implementation ran.
- [x] T-001: Daniel reviews/approves initial scope and authorizes implementation.
  Settle release schema bounds, substitutions, compatibility/provenance and
  no-overwrite publication contract before dependent implementation. Confirm
  initial release bytes/pins against accepted implementation baseline.

## Implementation

- [x] T-002: Add strict catalogue/schema/resolver and immutable initial release;
  consolidate starter consumers and implement baseline release immutability checks.
  Cover integrity, path/symlink, duplicate, bounds and compatibility refusals.
  (CAT-001/002; AC-001/002)
- [x] T-003: After T-002, add list/show and exact/default new selection, owned
  staging and serialized no-overwrite publication. Test deterministic generation,
  two offline releases, bad selection, collisions, races and interruption recovery.
  (CAT-001/003; AC-001/003)
- [x] T-004: Add separate release provenance validation and exact toolchain output;
  preserve legacy marker-only apps and edited sources. Package catalogue/releases
  into immutable provider snapshots and expose additive capabilities. Verify
  source/installed parity, default changes and bounded rollback compatibility.
  (CAT-004/005; AC-004/005)

## Verification and delivery

- [x] T-005: Write catalogue/release/recovery guide and generated usage guidance;
  update tests/CI to validate actual release generation and run existing frozen
  dependency/build/test/typecheck checks. Run repository checker, changed script
  syntax, whitespace and relative-link checks; record outcomes. (CAT-006; AC-006)
- [x] T-006: Run scoped synthetic private-web acceptance through the reviewed
  provider; confirm independent app availability and source-preserving stop.
  Record exact revision/release digest, timings, local/CI/live evidence and
  Daniel's acceptance in acceptance.md. Deliver/merge reviewed PR, mark only
  accepted PRJ-003 slice Delivered and retain broader-stack follow-ups. Clean
  only proven task-owned fixtures. (CAT-005/006; AC-005/006)

## Current handover

Daniel authorized implementation October 10 with “Ok, now implement the spec”.
Provider 1.3.0 implements schema-1 catalogue discovery, exact/default selection,
release integrity, separate provenance and atomic no-replace generation. Linux
renameat2 under a destination-derived runtime lock is the publication primitive;
failed stages remain owned recovery fixtures. The first release is the accepted
Next.js web starter with exact Node/pnpm selection. Existing ignored cache was
preserved at its original location and excluded from release assets/commits.

All 111 focused tests (32 lifecycle, 27 dependency, 31 toolchain, 21 catalogue),
repository checks and changed-script syntax/whitespace checks passed. Live frozen
install/test/build/typecheck/private page/health/17 assets, installed list/show
parity and source-preserving stop passed. A marker-only legacy acceptance app
validated/tested/started without rewriting metadata. The acceptance app is stopped;
its source/receipts are retained. Both independent demos remained ready.
[Acceptance](acceptance.md) records detailed evidence. All three final PR-head
CI workflows passed. Daniel accepted the reviewed slice with “ok, merge the PR”;
PR #50 merged as `527f04dfd6db8299418cfada88397b8e76e03d58` October 10.
T-006 and this initial scope are complete. Broader stacks, automatic upgrades,
GitHub automation and RES work remain outside scope.
