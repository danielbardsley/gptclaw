# SPEC-022: New GitHub repository automation

- **Status:** Delivered — initial private-repository slice merged and accepted
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Feature:** PRJ-004, initial personal-account private-repository slice
- **Design:** [TDD-022](technical-design.md) · **Tasks:** [TASKS-022](tasks.md)
- **Direction:** [Architecture](../platform/architecture.md) · [Catalogue](../platform/features.md) · [Sequence](../platform/sequence.md)

## Outcome

Daniel can turn a selected supported application starter into its own private
GitHub repository with a protected default branch, a reviewable initial pull
request and a clear setup receipt. He can preview the exact changes before
creation and resume interrupted setup without duplicating repositories or PRs.
The new application continues to use the existing private local runtime.

Daniel requested this specification and confirmed `danielbardsley` personal-account
repositories on October 10. He then instructed “Ok, implement the spec”, approving
the bounded requirements/defaults and authorizing implementation. He separately
authorized retaining `danielbardsley/gptclaw-prj004-verification` for live checks
with an explicitly supplied private provisioning token. Daniel subsequently supplied a creation-only token, approved a seven-day
expiry limit and authorized manual revocation on completion. The retained private
verification repository now exists; scoped configuration and full acceptance
remain pending. Review, merge and acceptance remain separate;
see [acceptance.md](acceptance.md).

## Scope and baseline

Include new private repositories under `danielbardsley`, the accepted exact
Next.js catalogue release, a minimal bootstrap `main`, starter content on a
`codex/` branch, an initial PR, verified branch protection, optional explicitly
selected development environments, and documentation of secret references.
No secret values are needed for the initial web starter. An empty environment
selection and an empty secret-reference list are valid and recorded.

Reuse SPEC-018's CLI/runtime, SPEC-019's dependency policy, SPEC-020's pinned
web toolchain and SPEC-021's immutable template catalogue. These initial slices
are Delivered. The current `new` interface creates local source; GitHub setup is
a new opt-in operation. The planning-only bootstrap script remains independent.
The existing GptClaw deploy key is specific to the platform repository and must
not be reused for application access or account administration.

Exclude organization repositories, importing/adopting existing repositories,
public repositories, automatic merge, production environments/deployment,
AWS/HCP changes, public previews, dashboards, generalized credential issuance or
rotation (PRJ-005), runtime secret materialization (SEC-001), and generated CI
workflow templates (QLT-002). The initial PR includes documented existing local
quality commands; new CI/status-check requirements need a reviewed follow-up.
Application source publishing is separate from running or exposing an app.

## Requirements

- REP-001: Provide a read-only plan identifying account/repository, private
  visibility, local destination, exact template/version/digest, initial branches,
  protection settings, selected development environments, secret-reference
  names/scopes and credential capabilities needed. Reject unsupported input,
  unsafe paths, existing destinations and name collisions before mutation.
  Planning never executes application content or reads application secret values.
- REP-002: Apply only the reviewed plan to `danielbardsley`; create a private
  repository and bind setup to its immutable repository ID and local target.
  Initialize `main` with only a minimal non-executable bootstrap README, then
  verify protection before pushing starter content to a `codex/` branch. Open
  exactly one initial PR to `main`; do not merge it. Starter contents preserve
  catalogue provenance, manifest v1, toolchain/dependency declarations and
  adapted repository guidance. Do not overwrite existing Git history or remotes.
- REP-003: By default, protect `main` against force pushes and deletion, require a PR and
  resolved review conversations, and enforce the policy for administrators.
  Propose zero required approvals for the single-owner initial slice, avoiding
  self-review deadlock. Do not require nonexistent CI checks or bypass protection
  to publish starter content. Read back actual settings; unavailable plan/API
  capabilities or unexpected drift produce an incomplete blocked outcome.
  Daniel may explicitly waive private protection for a recorded operation with
  no selected environments. Persist that waiver and report protection as
  `owner-waived`, never verified. Keep the repository private and use the starter
  branch/initial PR workflow; never remove existing verified protection.
- REP-004: Create only explicitly selected development environments with their
  reviewed supported settings. Record secret references as names and intended
  repository/environment scope, with pending provisioning clearly distinguished
  from verified existing metadata. Never fabricate secret objects, copy secret
  values, request secrets permission for the no-secrets path, or claim an
  environment establishes deployment approval. Production is excluded.
- REP-005: Use a separately authorized, bounded provisioning credential through
  a reviewed operator interface. Validate actor, target account and necessary
  capabilities; reject unrelated credentials. Keep credentials out of source,
  remotes, process arguments, output, receipts and application containers.
  Separate repository creation/configuration authority from ongoing project Git
  access. If PRJ-005 or an approved per-repository credential is unavailable,
  report that handoff as pending without claiming ongoing access is ready.
- REP-006: Persist a sanitized operation receipt with plan digest, repository ID,
  template provenance, completed steps, remote URLs, branch/commit/PR identifiers,
  settings readback and outstanding actions. Resume reconciles remote state
  before writes; ambiguous timeouts, concurrent requests and conflicting edits
  cannot duplicate resources or adopt an unrelated existing repository. Preserve
  generated source and partially created resources after failure. No automatic
  deletion, force push, protection weakening or remote rollback is allowed.
- REP-007: Keep local-only creation and existing private apps working unchanged.
  Document readiness, preview/apply/resume/status, owner handoff, credential
  revocation, recovery and retained-resource cleanup. Completion requires local
  failure tests, CI and a specifically authorized real private-repository exercise
  proving verified settings and a reviewable initial PR; no acceptance by mocks alone.

## Acceptance criteria

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| AC-001 | Preview lists all proposed changes and exact provenance. Invalid account, public visibility, unsupported template/options, unsafe paths, existing destinations and remote collision fail with no writes or source execution. | REP-001 |
| AC-002 | Authorized fixture creates one private repository with bootstrap-only main, protected before starter publication; one codex branch and one PR contain valid starter/guidance/provenance. Existing remotes/history and unrelated files are preserved. | REP-002 |
| AC-003 | Readback demonstrates PR enforcement including admins, zero approvals, conversation resolution and no force pushes/deletion. Unsupported private-plan capabilities, drift and denied administration fail without fallback. With protection enabled, a direct starter push to main is rejected. For Daniel's explicitly waived verification operation, verify the bound waiver, private visibility, no protection-removal calls and no enforcement claim instead. | REP-003 |
| AC-004 | Empty selections make no environment/secret writes. Selected development environments match readback; references distinguish pending from verified names. Production selection and secret-value inputs are rejected; logs/receipts contain synthetic names only. | REP-004 |
| AC-005 | Missing, expired, wrong-account and insufficient credentials stop safely. Synthetic-token tests demonstrate no credential leaks or container injection. Live evidence records credential class/capabilities/expiry without values and separately records ongoing Git handoff readiness. | REP-005 |
| AC-006 | Fault injection after every remote/local boundary, response loss after successful creation, competing requests and remote drift either resume the same bound operation or stop for reconciliation. One repository/branch/PR exists; retained source/resources and sanitized receipts support recovery without destructive cleanup. | REP-006 |
| AC-007 | Existing local new/test/start/stop behavior remains valid. An authorized private fixture passes the existing starter checks and private runtime smoke check, while an independent app remains available. Record revision, local results, CI, GitHub readback, owner acceptance and retained-resource disposition separately. | REP-007 |

## Decisions and completion

Daniel owns scope, settings, credentials and acceptance. Approved default policy
is private personal-account repositories, no environment/secrets unless selected,
and PR enforcement with zero approvals until an independent reviewer exists.
Daniel approved this scope and authorized implementation on October 10.

The implementation uses an explicitly supplied fine-grained PAT file and a
creation-only phase followed by a repository-specific provisioning credential.
Actual grants, expiry and account plan/API capabilities remain live readiness
checks; no account-wide administration fallback is assumed.
Private protection/environment availability depends on GitHub plan and feature;
verify support without changing visibility or silently dropping requirements.
See official [repository APIs](https://docs.github.com/en/rest/repos/repos),
[branch protection APIs](https://docs.github.com/en/rest/branches/branch-protection)
and [environment APIs](https://docs.github.com/en/rest/deployments/environments).
Do not assume a repository-scoped installation can create an uncreated personal
repository; resolve that bootstrap authority separately from PRJ-005.

Deliver CLI/provider integration, focused tests and an operator runbook through
a reviewed PR. Authorize the live fixture target and credential separately before
remote mutation; retain it unless Daniel separately authorizes removal. Record
actual acceptance evidence when available. Mark only this initial PRJ-004 slice
Delivered after implementation merge and all criteria pass; wider scope remains
future work. Offline implementation evidence is recorded in [acceptance.md](acceptance.md);
live verification and owner acceptance remain pending.

On October 10, after GitHub denied private protection for the retained fixture,
Daniel instructed “Ignore private branch protection requirement and continue.”
This authorizes an explicit waiver for that operation, preserves earlier
implementation/live authorization, and does not authorize public visibility or
production. Default protection and other requirement IDs remain intact.

## Completion — October 10

Daniel accepted the verified initial slice by instructing “Merge the platform
PR and mark as complete.” [PR #52](https://github.com/danielbardsley/gptclaw/pull/52)
merged as `869b1b7f275c4555ce8ce82acab2de0565d84069` after all three final-head CI workflows passed.
The approved owner waiver is recorded for the retained fixture; no private
protection enforcement is claimed there. [Acceptance](acceptance.md) records all
criteria and actual desktop/live evidence. Creating an initial reviewable app PR
was required; merging that fixture PR was explicitly not part of provisioning.
Manual token revocation remains Daniel's operational follow-through, and ongoing
credential automation is PRJ-005. Neither is represented as completed here.
