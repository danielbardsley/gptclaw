# TDD-022: New GitHub repository automation

- **Status:** Implemented on review branch; live verification pending
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-022](spec.md) · **Tasks:** [TASKS-022](tasks.md)

## Approach and boundaries

Extend the existing Python `scripts/gptclawctl.py` interface with an opt-in
repository operation group. Proposed verbs are `repo plan`, `repo apply`,
`repo resume` and `repo status`; final arguments and JSON schemas belong to the
implementation review. Existing `new` stays local-only. Prefer an explicit
new destination and selected catalogue release over publishing an arbitrary
existing working tree. Do not import existing projects in this slice.

Use a repository-owned adapter for authenticated HTTPS GitHub REST requests with
bounded timeouts, pagination and retries of observation-only requests. Never
blindly retry resource creation. Pin the supported API version after verifying
endpoint compatibility during implementation. No host package installation or
assumed `gh` dependency is required. Git and the existing Python/provider
packaging remain the local execution baseline.

Credential acquisition is an explicit private fine-grained PAT file supplied
by the operator, with a creation-only phase before repository-specific grants. Do not infer authority from global Git/CLI sessions. Review
endpoint-to-permission requirements for repository creation, contents, PRs,
administration and optional environments; document precisely which identity can
create a repository and then configure that new ID. A repository-scoped Git
credential alone cannot perform this administrative workflow. PRJ-005 supplies
future ongoing-access automation, not implicit provisioning authority.

## State and data flow

1. Validate request, target account, destination and exact catalogue selection.
   Resolve reviewed content and settings into a canonical versioned plan; report
   digest and remote capability/name observations with their time of observation.
   Readiness is provisional until apply rechecks it.
2. Apply revalidates the unchanged plan, actor and collision state, then locks the
   local operation. Generate into task-owned staging without running source.
   Use existing catalogue validators and preserve substitutions/provenance.
3. Create an empty private repository and journal its immutable ID immediately.
   Establish a minimal README commit on `main`, set default branch and install
   protection. This one-time bootstrap exception is recorded; app code reaches
   main only through the initial PR. Verify settings before further publication.
4. Publish the locally computed starter blobs/tree/commit through the GitHub
   Git-data API, verify exact SHAs and exclusively create a deterministic operation-owned
   `codex/` branch, create selected environments and inspect reference metadata
   only when authorized. Open the initial PR and read back final state. Bound
   Git authentication must avoid credentials in argv, remotes and persistent
   config; operator transport implementation must be reviewed before use.
5. Publish local generated source without overwriting a destination. Record the
   remote and sanitized receipt, PR URL and pending Git credential handoff.
   Runtime startup remains a separate existing lifecycle request.

Keep operation journals outside tracked app content in a user-private directory;
journals use schema version 1 at `private_apps.STORE/repositories/<operation ID>/receipt.json`. Store only target
IDs, hashes, step states and non-secret metadata. App source records template
provenance; operational receipts do not expand manifest v1. Use safe writes and
per-target locks. Bound request bodies/output and redact adapter errors rather
than echoing authentication headers or arbitrary GitHub response bodies.

An interrupted create with no recorded response is ambiguous. Stop and present
candidate metadata for operator reconciliation; never adopt by name alone. A
journaled repository is resumed only after ID/owner/visibility match. Validate
expected commit IDs and operation ownership before branch/PR writes; concurrent
remote edits stop for review. Rate limits/denials preserve the receipt and
resources. Resume skips verified complete steps and repairs only owned missing
steps; drift in protection requires explicit reconciliation, never weakening.

## Components and traceability

| Requirements | Proposed mechanism/components | Tasks | Acceptance |
|---|---|---|---|
| REP-001 | CLI plan/schema and catalogue resolver integration | T-002a/002b/003 | AC-001 |
| REP-002 | New repository adapter, staged Git publication, initial PR | T-004 | AC-002 |
| REP-003 | Explicit policy profile and settings readback | T-004/005 | AC-003 |
| REP-004 | Optional environments and metadata-only reference reporting | T-005 | AC-004 |
| REP-005 | Reviewed credential interface, sanitized transport/output | T-002a/002b/004 | AC-005 |
| REP-006 | Versioned journal, identity reconciliation and target locks | T-003/004/006 | AC-006 |
| REP-007 | Provider packaging, runbook and regression/live checks | T-007/008/009 | AC-007 |

Expected changes include `scripts/gptclawctl.py`, a new repository adapter/module,
focused fixtures in `scripts/tests/`, installed-provider packaging where required,
and a GitHub setup runbook. Exact file boundaries follow adapter review. Do not
modify the immutable `nextjs@1.0.0` release in place; any catalogue asset changes
require a new reviewed release. Adapt repository guidance through the provisioning
layer with separate recorded provenance, leaving catalogue bytes identifiable.

## Verification and delivery

Offline tests use synthetic API responses and tokens with a fake transport. Test
request permissions, no-write planning, state reconciliation, collision/drift,
secret redaction, unsupported plans and timeouts after successful mutation. Test
Git operations in isolated fixtures with hooks disabled and no unrelated
credential inheritance. Inspect actual published file inventory for prohibited
local artifacts and validate generated manifest/provenance. Reuse existing
starter quality checks; do not execute fetched repository instructions.

Run focused tests, repository checks and diff checks, then configured PR CI.
Use a specifically authorized retained private repository for live readback,
initial PR, enforcement denial and starter/runtime validation. No auto-merge or
fixture deletion. A live check must name account, target, credential class,
revision and exact results. Separate API settings from owner acceptance.

Release the provider through its existing reviewed packaging/update path; if
host IaC changes prove necessary, propose them separately through the protected
pipeline. Roll back the provider to its previous reviewed version while retaining
app source, journals and GitHub resources. Failed setup is recovered by status
and resume; deletion, protection changes and credential revocation need their
own scoped operator action. This draft changes no host or GitHub configuration.

## Readiness decisions

Daniel approved scope/defaults and authorized implementation October 10. The
reviewed interface uses a private fine-grained PAT file and anonymous-fd Git
askpass for the bootstrap push; configuration uses a repository-specific token.
HTTP/Git redirects, global credential/config inheritance and arbitrary local
Git configuration are rejected. API version is `2026-03-10`. The seven-day expiry
limit is operator metadata checked locally; GitHub enforces actual expiry/grants.
Account-plan support and ongoing per-repository access remain live readiness
checks. The retained verification target is separately authorized. Current personal-account selection is known;
subscription capabilities and provisioning credentials are unverified. Offline
contract design can proceed independently, but no live mutations or claims of
operational readiness follow from this proposal.

The [operator runbook](../../runbooks/manage-project-repositories.md) documents
commands, grants, private-file creation, ambiguity reconciliation, retained
local generation outcomes and rollback. `repo` ships in provider 1.4.0.
