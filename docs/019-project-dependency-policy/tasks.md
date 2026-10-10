# TASKS-019: Project dependency policy

- **Status:** Implementation authorized; code and local/live checks complete, review/CI pending
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-019](spec.md)
- **Design:** [TDD-019](technical-design.md)

## Planning and authorization

- [x] T-000: Inspect catalogue/sequence, manifest v1 and delivered container/job
  boundaries; draft this independent SYS-003 initiative. No package/service changes.
- [x] T-001: Daniel reviews the single-root/public-registry/no-hook scope and
  authorizes implementation. Resolve exact config/argument/journal contracts and
  verify pinned pnpm behavior before dependent changes. (DEP-001/002; AC-001/002)

## Implementation and verification

- [x] T-002: Implement versioned policy/schema, strict validator and negative
  fixtures; reject foreign paths/sources, executable config, hooks, runtime
  downloads and bypass options before installer calls. (DEP-001/002; AC-001/002)
- [x] T-003: Implement typed dependency operations with existing locks/bounds,
  staged manifest/lock changes, before/after receipts, no user-edit overwrite and
  same-operation crash/timeout recovery. (DEP-003–005; AC-003–005)
- [x] T-004: Integrate the gate/fingerprints into frozen startup/test preparation;
  verify no-hook Next.js compatibility, dirty dependency repair, busy refusal,
  integrity failures and two-project isolation. (DEP-002/004/005; AC-002/004/005)
- [ ] T-005: Update generated guidance/runbook/provider capabilities and tests;
  run relevant repository/CI checks and synthetic add/update/remove/frozen-restore
  plus build/test/private-page acceptance. Record commands, timings, file diffs,
  failure/recovery and Daniel's acceptance; deliver/merge the PR and update only
  the accepted SYS-003 scope. Clean only owned fixtures. (DEP-006; AC-006)

## Current handover

Daniel authorized SYS-003 implementation on October 10. Provider 1.1.0 supplies
strict policy/schema validation, typed deps operations, staged/hash-guarded
publication with captured originals, archived receipts and same-ID recovery.
Startup/test preparation and jobs/services use the policy controls; frozen
metadata mounts are read-only. No-hook frozen Next.js install/build/test and
live add/update/remove, unchanged frozen reuse, running-target refusal, actual
bad-integrity failure/abort/repair and unaffected existing demos were verified.
The full offline repository checker passed; final configured CI/review/merge,
owner acceptance and final delivery status remain T-005. [Acceptance](acceptance.md)
records the detailed evidence and cleanup disposition. SYS-002 remains Draft.
