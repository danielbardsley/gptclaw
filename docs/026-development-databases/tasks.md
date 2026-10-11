# TASKS-026: Development database lifecycle

- **Status:** Draft — planning complete; implementation not authorized
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-026](spec.md) · **Design:** [TDD-026](technical-design.md)

## Planning and authorization

- [x] T-001: Inspect repository/area guidance, Git state, catalogue/index, runtime,
  manifest/profile sources, SPEC-025 and existing snapshot/recovery contracts.
  Draft requirements/design/acceptance/tasks and update index/catalogue/sequence.
  Evidence: these documents; local development credentials were explicitly selected
  in the current chat, with production Secrets Manager deferred to production work.
- [ ] T-002: Project owner reviews the concrete scope and approves implementation
  separately from planning. Confirm the proposed synthetic-only native restore gate
  without closing broad RES-002/004; agree named live fixtures/reset scope before
  live data operations. Record authorization without asking again for settled local
  credential preference. Gate for T-003 onward; DB-009, AC-009.

## Implementation

- [ ] T-003: Finalize compatible exact PostgreSQL image/client tools, new manifest/
  catalogue/provider/receipt versions and closed web/API/DB contract. Implement
  observation-only validation, generation/provenance and old-provider refusal.
  Test unsafe declarations and v1–v3/release compatibility. Depends on T-002.
  DB-001; AC-001.
- [ ] T-004: Add versioned persistent ownership and data generations on the verified
  project-volume mount, no-follow/UID/permission checks and recoverable allocation.
  Distinguish uninitialized/missing/corrupt storage; prove no implicit reinitialization
  or deletion on lifecycle/rollback. Verify pinned image UID/PGDATA behavior and two
  project isolation. Depends on T-003. DB-002; AC-002.
- [ ] T-005: Implement local random role credentials, restricted store, selected
  read-only runtime snapshots, app/migration/admin grants and versioned stopped
  rotation with interruption recovery. Canary-test every output/argv/env/inspection
  boundary and privilege denial; never capture actual secrets as evidence.
  Depends on T-004. DB-003; AC-003.
- [ ] T-006: Extend owned group network/lifecycle/status/logs for DB-first readiness,
  schema checks, private backend access, bounded shutdown/resources and operation
  locks/journals. Prove outage/recovery, partial start, busy/interrupted reconciliation
  and retained data while legacy projects remain healthy. Depends on T-004/T-005.
  DB-004; AC-002, AC-004.
- [ ] T-007: Implement explicit Alembic plan/apply and schema-readiness contracts;
  tie approval to revisions/source/generation/credential epoch/verified backup.
  Test fresh setup, forward upgrade, changed plans, unsupported histories and failed
  migrations with restore recovery. Depends on T-006 and T-008 backup/restore gates;
  design migration revisions in parallel, but no existing-data apply before recovery
  is functional. DB-005; AC-005.
- [ ] T-008: Implement consistent bounded custom dumps, safe receipts, checksums,
  real restore verification, owned fresh-generation restore and explicit promotion/
  rollback. Recreate roles/grants without exporting passwords. Test corrupted,
  incompatible/unknown/wrong-project artifacts and interrupted promotion preserving
  active data. Depends on T-006. DB-006; AC-006.
- [ ] T-009: Add stopped reset, fixed synthetic seed and count/byte/free-space limits;
  preview/confirm exact prune IDs and preserve active/sole-verified/referenced data.
  Test stale approvals, missing backup, running/busy refusal, reset failures and
  unrelated-data preservation. Depends on T-007/T-008. DB-007; AC-007.
- [ ] T-010: Publish a separate exact persistent notes starter with complete locked
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

Planning only. The clean main baseline observed is `c1afac9`, merge of PR #58;
SPEC-025's historical acceptance closeout is still independently pending. The project
owner selected local development credential storage; no cloud secret resources or
production work is proposed. The draft uses per-project rootless PostgreSQL and a
new persistent notes release with explicit migrations and logical recovery.

Scope approval must accept the narrowed synthetic-only recovery prerequisite;
broad volume/host restore evidence is not invented or marked complete. Exact image/
locks/versions and measured budgets are finalized before activation. No database,
credentials, provider installation or data operation has been performed by this task.
Documentation verification passed: `git diff --check` and `git diff --cached
--check`; a task-local Python review resolved all 198 relative local links across
these three new documents and the index/catalogue/sequence, verified nine requirement
and nine acceptance IDs across the companion documents, and confirmed that only
T-001 is checked. No new tests were added for this documentation-only change;
repository runtime tests and Terraform checks were not run because no executable
or infrastructure files changed. CI and live database behavior are not claimed.
Implementation tasks remain unchecked; remote planning PR publication is pending.
