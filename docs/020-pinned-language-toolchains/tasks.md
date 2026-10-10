# TASKS-020: Pinned language toolchains

- **Status:** Implementation authorized; code, local/live and CI checks complete; review/merge pending
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-020](spec.md)
- **Design:** [TDD-020](technical-design.md)

## Planning and authorization

- [x] T-000: Inspect the fixed SPEC-018 image, manifest v1, sequence and host-tool
  boundaries; draft a separate initial Node/pnpm selection initiative.
- [x] T-001: Daniel reviews/authorizes implementation. Settle sidecar/registry/
  receipt schemas, metadata compatibility, exact artifact integrity and supported
  platform before acquisition. Confirm SYS-003 integration readiness; registry/
  validator work may proceed independently. (LNG-001/002; AC-001/002)

## Implementation and verification

- [x] T-002: Implement strict observation-only declaration/registry validation,
  immutable initial profile and synthetic distinct-profile fixtures. Preserve
  manifest v1 and reject unknown/ranged/conflicting selections. (LNG-001/002;
  AC-001/002)
- [x] T-003: Implement bounded rootless acquisition, per-profile serialization,
  integrity/actual-version verification, receipts and verified reuse; cover
  missing pins, conflicts and interrupted outcomes. (LNG-003; AC-003)
- [x] T-004: After the SYS-003 adapter is accepted, integrate one selected image
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

Daniel authorized this initial web slice on October 10, after SYS-003 acceptance
and merge. Provider 1.2.0 adds exact sidecar/profile selection, pinned artifact
verification, bounded acquisition, actual-version checks, receipts/reuse, typed
inspect/prepare and shared image/fingerprint integration. New apps have explicit
metadata; no-declaration legacy apps map to the frozen baseline without source
rewriting. Offline distinct-profile fixtures, failure/conflict/lock checks and
synthetic EC2 cold/reuse/frozen/build/test/private-page/legacy-adoption acceptance
are recorded in [acceptance.md](acceptance.md). Existing demo source/state and
private page/health remained unchanged. All 90 focused tests, the full repository checker and three configured CI
workflows passed. T-005 retains review, owner acceptance and merge gates. Python/uv/Expo belong to stage 12 and their stack specifications.
