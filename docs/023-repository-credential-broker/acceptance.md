# SPEC-023 acceptance evidence

- **Status:** Candidate implementation locally verified; live canary blocked on automatic App inclusion
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
activation and does not broaden permissions or introduce a PAT fallback when
capabilities are missing. It is not marked Delivered or operationally ready.

## Criteria

| Criterion | State | Actual local evidence | Remaining evidence/owner action |
|---|---|---|---|
| AC-001 | passed | Owner completed the proposed setup; configure and initial doctor validated App/installation identity, exactly the minimal grants and sole bootstrap selection. Key metadata passed. | Later doctor correctly rejects the incomplete canary's missing installation access; profile stays inactive. |
| AC-002 | failed | Real installation-authenticated personal creation returned private repository ID `1414446320`; subsequent installation lookup/inventory and restricted-token probe did not grant access. No-inclusion recovery retained the repository/receipt. | Resolve actual automatic inclusion without manually selecting every new repository or broadening scope. Second creation was not attempted. |
| AC-003 | pending | Singleton repository_ids and exact permission response checks reject missing/extra grants and cross-repo use; creation leases cannot enter Git. | Real token scope/readback and denied access to another private repo/platform. |
| AC-004 | pending | Key/fd/argv/token-shape/redaction/config/bundle tests pass using synthetic material. Live key metadata and minimal grants verified; no bearer values printed or persisted. | Full live project credential/container evidence remains pending. |
| AC-005 | pending | Fresh token/revocation, near-expiry renewal, locks, real different-key rotation, lost response and partial enrollment recovery pass offline. | Live renewal, signing-key rotation and installation/token revocation outcomes and owner key retirement. |
| AC-006 | pending | Activated-profile normal new, explicit local-only, unconfigured compatibility and effective no-publication preview tests pass. Manual PAT regressions remain valid; manual operations cannot be implicitly adopted. | Real configured normal new flow and independent runtime compatibility. |
| AC-007 | pending | Actual Git fetch/branch push over authenticated private TLS fixture through the production helper passed; later PR and dirty-source/remote preservation tests pass. | Real GitHub fetch/push/later PR after fresh token acquisition and worktree/owner observations. |
| AC-008 | pending | Existing template/provider checks passed; new source/installed bundle includes broker/helper with no keys. | Real two-app quality/page/health and independent-service checks, final-head CI and owner desktop acceptance. |

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

The real profile is configured but inactive. Use matching provider
1.5.0 for setup, prove the canary, then activate once. Normal future projects
should need no manual token creation; App grant/key revocation or maintenance
can still require an owner action. Ordinary Git helper tokens expire at reported
times because they must remain valid after helper exit; API leases are best-effort
revoked immediately. Deactivation/disable does not claim server-side revocation.

Merge, automatic-inclusion feasibility, remaining live criteria and owner acceptance remain pending.
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
