# SPEC-026 implementation acceptance

- **Status:** Implementation merged; managed/client acceptance pending
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-026](spec.md) · **Design:** [TDD-026](technical-design.md) · **Tasks:** [TASKS-026](tasks.md)
- **Merged implementation:** [PR #60](https://github.com/danielbardsley/gptclaw/pull/60)
- **Candidate:** provider 1.8.0; project/catalogue schema 4; group receipt 3; `notes-postgres@1.0.0`

The project owner approved implementation and selected local development credentials.
PR #60 merged at `f4ad780` after final-code CI passed. No managed provider rollout,
existing project/data reset, infrastructure apply, public exposure or production
secret change has been performed.

## Evidence recorded so far

- Existing focused multi-service suite: 16 tests passed after schema/lifecycle
  integration. Persistent offline ownership/plan suite: 10 tests passed. Catalogue/
  generation/immutability suite: 21 tests passed after excluding transient authoring
  caches from source-only fixtures and adding the new profile to provider fixtures.
- Exact official Linux-amd64 PostgreSQL image reports 18.6. Its digest is committed
  in `config/databases/v1.json`; matching clients are inside that image. Locked
  SQLAlchemy 2.1.4, Psycopg/Psycopg-binary 3.3.6 and Alembic 1.20.0 are in the new
  release, preserving published `notes@1.0.0` and existing defaults.
- `check_database_template.py` using rootless Podman and the existing exact Python
  authoring container passed API lint, strict types, real PostgreSQL tests/critical
  coverage gate, security/advisory checks and build. Actual container recreation
  retained synthetic rows; application DDL was denied. A custom-format dump restored
  to an isolated generation, with credentials absent from inspection/backup metadata.
- An extended isolated run passed confirmed reset, staged restore promotion and
  credential rotation. Old-login denial, generation pruning, failed-reset preservation, corrupt backup
  refusal and an explicit data-preserving forward migration also passed. The complete
  frontend/browser/OpenAPI workflow passed after resolving pending route callbacks
  before browser teardown. Interrupted-rotation/managed observations remain pending.
- The first broader repository run failed because template fixture copies included
  a container-owned untracked `.venv` with container-only interpreter symlinks.
  Source-only fixture copying and release-cache exclusions were corrected. The
  relevant 21-test suite then passed. This record does not claim that initial broad
  run passed; the final complete rerun passed 447 unittest cases and all shell/invariant/release
  gates. A negative manifest-version test was updated from 4 to 5 after adding v4.
  Source authoring was finalized before the successful full run; an earlier mid-edit
  run correctly rejected temporarily mismatching new release hashes.

- Final locked API coverage: 328/331 statements (99.09%) and 31/32 branches (96.88%).
  Both exact-container frontend gates and the real browser's CRUD/refresh/plain-text/
  failed-draft/keyboard/responsive checks passed. Browser teardown now waits for
  pending routing callbacks; it does not suppress application assertion failures.
- Output-size enforcement initially restricted Podman's metadata files and prevented
  readiness; it was replaced by bounded streaming. The later native rerun verifies
  generic public-schema content digests and schema-role-owned restore, avoiding a
  notes-only ownership assumption. Scoped Quadlet mode/override refusal passes offline;
  actual managed EBS/Quadlet observations are not claimed from disposable containers.

## Criteria

| Criterion | State | Evidence and remaining work |
|---|---|---|
| AC-001 | pending closeout | V4 generation/refusal and V1–V3 compatibility pass focused suites; final local broad gate passed; final-code CI passed at `9227990`; managed/client gates remain. |
| AC-002 | partial | Real isolated container recreation retains notes; missing/major/ownership refusals pass offline tests. Managed EBS mount/lifecycle and two-project observation pending. |
| AC-003 | partial | Role files/metadata exclusion, actual DDL denial and rotation passed isolated checks. Old-login denial passed; interrupted rotation and managed scoped-mount observations pending. |
| AC-004 | pending | Owned ordering/private-network/zero-published-port design implemented; legacy orchestration tests pass. Actual managed Quadlet/route/outage/limits acceptance pending rollout approval. |
| AC-005 | partial | Real initial Alembic setup/declared head and stale-plan tests pass. Actual forward existing-data migration preserves rows; managed failure/recovery closeout pending. |
| AC-006 | partial | Actual native dump/isolated restore and staged promotion pass. Corruption refusal passed; final-code CI passed; managed closeout pending. |
| AC-007 | partial | Actual confirmed reset retains prior generation; plan/backup/confirmation refusals pass. Generation pruning and failed-reset retention pass isolated checks; managed target evidence pending. |
| AC-008 | partial | Locked API quality/security/coverage passes actual PostgreSQL. Frontend/browser checks pass; generated Docker/browser CI passed; independent owner persistence observation pending. |
| AC-009 | pending | Final-code CI and implementation merge are complete. Authorized managed rollout, two-project/legacy checks and independent owner acceptance remain pending. |

Task-owned isolated synthetic fixture source/data are retained under task-specific
`/tmp/run011-database-*` directories for review; their owned containers/networks are
removed by bounded cleanup. These are not managed retained project datasets. Earlier
failed attempts and their owned metadata are preserved for diagnosis; no global prune
or deletion of unrelated data occurred. Local logical recovery does not establish
volume/host-loss recovery, RPO/RTO or production readiness; RES gates remain open.

## Publication status

The project owner approved public-repository publication and merge into main.
The redacted branch is published and [PR #60](https://github.com/danielbardsley/gptclaw/pull/60)
merged after all three final-code workflows passed. Managed rollout and independent
client acceptance remain separate gates.

## Confidentiality review

The proposed files and both unpublished commits were reviewed for credential/key
formats, credential-bearing URLs, private addresses, cloud-resource identifiers,
personal contact details and generated credential/state/dump files. No confidential
values were found. Private conversation quotations and internal approval-review
commentary were removed from the proposed public documentation. Runtime credentials,
dumps, authentication material and temporary environments remain outside Git.
Generic example paths, public artifact digests and required security/recovery
contracts are retained. This review covers the new changes, not a full historical
repository audit.

## PR validation follow-up

Both Terraform validation workflows passed at `43a978c`; the application workflow
failed in the new Docker database job's initial image build. The portable checker
now uses a task-owned empty Docker config instead of an unavailable forge home.
Final-head CI is required after this correction; no merge bypass is authorized.

Inspection of the pinned image initializer confirmed that its file-password helper
briefly exported a raw password during initial setup. The managed adapter now uses
a trusted read-only bootstrap script, `initdb --pwfile` and libpq passfiles; it
refuses raw password environment inputs. The native checker tests the actual server
process environment using a Boolean probe, without printing values. The change
also preserves schema/private SCRAM authentication and owned exited-fixture cleanup.

## Final CI and merge

Final code `9227990` passed all configured PR workflows:

- [Private application workflow #78](https://github.com/danielbardsley/gptclaw/actions/runs/38195739847): existing web/API/multi-service regressions plus real Docker PostgreSQL/native recovery and persistent frontend/browser checks.
- [Development host #185](https://github.com/danielbardsley/gptclaw/actions/runs/38195739858): repository quality, Terraform format/validation/mock tests.
- [Tailscale federation #89](https://github.com/danielbardsley/gptclaw/actions/runs/38195739849): configured repository/Terraform checks.

PR #60 merged as `f4ad780cbe75ad361bfc3e145bba75be043951af`. The post-merge
record update is documentation only. Catalogue status is Implemented, not Delivered:
T-012's managed EBS/Quadlet/private-route, two-project/legacy, fault/recovery and
independent owner browser acceptance remain unexecuted. Source merge does not install
the provider or complete any deferred RES/production feature.

## October 12 full platform acceptance in progress

The project owner directly confirmed two named, separate synthetic applications,
their private repositories, publication/merge, reviewed provider rollout and
persistence/reset/restore/rotation/browser tests. Local prepared projects have
application-specific planning, copied guidance/specification skills and distinct
web/API/relational database source. This preparation does not establish final
managed project creation, deployment, remote CI or client acceptance.

The first broker operation created its private repository and bootstrap main but
retains `recovery-required` at starter tree publication. A same-credential control
tree omitted only the workflow entry and succeeded, without publishing a commit
or branch. The accepted broker excludes Workflows permission; the
[concrete policy proposal](repository-workflow-publication.md) was explicitly approved by the project owner. Its owner-controlled App and
installation grant update remains pending; no live profile has been migrated.

A verification defect was found: evolved source was overlaid on starter migrations
and tests, and checks assumed a `notes` table. The 1.8.1 follow-up replaces only
disposable fixture source, selects application-owned browser checks, compares all
application records and performs a schema-independent synthetic forward migration.
A regression test proves removed starter files stay absent and provenance survives.
On both prepared applications, all locked API gates and real rootless
PostgreSQL recreation, DDL denial, native backup/verified restore, reset/restore,
rotation/old-login denial, failure preservation, corruption refusal and forward
migration passed. The reading-list frontend and real browser CRUD/refresh/progress/rating/filter/
failed-draft/keyboard/mobile journey passed. Task-tracker browser checks are in
progress; an ambiguous select label was corrected after its first real-browser
failure. A modal focus issue after a failed save was also corrected and rechecked.
T-012 remains pending; no Delivered or production-readiness claim is made.

## Rotation ownership correction (managed acceptance finding)

The authorized relational project remained ready and readable after 1.8.2 rotation,
but a new child-record insert failed: the foreign-key check executed as a previous
migration table owner whose schema access had been removed. This is a failed
writable-recovery check; the earlier read/persistence results alone did not close
rotation acceptance. Provider 1.8.3 reassigns application objects from retained,
validated project migration roles before selecting the new epoch.

Actual focused ownership tests pass (16 cases). A real rootless PostgreSQL workflow
passes locked API lint/type/tests/security/build, restart persistence, native
backup/reset/restore/rotation, old-login denial, corruption refusal and forward
migration. Its added post-rotation runtime identity/foreign-key insert and migration
DDL checks pass. These are disposable native tests; final-head CI, reviewed rollout
and both managed private browser rechecks remain separate pending evidence.

The installed runner also refused a source-started database stop because the
bootstrap mount referred to the working checkout. The group stopped its web/API
components and preserved the running database. The correction pins future mounts
to immutable snapshots and reconciles only known paths with matching trusted bytes
and otherwise exact units. Focused unknown-path/script/unit-edit refusal and final
CI/managed reconciliation are tracked separately from the ownership regression.

## Reviewed final provider and actual reconciliation

[PR #64](https://github.com/danielbardsley/gptclaw/pull/64) merged as `374a854`;
final code `5ae3348` passed every configured quality job:
[development host](https://github.com/danielbardsley/gptclaw/actions/runs/38283050283),
[federation](https://github.com/danielbardsley/gptclaw/actions/runs/38283050103), and
[private application](https://github.com/danielbardsley/gptclaw/actions/runs/38283050372).
Infrastructure plan/apply jobs were skipped by their existing triggers; no
infrastructure mutation was performed. Local final verification passed 463 unittest
cases, 18 focused database cases and real rootless PostgreSQL/native recovery.
Earlier candidates and the fixture owner/group permission correction are not
represented as final-head passes.

The installed immutable provider reports 1.8.3. It reconciled the exact known
source-bootstrap unit, stopped the retained database through the lifecycle interface
and restarted the private group with an immutable bootstrap mount. No unknown unit,
override, host ownership, permission or AWS resource was changed. The two distinct
applications previously passed locked private repository CI and native scoped Git
publication; negative cross-repository helper access and disable/enable recovery
also passed with the peer unaffected. Final managed fault/browser/hooks and
application merges are tracked below when observed.

## Managed migration and refusal evidence

The reviewed installed provider applied an existing-data forward migration while
retaining the complete API record/summary snapshot. An edit after preview refused
the stale source plan. A deliberate synthetic migration failure marked recovery
required and blocked group readiness; a reviewed source-compatible native restore
into a fresh generation recovered the exact prior records/schema. The peer
application stayed ready throughout. Only the owned temporary probe revisions were
retired; their source is retained privately for rollback review.

Managed running-operation and lock-conflict refusal, wrong-target reset refusal,
corrupt-backup refusal, active-generation prune refusal and all-verified-backup prune
refusal passed without changing selected data. The temporarily altered owned
synthetic dump was immediately restored and its original checksum reverified.
Explicit pruning removed only unprotected, superseded owned generations.

Five disposable pre-execution checks separately exercised backup count, backup
bytes, backup free-space, inactive-generation count and generation free-space
refusal. They invoked no database commands and wrote no data. The live volume was
not filled to simulate these limits. Actual host metadata measured 7,816 MiB total
memory, 3,690 MiB available and 66,340 MiB free on the project volume at that sample.
Each database had 1,024 MiB/1 CPU/128 PID ceilings and no published port; each web/API
container had 1,536 MiB/1 CPU/256 PID ceilings. Limits are ceilings, not reservations.
Native backup took about 9–12 seconds, reset about 19, restore about 10–17, rotation
about 8 and warm group starts about 18–27 on these small synthetic datasets.
No production performance or RPO/RTO claim follows from these measurements.

## Independent client and interruption acceptance

The project owner explicitly confirmed that synthetic create/edit changes in both
private applications survive a reload from their own browser. Both complete
application source PRs are merged after their actual private CI passed.
Both managed API source-reload checks passed with exact source restored. Actual
private Chromium CRUD/refresh/filter/draft/safe-text/keyboard/mobile workflows
passed after the ownership correction. Final role/network/mount inspection and
runtime DDL/cross-project login denial passed on the current epochs.

Both projects passed a controlled rotation interruption: only the task-owned CLI
was terminated after new-login verification. Readiness remained blocked; recovery
marked the recorded operation recovery-required and explicit resumption completed
that same operation, preserving the fresh complete API snapshot. The harness was
corrected to expect recovery-required as a nonzero status; earlier harness exits
are not represented as completed checks. Retired login denial passed separately.

The real installed commit hook subsequently found a source-copy integration
defect with generated Next.js output. Both live applications remain ready and
owner data is retained. [PR #65](https://github.com/danielbardsley/gptclaw/pull/65)
tracks the narrow output exclusion and its regression; full hook/evidence closeout
remains pending. No owner/browser or data-reset authorization is requested again.

## Installed-hook source-copy finding

Both complete private applications passed source CI and managed/client CRUD, but
the installed parent commit hook failed before database allocation: generated
Next.js development output was copied as source and rejected for its path names.
Provider 1.8.4 excludes `.next` and Python check caches, preserving application
source, generated provenance and selected browser checks. A disposable regression
uses the actual generated-name pattern plus an output symlink, proving that those
outputs are neither inspected nor copied and the original files remain.
Final-head gates, reviewed rollout and actual commit-hook reruns remain separate.
