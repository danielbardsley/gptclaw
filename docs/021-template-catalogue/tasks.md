# TASKS-021: Versioned template catalogue

- **Status:** Draft — implementation not authorized
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-021](spec.md) · **Design:** [TDD-021](technical-design.md)

## Planning and authorization

- [x] T-000: Inspect current roadmap, template creation, provider marker/bundle and
  accepted dependency/toolchain contracts; draft the initial PRJ-003 web-entry
  specification/design/tasks. Daniel requested planning; no implementation ran.
- [ ] T-001: Daniel reviews/approves initial scope and authorizes implementation.
  Settle release schema bounds, substitutions, compatibility/provenance and
  no-overwrite publication contract before dependent implementation. Confirm
  initial release bytes/pins against accepted implementation baseline.

## Implementation

- [ ] T-002: Add strict catalogue/schema/resolver and immutable initial release;
  consolidate starter consumers and implement baseline release immutability checks.
  Cover integrity, path/symlink, duplicate, bounds and compatibility refusals.
  (CAT-001/002; AC-001/002)
- [ ] T-003: After T-002, add list/show and exact/default new selection, owned
  staging and serialized no-overwrite publication. Test deterministic generation,
  two offline releases, bad selection, collisions, races and interruption recovery.
  (CAT-001/003; AC-001/003)
- [ ] T-004: Add separate release provenance validation and exact toolchain output;
  preserve legacy marker-only apps and edited sources. Package catalogue/releases
  into immutable provider snapshots and expose additive capabilities. Verify
  source/installed parity, default changes and bounded rollback compatibility.
  (CAT-004/005; AC-004/005)

## Verification and delivery

- [ ] T-005: Write catalogue/release/recovery guide and generated usage guidance;
  update tests/CI to validate actual release generation and run existing frozen
  dependency/build/test/typecheck checks. Run repository checker, changed script
  syntax, whitespace and relative-link checks; record outcomes. (CAT-006; AC-006)
- [ ] T-006: Run scoped synthetic private-web acceptance through the reviewed
  provider; confirm independent app availability and source-preserving stop.
  Record exact revision/release digest, timings, local/CI/live evidence and
  Daniel's acceptance in acceptance.md. Deliver/merge reviewed PR, mark only
  accepted PRJ-003 slice Delivered and retain broader-stack follow-ups. Clean
  only proven task-owned fixtures. (CAT-005/006; AC-005/006)

## Current handover

Planning files exist; scope approval and implementation authorization remain
pending. The initial proposal registers one accepted Next.js starter with exact
release discovery/selection and provenance. Other stacks, template upgrades,
GitHub automation and RES work are outside this initiative. Next action is
Daniel's review of SPEC-021/TDD-021, followed by T-001 before code changes.
