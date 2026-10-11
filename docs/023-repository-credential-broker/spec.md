# SPEC-023: Repository credential broker

- **Status:** In review — All repositories policy approved; live acceptance in progress
- **Owner:** Project owner
- **Date:** 2026-10-10 (America/New_York)
- **Feature:** PRJ-005, initial GitHub App broker; bounded PRJ-002/004 integration
- **Design:** [TDD-023](technical-design.md) · **Tasks:** [TASKS-023](tasks.md)
- **Direction:** [Architecture](../platform/architecture.md) · [Catalogue](../platform/features.md) · [Sequence](../platform/sequence.md)

## Outcome

After one owner-controlled GitHub App setup, the project owner can create successive private
projects under `danielbardsley` with their GitHub repositories, initial PRs and
ongoing Git access configured automatically. Creating the second and subsequent
projects requires no new manually generated PAT, per-repository deploy key or
GitHub installation-selection click. Normal fetch/push obtains fresh short-lived
credentials automatically, including after earlier credentials expire.

The normal configured project-creation request includes GitHub setup; explicit
local-only creation remains available. Automation changes credential mechanics,
not ownership or approval of project scope, source publication, merges or deployment.
A new project request must resolve a concrete repository/name/destination; it is
not authority to access an arbitrary existing repository.

The project owner selected this specification after completing SPEC-022. On October 10 he
selected a standing policy for this draft: private repositories and PR review
without GitHub-enforced branch protection on his current plan. This is a known
scope preference, not an unanswered decision. The subsequent instruction “Ok, now implement the spec” approved the bounded
spec/design and authorized implementation. App registration/installation/key
placement and exact live fixtures remain separately scoped owner steps. Candidate
provider 1.5.0 implements the broker; no real App/key/live project has been created
by offline implementation tests. The owner subsequently completed App setup and
approved both retained live targets/activation. Actual personal creation passed,
but automatic selected-installation inclusion failed the first canary; the
profile was left inactive at that point. The later All repositories amendment
recovered that operation and activated the profile; see [acceptance.md](acceptance.md).

On October 11 the project owner approved the proposed additional **GitHub App
installation repository access: write** permission by updating the App settings.
This amends CRD-001/002's access mechanism: provider 1.5.1 may explicitly enroll
an App-created repository through GitHub's installation API when automatic
inclusion is absent. Enrollment is limited to this App/installation and the
immutable repository ID in its matching creation journal/binding. No arbitrary
import, all-repositories installation, Administration or project Git enrollment
authority is added. The installation must accept the updated grant before use;
App settings alone are insufficient. The no-per-project-owner-action outcome
and all other acceptance requirements remain unchanged. This candidate mechanism
still requires live proof before activation.

After that candidate also failed live, the project owner instructed “Lets do all
repos” on October 11, approving the concrete account-wide installation proposal
in the design. The current accepted setup is the same private App installed on
**All repositories**, with Repository creation/Contents/Pull requests write and
Metadata read; the unused installation-access permission is removed. This grants
App root authority over every existing/future account repository, including the
platform and unrelated repositories. It does not authorize new writes to those
repositories or enroll them as managed projects. Project Git/API tokens remain
restricted to one approved immutable binding and exclude creation/administration.
Schema-2 profile policy records All repositories explicitly; a GitHub change
alone cannot implicitly migrate or activate the broker. The two authorized
retained targets and successful-canary activation gate remain in force.

## Baseline and scope

SPEC-022 provider 1.4.0 is Delivered (PR #52, completion PR #53). It creates a
private starter/initial PR and resumes by immutable ID but requires explicit
PAT files; ongoing Git access is reported pending. Its GitHub adapter accepts
fine-grained PATs and authenticates `/user`, so App tokens require a distinct
reviewed authentication path. Its bootstrap script and local app runtime remain
separate interfaces. The planning-only bootstrap skill does not create GitHub
repositories; this initiative does not turn it into an app generator.

The project owner reported revoking both temporary SPEC-022 tokens after verification. That
is owner-supplied confirmation, not an API revocation check. Do not reopen or reuse
them. The GptClaw platform deploy key remains specific to that repository.

Include one personal-account-only GitHub App, bounded creation authority,
per-repository installation-token issuance, normal Git credential integration,
refresh/revocation/key rotation and a combined configured `new` workflow consuming
SPEC-022's generator/state machine. Record the one-time unprotected-private-dev
policy and apply it explicitly to new managed projects. App runtime, package
installation and private routing remain the delivered SPEC-018–021 path.

Exclude organizations, production/cloud credentials, public repos/previews,
webhook servers or public OAuth callbacks, app runtime secrets, automatic merges,
GitHub Actions workflow-file writes, environments/secrets administration,
arbitrary repository import and dashboards. Account-wide installation is included
only under the explicit October 11 approval, not inferred after a denial.
Existing-repository onboarding is limited to explicitly approved owner-managed
verification/bootstrap repositories, with exact IDs approved during setup.
Deploy keys are a separately reviewed fallback if App feasibility fails; they
are not an automatic substitute or proof of the no-per-project-setup outcome.

## Requirements

- CRD-001: Provide a one-time setup/readiness workflow recording the approved
  account, App/installation IDs, selected bootstrap repository IDs, concrete
  permissions, private key location, project defaults and owner. Verify actual
  App/installation identity and authority before reporting ready. Record the
  approved All repositories policy separately from singleton project scope; never
  silently broaden to all repositories, add unrelated repositories, enable a
  public callback or substitute user/account-wide credentials after a denial.
- CRD-002: Automatically create each newly requested private repository using
  the approved creation capability, journal the returned immutable ID and obtain
  App access to that new repository. Bind it to the local project before issuing
  credentials. Installation reconciliation is bounded; delays, wrong identity,
  missing permissions or unsupported personal-account creation stop with retained
  resources and a specific operator action. Never require a new manual PAT for
  each project in the accepted automatic path.
- CRD-003: Issue GitHub installation tokens with exactly one bound repository ID
  and only the permissions needed for the operation. Creation credentials are
  confined to the provisioning path; ongoing project Git credentials cannot
  administer/delete repositories, create other repositories or access unrelated
  private repositories. Validate actual granted repository/permission metadata
  before use; never omit repository restriction on a project token or fall back
  to installation-wide Git access.
- CRD-004: Keep App keys, JWTs, tokens and any credential cache outside source,
  remotes, commits, arguments, logs, receipts, template/provider bundles and app
  containers. Pass Git authentication through a reviewed private channel; token
  bytes may traverse only the intended Git credential pipe/fd. Reject unsafe
  files, symlinks, wrong ownership, URL rewrites, unsupported hosts/protocols,
  credential-bearing URLs, malicious helpers and mismatched project bindings.
  Forge-owned controls do not create a hostile same-user security boundary.
- CRD-005: Acquire/renew credentials automatically from the approved App grant;
  use GitHub-reported lifetimes rather than guessed expiries or PAT prefix rules.
  Handle expiry, key rotation, suspension/uninstall, rate limits, clock skew and
  concurrent requests without credential leakage or broadening. Reconcile writes
  before retry; never replay an ambiguous push or repository-create blindly.
  Document immediate revocation, bounded residual token lifetime after crashes,
  recovery and operator follow-through for App key/grant removal.
- CRD-006: Once the owner activates the reviewed profile, normal `new` creates
  local starter, private GitHub repository, initial PR and usable per-project Git
  integration as one resumable operation. Preserve explicit local-only mode and
  unconfigured local-only behavior. Plans show remote side effects and resolved
  identity/provenance/policy. Apply the selected standing unprotected-private-dev
  policy as an explicit recorded choice; do not represent it as server enforcement,
  inherit the old fixture waiver silently, expose a repository publicly or merge
  the initial PR. Existing projects/runtimes and the manual SPEC-022 path remain
  intact until explicitly enrolled.
- CRD-007: Install a project-scoped normal Git interface supporting fetch and
  branch push with transparent credentials; provide the PRJ-004 API path with
  credentials for opening a later explicitly requested PR. Preserve real Git
  history, worktrees, remotes, user edits and standard review flow. Record
  identity, credential mode, expiry, operation results and pending owner actions
  as sanitized metadata. Do not print reusable token values as a convenience API.
- CRD-008: Verify two successive real private projects after one bootstrap, normal
  Git operations after credential renewal, negative cross-repository access,
  resume/revocation/rotation and private runtime compatibility. Completion must
  demonstrate no per-project manual token/installation intervention; an offline
  broker or a manually selected second installation alone is insufficient.

## Acceptance criteria

| ID | Required observable evidence | Requirements |
|---|---|---|
| AC-001 | Owner-reviewed App permissions, explicit All repositories policy and key handling are documented. Doctor/status verifies actual account/App/installation binding and rejects wrong account/key/install/grants or an unapproved policy switch, with no unauthorized mutation. | CRD-001 |
| AC-002 | After one setup, two authorized new private projects independently complete repository creation, automatic App inclusion, bound credentials and initial PRs without another PAT, deploy key or installation-selection click. Missing inclusion/creation support stops without widening scope. | CRD-002/006/008 |
| AC-003 | Actual token metadata matches one immutable repository ID and minimal operation permissions. A credential issued for A cannot read/push private B or obtain platform write authority; its helper rejects platform/foreign URL credential requests. Public metadata is inherently readable and is not claimed private. Missing restriction/extra grants are rejected offline. Creation authority is never handed to project Git. | CRD-003/004 |
| AC-004 | Synthetic-secret tests cover stdout/stderr/errors/receipts/remotes/argv/environment/container/bundle boundaries, unsafe key files, Git rewrites/helpers and binding substitution. Live evidence contains IDs/grant/expiry metadata only. | CRD-004 |
| AC-005 | Offline expiry/skew/rate-limit/response-loss/race tests pass. Live reacquisition and Git operations work after discarding or expiring a prior token, without owner action. Key rotation and installation/token revocation show documented outcomes, residual lifetimes and recoverable journals; no write replay or fallback. | CRD-005/008 |
| AC-006 | Activated profile gives the combined normal new flow, initial PR and explicit owner-selected unprotected-private-dev policy; local-only/unconfigured creation has no GitHub side effects. Existing manual PAT flow and unrelated apps retain behavior; no immutable template edits or implicit enrollment. | CRD-006 |
| AC-007 | Each generated repo supports ordinary fetch and branch push without copied tokens/global credential changes; a later requested PR opens through the scoped API path. Dirty sources/worktrees/remotes survive refresh and rollback. Receipts report actual credential readiness, including failures. | CRD-007 |
| AC-008 | Both retained projects pass existing manifest/provenance/build/test/typecheck and private page/health checks. One app stays ready while the other is operated. Record local tests, final-head CI, GitHub grant/identity readback and the project owner's desktop/owner acceptance separately. | CRD-008 |

## Decisions, ownership and completion

The project owner owns the App, selected bootstrap target/grants, private-key custody,
standing profile and acceptance. The primary path now uses the approved All
repositories installation. The earlier selected path and explicit enrollment
candidate failed live; those observations are preserved in acceptance. Project
installation tokens are narrowed by repository ID and permission. Gate adapter
selection on a concrete endpoint/permission review and live canary after explicit
setup/fixture authorization. [Installation](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app),
[token scope/lifetime](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app),
[App permissions](https://docs.github.com/en/rest/authentication/permissions-required-for-github-apps).

Propose the existing retained SPEC-022 verification repository as the sole initial
bootstrap reference; exact App name/ID, installation ID and grants are reviewed
before activation. Account-wide App access is explicitly approved, while writes
to/enrollment of GptClaw or other existing projects require their own task scope.
App creation/installation/private-key placement is one owner setup;
periodic key maintenance or revoked-grant reauthorization remains possible,
without a repeated setup for every project. Automatic personal-account creation
must be proven using the chosen App credential class; if it cannot satisfy the
requirements, return an amended proposal rather than silently add broader PATs.

Deliver broker/credential helper, provider integration, focused tests and an
operator runbook through reviewed PRs after implementation authorization. Add
acceptance.md when actual evidence is available; no acceptance is claimed by this
planning task. Mark Delivered only after implementation merge and all required
criteria pass. Manual token revocation from the previous feature is not a new
implementation prerequisite; the project owner's supplied report is retained as such.
