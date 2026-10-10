# TASKS-020: Pinned language toolchains

- **Status:** Draft; planning requested, implementation not authorized
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-020](spec.md)
- **Design:** [TDD-020](technical-design.md)

## Planning and authorization

- [x] T-000: Inspect the fixed SPEC-018 image, manifest v1, sequence and host-tool
  boundaries; draft a separate initial Node/pnpm selection initiative.
- [ ] T-001: Daniel reviews/authorizes implementation. Settle sidecar/registry/
  receipt schemas, metadata compatibility, exact artifact integrity and supported
  platform before acquisition. Confirm SYS-003 integration readiness; registry/
  validator work may proceed independently. (LNG-001/002; AC-001/002)

## Implementation and verification

- [ ] T-002: Implement strict observation-only declaration/registry validation,
  immutable initial profile and synthetic distinct-profile fixtures. Preserve
  manifest v1 and reject unknown/ranged/conflicting selections. (LNG-001/002;
  AC-001/002)
- [ ] T-003: Implement bounded rootless acquisition, per-profile serialization,
  integrity/actual-version verification, receipts and verified reuse; cover
  missing pins, conflicts and interrupted outcomes. (LNG-003; AC-003)
- [ ] T-004: After the SYS-003 adapter is accepted, integrate one selected image
  into dependency/build/test/start, state invalidation and inspect/prepare. Add
  explicit new-project metadata and fixed legacy compatibility/adoption; prove
  active-target refusal and unaffected second-app state. (LNG-004/005; AC-004/005)
- [ ] T-005: Write the support matrix/runbook, update provider snapshots and run
  relevant repository/CI plus synthetic uncached/cached/legacy/new live acceptance.
  Record versions, commands, timings, migration/rollback, failures and Daniel's
  acceptance. Merge implementation and update only the accepted web slice;
  remove only owned fixtures. Keep Python/uv/Expo follow-ups explicit. (LNG-006;
  AC-006)

## Current handover

Only planning is complete. No sidecar, registry, new profile/image, provider command
or live migration was created. Daniel owns scope review/authorization; implement
SYS-003 first for automatic dependency use. Existing apps stay on their accepted
fixed toolchain until an explicitly authorized migration. Later languages belong
to stage 12 and their selected stack specifications.
