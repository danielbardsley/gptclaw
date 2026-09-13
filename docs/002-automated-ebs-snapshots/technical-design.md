# TDD-002: Automated EBS Snapshots

- **Status:** Implemented and accepted; see [ACCEPTANCE-002](./acceptance.md)
- **Owner:** Daniel
- **Source:** [SPEC-002](./spec.md)
- **Implementation tasks:** [TASKS-002](./tasks.md)
- **Repository:** `danielbardsley/gptclaw`
- **Last updated:** 2026-09-13

## 1. Purpose and baseline

Implement RES-001 in the existing `infra/dev-host` root module. The project
volume is separately managed, encrypted, and protected by `prevent_destroy`.
Its ID comes from Terraform, not historical acceptance evidence. Preserve
compute, bootstrap, attachment, filesystem, keys, and networking.

The owner authorized implementation and explicitly accepts silent DLM failures.
DLM owns scheduling and retention; manual inspection provides diagnosis and
acceptance evidence. Remote plans/applies still require reviewed code on current
`main` through the protected GitHub/HCP workflow.

## 2. Decisions

| ID | Decision | Reason |
|---|---|---|
| D-001 | Custom DLM VOLUME snapshot policy. | Implements tagged scheduling and count retention. |
| D-002 | Daily at 03:00 UTC; retain seven snapshots. | Matches the specification's defaults. |
| D-003 | Rely on DLM; allow silent failures. | The owner excluded custom monitoring and failure notifications. |
| D-004 | Dedicated DLM role, separate from host/deployment roles. | Snapshot lifecycle privileges belong only to the service. |
| D-005 | Deliver deployment-role maintenance as a prerequisite. | Ordinary HCP roles cannot expand their own permissions. |

## 3. Architecture

~~~text
Reviewed code -> GitHub Actions -> HCP Terraform
                                      |
                                 DLM policy
                                      |
                                DLM service role
                                      |
                            tagged project volume
                                      |
                         encrypted private snapshots
                            automatic count retention
~~~

There is no host process, notification system, or status database. Individual
snapshots remain service-managed and outside Terraform state.

## 4. Resource and file ownership

| File | Responsibility |
|---|---|
| `infra/dev-host/storage.tf` | Add the dedicated selection tag to the existing volume. |
| `infra/dev-host/backups.tf` | DLM policy, role, and lifecycle permissions. |
| `infra/dev-host/variables.tf`, `outputs.tf` | Validated settings and non-secret discovery. |
| `infra/dev-host/hcp_identity.tf` | Narrow deployment-role permission additions. |
| `infra/dev-host/tests/backup-permissions.tftest.hcl` | Prerequisite permission boundary tests. |
| `infra/dev-host/tests/backups.tftest.hcl` | Policy configuration and validation tests. |
| `runbooks/inspect-backups.md` | Manual inspection, diagnosis, retention, rollback, and costs. |

Use the existing pinned Terraform/AWS provider and credential-free quality job.
No new runtime or packaging dependencies are needed.

## 5. Inputs and policy contract

| Input | Default / validation |
|---|---|
| `backup_policy_enabled` | `true`; disabling is a reviewed operating change. |
| `backup_interval_hours` | `24`; supported values 12 or 24. |
| `backup_start_time_utc` | `03:00`; validate 00:00-23:59. |
| `backup_retention_count` | `7`; integer 1-1000. |

Use the sole selector `GptClawBackup=development-projects`, deriving its
environment component from the existing variable. Do not select by general
project tags or deployment revision. Use `EBS_SNAPSHOT_MANAGEMENT`,
`resource_types=["VOLUME"]`, one schedule named `projects-daily`, hours-based
creation, and count-based retention.

Set `copy_tags=false` and explicitly add non-secret `Project`, `Environment`,
`Repository`, `BackupSet`, and `RetentionClass=daily` tags. Do not copy the
volume-selection tag to snapshots. DLM's system policy/schedule tags identify
ownership. No sharing, copying, archive, fast restore, or application scripts.

DLM starts within an hour of the scheduled time; completion is asynchronous.
Removing target tags stops management of existing snapshots. Count retention
supports 1-1000 snapshots. Account for these behaviors during rollout/rollback.
[AWS custom policies](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-ami-policy.html)

## 6. Identity design and prerequisite

### 6.1 Controlled deployment-policy maintenance

The existing [bootstrap runbook](../../runbooks/bootstrap-hcp-aws.md) section 3
permits a later deployment-policy update using temporary bootstrap credentials
in HCP. SPEC-001 restricts its original static-credential exception to the first
apply, so this design makes the later maintenance exception explicit for review;
it is not a standing grant or implicit authorization to use credentials now.

Use a separate first PR containing only deployment policy additions, their
tests, and the clarified maintenance runbook. Merge only when implementation is
authorized. The owner supplies an already-authorized, short-lived AWS session in
sensitive HCP environment variables, including `AWS_SESSION_TOKEN`. Its
permissions allow refresh of the existing root and update of the two named HCP
inline policies; it cannot mutate host/storage resources. The credential must
last through the protected plan and apply.

Temporarily disable HCP AWS dynamic provider authentication for these runs,
record variable names/settings to restore, and ensure shared variable sets do
not inject a competing authentication mode. Never expose values to GitHub,
the host, prompts, logs, or Terraform input/state. Inspect the remote plan and
apply only the two expected inline-policy changes; do not use `-target`.

Immediately remove all three session variables, restore
`TFC_AWS_PROVIDER_AUTH=true` and the existing phase-specific role ARNs, then
run a protected OIDC plan. Verify the apply identity on the subsequent ordinary
feature apply. Cleanup is required on failure too, with owner follow-up if the
session ends early. Do not create a new access key or temporary IAM role out of
band. Without an already-authorized session, this deployment stage is blocked;
planning and local implementation can continue.

### 6.2 Permission boundaries

| Identity | Additional scope |
|---|---|
| HCP plan | DLM policy/tag reads and the named DLM role/policy reads. |
| HCP apply | Tagged DLM policy creation/management, management of one named DLM role, and passing that role only to DLM. |
| DLM role | Read EC2 metadata, create snapshots of the exact project-volume ARN, tag new/owned snapshots, and delete only this policy's snapshots. |

The apply role remains unable to mutate itself, the plan role, or OIDC. The
host role remains unchanged. DLM trust requires the service principal, source
account, and a source policy ARN limited to the approved account/Region.

Avoid dependency cycles by creating the role/base permissions before the DLM
policy. Attach a separate lifecycle policy referencing the resulting policy ID
for deletion and post-creation tagging, conditioned on
`ec2:ResourceTag/aws:dlm:lifecycle-policy-id`. Create-time tagging is restricted
to `ec2:CreateAction=CreateSnapshot`. Complete permissions before the first
scheduled run and verify actual service tagging through snapshot evidence.
Do not resolve denial by allowing mutation of arbitrary snapshots.

EC2 describe operations require wildcard resources. New snapshot IDs require
a regional snapshot wildcard, but source-volume creation permissions use the
exact volume ARN. DLM policy creation requires a wildcard constrained by
Region/request tags; management is account/Region/tag scoped. No AWS-managed
broad DLM policy, host privileges, or speculative KMS permissions are added.
Inspect the existing encryption key read-only; review any required key-scoped
service access separately.
[AWS DLM service roles](https://docs.aws.amazon.com/ebs/latest/userguide/service-role.html),
[AWS DLM authorization](https://docs.aws.amazon.com/service-authorization/latest/reference/list_dlm.html)

## 7. Verification

Terraform tests cover defaults, allowed overrides, invalid schedule/retention,
stable exact-volume selection, private snapshot options, encryption preservation,
DLM trust, create/tag/delete permission scope, and unchanged host/deployment
boundaries. Existing repository and Terraform checks remain required.

After pipeline deployment, manually verify the actual matching volume set and
policy settings, then observe one naturally scheduled snapshot reach
`completed`. Record source volume, policy attribution, timestamp, encryption,
key relationship, and private permissions. Policy creation alone is not
acceptance. No failure injection or notification testing is required.

## 8. Deployment, rollback, and operations

1. Apply the reviewed identity prerequisite and restore OIDC.
2. Review/merge feature code and inspect a protected remote plan.
3. Apply using the exact-confirmation workflow. Stop for unexpected compute,
   attachment, deletion-protection, key, or inbound-access changes.
4. Verify target, permissions, policy, and scheduled completed snapshot.
5. Run a same-revision/variable plan and confirm no unexpected changes.

Expose policy ID/ARN, source volume ID, and schedule/retention settings.
The inspection runbook provides read-only discovery and manual latest-snapshot
inspection. Update recovery guidance to select a completed snapshot and perform
any restore-volume creation/attachment through the pipeline under RES-002.

Rollback disables or repairs the policy through Terraform while preserving
existing snapshots and the live volume. Record disablement explicitly because
there are no alerts. Policy deletion stops lifecycle management and leaves
snapshots; replacement does not adopt old snapshots. Later cleanup requires a
reviewed inventory and pipeline procedure.
[AWS policy deletion](https://docs.aws.amazon.com/service-authorization/latest/reference/list_dlm.html)

Record observed expiry or a dated follow-up after at least eight daily runs.
Inspect policy-attributed inventory and snapshot costs; seven recovery points
does not bound changed bytes or cost. This feature does not prove restoration.

## 9. Traceability

| Requirement | Design | Acceptance |
|---|---|---|
| BAK-001 | 3, 4, 6, 8 | AC-001, AC-002, AC-009 |
| BAK-002 | 5, 6, 7 | AC-001, AC-003 |
| BAK-003 | 5, 7, 8 | AC-004, AC-005 |
| BAK-004 | 5, 6, 7 | AC-001, AC-004 |
| BAK-005 | 6, 7 | AC-001, AC-002 |
| BAK-007 | 7, 8 | AC-004, AC-010 |
| Safety/rollback | 6, 8 | AC-002, AC-009, AC-010 |

BAK-006 and AC-006 through AC-008 were removed with monitoring/notifications.
Remaining identifiers are preserved for traceability.
