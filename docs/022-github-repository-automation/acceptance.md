# SPEC-022 acceptance evidence

- **Status:** Local and implementation CI verified; live/owner acceptance pending
- **Owner:** Daniel
- **Evidence date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-022](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- **PR:** [#52](https://github.com/danielbardsley/gptclaw/pull/52)
- **Implementation:** provider 1.4.0 on `codex/prj-004-spec`; verification worktree
  based on planning commit `9d835a2` (implementation commit `c60bd7a` and subsequent corrective revisions are linked by PR #52)

## Authorization and boundaries

Daniel authorized implementation on October 10 and separately approved retaining
`danielbardsley/gptclaw-prj004-verification` for live verification using an explicitly
supplied private token. He requested private-file creation instructions; those
are in the [runbook](../../runbooks/manage-project-repositories.md). No token/path,
actual expiry or grants have been supplied yet. No application repository,
credential, environment, infrastructure or private app was mutated in these
checks. Test data is synthetic; Git remotes are task-owned temporary bare repos.

## Criterion mapping

| Criterion | State | Observed evidence | Remaining action/owner |
|---|---|---|---|
| AC-001 | pending | Offline read-only plan, exact release, collision/path/input rejection and no-write tests pass. | Verify actual actor/account/name observations with supplied token. |
| AC-002 | pending | Real fixture Git proves README-only main, starter history/provenance/guidance and one PR; protection precedes exclusive starter ref. | Run authorized private GitHub fixture and record actual PR/files. |
| AC-003 | pending | Protection readback/denial/drift tests pass; no implicit policy repair or starter publication after denial. | Verify GitHub settings and actual direct-main denial. |
| AC-004 | pending | Empty selections cause no corresponding requests; development environment/readback and secret metadata states pass. No secret writes exist. | Record selected/no-selection behavior against actual GitHub. |
| AC-005 | pending | Private-file/type/expiry, wrong actor/plan, anonymous-fd askpass, HTTP redaction and redirected Git configuration rejection pass with synthetic credentials. | Verify actual grants/expiry and revoked provisioning tokens; record separate Git handoff. |
| AC-006 | pending | Lost creation response never auto-adopts; explicit ID reconciliation, response loss at object/ref/protection/environment/PR boundaries, locks, drift and atomic-local-publication recovery pass. Partial generation preserves owned staging for operator review. | Record live receipt/resource identity and retained-resource disposition. |
| AC-007 | pending | Existing template/provider and offline repository regressions pass; bundle includes adapter/helper and local-only interfaces remain supported. | Real GitHub starter/container checks, private runtime/independent-app check, merge and Daniel's acceptance; implementation CI passed. |

All criteria remain pending because their required live evidence is incomplete;
offline assertions do not establish deployed behavior or owner acceptance.

## Local verification

- `.venv-manifest/bin/python scripts/tests/test_project_repositories.py`: 36 tests passed on the final source, including the empty-repository API conflict case; earlier 25-test and 33-test runs passed
  before additional safety/API cases were added.
- `.venv-manifest/bin/python scripts/tests/test_project_templates.py`: 21 tests
  passed, including installed bundle parity, legacy creation and release integrity.
- `source .venv-manifest/bin/activate; ./scripts/check-repository.sh`: passed with exit code 0; its focused repository
  subprocess ran the then-current 33 tests before the final JSON/nested-path cases
  were added; the final focused run above verifies those additions. Its fixtures do not operate host services.
- `git diff --check` and `bash -n scripts/check-repository.sh`: passed during
  implementation; final changed-document relative-link checks also passed.

Terraform commands were not run: no Terraform/host infrastructure changed.
Live GitHub/configuration, real app/container/runtime checks and deployment were
not run because the specifically scoped provisioning token is not yet supplied.
Implementation CI outcomes are recorded below, separately from local checks. No test output contains token values or environment dumps.

## Verified implementation CI

The exact implementation revision `6b28922798fa4ff6471cf5b214130e6be928650e`
passed all three configured PR workflows:

- [Private application workflow](https://github.com/danielbardsley/gptclaw/actions/runs/38084743186): offline tests, template integrity, generated starter install/test/typecheck/build, dependency operations and selected toolchain acquisition/preparation passed.
- [Terraform development host quality](https://github.com/danielbardsley/gptclaw/actions/runs/38084743104): success; protected remote mutation was not performed.
- [Terraform Tailscale federation quality](https://github.com/danielbardsley/gptclaw/actions/runs/38084743139): success; protected remote mutation was not performed.

These establish CI quality for that exact code revision, not live GitHub setup,
host deployment or Daniel's acceptance. This subsequent evidence/task-status
update changes documentation only; any follow-up PR-head run is visible on PR #52.

## CI history

The first implementation revision `c60bd7a` failed the private-app CI job's
installed-provider test because it expected a host-only repository status error
on GitHub's differently numbered unprivileged user. The host correctly rejected
that user with `setup`; the test now checks portable version/help output instead,
without relaxing the host identity gate. The focused 35-test suite passed again
locally after correction. A further scoped API regression handles GitHub
empty-repository ref responses (409) without treating other conflicts as missing.
The final code revision passed as recorded above.
The related repository-check CI jobs include the same test; first-run failures
remain historical evidence, not acceptance. See [failed app run](https://github.com/danielbardsley/gptclaw/actions/runs/38084547944)
and [failed federation run](https://github.com/danielbardsley/gptclaw/actions/runs/38084547901).

## Delivery and remaining work

The operator interface supports creation-only authority followed by a token
selected for the new repository. GitHub may not offer the creation-only grant
in Daniel's UI; any alternative needs exact scope review rather than assumed
account-wide administration. Token grants cannot be introspected by this
adapter: actual endpoint enforcement and operator-reviewed metadata are required.
Local expiry is declared metadata; GitHub enforces its real expiry.

Retain the authorized fixture when live verification is performed. Revoke each
provisioning credential after its phase and record owner/scope/reason/expiry and
revocation follow-through without values. Ongoing per-repository Git access is
pending PRJ-005 or separate manual provisioning. No automatic merge, force push,
remote deletion, production dependency or public exposure is part of completion.
Merge and full acceptance remain pending; catalogue status stays In review.
