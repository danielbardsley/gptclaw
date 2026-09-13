# RES-001 implementation record

- **Status:** Accepted; retention-expiry follow-up recorded
- **Updated:** 2026-09-13
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
- The prerequisite and feature were deployed on 2026-09-12 through the protected
  GitHub/HCP pipeline. No manual snapshot creation/deletion was performed.

The implementation in [PR #4](https://github.com/danielbardsley/gptclaw/pull/4)
was merged at `ca4305966500e9824ae8f6305594f10d046ce515` after prerequisite
deployment, credential cleanup, and a no-change OIDC plan.

## Deployment and acceptance history

[ACCEPTANCE-002](./acceptance.md) closes the pending checks described below:
natural snapshot `snap-01b934e8e05f1018b` completed, encryption/privacy verified,
and post-snapshot plan #47 attempt 2 reported no changes. The historical
deployment checkpoint below is retained for traceability.

See the [sanitized deployment record](./deployment-attempt-2026-09-12.md) for
all run links, the owner's explicit one-time credential and tag-update exceptions,
and live safety evidence. Static HCP AWS credentials are removed and normal
phase-specific OIDC is verified, including the feature apply identity.

- [Feature apply #46](https://github.com/danielbardsley/gptclaw/actions/runs/34719893951)
  / [HCP apply](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-BgbfbBhsgrse2ZQf):
  four resources added, twelve tag-only updates, none destroyed.
- DLM `policy-0915f5294ae69132a` is enabled: every 24 hours at 03:00 UTC,
  retaining seven snapshots. Its selector matches only project volume
  `vol-0f53005235c1e39f3`; encryption, attachment, protection, SSH and SSM are
  preserved. Both scoped DLM inline policies are attached.
- [Same-revision plan #47](https://github.com/danielbardsley/gptclaw/actions/runs/34720055891)
  / [HCP plan](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-LMVVu3bSND81oCsd)
  reports no changes after deployment.
- No policy-attributed snapshots existed at the immediate post-deployment check.
  AC-004 remains pending until a naturally scheduled snapshot completes and its
  source, policy attribution, metadata, encryption/key and private permissions
  are verified. Repeat the no-change pipeline plan after that snapshot exists.
- Retention expiry is not yet observed. Daniel owns a follow-up on **2026-09-21**,
  after at least eight daily runs, to inspect policy-attributed count/expiry.
- A bounded acceptance follow-up is scheduled in the current local task for
  00:15 America/New_York daily, beginning after the first scheduled window;
  stop it when acceptance passes. This adds no AWS monitoring or notification
  resources. The computer and desktop app must remain running for local checks.

RES-001 is now accepted as recorded in ACCEPTANCE-002. Retention expiry remains
Daniel's dated follow-up; no restore has been performed, which remains RES-002.
