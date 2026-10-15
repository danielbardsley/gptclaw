# SPEC-036 acceptance evidence

Status: Implementation locally verified; final CI/Android/installed/owner acceptance pending.
Owner: Project owner. Evidence date: 2026-10-15 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
[Review PR #83](https://github.com/danielbardsley/gptclaw/pull/83).

The project owner authorized implementation in this chat after the planning PR.
Local checks described below ran against the implementation working tree based on
`65183dd`; the implementation commit is recorded by the PR. This record does not
establish merge, provider installation, physical interaction or M1 completion.

## Criterion mapping

| Criterion | State | Evidence and remaining action |
|---|---|---|
| AC-001 | Pending | Offline strict binding, identity/profile/URL refusal and historical-validator rejection are covered by `test_mobile_backend.py`; installed managed activation remains to be observed. |
| AC-002 | Pending | Both exact starters generate and validate offline. API-only ordered start/stop, ownership/receipt and gateway-refusal regressions pass locally. Generated Python CI uses real disposable PostgreSQL with no web service; installed managed lifecycle/route acceptance is pending. |
| AC-003 | Pending | Real FastAPI OpenAPI is checked against the native contract; generator determinism/breaking-input tests and native strict quality checks pass. Device private HTTPS/docs checks remain pending. |
| AC-004 | Pending | Native mocked interaction and real PostgreSQL CRUD/restart checks pass. Physical Android CRUD, backend/Metro restart, source reload and application relaunch evidence is pending. |
| AC-005 | Pending | Native error/uncertain-write/draft-retention tests pass and platform lifecycle isolation is covered offline. Device outages/reconnect and unrelated-service preservation remain pending. |
| AC-006 | Pending | Native notebook/list/editor and exceptional-state tests pass; normal text colour tokens are selected for contrast and all custom buttons have 48 dp minimum height. Screenshots, owner visual review, physical keyboard/TalkBack/large-text/reduced-motion checks remain pending. |
| AC-007 | Pending | Existing stopped-writer database recovery verification is extended to the API-only shape and a retained compiled native v1 client. Final migration/recovery results are recorded below; installed capable-provider rollback remains pending. |
| AC-008 | Pending | Implementation and generated CI are prepared in PR #83. Remote final-head CI, review/merge, installed provider parity and owner acceptance remain distinct pending gates. |

## Executed local verification

- `python scripts/tests/test_project_groups.py` in the prepared Python 3.12
  manifest environment: all 16 legacy group tests passed.
- `python scripts/tests/test_mobile_backend.py`: initial eight binding/topology/
  lifecycle tests passed. Expanded historical-validator/stop checks are included
  in the final verification below.
- New Python starter, inside existing reviewed rootless image `5c38ecb76795`:
  exact `uv sync --locked --all-groups --no-install-project --no-config
  --no-python-downloads --cache-dir=.gptclaw-cache/uv` passed; `python
  scripts/quality.py format`, `lint`, `typecheck` and `build` passed.
- `python3 templates/apps/releases/fastapi-postgres/1.0.0/checks/verify.py
  --engine podman --reuse-api-image 5c38ecb76795`: passed real disposable
  PostgreSQL setup, locked Python quality/test/security/build and restart
  persistence. Coverage was 282/285 statements and 29/30 branches.
- New native starter inside existing reviewed rootless
  `localhost/gptclaw-node:24.21.0-pnpm12.10.1`: frozen, scripts-disabled install;
  `pnpm format`, `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm security` and
  `pnpm build` passed. Both iOS and Android JavaScript/assets were exported;
  no signed binary or physical-iOS acceptance is claimed. The final interaction
  run passed 9 Jest tests plus 3 generator/security checks, with 82.18% combined
  branch coverage (79.45% notebook; 96.42% API adapter).
- Advisory checks used the existing exact graph and existing bounded source/export
  exceptions; no new exception, severity suppression or runtime scope was added.
- `python scripts/check-template-releases.py --baseline main`: catalogue integrity
  and historical published-release immutability passed.
- `git diff --check`: passed during verification. Final diff/staged/link results
  are recorded with delivery below.

Early native verification exposed a per-test timeout and a branch-coverage gap.
The final suite adds real API adapter/missing-record failure coverage, retains the
80% threshold, uses a bounded 30-second per-test timeout, direct input-change events and wraps explicit native
alert callbacks in `act`. The final interaction rerun passed without React act warnings. A subsequent recovery
review added an uncertainty latch that survives failed refresh and visible saved-record
readback; its regression passes. Initial loading now handles async completion directly
to satisfy React effect lint. Earlier full-repository runs overlapped starter edits and
correctly rejected stale asset hashes; a frozen-inventory final rerun is tracked separately.
An initial isolated migration checker was interrupted to narrow the Node client's
output mount. No retained-client job ran with the broader mount; ownership and
source-volume queries verified no interrupted fixture containers remained. Its
corrected rerun uses a dedicated public-output directory and never mounts DB roles
into Node. Only owned synthetic source/data fixtures are used.

## Database migration/recovery completion

`python scripts/tests/check_database_template.py
/tmp/gptclaw-spec036-db-acceptance-final --engine podman
--source-root /tmp/gptclaw-spec036-runtime-check-source/notes-backend
--api-image 5c38ecb76795 --node-image localhost/gptclaw-node:24.21.0-pnpm12.10.1`
passed the API/DB-only path. This included Python lint/types/tests/security/build,
container recreation persistence, runtime DDL denial, verified backup and staged
restore, credential metadata checks, post-rotation foreign-key/identity writes,
confirmed reset/restore/rotation, failed-reset preservation, corrupt-backup refusal,
data-preserving forward migration and retained native v1 HTTP CRUD before and after
that migration. The fixture used task-owned synthetic state and source; its API/DB
containers and private network were cleaned up by the runner. Source/data remain
under the named temporary fixture for evidence, outside Git.

The expanded `test_mobile_backend.py` suite passed all 11 tests, including actual
historical-validator refusal and API/DB-only stop/source retention. A numerical
normal-text contrast check passed at 5.06:1–12.93:1 across the chosen surfaces;
this does not replace device accessibility or visual review. The documented stable
launcher reports provider 1.12.0 and schemas 1–6. It was inspected read-only and has
not been replaced by this implementation.

## Starter adaptation and remaining operations

The native counter/about screens and counter test were removed. The Python echo/
examples routes, services/models and their unrelated tests were removed; operational
health/readiness, bundled docs, safe request metadata and security tests were retained
and adapted to notes. Notes CRUD and shared synthetic records are deliberate fixture
scope. The actual OpenAPI contract contains only the two notes collection/item paths.
Existing published starter bytes and application data were not changed.

No Terraform change, infrastructure mutation, public endpoint, installed-provider
replacement, real-data import, signing/account action or physical-device test ran.
The new Metro contract retains existing security, operator routing, freshness and
expiry gates. Obtain scoped installed rollout and real Android observations,
including screenshots and owner acceptance, before changing MOB-010 to Delivered
or closing M1. Provider rollback must preserve source/data/roles/backups and use a
capable provider to reconcile new contracts; database schema rollback is separate.

## CI and final verification follow-through

Implementation commit `b5312e8` passed the new combined mobile/Python job, existing
mobile-source, development-database, Python API and multi-service jobs in
[application workflow run 177](https://github.com/danielbardsley/gptclaw/actions/runs/38685254980).
Its legacy template job found two test-fixture issues: discovery still expected
catalogue 5, and the historical-release fixture's Git commit omitted the intentionally
ignored synthetic config asset. The correction expects catalogue 7 and explicitly
commits each declared asset in that isolated baseline. All 21 template tests pass
after the correction; no runtime behavior or published starter bytes changed.
The final native `pnpm verify` passed all gates and both bundle exports after the
uncertain-refresh fix. Relative links across 10 changed planning/runbook/index
documents, release integrity against `main` and diff checks pass.

At this record, the complete frozen-source repository rerun and corrected-head CI
remain in progress. Current PR checks are authoritative for later results; the
rollout/device/owner gates above remain pending regardless of automated results.

The final ownership review adds explicit refusal when the selected backend ID has
a runtime receipt belonging to another canonical root, before rewriting a binding.
The 11-test focused rerun passed, including preserved binding bytes on refusal.
A targeted receipt test also passed for invented components, wrong versions and
fractional/boolean schema values; valid historical receipts remain supported.

Historical-provider rejection now uses a SHA-256-pinned copy of the real v6
validator from `cce6476`, so shallow CI checkouts do not need a local `main`
branch. The targeted historical-validator test passed with the committed fixture.

The full local repository command exposed one existing worktree-test timing race:
its assertion observed a runnable child immediately after SIGKILL delivery. The
production cleanup code was unchanged. The test now waits at most two seconds for
absence or zombie state and still fails for a surviving descendant. The focused
timeout regression and the complete corrected 28-test worktree suite passed. The
original full-run failure is retained as evidence rather than reported as a pass.

## Final local reconciliation

The repository command completed 43 suites / 837 tests: 42 suites passed, with
only the immediate post-SIGKILL assertion failing in the original 28-test worktree
suite. Its complete corrected rerun passed all 28 tests. The original full command
therefore exited 1; this record does not relabel that invocation as a pass. All
other suites completed successfully, including the new binding, legacy project,
Metro, repository, database and dashboard checks.

Two subsequent targeted binding cases passed: recreating ignored generated config
after a fresh clone and preserving existing public-input fingerprint checks. The
controller now creates only its owned public config directory/module using the
reviewed atomic writer. Generated config declares stable public field types,
avoiding accidental URL-literal types after binding. A separate synthetic bound
fixture passed `pnpm typecheck` in the reviewed Node container with networking
disabled; the combined CI helper now repeats that bound-config check. No starter
asset bytes or application API/database behavior changed in these corrections.

Final remote CI remains separately tracked on PR #83. Implementation/source and
local verification are ready for review; installed rollout, private device HTTPS,
Android interaction/screenshots/accessibility, owner acceptance and merge remain
pending. The implementation worktree is clean after publishing the record;
unrelated Fastify work in the original checkout was preserved.
