# Development PostgreSQL operations

[SPEC-026](../docs/026-development-databases/spec.md) introduces provider 1.8.0,
project/catalogue schema 4 and group receipt 3. Deployment/live acceptance remain
pending in [the acceptance record](../docs/026-development-databases/acceptance.md).
Do not use these commands through an older provider or assume installation from
source alone. Existing v1–v3 projects and `notes@1.0.0` retain their behavior.

## Create and operate

Select the new release explicitly; production databases and cloud secrets are separate.
Use the installed reviewed runner after authorized rollout. Replace the example
root and project ID with the exact authorized target.

```bash
gptclawctl new example-db --template notes-postgres --template-version 1.0.0 --local-only
gptclawctl validate --project-root /srv/forge/projects/example-db
gptclawctl db init --project-root /srv/forge/projects/example-db
gptclawctl start --project-root /srv/forge/projects/example-db
gptclawctl status --project-root /srv/forge/projects/example-db
gptclawctl db status --project-root /srv/forge/projects/example-db
gptclawctl logs --project-root /srv/forge/projects/example-db --component db --lines 40
gptclawctl stop --project-root /srv/forge/projects/example-db
```

Initialization is explicit and refuses an occupied/unrecognized data root. It creates
one project-owned rootless PostgreSQL 18.6 database from the digest-pinned profile,
local role files and the initial Alembic schema. Start never runs migrations or
reinitializes missing data. Database/API/web startup is ordered and publication
requires schema/readiness. Database ports are not published. Stop retains storage,
backups and credentials and withdraws owned service activation.

Persistent material is outside source at `/srv/forge/projects/.gptclaw-runtime/v1/data/projects/<id>/` on the
existing encrypted project volume. The selected runtime/migration/admin files have
restricted ownership/modes. Do not inspect or print their contents, mount the whole
store, use credential-bearing environment values/URLs or commit them. Processes
sharing forge can access forge's files; these are development disclosure controls,
not hostile-project isolation. EBS snapshots can retain earlier credential copies.

## Backup, migration, reset and restore

Stop the group before these first-slice operations. Native backups are local,
on-demand and bounded; they are not independent host/volume-loss protection.

```bash
gptclawctl db backup --project-root /srv/forge/projects/example-db
gptclawctl db migrate --project-root /srv/forge/projects/example-db
gptclawctl db reset --project-root /srv/forge/projects/example-db
gptclawctl db restore --project-root /srv/forge/projects/example-db --backup-id BACKUP_ID
```

Migration/reset/restore without an operation ID prepares a plan. Review its exact
project, data generation, revision, source fingerprint and selected backup. Apply
only the same action, with that returned operation ID and exact project confirmation:

```bash
gptclawctl db migrate --project-root /srv/forge/projects/example-db --operation-id OPERATION_ID --confirm example-db
```

The apply gate rechecks source/generation/credential epoch; changed plans must be
reviewed again. Existing-data mutations create and restore-check a native backup
within the same locked stopped-writer operation. Reset stages an empty migrated
generation. Restore validates an owned artifact's digest/major/revision, stages a
fresh generation and promotes it only after checks. Both retain the prior generation.
An old-schema restore needs compatible reviewed application source; never reset Git
or assume provider rollback reverses migrations. Unknown/external dumps are unsupported.

`db seed` is an explicit stopped-project synthetic seed and refuses existing notes.
It never runs on start. No real-data imports or production credentials are supported.

## Rotation and recovery

`db rotate` prepares a stopped-project plan; apply with its operation ID/confirmation.
Replacement role files/logins are staged and verified before selection/revocation.
The API receives DML grants; migrations use the schema role and controlled jobs use
admin. Interrupted rotation resumes with that same ID after owned jobs are resolved;
do not create a competing rotation or manually edit role files/initialization variables.

Status preserves unknown/failed operation stages. Never delete a job/receipt or retry
a destructive command blindly. If an owned timed-out job remains, retain it and wait
for its bounded execution outcome; `recover` refuses while that job exists. Once its
outcome can be inspected, explicitly reconcile its exact ID:

```bash
gptclawctl db recover --project-root /srv/forge/projects/example-db --operation-id OPERATION_ID --confirm example-db
```

Recovery preserves data and blocks publication; it does not reexecute a migration.
Then review a restore plan against the retained verified pre-change backup, or resume
the same rotation. Failed initial setup can be reconciled with `db init --operation-id
OPERATION_ID` only for its owned initialization receipt; missing/corrupt ownership or
nonempty uninitialized PGDATA requires operator diagnosis, not blank reinitialization.

## Retention and rollback

Limits: seven completed dumps, 1 GiB dump total, 128 MiB per dump, two inactive data
generations and at least 512 MiB free volume headroom plus the estimated allocation.
The synthetic fixture is capped at 100 notes. These bounds do not impose a general
PGDATA disk quota or provide automatic capacity alerts. Exceeding a gate refuses new
work; it never deletes unknown/shared storage to make room.

`db prune --ids backup:ID,generation:ID` previews exact owned artifacts. Apply with
its returned ID and project confirmation. Active/latest rollback generations, an
operation's protected backup and the sole verified recovery point are excluded.
This is a destructive data operation requiring the selected target's review, not
permission to delete every project or an unrecognized directory.

Before provider rollback, stop/reconcile with the capable provider and preserve
source/data/credentials/backups. Older providers must refuse schema 4/receipt 3.
Restore compatible application/schema through the reviewed native workflow. Major
PostgreSQL upgrades, DLM restore-volume exercises, host replacement, automatic backup
schedules, remote exports and production migration/recovery are separate work.

## Evolved application verification

Provider 1.8.1 copies the selected API, web and project-owned browser checks into
a new disposable fixture, retaining generated component provenance. Removed starter
migrations/tests are removed from that fixture as well. Group `test`/`verify` checks
all application table contents across recreation/reset/restore and a synthetic
forward migration, rather than assuming a `notes` table. Source, managed data and
other projects are not modified by those isolated checks. Explicit managed and
independent-client acceptance remains separate.

Provider 1.8.2 requires `database.storage: runtime-volume-v1` for managed database
operations. Fresh generation sets it; older strict providers refuse that field.
Existing uninitialized v4 source needs a reviewed selector update after checking
that neither a legacy store nor an owned database allocation exists. An existing
legacy `/srv/forge/data/projects` directory requires separate reviewed migration;
never move/copy it automatically or change host permissions to make initialization
pass. The store stays outside repositories on the same verified project volume.

### Rotation object ownership

Provider 1.8.3 transfers application object ownership from validated retained
migration identities to the selected migration login before selecting a new
epoch. This preserves foreign-key and identity writes as well as later migrations.
For a project already rotated by 1.8.2, stop the group and perform another reviewed
rotation with 1.8.3; that operation also repairs earlier migration ownership.
A readiness query or read-only check alone does not establish writable recovery.

Database units mount the bootstrap from an immutable provider snapshot. A source
runner and installed runner can reconcile earlier known checkout/provider mount
paths only when the reviewed bootstrap bytes and all other unit bytes match.
Changed bootstrap content, unknown mount paths, unit edits and overrides remain
conflicts; do not rewrite them to bypass refusal.
