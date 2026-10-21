# TDD-045 — Database migration gates

Status: Implementation authorized; design updated with source changes. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

SPEC-026 already delivers a synthetic PostgreSQL development slice with separate roles,
locked plan/apply, migration fingerprints and verified logical backup/restore
prerequisites. SPEC-036 extends API/DB use. This initiative standardizes
generated-project review/CI gates around those controls; it does not replace their
acceptance or establish host-loss/production recovery.

Reuse SPEC-026 database ownership/backup/recovery interfaces and QLT-001/002 CI. QLT-008
provides client/API compatibility assertions; broader RES recovery and production
authorization remain separate.

Run fresh-schema and previous-release-to-current forward migrations in isolated
synthetic databases. Include data-preservation and representative old-client checks.
Flag destructive SQL patterns and require a human risk declaration; arbitrary migration
Python means static detection is advisory, never proof of safety. Managed execution
keeps SPEC-026 target/source/backup fingerprint checks and locks. New-empty
initialization remains distinct from mutating existing data.

Reuse the version and command sources linked in the specification. Any new
packages/actions/images need exact reviewed pins during implementation; this planning
change installs nothing and reserves no future schema version. Application-provided
commands and fetched content remain untrusted task data. Validate identity/capability
before execution; run authorized checks in the reviewed container boundary rather than
during metadata discovery.

## Components and traceability

The following components are proposed responsibilities, not claims that new interfaces
already exist. T-01 through T-05 identify implementation work; follow the dependency
order in the task list. T-06 covers combined verification and T-07 covers
acceptance/delivery.

| Requirement | Planned mechanism/component change | Task | Acceptance |
|---|---|---|---|
| QLT-007-R01 | Use isolated PostgreSQL/Alembic fixtures and explicit previous-release seeds, without borrowing credentials or data from a managed project. | T-01, T-06, T-07 | QLT-007-AC01 |
| QLT-007-R02 | Combine bounded heuristic analysis with a reviewed migration checklist and owner disposition; never execute code during discovery to classify it. | T-02, T-06, T-07 | QLT-007-AC02 |
| QLT-007-R03 | Reuse SPEC-026 plan/apply and backup verification; CI evidence cannot stand in for a target-specific backup. | T-03, T-06, T-07 | QLT-007-AC03 |
| QLT-007-R04 | Keep operation receipts and reconciliation rules; use staged restore and explicit writer exclusion from SPEC-026, with no automatic downgrade. | T-04, T-06, T-07 | QLT-007-AC04 |
| QLT-007-R05 | Pair QLT-008 contract fixtures with DB integration tests and isolated role provisioning; keep runtime secrets outside source/artifacts. | T-05, T-06, T-07 | QLT-007-AC05 |

## Verification and evidence

Use the acceptance scenarios in [the specification](spec.md), including negative
and interrupted/failure cases where mapped. Keep fixtures synthetic, bounded and
task-owned; clean up only resources whose ownership is established. Preserve
unrelated source, projects, persistent data and historical acceptance evidence.

For implementation, run `git diff --check`, `git diff --cached --check` and the relevant
script/stack tests. Script, template, workflow or schema changes also require the
prepared-environment `./scripts/check-repository.sh`; changes to published template
infrastructure require release integrity/immutability checks against the merged base.
Run generated-project checks with their actual pinned stack prerequisites, not an
assumed host toolchain. Do not install host packages to make tests pass. A changed check
must be shown to reject its mapped fault, not merely pass the starter.

Report local unit/static, generated-container, CI, managed runtime and independent
client/device results separately. Skip inapplicable layers with a reason; missing
required evidence remains pending. Store source/toolchain identities and sanitized
results, not credentials, private host defaults or whole environment/log dumps.
Draft-document verification is limited to links, traceability, statuses and diff
quality; the commands above describe future implementation gates.

## Rollout, recovery and limitations

Add generated CI gates via new releases; adopt existing applications explicitly. A
failed gate blocks the change. A provider/code rollback cannot undo a schema migration;
recovery is a separate target-specific operation using the verified backup and reviewed
restore procedure.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Implementation decisions

Selected under the project owner’s 2026-10-21 delegation:

Reuse existing managed backup-bound plan/apply/role controls. Add fingerprinted risk review plus real isolated fresh/forward/failure/restore and retained-client trials. Do not introduce automatic managed migration, downgrade or retained-data reset.

Implementation, tests and PR publication are authorized. Merge, deployment and
owner/client/device acceptance remain separate; no overnight answer is required.

## Implementation interfaces

The shared implementation uses [the portable runner](../../scripts/project_quality_core.py),
[exact-release golden tests](../../scripts/quality_templates.py),
[guarded source sealing](../../scripts/seal-quality-releases.py) and
[the quality runbook](../../runbooks/manage-project-quality.md).
The new exact 1.1.0 releases retain provider/lifecycle versions and historical
release bytes. Existing runtime, dependency, database and contract capabilities
are reused rather than duplicated as unrelated initiatives.
