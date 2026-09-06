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
| D-001 | Use a custom DLM volume snapshot policy. | Directly implements tagged scheduling and count retention. |
| D-002 | One daily schedule at 03:00 UTC, seven retained snapshots. | Matches the approved specification's starting settings. |
| D-003 | Use a scheduled Python Lambda for policy/target/freshness inspection. | Detects missing backups independently of host availability and service failure events. |
| D-004 | CloudWatch alarms publish to one SNS email topic. | Provides state transitions and an independent missing-monitor alarm without a status database. |
| D-005 | Keep runtime IAM separate from host and deployment identities. | Neither the host nor monitor can create or delete backups. |
| D-006 | Use isolated fixture telemetry for live alarm tests. | Exercises notifications without disrupting live backup protection. |
| D-007 | Use the existing controlled identity-maintenance procedure as a separately reviewed prerequisite. | Normal HCP identities cannot expand their own permissions. |

## 3. Architecture

~~~text
Reviewed code -> GitHub Actions -> HCP Terraform -> AWS resources
                                                    |
                        +---------------------------+-------------------+
                        |                           |                   |
                  DLM policy                  EventBridge rule      CloudWatch
                        |                     every 5 minutes       DLM failure
                  DLM service role                  |                metrics
                        |                     Inspector Lambda          |
              tagged project volume           read-only AWS            |
                        |                           |                   |
                 private snapshots         logs + custom metrics       |
                 automatic retention               |                   |
                                             CloudWatch alarms --------+
                                                    |
                                                SNS topic
                                                    |
                                           confirmed owner email
~~~

There is no dependency on EC2 uptime, an SSH session, a VPC-connected Lambda,
or a public application endpoint. All new infrastructure is Terraform-managed;
individual DLM-created snapshots remain service-managed and outside Terraform
state. No snapshot-import loop or infrastructure provisioner is introduced.

## 4. Resource and file ownership

| File under `infra/dev-host` | Planned responsibility |
|---|---|
| `storage.tf` | Add only the dedicated selection tag to the project volume. |
| `backups.tf` | DLM policy, schedule, service role, and lifecycle permissions. |
| `backup-monitoring.tf` | Lambda, log group, EventBridge rule/target, invocation permission, metrics alarms, SNS and subscription. |
| `backup-monitor/handler.py` | Read adapters, pure state evaluator, sanitized logging, metric publication. |
| `backup-monitor/test_handler.py` | Standard-library unit tests with fake AWS clients and time. |
| `backup-monitor/fixtures/` | Non-secret synthetic observations for isolated acceptance checks. |
| `backup-monitoring-test.tf` | Optional isolated test function, schedule, and alarm instances, disabled by default. |
| `tests/backups.tftest.hcl` | Terraform mock-provider assertions and invalid-input tests. |
| `variables.tf`, `outputs.tf` | Validated settings and non-secret discovery outputs. |
| `hcp_identity.tf` | Narrow additional plan/apply permissions, delivered through the prerequisite stage. |

Extend the existing quality job with Python unit tests. Keep all deployed
function sources inside the HCP configuration archive. Use an exactly pinned
HashiCorp archive provider and committed lockfile to build a ZIP from a staging
directory containing only runtime source; exclude tests and generated files.
The archive is generated independently during each remote run, with
`source_code_hash` controlling updates. Verify stable archive contents/hash and
that `.terraformignore` includes source and excludes generated artifacts.

Use `python3.13`, 128 MiB memory, 60-second timeout, reserved concurrency 1,
and a Terraform-managed log group with 14-day retention. The function uses the
runtime's Boto3 SDK; record its observed version at acceptance and test adapters
against the runtime API surface. No pip install is needed during HCP execution.
Python 3.13 is a supported Lambda runtime. [AWS Python runtime documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

## 5. Inputs and policy contract

| Input | Default / validation |
|---|---|
| `backup_policy_enabled` | `true`; disabling requires reviewed operational intent. |
| `backup_interval_hours` | `24`; supported slice permits only 12 or 24. |
| `backup_start_time_utc` | `03:00`; validate actual 00:00-23:59 range. |
| `backup_retention_count` | `7`; integer 1-1000. |
| `backup_freshness_hours` | `26`; positive number, at least interval plus two hours. |
| `backup_initial_enablement_utc` | Required fixed RFC3339 UTC timestamp for initial rollout. |
| `backup_notification_email` | Required nonempty email; sensitive Terraform input. |
| `backup_acceptance_test_enabled` | `false`; explicitly enabled only for bounded synthetic testing. |

The initial enablement timestamp must be at or before the enablement apply and
within the preceding hour. It grants at most 26 hours of initial no-snapshot
grace. Never derive it from `timestamp()`, deployments, monitor restarts, or
policy state changes. Ordinary redeployment and re-enablement preserve it.
Future timestamps are configuration errors; deliberate replacement of a policy
does not silently restart grace.

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

DLM may start within an hour of the scheduled time; snapshot completion is
asynchronous. Removing target tags stops management of existing snapshots.
Count retention allows 1-1000 snapshots. These behaviors drive the grace and
rollback procedures. [AWS custom snapshot policy documentation](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-ami-policy.html)

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
| HCP plan | Existing reads plus DLM get/list/tags, Lambda configuration/code metadata/policy reads, EventBridge rule/target reads, CloudWatch alarm reads, SNS topic/subscription reads, and named new IAM role/policy reads. No mutations or snapshot contents. |
| HCP apply | Plan reads plus lifecycle CRUD/tagging for named backup resources and inline policies on the two new runtime roles. Pass only DLM role to `dlm.amazonaws.com` and inspector role to `lambda.amazonaws.com`. |
| DLM role | Trust only DLM; describe necessary EC2 metadata, create snapshots of the exact Terraform project-volume ARN, tag owned snapshots, and delete snapshots belonging to this policy. |
| Inspector role | Trust only Lambda; describe volume/snapshot metadata, get the exact policy, publish only `GptClaw/Backups` metrics, and write its own log streams. No SNS publish or storage/IAM mutation. |
| Test inspector role | No EC2/DLM reads; publish only `GptClaw/BackupsTest` and write test logs. |

The apply role remains unable to mutate itself, the plan role, or OIDC provider.
Add no runtime permissions to the host role. Use source-account/source-ARN
conditions for service resource policies where supported. SNS permits publish
only from the named CloudWatch alarms in this account; EventBridge may invoke
only the intended function through its rule-scoped Lambda permission.

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
EC2 describe APIs, CloudWatch `PutMetricData`, and some list/create APIs require
`Resource="*"`; constrain by Region, metric namespace, request tags, or resource
naming where supported. Do not attach the broad AWS-managed DLM policy.
Confirm the deployed EBS KMS key read-only; do not add speculative KMS decrypt,
key-admin, or grant permissions. If its key policy requires additional service
access, review the exact key-scoped addition before proceeding.
[AWS DLM service roles](https://docs.aws.amazon.com/ebs/latest/userguide/service-role.html),
[AWS DLM authorization reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_dlm.html)

## 7. Inspector and telemetry

### 7.1 Observation algorithm

Every five minutes, obtain UTC observation time from the function clock, not
the event payload. Inputs such as volume ID, policy ID, selector, threshold,
and initial enablement come only from Terraform configuration.

1. Read the exact policy and verify enabled state, expected target type/tag,
   schedule, and retention. Missing, disabled, error, or unexpected settings
   produce policy-unhealthy state.
2. Paginate volumes matching the selector. Require exactly the configured
   volume, with encryption enabled. Missing or extra targets are unhealthy.
3. Paginate own-account snapshots filtered by source volume and DLM policy tag.
   Recheck attribution in code; select only `completed` snapshots. Choose the
   greatest `StartTime`; ties break deterministically by snapshot ID.
4. Compute age from `StartTime`, not completion time. Reject future timestamps
   and invalid data. No snapshot is `no_recovery_point`, even during grace.
   A valid age greater than the threshold is stale.
5. Publish one current metric set only after all observations are evaluated.
   On API/parser failure, publish inspection-failed and unhealthy indicators;
   if metric publication fails, fail the invocation and leave no heartbeat.

Use bounded SDK retries/timeouts within the Lambda deadline. Never log complete
API responses or exception payloads. Log a single structured, allowlisted
summary: observation time, environment, Region, policy/volume IDs, state/reason
codes, newest snapshot ID/time/age, target count, retention, and invocation ID.
A status read must show the observation timestamp; old logs are not current
health. There is no persistent status database.

### 7.2 Metrics and alarms

Custom namespace `GptClaw/Backups`; dimensions `PolicyId` and `VolumeId`.
Emit each expected gauge on every successful publication, including zeros.
Initial grace suppresses only no-recovery-point alerting, not policy or
inspection failures. Logs continue to say `no_recovery_point`.

| Metric / source | Alarm |
|---|---|
| `PolicyUnhealthy` | Maximum > 0, 300 seconds, 1 of 1. |
| `RecoveryPointUnhealthy` | Maximum > 0, 300 seconds, 1 of 1; stale or missing beyond grace. |
| `InspectionFailed` | Maximum > 0, 300 seconds, 1 of 1. |
| `Heartbeat` | Metric math `FILL(m, 0)`, Minimum < 1, 300 seconds, 3 of 3. |
| `SnapshotAgeSeconds` | Diagnostic gauge only; omit when no valid completed snapshot exists. |
| DLM `SnapshotsCreateFailed` and `SnapshotsDeleteFailed` | `AWS/EBS`, dimension `DLMPolicyId`, Sum > 0, 300 seconds, 1 of 1; sparse missing data not breaching. |
| Lambda Errors/Throttles and EventBridge FailedInvocations | Named-function/rule alarms, Sum > 0, 300 seconds, 1 of 1; missing not breaching. |

Use missing-as-breaching on the three status alarms; use the explicit
zero-filled heartbeat expression to avoid treating an older datapoint as a
current heartbeat. Verify delayed metric arrival does not create persistent
false alarms. Native DLM metrics describe failed lifecycle actions; the
inspector independently determines whether a completed recovery point exists.
[AWS DLM metrics](https://docs.aws.amazon.com/ebs/latest/userguide/monitor-dlm-cw-metrics.html),
[CloudWatch missing-data behavior](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarms-and-missing-data.html)

Operational targets under normal AWS availability: observations within five
minutes; status alarms/SNS publication within ten minutes of an observable
fault; monitor silence within twenty minutes; email received within fifteen
minutes of alarm transition during acceptance. These are measurable acceptance
bounds, not AWS or email guarantees. Native failures are measured from metric
arrival, whose upstream delay is outside these bounds. Record any violation
and correct configuration before acceptance.

Send ALARM and OK transitions to SNS. Alarm descriptions contain environment,
Region, policy, volume, category, and the runbook/console diagnostic route;
native messages provide transition time. No periodic reminder service is
introduced: persistent alarms remain visible and notify again only after
recovery and recurrence. An OK transition for a sparse failure metric means
the recent failure signal cleared, not that backups are fresh. Consult the
freshness and policy alarms for recovery.

Create the SNS email subscription in Terraform; the owner confirms the email.
The address is sensitive input but will exist in restricted Terraform state
and SNS, since no write-only subscription endpoint exists. Never output it or
include it in committed examples/evidence. Inspect confirmation status without
printing the endpoint. Common failure of CloudWatch/SNS/email remains a shared
regional dependency; this feature does not claim independent disaster alerting.

## 8. Verification and safe synthetic tests

Pure evaluator tests inject observations/time and cover threshold equality,
initial grace expiry, no grace reset, pagination, malformed/future timestamps,
wrong ownership/policy/volume, completed versus pending snapshots, disabled or
deleted policy, unexpected tag matches, read denial, and metric-write failure.
Terraform tests inspect IAM and negative scope, validation, encryption/privacy
settings, alarm dimensions/actions, invocation permissions, and source packaging.

The optional acceptance harness deploys the same evaluator/publisher code with
a fixture adapter in a separate function and separate metric namespace, roles,
schedule, and alarm dimensions. The live handler cannot select fixture mode
from an event. Test alarms share the real SNS destination and carry a clear
TEST label and run ID. No test role can write live metrics or read project data.

Drive a committed, bounded fixture timeline from a fixed test start timestamp:
healthy, stale, recovered, inspection failure, recovered, withheld heartbeat,
then recovered. Each phase lasts at least twenty minutes to exercise the actual
alarm periods; the whole timeline is at most three hours. At expiry resume
healthy test telemetry until harness removal so silence does not cause
unending test alarms. Test DLM failure-alarm wiring with a parallel test metric
of the same shape; never publish synthetic data into an AWS namespace.

Configure this harness only through a protected Terraform change, observe via
read-only APIs, record notification arrival and recovery, then remove it through
the pipeline. A synthetic event does not prove AWS will emit every real failure;
live scheduled snapshot completion and real DLM metric dimensions are separate
evidence. Service events are best effort, so event-only monitoring is not used.
[AWS DLM event delivery](https://docs.aws.amazon.com/ebs/latest/userguide/monitor-cloudwatch-events.html)

## 9. Deployment, rollback, and operations

1. Complete the reviewed identity-maintenance prerequisite and restore OIDC.
2. Merge implementation only after its checks and design review. Supply the
   email and fixed initial timestamp in HCP; inspect a protected remote plan.
3. Apply through the existing exact-confirmation workflow. Confirm no compute,
   attachment, deletion-protection, or inbound-access regression.
4. Confirm email delivery, exact target matching, all runtime permissions, and
   telemetry. Observe at least one naturally scheduled completed snapshot.
5. Run isolated acceptance checks; remove their resources. Repeat a plan with
   the same revision/variables and record no unexpected changes.

Expose policy ID/ARN, source volume ID, schedule/retention/freshness settings,
monitor/log-group names, alarm names, and SNS topic ARN. Provide
`runbooks/inspect-backups.md` with read-only DLM/EC2/CloudWatch/SNS discovery and
safe redaction. Update the recovery runbook's snapshot-selection and
pipeline-only restore handoff, preserving historical SPEC-001 evidence.

Rollback disables/repairs the policy through Terraform and leaves monitoring
active to report lost protection. Preserve existing snapshots and the live
volume. A deleted DLM policy stops its creation/deletion management and leaves
snapshots behind; inventory before deletion. Policy replacement changes
attribution and does not automatically adopt prior snapshots. Do not import
those snapshots merely to destroy them. Any later cleanup needs its own reviewed
target inventory and pipeline procedure. [AWS policy deletion semantics](https://docs.aws.amazon.com/service-authorization/latest/reference/list_dlm.html)

Do not promise live retention expiry on deployment day. Record a follow-up date
after at least eight daily runs and compare policy-attributed snapshots and
delete metrics. If failures prevent expiry, retain the limitation and follow-up
owner. Cost inspection covers incremental snapshot storage, Lambda invocations,
CloudWatch metrics/alarms/logs, SNS, and temporary test resources. No fixed price
is assumed; retaining seven recovery points does not cap changed bytes.

## 10. Traceability

| Specification | Design sections | Acceptance |
|---|---|---|
| BAK-001 | 3, 4, 6, 9 | AC-001, AC-002, AC-009 |
| BAK-002 | 5, 6, 7.1 | AC-001, AC-003 |
| BAK-003 | 5, 9 | AC-004, AC-005 |
| BAK-004 | 5, 6.2, 7.1, 9 | AC-001, AC-004 |
| BAK-005 | 6 | AC-001, AC-002 |
| BAK-006 | 7, 8 | AC-006, AC-007, AC-008 |
| BAK-007 | 7.1, 9 | AC-004, AC-010 |
| Safety and rollback | 6, 8, 9 | AC-002, AC-009, AC-010 |

Before coding, review the explicit identity-maintenance exception and the
monitoring/notification decisions. Implementation must verify provider schema,
service IAM conditions, and live timing with the pinned dependency versions;
any change to scope or safety boundaries returns to document review.
