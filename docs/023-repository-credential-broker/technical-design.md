# TDD-023: Repository credential broker

- **Status:** Draft proposal; App/endpoint feasibility and owner setup pending
- **Owner:** Project owner
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-023](spec.md) · **Tasks:** [TASKS-023](tasks.md)

## Architecture and grant boundary

Use a private personal-account GitHub App owned by the project owner, initially installed on
an explicitly selected bootstrap repository. GitHub documents automatic App
access to repositories it creates; rely on that supported mechanism only after
verifying the exact personal-account create/inclusion path. Do not choose an
all-repositories installation as a convenience workaround. Its signing key is
long-lived root authority for the selected installation and future App-created
projects; every normal project token is narrowed separately. The key is private
owner material, not an application credential or a shared project token.

Proposed App grants are Repository creation write, Contents write, Pull requests
write and automatically needed Metadata read. Ongoing Git tokens request only
one repository ID with Contents write/Metadata read; PR API operations request
only their required PR/content read permissions. Creation-only tokens carry the
minimum supported creation grant and never enter Git helpers/containers. Review
actual endpoint permission combinations before implementation. Administration,
Secrets, Environments, Workflows and organization permissions are excluded from
this initial unprotected-private-dev profile. If setting default main requires
Administration, first review the creation/default-branch mechanism; do not add
that standing grant implicitly. Require/read back main before opening its PR.

The current REST documentation lists App credential types for personal repository
creation. Propose an installation-authenticated creation path and prove it in the
canary; do not assume `/user` authentication works for installation tokens or
silently introduce an expiring user token/refresh-token store. Bind App JWT/API
readback to the expected App and installation account. If this path is unavailable,
stop the affected task and present a concrete alternative grant design to the project owner.
Official references: [personal repository creation](https://docs.github.com/en/rest/repos/repos#create-a-repository-for-the-authenticated-user),
[App token endpoints](https://docs.github.com/en/rest/apps/apps),
[installation behavior](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app).

No public callback/webhook service, new AWS resources, privilege change or host
package install is required by the proposal. This is a user-scoped local broker
library/helper. A maintained JWT signing dependency, if needed, must be pinned in
an isolated project Python environment via reviewed requirements/setup changes;
verify available tools before choosing it. Do not hand-code cryptography or assume
an uninstalled SDK/runtime. App settings/key provisioning are separate owner steps.
All forge processes share an identity: private files and validation reduce
accidental leakage but do not isolate an App key from hostile same-user code.
The accepted project containers continue to exclude the home/key directory.

## Interfaces and flow

Proposed commands are `credentials doctor/status/rotate/revoke` and a configured
`new` flow; exact flags/JSON schemas are implementation deliverables. The broker
has no command that prints reusable bearer tokens. Plans/status are observation
interfaces returning non-secret IDs, permissions, lifetimes and actions only.

1. Owner configures one private App/installation/key and approves the standing
   unprotected-private-dev profile. Doctor verifies actual identity/grants and
   explicit bootstrap selection. Profile activation opts new project requests
   into private GitHub setup; absent activation keeps existing local-only behavior.
2. A concrete new request resolves an exact supported template/name/destination
   and previews remote effects/policy. `new --local-only` uses the delivered local
   path without credentials, network, repository metadata or helper enrollment.
3. The provisioning adapter obtains creation authority, uses SPEC-022's durable
   create intent/immutable ID journal and reconciles automatic installation access.
   Retry only bounded observations; ambiguous creation stays operator-required.
   Scope the next token to the newly bound repository ID and verify response grants.
4. Reuse SPEC-022's bootstrap, starter objects/exclusive ref, initial PR and local
   publication. Apply the activated standing policy explicitly as approved metadata,
   not by silently reusing the earlier fixture waiver. No protection enforcement
   or production environment is claimed. Record keyless non-secret project binding.
5. Enroll a reviewed local Git credential helper for that project. Exact HTTPS
   github.com host/path and immutable binding must match the owner registry; no
   global Git credential store, borrowed SSH key, token-bearing remote or fallback.
   Helper protocol responses carry the short-lived token only to Git through pipes.
   Credential requests from another project/URL are rejected, not redirected.
6. Subsequent fetch/push acquires a fresh one-repository Git credential. A later
   explicitly requested PR uses its own minimal API capability. Token acquisition
   and scope validation happen automatically without per-project owner interaction.

Existing SPEC-022 Git configuration validation currently rejects arbitrary local
helper configuration; extend its reviewed allowlist for this exact owned helper
rather than disable validation. Replace PAT-specific checks only in the distinct
App provider; preserve manual PAT behavior. App tokens are not validated by fixed
PAT prefixes or fixed lengths. Version credential receipts/profile independently
of manifest v1 and keep existing provenance/template releases unchanged.

## Storage, refresh and failure handling

Private key stays outside projects/provider bundles in an owner-approved private
location, mode 0600 under mode 0700; validate owner/type/link/path/bounds. Store
only App/installation IDs, immutable repository bindings, activated profile,
operation intents and non-secret receipts in broker metadata. Project source may
record safe repository identity/provenance; it must not hold key/token material.
Use atomic writes and per-repository locks. A manipulated project config cannot
replace the platform's canonical binding; validate on each credential operation.

Prefer fresh short-lived tokens per bounded operation, with no persistent bearer
cache in the initial slice. GitHub installation tokens currently expire after an
hour; validate actual response expiry/scope and acquire again before insufficient
remaining lifetime. Proposed best-effort post-operation token revocation uses the
matching token's own supported endpoint. Record uncertain revocation/expiry after
crash without values. If later caching is necessary, propose its private storage,
concurrency, expiry and deletion rules before adding it.

Authentication failures stop dependent writes. Retry a verified read after renewal
where safe; reconcile branch/ref/PR identities before deciding whether a failed
write ran. Never retry an ambiguous Git push blindly. Expose suspended/uninstalled
App, missing repository selection, clock skew, stale binding, insufficient grants,
unsafe keys and key rotation as actionable sanitized states. No permission denial
causes a broader token, different account, all-repositories install or PAT fallback.

Rotation validates a new App key/identity with the old key retained for owner
rollback, then atomically selects the new reference and retires the old key through
an explicitly scoped operator step. Removing an old signing key must not be claimed
to revoke already issued tokens. Per-project disable stops future local issuance;
active tokens must be explicitly revoked where available or have a recorded
remaining lifetime. App uninstall/global revocation is a separately scoped owner
operation with effects on all managed projects. Do not delete repositories/source.

## Changes and traceability

| Requirements | Proposed component/mechanism | Tasks | Acceptance |
|---|---|---|---|
| CRD-001 | Owner App setup guide, private profile and doctor identity/grant checks | T-002/003 | AC-001 |
| CRD-002 | Installation-authenticated creation canary, automatic inclusion reconciliation and bound registry | T-002/005 | AC-002 |
| CRD-003 | Token issuer with explicit repository_ids/permissions and response validation | T-004 | AC-003 |
| CRD-004 | Private key reader, sanitized transport/helper and bundle/container boundaries | T-004/006 | AC-003/004 |
| CRD-005 | Fresh credentials, bounded lifetime, revocation/rotation and recovery receipts | T-004/007 | AC-005 |
| CRD-006 | Profile-driven new integration, recorded standing policy and local-only compatibility | T-005/006 | AC-002/006 |
| CRD-007 | Project-local Git helper and later PR API path with immutable binding | T-006/007 | AC-007 |
| CRD-008 | Offline suites plus authorized two-project GitHub/private runtime acceptance | T-008/009 | AC-002/005/008 |

Expected code areas: `scripts/gptclawctl.py`, `project_repositories.py`, a new
broker/credential helper, `private_apps.py` provider inventory and focused tests;
operator runbook and isolated Python requirements/setup only if needed. No
secret/authentication files are bundled. The planning-only bootstrap skill remains
unchanged; a combined creation skill can be separately selected after the CLI path
is accepted. Do not expand into general runtime secret management or CI generation.

## Verification, rollout and open decisions

Offline fixtures use synthetic identities/tokens and task-owned signing fixtures
never logged or committed. Cover omitted repository restriction, excess grants,
installation-wide fallback, cross-project requests, auth redaction, revoked/expired
tokens, concurrent acquisition, partial Git/config/profile publication, atomic
key switch and ambiguous API/Git writes. Test normal Git via a private fixture
transport as well as the helper protocol; do not rely only on mocked helper output.
Test source/installed bundle parity, manual PAT/local-only compatibility, dirty
worktrees and unchanged unrelated services.

After implementation authorization, the project owner separately approves exact App settings,
bootstrap selection/private-key handling and retained live target names. The first
canary must prove personal-account App creation and automatic selected-installation
inclusion without manual reassignment. Then two successive projects prove normal
fetch/branch push, later PR creation, credential reacquisition, denial for another
private repo, key rotation/revocation and private runtime checks. Record exact
revisions/grants/expiry/CI and owner observations without secret material.

Rollout is an explicit owner profile activation after readiness; normal new becomes
remote-enabled only then. Rollback deactivates that profile and returns creation
to local-only, removes only the owned helper enrollment where safely reviewed and
preserves repositories/source/remotes/history/bindings. Existing issued tokens may
remain valid until revoked/expired; rollback does not claim GitHub revocation.
No compute replacement or production promotion is needed.

The project owner's selected standing branch policy is known. App name/grant/installation and
bootstrap repository approval, exact creation capability/default-branch behavior,
and signing dependency remain substantive implementation-readiness decisions.
The proposed bootstrap selection is the retained SPEC-022 verification repo, not
the platform repository. Drafting can complete now; no live mutation or automatic
permission expansion is authorized by this planning request.
