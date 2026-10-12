# TASKS-026: Development database lifecycle

- **Status:** Approved — implementation in progress
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-026](spec.md) · **Design:** [TDD-026](technical-design.md)

## Planning and authorization

- [x] T-001: Inspect repository/area guidance, Git state, catalogue/index, runtime,
  manifest/profile sources, SPEC-025 and existing snapshot/recovery contracts.
  Draft requirements/design/acceptance/tasks and update index/catalogue/sequence.
  Evidence: these documents; local development credentials were explicitly selected
  in the current chat, with production Secrets Manager deferred to production work.
- [x] T-002: Project owner reviews the concrete scope and approves implementation
  separately from planning. Approve the synthetic-only native restore gate
  without closing broad RES-002/004; keep named live fixtures/reset scope as the
  separate T-012 approval gate. Record authorization without asking again for settled local
  credential preference. Gate for T-003 onward; DB-009, AC-009. Evidence: project owner scope and
  implementation approval; named live fixtures and destructive-operation confirmations
  remain separate gates.

## Implementation

- [x] T-003: Finalize compatible exact PostgreSQL image/client tools, new manifest/
  catalogue/provider/receipt versions and closed web/API/DB contract. Implement
  observation-only validation, generation/provenance and old-provider refusal.
  Test unsafe declarations and v1–v3/release compatibility. Depends on T-002.
  DB-001; AC-001.
- [x] T-004: Add versioned persistent ownership and data generations on the verified
  project-volume mount, no-follow/UID/permission checks and recoverable allocation.
  Distinguish uninitialized/missing/corrupt storage; prove no implicit reinitialization
  or deletion on lifecycle/rollback. Verify pinned image UID/PGDATA behavior and two
  project isolation. Depends on T-003. DB-002; AC-002.
- [x] T-005: Implement local random role credentials, restricted store, selected
  read-only runtime snapshots, app/migration/admin grants and versioned stopped
  rotation with interruption recovery. Canary-test every output/argv/env/inspection
  boundary and privilege denial; never capture actual secrets as evidence.
  Depends on T-004. DB-003; AC-003.
- [x] T-006: Extend owned group network/lifecycle/status/logs for DB-first readiness,
  schema checks, private backend access, bounded shutdown/resources and operation
  locks/journals. Prove outage/recovery, partial start, busy/interrupted reconciliation
  and retained data while legacy projects remain healthy. Depends on T-004/T-005.
  DB-004; AC-002, AC-004.
- [x] T-007: Implement explicit Alembic plan/apply and schema-readiness contracts;
  tie approval to revisions/source/generation/credential epoch/verified backup.
  Test fresh setup, forward upgrade, changed plans, unsupported histories and failed
  migrations with restore recovery. Depends on T-006 and T-008 backup/restore gates;
  design migration revisions in parallel, but no existing-data apply before recovery
  is functional. DB-005; AC-005.
- [x] T-008: Implement consistent bounded custom dumps, safe receipts, checksums,
  real restore verification, owned fresh-generation restore and explicit promotion/
  rollback. Recreate roles/grants without exporting passwords. Test corrupted,
  incompatible/unknown/wrong-project artifacts and interrupted promotion preserving
  active data. Depends on T-006. DB-006; AC-006.
- [x] T-009: Add stopped reset, fixed synthetic seed and count/byte/free-space limits;
  preview/confirm exact prune IDs and preserve active/sole-verified/referenced data.
  Test stale approvals, missing backup, running/busy refusal, reset failures and
  unrelated-data preservation. Depends on T-007/T-008. DB-007; AC-007.
- [x] T-010: Publish a separate exact persistent notes starter with complete locked
  SQLAlchemy/Psycopg/Alembic dependencies, source migrations, concurrent-safe CRUD/
  capacity constraints, updated UI/README and synthetic seed. Preserve existing
  defaults/releases. Add real PostgreSQL/browser/generated CI and meaningful quality/
  security/coverage failure tests. Depends on T-003/T-007/T-009. DB-008; AC-008.

## Verification and delivery

- [ ] T-011: Run focused isolated suites, prepared repository gates, changed shell
  syntax, generated exact-container checks and real database/browser/golden CI.
  Review links/whitespace, capability/compatibility and secret/data exclusion.
  Write database runbook with actual command syntax, protected recovery/reset/prune,
  rollout/rollback and snapshot/host-loss limitations. Submit implementation PR and
  record final-head CI. Depends on T-010. DB-001–009; AC-001–009.
- [ ] T-012: After authorized provider rollout and named synthetic fixture selection,
  prove managed EC2 persistence, roles/networks, rotation, migrations, dump/restore,
  reset/retention, failed/interrupted recovery and two-project/legacy isolation.
  Measure budgets/timings and trial safe provider/generation rollback. Obtain
  independent browser persistence confirmation. Record sanitized acceptance.md by
  AC-001–009, actual local/CI/live/client results, revisions and fixture disposition.
  Complete review/merge and project owner acceptance, then mark only this initial
  RUN-011 slice Delivered. Broader SEC/RUN-012/RES/production remains separately
  scoped. Depends on T-011 and actual evidence. DB-009; AC-009.

## Current handover

Implementation is complete on `codex/run-011-spec`; review/CI and managed/client
acceptance remain. The project owner approved the scope and local development credential decision. Provider 1.8.0 adds project/
catalogue v4 and group receipt v3, exact PostgreSQL 18.6, retained per-project data,
closed local role-file materialization, DB-first private lifecycle, migration/backup/
restore/reset/seed/rotation/prune/recovery commands and `notes-postgres@1.0.0`.
Existing releases/defaults and infrastructure are preserved.

Actual local results: `./scripts/check-repository.sh` passes 447 unittest cases and
its shell/invariant/release gates. Focused DB ownership suite passes 11 tests,
including unit permissions/unknown systemd overrides. Real rootless PostgreSQL
checks pass initialization, role denial, container recreation persistence, native
backup/verified restore, confirmed reset/restore/rotation, old-login denial, generation
prune, failed-reset preservation, corruption refusal and a data-preserving forward
migration. All locked API gates and the complete frontend/browser/OpenAPI workflow
pass. Critical API coverage is 328/331 statements and 31/32 branches. A final native
rerun covers the subsequent generic schema-content digest/schema-role restore change.

Whitespace, changed Bash syntax, Python compilation, local-link review and old
release immutability pass. Terraform checks/apply were not run locally because no
Terraform source changed. Earlier unsuccessful checks and their fixes are recorded
in [acceptance](acceptance.md); they are not represented as passes. CI is not inferred
from local checks. T-011 remains open for the implementation PR/final-head CI;
T-012 remains open for managed rollout, two-project/legacy/client observations and
review/merge/acceptance. No managed provider or existing data has been changed.

The available proposed managed acceptance targets are `run011-notes-a` and
`run011-notes-b`, checked absent in source/data/runtime metadata. They remain proposals,
not created projects. After review, the owner must approve their scoped provider
rollout and synthetic reset/restore/rotation trials before live operations. Retain
source and data after acceptance unless exact cleanup is separately authorized.

The project owner approved public-repository publication and merge into main.
[PR #60](https://github.com/danielbardsley/gptclaw/pull/60) is open and its three
configured workflows are running. Local code/checks are complete; final-head CI
and the authorized merge remain in T-011. Managed acceptance remains in T-012. The
confidentiality review found no actual secrets/private identifiers in the candidate
or its unpublished commits and removed private-chat/internal review commentary.
