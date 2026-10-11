# SPEC-023 acceptance evidence

- **Status:** All repositories verified live; signing-key rotation, final-head CI and merge pending
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-023](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- **PR:** [#54](https://github.com/danielbardsley/gptclaw/pull/54)
- **Implementation:** provider 1.5.0 on `codex/prj-005-spec`; tested candidate worktree based on `cb6c8df`, committed revision linked by the PR

## Authorization and boundary

The project owner instructed “Ok, now implement the spec”, authorizing the bounded
implementation and selected standing private/PR policy. One-time App settings,
selected bootstrap repository/key handling and retained live target authorization
were requested separately using the concrete [setup runbook](../../runbooks/manage-repository-credentials.md)
and [settings checklist](../../config/repository-credentials/github-app-settings.json).
The project owner subsequently completed the proposed App registration,
selected installation and private-key transfer, supplying App ID `5274762`,
installation ID `170289816` and the proposed external key path. The owner also
explicitly approved retained private targets `gptclaw-prj005-one` and
`gptclaw-prj005-two`, their local projects/private runtimes and activation after
the first successful canary. No real App/private key/token/profile or remote
repository was used during the earlier offline implementation tests. Previous
revoked PATs were not read/reused.

App personal creation succeeded, but automatic access under the selected
installation failed the live canary. The candidate requires a successful canary before profile
activation and does not implicitly broaden permissions or introduce a PAT
fallback. The later explicitly approved All repositories mode is now active and
operationally verified, while merge/full acceptance remain pending.

## Criteria

| Criterion | State | Actual local/live evidence | Remaining evidence/owner action |
|---|---|---|---|
| AC-001 | passed | Explicit All repositories approval/migration; actual App/installation identity, exact four grants, key metadata and ready doctor/status verified. | No further setup action; root account-wide authority remains documented. |
| AC-002 | passed | Retained canary recovered and successive configured normal new completed with initial PRs/bindings; no per-project token, deploy key or selection click. Earlier failures retained below. | Evidence is recovery plus one fresh creation under final policy, not two fresh All-mode creates. |
| AC-003 | passed | Exact singleton grant/ID/Selected token response; actual other-private-repo HTTP 404; platform has no token write authority; both helpers reject foreign paths. | Platform public metadata remains readable; no false private-read denial claim. |
| AC-004 | passed | Offline secret/path/argv/bundle/container checks and real bounded metadata/receipts; key stays outside source/containers, tokens are not logged/persisted. | Issued Git leases retain bounded reported expiry as documented. |
| AC-005 | pending | Fresh reacquisition, API token revocation, disable/enable and retained recovery passed live; different-key rotation/expiry/race/response-loss checks passed offline. | Actual owner signing-key rotation/retirement remains. |
| AC-006 | passed | Activated normal new completed; explicit local-only preview has no GitHub effects; compatibility/regression tests and independent runtime checks passed. | No automatic initial-PR merge or production promotion. |
| AC-007 | passed | Native fetch/worktree branch push and later scoped PRs passed in both projects; refresh/disable/enable preserved dirty source hashes. | Four retained fixture PRs await ordinary owner review. |
| AC-008 | pending | Both projects passed manifest/provenance/build/test/typecheck/private page/health; owner confirmed both desktop URLs; independent app remained ready. | Exact final-head CI/implementation merge pending. |

Offline fixtures prove implementation contracts, RSA signing and native Git wire
behaviour, not GitHub App endpoint/account feasibility or full acceptance.

## Executed checks

- `.venv-manifest/bin/python scripts/tests/test_repository_credentials.py`: final
  39 tests passed in 60.619 seconds; the prior 38 tests passed in 58.990 seconds, including real RSA signature verification,
  two-project real Git history/objects, selected-scope negative cases, controlled
  Git helper handoff, private authenticated TLS fetch/push, response-loss/lock
  recovery and rotation using a different signing key. Earlier 24/32/33/34/35/37
  test runs also passed after cases were added.
- Initial synthetic integration run failed because its fake create response ID
  differed from its persisted fake repository ID; the fixture was corrected,
  preserving the production scope rejection. A separate fixture initially did
  not model closed-token rejection; it was corrected and production closed-token
  transport is explicitly guarded. Test-owned TLS sockets are explicitly closed.
- `.venv-manifest/bin/python scripts/tests/test_project_templates.py`: 21 passed,
  including immutable release, source/installed provider and legacy checks.
- `.venv-manifest/bin/python scripts/tests/test_project_repositories.py`: 41 tests passed on the final regression run (28.543 seconds).
- `git diff --check`, shell syntax for the helper/repository checker and Python
  compilation passed during implementation. Changed-document link checks passed. Full repository checker passed with exit
  0, including 41 provisioning tests and the then-current 38 broker tests. The
  final focused run covers the added failed-revocation cleanup regression.

The native transport fixture binds only task-owned loopback sockets and uses its
own temporary TLS trust for that Git command, not a global security change. GitHub
traffic is intercepted by the private fixture proxy; no internet/App credential
is used. Generated signing keys/certificates stay in task-owned temporary paths,
are never logged/committed and are cleaned with those fixtures. API fixtures use
synthetic identities/tokens. No Node process, unrelated runtime, infrastructure,
production or public callback was changed.

The existing `/usr/bin/openssl` was observed as OpenSSL 3.0.13; signing uses its
RS256 implementation via a private fd. No host package or new Python dependency
was installed. Actual GitHub token expiries/scopes will come from its responses,
not fixed token prefixes/lengths or user-entered PAT lifetimes.

## Remaining work and handover

Implementation authorization is complete. External setup/live targets are a
separate owner step and have not been inferred from the code request. The primary
path is selected-repository App installation with creation-only authority plus
single-repository project credentials. If real account/API support fails, retain
resources and present a reviewed scope alternative; do not silently request
Administration, all repositories, OAuth/user refresh material or PATs.

The real All repositories profile is active with provider
1.5.0 for setup, prove the canary, then activate once. Normal future projects
should need no manual token creation; App grant/key revocation or maintenance
can still require an owner action. Ordinary Git helper tokens expire at reported
times because they must remain valid after helper exit; API leases are best-effort
revoked immediately. Deactivation/disable does not claim server-side revocation.

Merge, final-head CI and actual signing-key rotation remain pending; current All
mode and desktop acceptance have passed as recorded below.
The previous SPEC-022 slice remains Delivered, with its retained source/app/PR
and explicit reported token revocation unchanged.

## Implementation CI verification

Exact code revision `30bf742497ee116db6bf59bb5efd9626ae5df5d1` passed all three
configured workflows:

- [Private application workflow](https://github.com/danielbardsley/gptclaw/actions/runs/38092377986): 39 broker tests, existing suites, template integrity, generated app build, dependency operations and toolchain preparation passed.
- [Development-host quality](https://github.com/danielbardsley/gptclaw/actions/runs/38092377978): success.
- [Tailscale federation quality](https://github.com/danielbardsley/gptclaw/actions/runs/38092377976): success.

No protected infrastructure deployment was performed. These prove code quality
for this revision; they do not establish the separately pending live App/account
feasibility or owner acceptance. This follow-up records documentation only.
The final worktree was clean after implementation push; no private material was
staged. Only task-owned fixtures were removed by tests.

## Live owner setup and retained canary — October 11

Tested source revision `ee2ee2dc765984d8a1582f3eed95bfff6522a6e1`, provider
1.5.0. `stat` observed forge-owned directory mode 0700 and regular key mode
0600, link count 1, at the external runbook path. Key contents were not displayed.

Executed `credentials configure` with the supplied IDs/path and bootstrap
repository ID `1413668232`, then `credentials doctor`. Both returned
`canary-required`, `active:false`, selected installation containing only that
bootstrap repository, and exactly Repository creation/Contents/Pull requests
write plus Metadata read. This is actual signed App/API readback.

After explicit target/activation approval, executed `credentials canary
--repository gptclaw-prj005-one --directory
/srv/forge/projects/gptclaw-prj005-one`. GitHub created the private repository
[gptclaw-prj005-one](https://github.com/danielbardsley/gptclaw-prj005-one),
immutable ID `1414446320`, operation `148056feb07746a5be813c8e0f2dfac5`.
The command exited 1, retaining a `recovery-required` receipt with
`last_error:credential-recovery`. No local bootstrap/publication or initial PR
completed, and the destination was not published.

Read-only App JWT `GET /repos/.../installation` returned missing, and fresh
audit-token inventory still listed only `1413668232`. A token request explicitly
restricted to `1414446320` was denied (`repository-api`); no token with broader
scope was substituted. Later bounded read-only observations again found no
inclusion. Doctor now returns `credential-scope` because the registered canary
is absent from the installation. Automatic access is not proved by the successful
create response or by GitHub's documented behavior alone.

The repository/journal/binding were retained. Activation, second creation,
Git/PR/runtime/rotation checks and new desktop acceptance were skipped because
the first canary cannot access its own repository. No manual installation change,
all-repositories selection, Administration grant, PAT reuse or infrastructure
mutation was performed. Recover only the same operation after reviewing a
supported automatic-inclusion path; do not replay its create request or count
manual selection as AC-002 passing.

## Explicit enrollment amendment — October 11

The project owner followed the proposed additional permission change, then found
and approved GitHub's permission-update email. Signed App and installation
readback now both report exactly Contents write, Pull requests write, Repository
creation write, `installation_repositories:write` and Metadata read, with
`repository_selection:selected`. Initially only the App reported the new grant;
the broker did not attempt enrollment until installation approval was verified.

Candidate provider 1.5.1 adds a separate enrollment role, journal/binding/App
validation, durable intent, bounded membership readback and recovery. Project
Git/PR tokens retain their previous exact grants and exclude installation access.
The focused suite passed 43 tests in 60.201 seconds, including two explicit
enrollments, denied enrollment, mismatched binding, missing updated grant and
lost-response reconciliation without repeating create or a completed PUT.
The initial expanded run exposed enrollment metadata being overwritten by the
provisioning receipt; preserving that metadata corrected the regression.
The full repository checker also passed with exit 0, including 43 broker tests
in 64.232 seconds, 41 provisioning tests and 21 template tests. Changed Markdown
links and `git diff --check` passed. These are candidate source/local checks;
final-head CI for the enrollment amendment is not yet claimed.

Executed `credentials resume --operation-id
148056feb07746a5be813c8e0f2dfac5` using the tested candidate after permission
approval. GitHub issued an enrollment token with exactly installation repository
access write and Metadata read, reported expiry 12:15:02 p.m. America/New_York,
then rejected/could not verify the membership PUT. The resume exited 1 with
`last_error:repository-api`; the receipt retained enrollment state `requested`
and token revocation outcome `revoked`. No bearer value was displayed or stored.
Later doctor still returned `credential-scope`: no installation access to
repository `1414446320` was established. The transport intentionally suppresses
raw error bodies, so the exact HTTP failure reason was not retained or inferred.

AC-001's actual updated grant approval/readback is verified; AC-002 remains failed.
Profile remains inactive, no local destination or initial PR completed, and the
second repository remains uncreated. No additional permission/installation
selection change was attempted. The [design alternatives](technical-design.md)
require a new owner scope decision; the existing approvals remain valid for
their bounded targets and grants. The App/key are retained privately.

## Approved All repositories recovery — October 11

The owner instructed “Lets do all repos”, approving the concrete account-wide
proposal, and removed the unused installation-access permission. Actual App and
installation readback now show All repositories and exactly Repository creation,
Contents and Pull requests write plus Metadata read. App root authority covers
all existing/future account repositories; project credentials remain singleton.
No unrelated source was read/enrolled and no unrelated write was attempted.

Provider 1.5.2/profile schema 2 passed 47 focused tests in 66.264 seconds. The full
repository checker passed exit 0, including 47 broker tests in 82.667 seconds,
41 provisioning tests and 21 template tests. Whitespace and changed Markdown
relative links passed. Exact final revision/CI follows the PR; no private file
is staged. Previous selected/enrollment failures remain historical evidence.

Executed inactive `credentials installation-policy --repository-selection all`,
retaining the previous profile, then resumed operation
`148056feb07746a5be813c8e0f2dfac5`. It completed the first retained repository
without replaying creation, opened initial PR #1 and published the local starter.
The previous failed PUT is marked superseded, not falsely verified successful.
Then `credentials activate`, `new gptclaw-prj005-two --plan` and normal
`new gptclaw-prj005-two` completed. This proves first-canary recovery plus one
successive fresh configured creation, not two fresh creates under the final
policy. No per-project PAT/deploy key/installation selection was required.

| Project | Repository ID / operation | Main / starter SHA | Initial / later PR |
|---|---|---|---|
| gptclaw-prj005-one | `1414446320` / `148056feb07746a5be813c8e0f2dfac5` | `ee364671806f64ea136ddf24defa59a35a7f98a7` / `8225e9e34cc924a0834135d44118bf3e874a6748` | [#1](https://github.com/danielbardsley/gptclaw-prj005-one/pull/1) / [#2](https://github.com/danielbardsley/gptclaw-prj005-one/pull/2) |
| gptclaw-prj005-two | `1414488910` / `ddf88444efa54a1ea92e870d1c2deef6` | `8324fd7ea41628102f95c3d2c66aa6e738afeee4` / `5c1e8fdd625eaba67aaf93b56f8e5a560f613186` | [#1](https://github.com/danielbardsley/gptclaw-prj005-two/pull/1) / [#2](https://github.com/danielbardsley/gptclaw-prj005-two/pull/2) |

Doctor reports ready/active/creation verified, 16 installation repositories and
managed IDs `1413668232`, `1414446320`, `1414488910`. Both default branches read
back as main and protection is explicitly owner-waived, `verified:false`. All
four fixture PRs are open; no fixture merge is implied or performed.

### Git isolation, renewal and source preservation

Native fetch passed in both projects. A parallel second fetch failed while a
scope probe issued credentials; its serialized read-only retry passed. No broader
fallback was used. Each project token's response proved exactly one immutable ID,
Selected token scope and Contents-write/Metadata-read grants despite the All
installation. Actual GitHub reads to the other private project returned 404.
Fresh reacquisition after discarding/revoking previous leases passed; explicit
API lease revocation returned `revoked`. No one-hour expiry wait is claimed.

The platform repository is public (`private:false`): metadata GET returned 200
with admin/maintain/push/triage/pull permissions all false for these tokens.
Public read is not denied private access; AC-003 now states that distinction.
Both helpers rejected platform/foreign URL requests before issuing credentials,
with empty output. No platform write was attempted.

Native pushes from two task-owned worktrees to `codex/credential-verification`
passed. Minimal singleton PR leases (Contents read, Pull requests write, Metadata
read) opened the later PRs above and revoked afterwards. Temporary worktrees were
removed normally; branches/PRs are retained. Disable of the first binding denied
new issuance while the second's fresh fetch passed; enable and first fetch passed.
Hash comparison proved dirty `next-env.d.ts` and `tsconfig.json` files unchanged
across refresh/recovery. Next generated those edits; they remain uncommitted.

An initial diagnostic used a non-context-manager token object and exited before
revoking one singleton Git lease. No bearer was displayed/persisted; its exact
expiry was not recorded but issuance validation bounds it within 65 minutes.
Subsequent diagnostics used explicit finally/revocation. Ordinary native Git
handoffs also stay valid until reported expiry; immediate revocation is not
claimed. `new prj005-local-preview --local-only --plan` reported no GitHub action
or provider; no additional local/remote project was created.

### Private runtime and owner checks

Both manifest/provenance validations passed. Scoped start passed frozen dependency
installation/build and private readiness. First start operation
`998ee5ed316740b490f5129b9779387c` took 48.433 seconds, second
`d121000baa2641f39b90f6450d9052ff` 36.585 seconds. Declared tests passed in
operations `7fae3195611a4508a5748197f903c6cf` and
`0caa48b8e900422dab574a02c17d3f5a`. Explicit container `pnpm typecheck` passed
for each through the reviewed resource-limited provider job.

Both private HTTPS pages and health endpoints returned 200 and matching project
identity. The owner answered “Both load correctly” for
[one](https://forge-dev-01-4.tail8c3304.ts.net/projects/gptclaw-prj005-one/) and
[two](https://forge-dev-01-4.tail8c3304.ts.net/projects/gptclaw-prj005-two/).
They remain ready on loopback ports 18086/18087. `hello-second` remained ready on
18081 before, between and after operations and passed private page/health checks.
The stable installed runner reports 1.5.2/schema 2. No unrelated runtime, public
exposure, host package, infrastructure or production mutation occurred.

Current disposition: AC-001/002/003/004/006/007 pass for the explicitly approved
All repositories slice and observed recovery path. AC-005 still needs actual
owner signing-key rotation/retirement; renewal/token revocation/disable/enable/
recovery passed and real different-key rotation passed offline. AC-008's live
app/independent-service/owner checks pass; final-head CI remains pending. Merge
and Delivered remain pending. App/key, both repositories/projects/private apps
and four open fixture PRs are retained as authorized. Revoked PATs were not reused.
