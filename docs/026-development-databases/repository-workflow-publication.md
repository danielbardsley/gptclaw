# Proposed workflow publication prerequisite

- **Status:** Project-owner approved October 12; implementation and live verification in progress
- **Owner:** Project owner
- **Related:** [RUN-011 acceptance](acceptance.md), [SPEC-023](../023-repository-credential-broker/spec.md)

## Observed gap

The authorized persistent-project creation reached private repository creation and
bootstrap main publication. Starter tree publication then returned HTTP 403,
`Resource not accessible by integration`, with the existing one-repository
Contents-write/Pull-requests-write token. A control tree with the same source and
credential, omitting only `.github/workflows/quality.yml`, succeeded. No control
commit or branch was created. The original operation and source remain retained.
This isolates the workflow entry as the denied addition; creation itself succeeded.
Do not retry by recreating the repository, remove its CI claim, broaden a grant
silently, use an unrelated credential or edit the retained journal/source inventory.

SPEC-023's accepted profile explicitly excludes Workflows. The published persistent
starter includes generated CI. Those contracts currently cannot complete combined
broker provisioning together. Repository creation/publication authorization does
not silently approve a change to the accepted credential policy.

## Approved extension

The project owner explicitly approved this workflow-capable provisioning policy.
The owner completed **Workflows: read and write** in the existing private GitHub
App settings and approved its installation permission update. Preserve all current
permissions and identifiers; no key/token is requested in chat and no reinstall is
needed. Because the existing installation is All repositories, this adds root App
workflow authority across the account. That account-wide root authority must be
reviewed explicitly, even though issued project tokens remain narrowly scoped.

The implementation adds an explicit versioned opt-in profile migration, verifying
App and installation identity and exact approved grant readback before activation.
Existing profiles remain compatible and fail clearly for a workflow-containing
starter before repository creation. No automatic inference from changed GitHub
settings is allowed. Initial provisioning leases add Workflows-write only
for the one immutable App-created private repository, with bounded expiry and
revocation. Creation-only, ordinary Git, audit and PR leases keep existing scopes.

Before profile migration, update only validated registered helper paths to the
compatible immutable provider. Hash-bound journals resume an interrupted config/
binding write and refuse unknown edits. Ordinary Git permissions stay unchanged;
application runtimes are unaffected. Profile migration remains inactive until
actual workflow publication is verified, then activation is explicit.

For this acceptance run, apply the opt-in only to the two directly authorized test
projects. Resume the retained first operation using its immutable repository ID;
then create the second once preflight proves its required scope. Retain exact
starter workflow bytes, source inventory and deterministic commit checks. Ordinary
application changes must not alter workflow files using a Contents-only helper.
A later general workflow-editing interface or standing extension to other projects
requires a separate concrete design and authorization.

## Verification and rollback

Offline tests must prove legacy profiles stay valid, unapproved/extra grants fail,
changed installation grants do not silently activate, preflight precedes remote
creation, workflow leases carry one exact approved repository ID, and other roles
never acquire Workflows. Live checks must prove retained-operation recovery,
private PR/CI publication and actual checks on both applications.

Rollback disables the explicit workflow policy and new issuance, retaining project
source/repos/data and pending operation journals. The project owner removes the
App/installation Workflows grant; previously issued tokens retain their reported
lifetime. No data reset or permission replacement is part of rollback.

## Approved decision and actual outcome

The project owner directly approved the scoped policy extension and completed the
App/installation Workflows update. Exact five-grant readback, explicit inactive
schema-3 migration, first retained-operation recovery, real workflow publication,
activation and normal second creation passed. Reviewed provider 1.8.1 merged through
[PR #62](https://github.com/danielbardsley/gptclaw/pull/62), with all final-code
workflows passing. Both complete private applications passed their actual
repository CI. Ordinary Contents/Metadata helpers published application source;
cross-repository denial and target-only disable/enable recovery passed.

The bounded two-project policy remains selected for the retained applications.
The broad root App grant and its owner-controlled removal step remain explicit;
this acceptance does not authorize general workflow editing or other projects.
