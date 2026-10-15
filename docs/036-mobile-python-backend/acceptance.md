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

## Expo Go preview preparation — October 15, 2026

The project owner requested an Expo Go preview and reported the same Android 11 /
Expo Go 57.0.9 versions, with the phone connected to Tailscale. This is a supplied
client report, not a physical launch result. All four final implementation CI
workflows passed at a2e362276e52394f101aaeb8394e203f5c49c4b1.

Main subsequently merged SPEC-035 in PR #82. Merge f064cac preserves both optional
Fastify schema 7/catalogue 6 and Python/mobile schemas 8/9/catalogue 7, including
provider capabilities, dispatch, snapshots and both generated CI jobs. The updated
manifest unsupported-version test passes (28 tests). Combined-head CI and ongoing
local regression results remain pending at this checkpoint.

Installed provider remains 1.12.0. Read-only new-project plans for `fieldnotes-api`
and `fieldnotes-mobile` refused with `credential-workflow-policy`: neither name
is on the existing four-repository workflow-publication policy. No credentials,
policy, projects, installed provider or services were changed. An exact
[preview plan](preview-plan.md) retains those names/grants and proposes the two
private targets. The next unused sticky Metro slot requires private HTTP 8445 to
loopback 18605 through the existing operator path; old slots remain reserved. This
is a proposed routing amendment to the original design's listener-reuse assumption.
Named policy/publication and the exact additional listener await owner approval.
No current Go link or device acceptance is claimed.


## Explicit preview approval and policy compatibility correction

The project owner explicitly approved adding only `fieldnotes-api` and
`fieldnotes-mobile`, creating both private repositories and the private 8445 route.
The initial update refused `credential-policy` before changing the four-name
profile, because schema 4 has a four-name ceiling. The same existing profile was
reactivated successfully through the managed CLI. No grants were expanded.
A versioned schema-5 six-name correction and regression coverage are being
verified before another policy transition. Previous two/four-name schemas remain
strict and ordinary Git/PR tokens retain their existing scopes.

After merging current main, all 12 focused mobile/backend tests passed in
187.533 seconds. The corrected 28-test manifest suite passed. Combined-head
private-application and dashboard CI passed at 9429b13; Terraform checks were still
pending/running when observed. The earlier broad local command encountered the
now-corrected unsupported-version test and is not recorded as a passing invocation.


## Private preview rollout checkpoint — October 15

The owner-approved schema-5 six-name workflow policy was applied with all four
prior names and existing grants retained. Registered owned helpers were refreshed
through the managed updater. Scoped first publication of `fieldnotes-api` completed
at operation `67550ad087814c529f0c8216ceb6b008`, repository 1420817009,
[initial PR](https://github.com/danielbardsley/fieldnotes-api/pull/1), source
0e28453355cdf8e7434f74f90b43020321e6a93c. The profile was reactivated; ordinary
creation of `fieldnotes-mobile` completed at operation
`dd2995f203aa468d80d0e8f666319da4`, repository 1420819339,
[initial PR](https://github.com/danielbardsley/fieldnotes-mobile/pull/1), source
b0b0d4079c5e6d9c2efe928c27a9a5107e0b0f8a.
Both generated CI workflows passed: backend run 38747345148 and mobile run
38747570563. No main-branch merge is implied.

The six-name publication test found that initial publication attempted to stage
the ignored public backend-config placeholder. Source correction 99cac1c omits
that exact local input from repository publication; binding/checks recreate it.
The corrected end-to-end isolated test passed (1 test, 46.769 s), including old
profile-bound refusal, foreign-target refusal, no public-config publication and
scoped/revoked workflow tokens. The earlier full credential invocation loaded the
pre-correction implementation and completed 59 tests with that one known error;
its remaining 58 tests passed. Do not describe that invocation as passing.
Actual new-repository publication also passed with the correction.

New-database initialization allocated generation dadb615759694425b662f50dc2d7bcde
and operation 550a40946b8242d4afca64e3ab11d564. Its first attempt stopped during API
dependency preparation and retained the allocated data/roles; the original command
error has no established finer cause. Scoped dependency installation completed
without source/lock changes at 282dea0d9be44f5d9002c4d11c1ddfba. Resuming the same
init operation succeeded. Group start 4e8760a2b7e649308df249835fb6bb65 is passed/Ready
with API and DB ready, no web component, and the existing private HTTPS route
configured. Actual HTTPS ready and notes-list probes returned 200 (zero initial
records). Data/source/roles are retained; no existing dataset was reset.

The installed stable provider is now 1.14.0 at immutable digest
87b27973e04c7612f9a9ab37f718e919f7c1268f04463a5b84fa844af3b73059. Source and
installed --version capability JSON match exactly, including manifest schemas
1–9 and credential profiles 1–5. Binding/inspect ran through the installed CLI
and selected the canonical Python backend with development contract v1.
Mobile frozen dependencies completed at 4fdc47d0cce948c59d0dce0586a5cd77 with
unchanged dependency hashes. Initial Metro preflight refused before session
submission when those dependencies were missing; after preparation the single
submitted generation 9ceeacbc17b7473d9869515e02d8ffb6 reached process Up and protocol
Ready. Expiry is October 15 at 12:09 p.m. Eastern.

The exact route plan c094b8cfeb550652a309818271bd543b5a75c7621fb9ed8db0a18e21ffaa4d85
was recorded through the installed CLI against baseline
d0c41e928966c5d085e704d5826120b76ae4b4af854eb0aa570e447d52db5539. It selects
only private HTTP 8445 to loopback 18605. The existing SSM operator was given the
exact reviewed add command. Forge performed no Tailscale mutation. At this
checkpoint the route remains operator-required, transport unavailable and no Go
launch link is available; physical Android, screenshots, owner acceptance and full
T9 acceptance remain pending. All 443 HTTPS handlers and Funnel-off must be
independently checked after operator execution.


## Preview verification before operator handoff

The broad repository command finished with 44 suites / 845 tests and exit 1.
Forty-three suites passed; the only failing suite was the initial manifest test
that still treated schema 8 as unsupported. Its corrected full 28-test rerun
passed separately. The later full 59-test credential suite passed against the
corrected publication/profile implementation; the known earlier invocation's
error is retained above. No other broad-suite failures remain recorded.

A first bounded Android loopback bundle probe returned a non-200 response; its
finer cause was not retained. A subsequent bounded check returned 200, followed
by a successful complete Android manifest/bundle probe through the owned proxy:
6,464,006 bundle bytes, SHA-256
68aec52e5b6ea06ab6e4f55363c7446c228805e9fd68099076c541cf745fcc10.
No manifest or bundle contents were retained. Current process/protocol remain Up/
Ready; private transport remains route-pending. These are host checks, not phone
launch or owner acceptance.

Actual private HTTPS API create/read/update/delete passed using one uniquely
identified synthetic check record. Only that record was deleted afterward. No
other notes/data were reset or removed. The complete previous Serve baseline is
unchanged, Funnel remains off and approved HTTP 8445 is still absent at the latest
readback. The exact add command has been requested from the existing SSM operator.


## Operator route verified and Expo Go launch available

After the project owner reported the SSM command complete, independent Serve
readback verified only the approved HTTP 8445 -> loopback 18605 addition. Removing
that exact owned entry from the observed config reproduces the complete retained
baseline; all prior HTTPS handlers are preserved and Funnel remains off.
Installed status reports Ready with process Up, protocol Ready and private route
Verified for generation 9ceeacbc17b7473d9869515e02d8ffb6. Installed `go launch`
reports compatible/launch available for the owner-reported Android 11 / Go 57.0.9
profile, using the generation-bound URI and unchanged 12:09 p.m. Eastern expiry.
The private URI is returned only to the owner, not committed to source.
Actual physical launch, native CRUD, visual/accessibility review, review/merge and
the remaining T9 scenarios are still pending. Earlier route-pending checkpoints
above are historical.


## Owner-confirmed Android Expo Go preview — October 15

After receiving the locally generated QR for the verified current Fieldnotes
generation, the project owner reported: “That works perfectly.” Record this as
owner-reported successful Android Expo Go preview and positive overall feedback
on the accepted Android 11 / Go 57.0.9 device profile. The earlier physical-launch
pending checkpoint is superseded for this basic preview. This is owner evidence,
not a host-observed phone session or a screenshot.

The report does not enumerate individual CRUD, restart/persistence, failure/
recovery, keyboard, TalkBack, large-text or reduced-motion scenarios. Those T9
items, screenshots, implementation review/merge and final criterion-by-criterion
acceptance remain open. Do not infer full AC-004–008 acceptance or mark MOB-010/M1
Delivered solely from this general preview confirmation. No runtime was stopped,
renewed or otherwise changed to record this report.
