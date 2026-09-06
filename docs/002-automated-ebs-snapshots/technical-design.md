# TDD-002: Automated EBS Snapshots

- **Status:** Draft for review
- **Owner:** Daniel
- **Source:** [SPEC-002](./spec.md), approved for planning
- **Implementation tasks:** [TASKS-002](./tasks.md)
- **Repository:** `danielbardsley/gptclaw`
- **Last updated:** 2026-09-06

## 1. Purpose and baseline

Implement RES-001 in the existing `infra/dev-host` root module. The current
project EBS volume is separately managed, encrypted, and protected with
`prevent_destroy`. Its ID comes from Terraform, not historical acceptance
evidence. No host bootstrap, instance, attachment, filesystem, or network change
is required. Review plans for incidental replacement caused by unrelated AMI
or bootstrap drift and stop if one appears.

This document and the task list remain on the feature branch for review.
They do not authorize deployment. The existing workflow permits remote plans
and applies only after a reviewed merge to current `main`.

## 2. Decisions

| ID | Decision | Reason |
|---|---|---|
| D-001 | Use a custom DLM volume snapshot policy. | Implements tagged scheduling and count retention. |
| D-002 | One daily schedule at 03:00 UTC, seven retained snapshots. | Matches the specification's starting settings. |
| D-003 | Rely on DLM to execute the configured policy. | No custom freshness checker or scheduled inspection service is needed. |
| D-004 | Native DLM failure alarms and policy-error events publish to SNS email. | Retains failure visibility through AWS-managed services. |
| D-005 | Use a dedicated DLM role, separate from host and deployment identities. | Snapshot lifecycle permissions stay with DLM. |
| D-006 | Test delivery with a temporary Terraform-managed test alarm. | Exercises the alarm/SNS path without disrupting backups. |
| D-007 | Use the existing controlled identity-maintenance procedure as a separately reviewed prerequisite. | Normal HCP identities cannot expand their own permissions. |

## 3. Architecture

~~~text
Reviewed code -> GitHub Actions -> HCP Terraform -> AWS resources
                                                    |
                          +-------------------------+----------------+
                          |                         |                |
                     DLM policy                DLM failure      DLM policy
                          |                      metrics        error events
                    DLM service role                |                |
                          |                    CloudWatch       EventBridge
                tagged project volume             alarms        event rule
                          |                         |                |
                   private snapshots                +-------+--------+
                   automatic retention                      |
                                                        SNS topic
                                                            |
                                                   confirmed owner email
~~~

There is no dependency on EC2 uptime or an SSH session. DLM owns scheduling and
retention; the notification path consumes its native failure signals. No
scheduled polling, application runtime, custom metrics, or status database is
introduced. Individual DLM-created snapshots remain service-managed and outside
Terraform state.

## 4. Resource and file ownership

| File under `infra/dev-host` | Planned responsibility |
|---|---|
| `storage.tf` | Add only the dedicated selection tag to the project volume. |
| `backups.tf` | DLM policy, schedule, service role, and lifecycle permissions. |
| `backup-notifications.tf` | DLM failure alarms, policy-error event rule/target, SNS topic/subscription, and optional test alarm. |
| `tests/backups.tftest.hcl` | Terraform mock-provider assertions and invalid-input tests. |
| `variables.tf`, `outputs.tf` | Validated settings and non-secret discovery outputs. |
| `hcp_identity.tf` | Narrow additional plan/apply permissions, delivered through the prerequisite stage. |

Use the existing Terraform/AWS provider and credential-free quality job.
There are no runtime sources, language dependencies, ZIP packaging, or archive
provider additions.

## 5. Inputs and policy contract

| Input | Default / validation |
|---|---|
| `backup_policy_enabled` | `true`; disabling requires reviewed operational intent. |
| `backup_interval_hours` | `24`; supported slice permits only 12 or 24. |
| `backup_start_time_utc` | `03:00`; validate actual 00:00-23:59 range. |
| `backup_retention_count` | `7`; integer 1-1000. |
| `backup_notification_email` | Required nonempty email; sensitive Terraform input. |
| `backup_notification_test_enabled` | `false`; enables only a temporary TEST-labeled alarm. |

Use the single volume tag `GptClawBackup = development-projects` (derive the
environment component from the existing variable). Do not reuse common
`Project` or `DeploymentRevision` tags as selectors. Configure
`EBS_SNAPSHOT_MANAGEMENT`, `resource_types = ["VOLUME"]`, one schedule named
`projects-daily`, `interval_unit = "HOURS"`, and count-based retention.

Set `copy_tags = false`. Add an explicit snapshot allowlist: `Project`,
`Environment`, `Repository`, `BackupSet`, and `RetentionClass=daily`.
Do not put the volume selection tag on snapshots. DLM's system policy/schedule
tags provide attribution. Do not configure sharing, archive, fast restore,
cross-Region copy, or pre/post scripts.

DLM may start within an hour of the scheduled time; completion is asynchronous.
Removing target tags stops management of existing snapshots. Count retention
allows 1-1000 snapshots. Account for these behaviors during deployment and
rollback. [AWS custom snapshot policy documentation](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-ami-policy.html)

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

| Identity | Required scope |
|---|---|
| HCP plan | Existing reads plus DLM get/list/tags, EventBridge rule/target reads, CloudWatch alarm reads, SNS topic/subscription reads, and the named DLM role/policy reads. No mutations or snapshot contents. |
| HCP apply | Plan reads plus lifecycle CRUD/tagging for named backup and notification resources and inline policies on the DLM role. Pass only that new role to `dlm.amazonaws.com`. |
| DLM role | Trust only DLM; describe necessary EC2 metadata, create snapshots of the exact Terraform project-volume ARN, tag owned snapshots, and delete snapshots belonging to this policy. |

The apply role remains unable to mutate itself, the plan role, or OIDC provider.
Add no runtime permissions to the host role. SNS resource policies permit
CloudWatch to publish from the named alarms in this account and EventBridge to
publish policy-error notifications. Use service-supported source conditions;
test the EventBridge-to-SNS resource policy against AWS's supported policy
shape rather than reusing CloudWatch conditions blindly. The rule itself must
match the exact account, Region, and policy ARN. No extra execution role is
needed for direct SNS delivery.

Avoid a Terraform dependency cycle: create the DLM role and base create/read
policy first, then the DLM policy referencing the role. Attach a separate
snapshot-management inline policy referencing the resulting DLM policy ID,
with `ec2:ResourceTag/aws:dlm:lifecycle-policy-id` equal to that ID on deletion
and post-creation tagging. Constrain create-time tagging to `CreateSnapshot`;
test the service's actual tag-on-create/post-create path. Initial deployment
must finish all permissions before the first schedule; otherwise fail
acceptance and repair through the pipeline. Never solve tagging denial by
allowing mutation of arbitrary snapshots.

Document each action and its supported resource/condition keys during coding.
EC2 describe APIs and some list/create APIs require `Resource="*"`; constrain
by Region, request tags, or naming where supported. Do not attach the broad
AWS-managed DLM policy. Confirm the deployed EBS KMS key read-only; do not add
speculative KMS decrypt, key-admin, or grant permissions. If its key policy
requires additional service access, review the exact key-scoped addition.
[AWS DLM service roles](https://docs.aws.amazon.com/ebs/latest/userguide/service-role.html),
[AWS DLM authorization reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_dlm.html)

## 7. Native failure notifications

### 7.1 Snapshot failures

Create two CloudWatch alarms in namespace `AWS/EBS`, dimension
`DLMPolicyId=<policy ID>`: `SnapshotsCreateFailed` and
`SnapshotsDeleteFailed`. Use Sum > 0 over 300 seconds, one evaluation period,
one datapoint to alarm, and missing data treated as not breaching. These are
sparse failure metrics; absence of datapoints must not trigger an alert.
[AWS DLM metrics](https://docs.aws.amazon.com/ebs/latest/userguide/monitor-dlm-cw-metrics.html)

Send ALARM and OK transitions to the SNS topic. A persistent alarm notifies
again only after clearing and recurring; there is no reminder service. OK means
the recent failure signal cleared, not that a new backup completed. Alarm
descriptions include environment, Region, policy, volume, category, and a
runbook/console diagnostic route; native messages include transition time.

### 7.2 Policy errors

Use an EventBridge event-pattern rule, with no schedule expression, matching
`source=aws.dlm`, `detail-type=DLM Policy State Change`, `detail.state=ERROR`,
the approved account/Region, and the exact policy ARN in `resources`. Route
directly to the same SNS topic. Use an input transformer with allowlisted event
ID/time/state and Terraform-supplied environment, policy, volume, and diagnostic
link. Do not forward the whole event or arbitrary error text.

These events report policy errors on a best-effort basis. They do not provide
independent detection of a disabled policy, removed target tag, or missing
snapshot. This design relies on DLM scheduling; manual inspection is available
when needed. [AWS DLM event delivery](https://docs.aws.amazon.com/ebs/latest/userguide/monitor-cloudwatch-events.html)

### 7.3 Subscription and timing

Create the SNS email subscription in Terraform; the owner confirms the email.
The address is sensitive input but will exist in restricted Terraform state
and SNS, since no write-only subscription endpoint exists. Never output it or
include it in committed examples/evidence. Inspect confirmation without
printing the endpoint.

Under normal AWS availability, target alarm/SNS publication within ten minutes
of a failure metric becoming available and email receipt within fifteen minutes
of an alarm transition during acceptance. Record actual timings. These are
acceptance expectations, not guarantees of upstream DLM signal or email
delivery. The policy-error path depends on event arrival and AWS delivery
retries. No custom service is introduced to supervise this notification path.

## 8. Verification

Terraform tests cover input validation, selection, IAM positive/negative scope,
encryption/privacy, failure metric names/dimensions, sparse missing-data handling,
alarm actions, event filtering, and SNS permissions. Verify matching policy-error
fixtures and nonmatching policy/account/Region/state fixtures with EventBridge's
read-only event-pattern test API. Keep fixtures sanitized.

For end-to-end alarm/SNS delivery, enable a temporary TEST-labeled CloudWatch
alarm through Terraform. It references a unique unused metric in
`GptClaw/NotificationTest`, with a 60-second period, one evaluation period,
and missing data treated as breaching. It therefore enters ALARM without a
metric publisher or a real backup failure. Use the same SNS topic and service
policy construction as the DLM alarms. No custom metric is published.

Confirm receipt, record the transition/arrival times, then remove the test alarm
through the pipeline by restoring `backup_notification_test_enabled=false`.
Its evidence proves the alarm/SNS path, not real DLM failure emission.
Event-pattern matching and deployed target/policy inspection are separate
evidence for the EventBridge path. Do not break live IAM, disable protection,
delete backups, or mutate live alarm state to produce a test failure.

## 9. Deployment, rollback, and operations

1. Complete the reviewed identity-maintenance prerequisite and restore OIDC.
2. Merge implementation after checks and design review. Supply the email in
   HCP and inspect a protected remote plan.
3. Apply through the existing exact-confirmation workflow. Confirm no compute,
   attachment, deletion-protection, or inbound-access regression.
4. Confirm subscription, exact target matching, all DLM permissions, and native
   alert configuration. Observe one naturally scheduled completed snapshot.
5. Test notifications and remove the test alarm. Repeat a plan with the same
   revision/variables and record no unexpected changes.

Expose policy ID/ARN, source volume ID, schedule/retention settings, alarm names,
event-rule name, and SNS topic ARN. Provide `runbooks/inspect-backups.md` with
read-only DLM/EC2/CloudWatch/SNS discovery and safe redaction. An operator can
inspect the latest completed snapshot's timestamp and age; no scheduled process
performs this inspection. Update recovery guidance for snapshot selection and
pipeline-only restore handoff, preserving historical SPEC-001 evidence.

Rollback disables/repairs the policy through Terraform and preserves existing
snapshots and the live volume. Record deliberate disablement explicitly; native
failure alerts are not a check for disabled protection. A deleted DLM policy
stops creation/deletion management and leaves snapshots behind; inventory before
deletion. Replacement changes attribution and does not automatically adopt old
snapshots. Any later cleanup needs a reviewed inventory and pipeline procedure.
[AWS policy deletion semantics](https://docs.aws.amazon.com/service-authorization/latest/reference/list_dlm.html)

Record observed retention expiry or a dated follow-up after at least eight daily
runs, using policy-attributed inventory and delete metrics. If failures prevent
expiry, retain the limitation and follow-up owner. Cost inspection covers
incremental snapshot storage, CloudWatch alarms, event delivery, SNS, and the
temporary test alarm. Seven recovery points does not cap changed bytes or cost.

## 10. Traceability

| Specification | Design sections | Acceptance |
|---|---|---|
| BAK-001 | 3, 4, 6, 9 | AC-001, AC-002, AC-009 |
| BAK-002 | 5, 6, 9 | AC-001, AC-003 |
| BAK-003 | 5, 9 | AC-004, AC-005 |
| BAK-004 | 5, 6.2, 9 | AC-001, AC-004 |
| BAK-005 | 6 | AC-001, AC-002 |
| BAK-006 | 7, 8 | AC-006, AC-007 |
| BAK-007 | 9 | AC-004, AC-010 |
| Safety and rollback | 6, 8, 9 | AC-002, AC-009, AC-010 |

Before coding, review the explicit identity-maintenance exception and native
notification decisions. Verify provider schema and service IAM conditions with
the pinned versions; changes to scope or safety boundaries require review.
