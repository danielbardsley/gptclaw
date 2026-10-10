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
are in the [runbook](../../runbooks/manage-project-repositories.md). At the initial offline baseline, no token/path,
actual expiry or grants had been supplied. The authorized live creation phase
has now run as recorded below. The earlier offline checks mutated no application repository, credential,
environment, infrastructure or private app. Test data is synthetic; Git remotes are task-owned temporary bare repos.

## Live creation phase — October 10

Daniel supplied the private provisioning-token file and reported **All repositories**
selection with **Repository creation** permission. The directory/file are owned
by `forge` (UID 1002), mode `0700`/`0600`, regular/no symlink. Read-only GitHub
metadata authenticated `danielbardsley` and reported actual token expiration
`2026-10-17T21:01:18Z` (October 17, 5:01 p.m. America/New_York).

Daniel explicitly authorized a seven-day implementation limit and committed to
manual token removal when finished. Temporary credential scope: owner Daniel;
reason SPEC-022 retained verification; all-repository selection with creation-only
permission as reported, actual creation endpoint succeeded; expiry above; removal
step revoke in GitHub and remove the private file under Daniel's control. Revocation
is pending; this is not standing application Git access or authority over other
repositories. Full token grants cannot be introspected by the adapter.

GitHub fine-grained `/user` omitted private subscription metadata. This is recorded
as `endpoint-verification-required`, not proof of a supported plan. Explicitly
reported unsupported plans still fail; configuration must verify protection
through actual endpoint write/readback before starter publication.

Executed on candidate revision `ebfe69c22a217d2ae4355a357df4a5386d5790b7`:

- `scripts/gptclawctl repo plan` for the authorized target succeeded read-only.
- The first `repo apply --create-only` rejected the saved CLI preview's timing
  envelope before mutation. The reader now accepts that exact bounded envelope;
  an offline regression covers apply and rejects unexpected fields.
- The same `repo apply --create-only` then returned `operator-required` (exit 1,
  intended credential handoff). Operation `c33aa2188ed84326a0f6bc2dc0fe2ad1` is
  journaled with immutable repository ID `1413668232`.
- Independent `GET /repos/danielbardsley/gptclaw-prj004-verification` readback
  verified owner, private visibility, matching operation description and size 0.
  [Retained repository](https://github.com/danielbardsley/gptclaw-prj004-verification).

No starter branches, protections, environments, secrets, PR or local app source
were published in creation-only mode. Resume awaits a second token selected only
for this repository, with Administration/Contents/Pull requests write permissions.
No permission fallback, deletion, production operation or app restart occurred.
The first token can be revoked by Daniel after creation; do not delete the retained
repository or its journal. Ongoing Git credentials remain a separate handoff.

The final focused suite after expiry/subscription/saved-plan fixes ran 38 tests
in 24.718 seconds, all passed. The updated full repository checker passed with exit 0 (including 38 focused tests).
All three code-revision CI workflows passed at `ebfe69c`:
[app workflow](https://github.com/danielbardsley/gptclaw/actions/runs/38086612822),
[development-host quality](https://github.com/danielbardsley/gptclaw/actions/runs/38086612864)
and [federation quality](https://github.com/danielbardsley/gptclaw/actions/runs/38086612890).
No protected infrastructure deployment was performed. Whitespace, shell syntax
and updated relative-link checks passed. This subsequent evidence update is
documentation only; its follow-up PR-head checks remain visible on PR #52.

## Criterion mapping

| Criterion | State | Observed evidence | Remaining action/owner |
|---|---|---|---|
| AC-001 | pending | Offline read-only plan, exact release, collision/path/input rejection and no-write tests pass. | Actual actor/account/target preview observed; final setup readback remains pending. |
| AC-002 | pending | Real fixture Git proves README-only main, starter history/provenance/guidance and one PR; protection precedes exclusive starter ref. | Private repository ID/owner verified; protected bootstrap/starter PR and files await scoped token. |
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
Live GitHub creation/readback ran as recorded above. Remaining configuration
and real app/container/runtime checks await the repository-specific token; no
host/infrastructure deployment was performed.
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
