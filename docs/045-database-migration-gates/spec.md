# SPEC-045 — Database migration gates (QLT-007)

- **Status:** Draft for review; implementation not authorized by this planning request.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-007
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

Application database changes reach review and managed execution only with tested forward
migrations, verified backup prerequisites, explicit destructive-risk review and a
credible recovery path.

Run fresh-schema and previous-release-to-current forward migrations in isolated
synthetic databases. Include data-preservation and representative old-client checks.
Flag destructive SQL patterns and require a human risk declaration; arbitrary migration
Python means static detection is advisory, never proof of safety. Managed execution
keeps SPEC-026 target/source/backup fingerprint checks and locks. New-empty
initialization remains distinct from mutating existing data.

This request authorizes drafting the specification, design and tasks. Specification
approval, implementation authorization, PR review/merge, rollout and acceptance remain
separate. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

SPEC-026 already delivers a synthetic PostgreSQL development slice with separate roles,
locked plan/apply, migration fingerprints and verified logical backup/restore
prerequisites. SPEC-036 extends API/DB use. This initiative standardizes
generated-project review/CI gates around those controls; it does not replace their
acceptance or establish host-loss/production recovery.

Reuse SPEC-026 database ownership/backup/recovery interfaces and QLT-001/002 CI. QLT-008
provides client/API compatibility assertions; broader RES recovery and production
authorization remain separate.

Source/previous-record evidence, not a new runtime verification:

- [docs/026-development-databases/spec.md](../../docs/026-development-databases/spec.md)
- [docs/026-development-databases/technical-design.md](../../docs/026-development-databases/technical-design.md)
- [scripts/project_database.py](../../scripts/project_database.py)
- [scripts/tests/test_project_database.py](../../scripts/tests/test_project_database.py)
- [templates/apps/releases/fastapi-postgres/1.0.0/api/migrations/versions/0001_notes.py](../../templates/apps/releases/fastapi-postgres/1.0.0/api/migrations/versions/0001_notes.py)
- [runbooks/manage-development-databases.md](../../runbooks/manage-development-databases.md)

## Requirements

### QLT-007-R01 — Forward migration tests

Test empty initialization and upgrade from the previous accepted application schema,
preserving synthetic records and application invariants; reject ambiguous revision
graphs and missing revisions.

### QLT-007-R02 — Risk review

Detect common destructive operations and require a declared risk/recovery assessment for
all migration-code changes, with stronger review for destructive or opaque operations.

### QLT-007-R03 — Backup-bound execution

Retain recent verified restore-tested backup prerequisites for existing-data mutation,
bound to canonical target/schema generation, migration fingerprint and source revision
under the existing lock.

### QLT-007-R04 — Recovery and interruption

Document and rehearse roll-forward or restore with expected data consequences; preserve
data/backups on failure and prevent publication after unresolved partial migration.

### QLT-007-R05 — Compatibility and separation

Check the previous accepted API/client against compatible schema upgrades, keep
migration/admin roles out of application/PR environments and report production/recovery
limitations.

## Acceptance criteria

All criteria are pending; drafting does not establish implementation acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-007-AC01 | Fresh and forward trials pass with preserved rows; duplicate/missing heads, failing migration and data-loss fixtures fail CI. | QLT-007-R01 |
| QLT-007-AC02 | Drop/rename/narrowing/raw-code fixtures trigger review findings; absent assessment blocks the gate; clean static output never suppresses the human declaration. | QLT-007-R02 |
| QLT-007-AC03 | Missing, stale, corrupt or wrong-target backup and changed-plan/source cases are refused without mutation; a matching reviewed plan succeeds on an owned fixture. | QLT-007-R03 |
| QLT-007-AC04 | An injected interrupted/nontransactional failure blocks readiness/publication; a separate synthetic recovery rehearsal restores verified data; code revert alone is not reported as schema recovery. | QLT-007-R04 |
| QLT-007-AC05 | An additive change preserves old-client behavior; an incompatible fixture fails; ordinary app role DDL is denied and hosted PR checks contain only ephemeral credentials. | QLT-007-R05 |

## Decisions and completion

Project owner confirms the initial PostgreSQL/Alembic matrix and migration-risk
classification. Extend to other engines only after their own backup, restore and
privilege contracts are reviewed.

This is a proposed default, not a recorded owner decision. The project owner reviews the
open decision before dependent implementation; source discovery and planning review can
proceed meanwhile. Implementation should recheck current source versions, supported
templates and applicable guidance rather than assume this snapshot establishes installed
capability.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.