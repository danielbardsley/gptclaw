# SPEC-023 acceptance evidence

- **Status:** Candidate implementation locally verified; App/live acceptance pending
- **Owner:** Project owner
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-023](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- **PR:** [#54](https://github.com/danielbardsley/gptclaw/pull/54)
- **Implementation:** provider 1.5.0 on `codex/prj-005-spec`; tested candidate worktree based on `cb6c8df`, committed revision linked by the PR

## Authorization and boundary

The project owner instructed “Ok, now implement the spec”, authorizing the bounded
implementation and selected standing private/PR policy. One-time App settings,
selected bootstrap repository/key handling and retained live target authorization
were requested separately using the concrete [setup runbook](../../runbooks/manage-repository-credentials.md)
and [settings checklist](../../config/repository-credentials/github-app-settings.json).
That setup response and actual App/installation IDs/private-key file path are
pending. No real App/private key/token/profile or remote repository was used or
created during implementation tests. Previous revoked PATs were not read/reused.

App personal creation and automatic access under a selected installation remain
unverified. The candidate deliberately requires a successful canary before profile
activation and does not broaden permissions or introduce a PAT fallback when
capabilities are missing. It is not marked Delivered or operationally ready.

## Criteria

| Criterion | State | Actual local evidence | Remaining evidence/owner action |
|---|---|---|---|
| AC-001 | pending | Private mode/path/profile checks, signed identity contracts, wrong account/selection/grants and suspension tests pass. Setup proposal names exact minimal grants and bootstrap selection. | Owner authorizes/configures the real App, supplies IDs/path; doctor validates actual installation. |
| AC-002 | pending | Two successive fixture projects complete the real provisioning/Git-object flow after one synthetic setup; no-inclusion case retains one repository/receipt without fallback. | Prove two real personal-account App creations and automatic inclusion with no additional owner clicks. |
| AC-003 | pending | Singleton repository_ids and exact permission response checks reject missing/extra grants and cross-repo use; creation leases cannot enter Git. | Real token scope/readback and denied access to another private repo/platform. |
| AC-004 | pending | Key/fd/argv/token-shape/redaction/config/bundle tests and actual native Git protocol checks pass using synthetic material. Tokens are not persisted in metadata. | Real non-secret grant/expiry/key-handling evidence only; no live key was supplied. |
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

Profile remains absent/inactive in the real environment. Use matching provider
1.5.0 for setup, prove the canary, then activate once. Normal future projects
should need no manual token creation; App grant/key revocation or maintenance
can still require an owner action. Ordinary Git helper tokens expire at reported
times because they must remain valid after helper exit; API leases are best-effort
revoked immediately. Deactivation/disable does not claim server-side revocation.

Merge, actual App feasibility, live criteria and owner acceptance remain pending.
The previous SPEC-022 slice remains Delivered, with its retained source/app/PR
and explicit reported token revocation unchanged.
