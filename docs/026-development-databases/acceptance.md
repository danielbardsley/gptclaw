# SPEC-026 implementation acceptance

- **Status:** Implementation PR open; CI/managed/client acceptance pending
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-026](spec.md) · **Design:** [TDD-026](technical-design.md) · **Tasks:** [TASKS-026](tasks.md)
- **Implementation review:** [PR #60](https://github.com/danielbardsley/gptclaw/pull/60)
- **Candidate:** provider 1.8.0; project/catalogue schema 4; group receipt 3; `notes-postgres@1.0.0`

The project owner approved implementation and selected local development credentials.
No PR merge, managed provider rollout, existing project/data reset, infrastructure
apply, public exposure or production secret change has been performed.

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
| AC-001 | pending closeout | V4 generation/refusal and V1–V3 compatibility pass focused suites; final local broad gate passed; final-head CI pending. |
| AC-002 | partial | Real isolated container recreation retains notes; missing/major/ownership refusals pass offline tests. Managed EBS mount/lifecycle and two-project observation pending. |
| AC-003 | partial | Role files/metadata exclusion, actual DDL denial and rotation passed isolated checks. Old-login denial passed; interrupted rotation and managed scoped-mount observations pending. |
| AC-004 | pending | Owned ordering/private-network/zero-published-port design implemented; legacy orchestration tests pass. Actual managed Quadlet/route/outage/limits acceptance pending rollout approval. |
| AC-005 | partial | Real initial Alembic setup/declared head and stale-plan tests pass. Actual forward existing-data migration preserves rows; managed failure/recovery closeout pending. |
| AC-006 | partial | Actual native dump/isolated restore and staged promotion pass. Corruption refusal passed; managed/final-head closeout pending. |
| AC-007 | partial | Actual confirmed reset retains prior generation; plan/backup/confirmation refusals pass. Generation pruning and failed-reset retention pass isolated checks; managed target evidence pending. |
| AC-008 | partial | Locked API quality/security/coverage passes actual PostgreSQL. Frontend/browser checks pass; generated CI and independent owner persistence observation pending. |
| AC-009 | pending | Final-head CI, implementation PR/merge, authorized managed rollout, two-project/legacy checks and independent owner acceptance remain separate. |

Task-owned isolated synthetic fixture source/data are retained under task-specific
`/tmp/run011-database-*` directories for review; their owned containers/networks are
removed by bounded cleanup. These are not managed retained project datasets. Earlier
failed attempts and their owned metadata are preserved for diagnosis; no global prune
or deletion of unrelated data occurred. Local logical recovery does not establish
volume/host-loss recovery, RPO/RTO or production readiness; RES gates remain open.

## Publication status

The project owner approved public-repository publication and merge into main.
The redacted branch is published and [PR #60](https://github.com/danielbardsley/gptclaw/pull/60)
is open. All three configured workflows started; merge waits for successful final-head
checks. Managed rollout and independent client acceptance remain separate gates.

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
