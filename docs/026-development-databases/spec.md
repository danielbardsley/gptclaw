# SPEC-026: Development database lifecycle

- **Status:** Draft — scope review; implementation not authorized
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Primary feature:** RUN-011, initial per-project PostgreSQL slice
- **Supporting slices:** RUN-006, SEC-001/002/007, QLT-007/009, RUN-012
- **Design:** [TDD-026](technical-design.md) · **Tasks:** [TASKS-026](tasks.md)
- **Dependencies:** [SPEC-025](../025-multi-service-projects/spec.md), [SPEC-024](../024-python-fastapi-template/spec.md), [manifest contract](../project-manifest.md), [backup scope](../002-automated-ebs-snapshots/spec.md), [sequence](../platform/sequence.md)

## Outcome and authorization

Create a private web + FastAPI + PostgreSQL development project whose data survives
API reload, project stop/start and container replacement. The project owner can
inspect database health, apply reviewed migrations, make a consistent logical
backup, restore it safely and reset only an explicitly selected development target.
Prove this using a separately versioned persistent notes starter and synthetic data.

The project owner selected RUN-011 and requested its specification on October 11.
This authorizes planning and a reviewable planning PR, not implementation, runtime
installation, database creation, data reset or deployment. The owner explicitly
selected a **local development credential store**, with AWS Secrets Manager reserved
for the production deployment workflow. That development decision is recorded here;
it is not an unanswered dependency or authorization to provision production secrets.
All other choices below are proposals for scope review.

## Scope and existing readiness

Include one rootless PostgreSQL container per managed group, one application
database, separate runtime/migration/admin credentials, persistent storage outside
Git, readiness-gated lifecycle, explicit migrations, local logical backups and
restore verification, controlled reset, bounded retention and a synthetic seed fixture.
Extend the manifest/catalogue/provider contracts explicitly; use the existing
Next.js/FastAPI adapters, private ingress and project operation lock.

SPEC-025 implementation is on main at `c1afac9` (merge of PR #58). Its acceptance
record still has final delivery/merge closeout pending; this observation does not
rewrite that record. The existing contracts support v1 web, v2 API and v3 ephemeral
web/API groups. They do not provide managed databases, persistent application data
or runtime secrets. Existing EBS snapshots are crash-consistent, accept silent
failures and have no database-consistency or tested-volume-restore guarantee.

Exclude RDS/Aurora, production deployment, AWS/IAM/Terraform changes, shared database
clusters, arbitrary service graphs, standalone database/API-only topologies, caches,
workers, database admin UI, published database ports, public exposure, authentication/
accounts, real-data import, automatic major upgrades, PITR/WAL archiving, replication,
cloud backup storage, scheduled native backups, alerts and the platform dashboard.
This initial slice supports only synthetic development datasets. Other data needs
its own approved handling and recovery scope.

The delivery sequence's broad RES-002/004 recovery gates remain open. This draft
proposes allowing the synthetic RUN-011 slice after its own native-backup/restore
proof, without requiring a new AWS volume/host recovery exercise. Scope approval
must explicitly accept this narrowed prerequisite; it does not complete RES-002,
RES-003 or RES-004, or provide a host-loss recovery promise. SEC-001/002 handling is
implemented here only for development database credentials, not a general secret
manager. Broader seed-data orchestration remains RUN-012.

## Requirements

### DB-001 — Explicit database contract and compatibility

Add a new manifest version for exactly web, API and a managed PostgreSQL dependency.
Declare an exact reviewed database profile, persistent-data mode and supported
migration/seed interface. Store no passwords, arbitrary bind paths, image URLs,
host ports or executable database plugins in the source manifest. Validation and
discovery remain observation-only and reject unsafe paths/topologies/fields before
execution. Existing versions, published releases and runtime/data receipts retain
their meaning. Adoption is explicit; no migration of existing ephemeral projects.

### DB-002 — Project-owned durable storage

Allocate database data, credentials and backups outside Git on the existing
protected project EBS volume. Validate mount, ownership, permissions and distinct
project identity before writes; refuse symlinks, unowned paths, missing expected
storage and conflicting receipts. Stop, restart, failed start, source deletion and
provider rollback never implicitly delete persistent data or credentials. Missing
or corrupt previously initialized storage is an error, never a blank reinitialization.
Record PostgreSQL major/image and data generation; incompatible majors fail before
mounting. Preserve another project's storage and all unknown resources.

### DB-003 — Local development credentials and least privilege

Generate strong unique local credentials without printing them. Keep the store
forge-owned, directories mode 0700 and files 0600; reject unsafe ownership, links
and permissions. Materialize only selected role credentials as read-only runtime
files. The API receives a limited DML role; migrations receive a schema-owner role;
bootstrap/restore receives admin credentials. Do not grant the application
superuser, role creation or database creation. Passwords never enter arguments,
source, environment values, receipts, container/unit inspection metadata, logs,
tracebacks or evidence. Show configured/version state only.

Provide explicit stopped-project credential rotation and recoverable version
receipts; verify new credentials before revoking the old login and report partial
failure honestly. Database role changes, not changed initialization variables,
update an existing database. The shared forge account remains able to access its
local store: this is accidental-disclosure protection, not hostile-project isolation.
Local credentials may be captured by encrypted EBS snapshots; snapshot access and
retention remain part of their protection. Production must use its separately
reviewed external secret manager and identity, never these credentials.

### DB-004 — Ordered private lifecycle and diagnosis

Start the database first, prove authenticated database readiness and expected schema,
then API, then web; publish only a ready group. Stop withdraws routes and stops web,
API, then database with bounded graceful shutdown. One project lock coordinates
lifecycle, migration, backup, restore, reset, seed and rotation. Reconcile interruptions
using persisted operation/resource identities; never retry destructive stages blindly.
The database has no host-port publication and no Serve/Funnel route. Only the API
and selected managed jobs receive backend-network access. Health distinguishes
process liveness, authenticated connectivity and migration mismatch. An outage
makes the group degraded and note operations unavailable; recovery preserves data.
Status/logs remain bounded, secret-safe and honest about retained data and unresolved
operations. Apply finite container/job and connection limits without host resizing.

### DB-005 — Versioned migration gates

Keep migrations in application source and run them explicitly in the reviewed
container using the migration role. Start/reload must not silently migrate an
existing schema. Refuse unknown/ahead/divergent revisions and concurrent operations.
Before an existing database mutation, require a recent consistent backup successfully
restored and checked against that database/schema generation. Show a plan tied to
source/target revision, migration fingerprint, operation ID and backup identity.
Explicit approval is required for applying that plan; a changed plan cannot reuse it.

Do not claim static SQL analysis proves a migration non-destructive: migration code
is arbitrary application code. Apply recovery gates to all existing-database changes.
Failed/interrupted migrations prevent publication until reconciled; no automatic
migration downgrade or claim that a transactional failure covers every DDL pattern.
Initial empty-database setup is separately identified and requires no fictional
pre-existing backup. Verify fresh setup and forward upgrades preserving notes.

### DB-006 — Consistent backups and staged restore

Create a project-scoped logical database backup with compatible pinned tools,
bounded time/size, checksum, database/schema revision and source generation metadata.
Publish it only after success; partial dumps are not recovery points. Never include
role passwords, raw payloads or environment dumps in receipts. Recreate platform
roles/grants from the credential store instead of exporting password-bearing globals.

Restore a selected owned backup into a new isolated data generation and prove schema,
constraints and synthetic CRUD before promotion. Reject corruption, incompatible
versions, wrong ownership/project and unknown backup sources. Promotion requires a
stopped project, compatible application source/schema, matching reviewed plan and
confirmation, and retains the previous
generation for rollback. A failed restore leaves the selected active generation
unchanged. Label local backup, verified local restore and snapshot/host recovery
separately. A same-volume dump does not protect against volume loss; no RPO/RTO or
continuous backup guarantee is made.

### DB-007 — Controlled reset, seeding and bounded retention

Reset only a stopped, explicitly selected project after a verified pre-change
backup and a plan bound to project, operation, active data generation and backup.
Confirmation must name that target and match the plan; there is no broad force,
all-project reset or automatic destructive cleanup. Construct a new empty generation,
apply reviewed migrations and optionally the fixed synthetic seed, verify it and
promote atomically; retain the old generation. Failure preserves recovery options.
Seed only known synthetic records through an explicit operation; never silently
truncate existing notes or seed on ordinary start.

Bound backup growth by declared count/bytes and report storage consumption. Before
creating a dump or new generation, check free space and configured limits; failure
refuses the mutation. Pruning uses a preview of exact owned backup/generation IDs,
excludes active/in-progress/recovery-referenced artifacts and requires confirmation.
Never prune shared runtime storage, unknown directories, credentials, the active
generation or the sole verified recovery point. If safe pruning cannot fit the
budget, stop and report the required decision instead of deleting more data.

### DB-008 — Persistent application example and quality

Publish a new exact persistent notes release; preserve `notes@1.0.0` and existing
defaults. Retain typed CRUD, bounded input/pagination, accessible error/draft states
and safe text handling, with durable notes across API reload, group restart and
container recreation. Use transactions and database constraints so concurrent
creates cannot bypass the 100-note fixture limit. Update the UI/README to explain
shared tailnet access, persistent development data and reset/recovery limitations.
Retain the existing Python standards, strict typing, security gates and critical
statement/branch coverage >=80%. Generated CI must run real PostgreSQL, migrations,
CRUD, restart persistence and backup/restore, not substitute an in-memory database.

### DB-009 — Reviewable rollout and actual acceptance

Deliver versioned platform code/profiles/contracts, a reusable starter, runbooks and
meaningful failure/recovery tests through reviewed PRs after implementation approval.
Record local, CI, managed EC2, independent browser and owner acceptance separately.
Prove two database projects have distinct storage/credentials and unaffected
single-service/ephemeral-group behavior. Preserve retained development fixtures
unless their specific cleanup is authorized. Mark only the accepted initial slice
Delivered after merged implementation and all acceptance criteria pass.

## Acceptance criteria

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| AC-001 | Offline validator/generator tests accept the new topology and reject unsafe/unknown declarations without execution/writes. V1–v3 and old releases remain unchanged; adoption requires an explicit new release/manifest. | DB-001 |
| AC-002 | Managed write/read tests retain synthetic notes through API reload, stop/start and owned container replacement. Missing expected data/mount, bad ownership/link, unknown generation and major mismatch fail without initialization/deletion; a second project retains its data. | DB-002, DB-004 |
| AC-003 | Synthetic credential canaries never appear in source, argv, environment values, unit/container metadata, captured logs/errors or receipts. Selected mounts/permissions pass; application DDL/role/database creation and cross-project authentication fail. Successful rotation rejects old credentials; fault/interruption recovery preserves a usable login. | DB-003 |
| AC-004 | Real rootless lifecycle proves database/API/web ordering, readiness-gated private routing, outage/recovery, graceful stop, resource limits, backend isolation and zero published database ports. Lock conflicts, partial startup and interrupted operations fail/reconcile without touching retained data or unrelated services. | DB-004 |
| AC-005 | Fresh migration and an existing-data forward upgrade pass. Unknown/ahead/divergent revisions, source changes after preview, stale/unverified backup and concurrent mutation refuse. A failed/interrupted migration blocks readiness and a proven restore recovers prior data/schema without an automatic downgrade. | DB-005 |
| AC-006 | A real consistent dump restores into a new generation with matching synthetic records/schema/constraints and working CRUD. Corrupt/truncated/wrong-project/incompatible/unknown backups fail without changing active data; successful stopped promotion and rollback retain/restore the prior generation. | DB-006 |
| AC-007 | Reset/seed tests prove exact target/plan confirmation, required backup, stopped/busy refusal, fresh-generation migration, failed-reset recovery and unrelated-data preservation. Count/byte/free-space gates and previewed pruning refuse protected artifacts and cannot remove the sole verified recovery point. | DB-007 |
| AC-008 | New immutable starter passes locked frontend/Python checks, critical coverage >=80%, real database/browser/golden CI and concurrent capacity/CRUD tests. Independent browser create/edit/refresh/restart observation proves persistence and clear reset/error behavior; existing ephemeral release still loses data as documented. | DB-008 |
| AC-009 | Sanitized evidence records versions/revisions, final-head CI, actual EC2 limits/timings, two-project and legacy regressions, failure recovery, rollback and fixture disposition. Scope approval accepts the local-secret choice and narrowed synthetic recovery gate; implementation merge and owner acceptance are recorded separately. | DB-009 |

## Ownership and review decisions

The project owner owns scope review, named live targets, any destructive-operation
approval and final acceptance. Local database secrets were selected in this chat;
there is no expiry for this standing development-only choice. Review it when data
handling changes or production is designed. Removal means rematerializing credentials
through the replacement store, rotating affected roles and deleting only obsolete
owned local copies after verification; snapshot retention may retain older copies.

Proposed review choices: per-project PostgreSQL container; synthetic data only;
local backups with no host-loss guarantee; explicit migrations and stopped reset/
restore/rotation; new persistent notes release; narrow RUN-012 and SEC/QLT support.
Exact PostgreSQL patch/image digest, Python locks, provider/catalogue versions,
measured budgets and final CLI syntax are implementation-review decisions recorded
before activation. Do not invent pins or advertise proposed commands as installed.
The narrowed stage-7 dependency is a proposal pending scope approval. No acceptance
record exists yet because implementation and behavioral evidence are pending.
