# RES-001 implementation record

- **Status:** Code implemented; deployment and live acceptance pending
- **Updated:** 2026-09-06
- **Specification:** [SPEC-002](./spec.md)
- **Tasks:** [TASKS-002](./tasks.md)

The owner authorized implementation, then removed all backup monitoring and
notifications. The final code contains only the DLM snapshot policy, dedicated
service role, source-volume selection tag, validated settings, and outputs.
The platform architecture/catalogue and operational guidance reflect that
silent DLM failures are accepted.

## Verification

- Terraform 1.16.1, locked AWS provider 6.63.0, cloudinit provider 2.4.0.
- Backend-free initialization, formatting, and validation pass.
- All 15 Terraform mocked test runs pass, including invalid settings, exact
  source-volume permissions, policy-attributed cleanup, private snapshot options,
  and unchanged host boundaries.
- Repository security/whitespace checks and relative documentation links pass.
- [Prerequisite PR #3](https://github.com/danielbardsley/gptclaw/pull/3) has passing
  [CI run 34](https://github.com/danielbardsley/gptclaw/actions/runs/34054724248).
- No live Terraform apply, snapshot creation/deletion, or host change was made.

The implementation is available in
[PR #4](https://github.com/danielbardsley/gptclaw/pull/4), stacked on the
prerequisite. The pull request's checks record CI results for its current head.

## Deployment handoff

The prerequisite must be applied using the temporary authorized HCP maintenance
session, then static session variables must be removed and normal OIDC verified.
The current task has no HCP credential/configuration tool or authorized AWS
maintenance session available. No credential values have been requested in chat.

After prerequisite deployment, merge/apply the feature through the protected
pipeline and collect actual target/encryption checks, one naturally scheduled
completed snapshot, retention evidence or dated follow-up, and a no-change
plan. These are pending, not passed acceptance criteria. No email configuration
or notification test is needed. Create the final acceptance record only after
live verification.
