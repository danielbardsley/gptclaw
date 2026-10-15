# TASKS-026: Development database lifecycle

- **Status:** Delivered — initial development slice; merged implementation and actual managed/client acceptance
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

- [x] T-011: Run focused isolated suites, prepared repository gates, changed shell
  syntax, generated exact-container checks and real database/browser/golden CI.
  Review links/whitespace, capability/compatibility and secret/data exclusion.
  Write database runbook with actual command syntax, protected recovery/reset/prune,
  rollout/rollback and snapshot/host-loss limitations. Submit implementation PR and
  record final-head CI. Depends on T-010. DB-001–009; AC-001–009.
- [x] T-012: After authorized provider rollout and named synthetic fixture selection,
  prove managed EC2 persistence, roles/networks, rotation, migrations, dump/restore,
  reset/retention, failed/interrupted recovery and two-project/legacy isolation.
  Measure budgets/timings and trial safe provider/generation rollback. Obtain
  independent browser persistence confirmation. Record sanitized acceptance.md by
  AC-001–009, actual local/CI/live/client results, revisions and fixture disposition.
  Complete review/merge and project owner acceptance, then mark only this initial
  RUN-011 slice Delivered. Broader SEC/RUN-012/RES/production remains separately
  scoped. Depends on T-011 and actual evidence. DB-009; AC-009.

## Current handover

The approved initial RUN-011 slice is delivered through reviewed implementation
PRs #60/#62/#63/#64/#65 and installed provider 1.8.4. Two distinct private full
web/API/PostgreSQL applications have their own roots, specs/guidance/copied skills,
repositories, source CI and managed data. Actual private browser CRUD and owner
synthetic write/reload acceptance pass. Managed persistence, native backup/reset/
restore, forward/failed migration, interrupted rotation recovery, roles/networks,
protected-operation refusals and legacy isolation pass. Both actual installed Git
commit hooks pass full isolated database/quality/browser verification.

Local final repository checks pass 464 unittest cases; all final provider CI
workflows pass. Source and owner changes, selected credentials, local verified
backups and active/rollback generations are retained. Evidence distinguishes
isolated, CI, managed and owner observations, including earlier failed attempts
and a non-reproduced isolated reset failure. Production/cloud-secret management,
volume/host-loss recovery, RPO/RTO and broader SEC/RUN-012 work remain separate.
See [acceptance](acceptance.md) for exact revisions, limits and fixture disposition.

## Managed storage correction

- [x] T-013: Correct the unwritable pre-allocation data-root assumption using the
  existing private owned volume runtime directory. Add a closed storage selector
  with older-provider and absent-selector refusal; preserve published releases and
  reject implicit legacy-data migration. Run relevant isolated/real/CI gates, merge
  the reviewed 1.8.2 provider and resume both uninitialized authorized targets.
  DB-001/002/003/009; AC-001/002/003/009. This reversible unprivileged correction
  is necessary to the directly authorized full platform test; AWS/host privilege
  changes remain excluded. Initial failure allocated no data or role credentials.

## Rotation ownership correction

- [x] T-014: Transfer owned application objects from retained migration identities
  during grants/rotation; block readiness for unfinished operation journals.
  Actual managed relational writes failed after 1.8.2
  rotation while readiness/read tests passed; foreign-key checks ran under a prior
  table owner without schema access. Add native post-rotation foreign-key/identity
  writes and migration DDL regression; review/merge provider 1.8.3, rotate both
  authorized synthetic projects and rerun actual private browser CRUD.
  DB-003/005/009; AC-003/005/008/009. Preserve data and existing grants/scopes.

- [x] T-015: Pin database bootstrap mounts to the immutable provider and reconcile
  source/previous-provider paths only when trusted bootstrap bytes and every
  other unit byte match. The installed runner refused a source-started database
  stop with a bootstrap-path conflict; retained data was preserved. Test changed
  scripts, unknown paths and unrelated unit edits; resume managed acceptance
  through the reviewed installed runner after final-head CI/merge. DB-002/004/009;
  AC-002/004/009. No unknown unit or host control may be overwritten.

- [x] T-016: Exclude generated frontend/Python check output from evolved-source
  verification fixtures. A real installed commit hook copied Next.js development
  output and refused its generated path names before allocating a database.
  Add an unsafe-name/output-link regression, deliver reviewed provider 1.8.4,
  replace only the exact task-owned prior hook through its installer, and prove
  both actual Git commit hooks. Preserve live data, source and unknown hooks.
  DB-008/009; AC-008/009.

- [x] T-017: Require the final PostgreSQL listener before readiness during fresh
  initialization, including staged restore/reset generations. The controlled five-
  second bootstrap pause and focused polling regression pass with corrected code;
  full repository checks pass 465 cases. Deliver through reviewed provider 1.8.5.
  The two named hook updates and full isolated cleanup gates are tracked in their
  application cleanup PRs; preserve data and published releases.
