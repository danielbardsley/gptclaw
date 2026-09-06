# SPEC-002: Automated EBS Snapshots

- **Status:** Draft
- **Owner:** Daniel
- **Feature catalogue:** RES-001
- **Dependency:** [SPEC-001](../001-bootstrap-remote-development-host/spec.md), complete
- **Architecture:** [Platform architecture](../platform/architecture.md)
- **Last updated:** 2026-09-06

## 1. Summary

Protect the persistent project volume mounted at `/srv/forge` with automated,
encrypted EBS snapshots, bounded retention, and visible failures. Manage the
policy, permissions, and monitoring through GitHub Actions and HCP Terraform.

This covers RES-001 and the missing automated-backup capability recorded in
[ACCEPTANCE-001](../001-bootstrap-remote-development-host/acceptance.md).
A completed snapshot is a candidate recovery point; proving a restore belongs
to RES-002. This draft does not authorize infrastructure implementation.
Technical design and implementation tasks follow specification review.

## 2. Desired outcome

The owner can leave the host unattended and have its project volume backed up
without an active SSH session or host process. The owner can identify the latest
completed snapshot, understand retention, and receive notifications when creation,
retention, or backup freshness is unhealthy.

Preserve the live volume, attachment, deletion protection, and access paths.
This feature requires no compute replacement or filesystem interruption.

## 3. Scope

### 3.1 Included

- Terraform-managed, enabled, tag-targeted EBS snapshot lifecycle policy.
- Dedicated backup-selection tag on `aws_ebs_volume.projects`.
- Configurable schedule and retention with validated inputs.
- Dedicated service role and narrowly scoped deployment permissions.
- Encrypted, private snapshots with traceable non-secret metadata.
- Failure alerts and detection of missing or stale completed snapshots.
- Read-only inspection instructions, rollback guidance, and acceptance evidence.

### 3.2 Excluded

- RES-002 restore drills, restored-volume creation, and live-volume replacement.
- RES-003 and DSH-008 dashboard UI or a general platform status collector.
- Root-volume backups, AMIs, and home-directory authentication-state recovery.
- Database-native backups, write quiescing, and application-consistent snapshots.
- Cross-account/Region copies, archive tiers, and immutable retention.
- On-demand backup commands, general alert routing, Slack, and production backups.

A documented handoff to RES-002 is included; an executed restore is not an
acceptance claim for this feature.

## 4. Proposed defaults

These are proposals for review, not previously approved operating settings.

| Setting | Proposed default |
|---|---|
| Service | Amazon Data Lifecycle Manager (DLM), custom EBS snapshot policy |
| Target | Only the persistent project volume, selected by a dedicated tag |
| Deployment | Existing `infra/dev-host` and `gptclaw-dev-host` HCP workspace |
| Account and Region | Existing approved development account and Region |
| Schedule | Every 24 hours, starting at 03:00 UTC |
| Retention | Seven snapshots per target volume, count-based |
| Storage | Standard snapshot tier |
| Encryption | Preserve source-volume encryption and key relationship |
| Sharing | Private to the development AWS account |
| Freshness threshold | Latest completed recovery point older than 26 hours |
| Freshness evaluation | At least hourly, independently of the EC2 host |
| Notification | Owner-confirmed email subscription |
| Consistency | Crash-consistent block storage; no application-consistency guarantee |

Daily scheduling is a nominal cadence, not a guaranteed 24-hour recovery point
objective. Scheduling delay, snapshot duration, and failures can increase data
age. The freshness threshold is an alert boundary. Seven snapshots does not
promise seven calendar days of coverage or a fixed storage bill.

## 5. Functional requirements

### BAK-001: Pipeline-managed policy

Declare the policy, tags, role, monitoring, and notification resources in
`infra/dev-host`. Provision and change them only through committed code ->
GitHub Actions -> HCP Terraform -> AWS, preserving the protected workflow,
dynamic credentials, and revision traceability. Scheduled creation and expiry
are AWS service actions delegated by the reviewed policy, without a new apply.

Do not add host cron, local applies, long-lived AWS credentials, or direct AWS
CLI/console infrastructure mutation procedures.

### BAK-002: Exact volume selection

Use a stable, dedicated selection tag on the project volume. Target volumes,
not all disks attached to the instance. Verify the actual matching set contains
exactly the intended project volume, excluding root and unrelated volumes.
Selection must not depend on a historical hard-coded volume ID or deployment
revision. Restored/test volumes must not inherit an active selection tag without
deliberate enrollment.

### BAK-003: Schedule and retention

Run independently of host sessions and expire snapshots under the declared
retention rule. Reject invalid inputs before apply. Cleanup must not include
unrelated or manually created snapshots.

Document initial scheduling, retention during failures, and behavior when the
policy is disabled, replaced, or deleted. Call out retention decreases and
replacement in plan review, including recovery-point loss and orphaned costs.

### BAK-004: Encryption and sensitive data

Keep snapshots encrypted and private, preserving access to the recovery key.
Do not rotate/replace the volume key or enable public/cross-account sharing.
Snapshots contain full volume contents, potentially including uncommitted work,
secrets, and runtime data; treat access as access to that data. Copy only reviewed
non-secret tags. Do not include file contents, credentials, or environment dumps
in outputs, alerts, logs, or evidence.

### BAK-005: Least-privilege identities

Use a dedicated DLM role with only required lifecycle permissions, scoped to
resources/tags where AWS supports it. Restrict role passing to the intended
service and role. Explain actions requiring wildcard resource scope.

Use a separate monitoring identity where needed, limited to required reads and
telemetry/notification writes. Grant no new snapshot mutation or infrastructure
privileges to the EC2 role or `forge`.

Resolve deployment-permission prerequisites in the design: the existing HCP
apply role cannot modify itself. Use an explicit reviewed repository/pipeline
path; do not grant self-administration or edit IAM out of band.

### BAK-006: Failure and freshness visibility

Notify the owner of creation/deletion failures, policy errors, and missing/stale
completed recovery points. Detect disabled policies and missing targets even
when no failure event arrives. Operate independently of the development host.

Calculate age from the recovery-point/start timestamp of a `completed` snapshot
belonging to the intended policy and volume. Pending, failed, or unrelated
snapshots cannot make state healthy. With no completed snapshot, report
`no recovery point`; allow at most the freshness threshold from initial
enablement before alerting on that condition.

Inspection errors and missing monitor heartbeats must be visible as
unknown/unhealthy, never fresh. Define bounded detection/delivery timing,
repeat notifications, recovery notification, and monitoring of the monitor in
the technical design.

Alerts identify environment, Region, policy, volume, category, observed time,
and diagnostic route without exposing data. Confirm the email subscription and
verify delivery before acceptance. This does not deliver the deferred dashboard.

### BAK-007: Inspection and recovery handoff

Provide non-secret outputs and read-only runbook steps to find policy, target,
retention, notification status, and latest completed snapshot with ID, state,
timestamp, encryption, and age. Distinguish configured policy, completed
snapshot, and tested restore.

Explain snapshot selection for RES-002 and require replacement-volume creation
and attachment through reviewed Terraform and the pipeline. Metadata alone
must not be presented as a successful restore or recovery-time guarantee.

## 6. Safety and rollback

- Preserve live-volume and identity-resource `prevent_destroy`. Do not detach,
  replace, reformat, or stop the live volume or host.
- Preserve SSM/Tailscale and the security group's zero inbound rules.
- Roll back through a reviewed pipeline change disabling or repairing the policy
  while preserving recovery points. Snapshot deletion is not routine rollback.
- Document retention after disablement/removal, retained-snapshot inventory,
  and cleanup ownership. Removing Terraform configuration must not be assumed
  to remove policy-created snapshots.
- Test failures with fixtures and an isolated/synthetic notification path. Do
  not break live IAM, delete backups, or disable protection to trigger an alarm.
  Label synthetic evidence clearly.
- Document snapshot/monitoring cost drivers and usage inspection. Retention
  bounds count, not changed bytes or total cost.

## 7. Acceptance criteria

All criteria require evidence before SPEC-002 is marked complete.

| ID | Acceptance condition |
|---|---|
| AC-001 | Repository checks and Terraform formatting, validation, and focused tests pass for selection, enabled state, schedule/retention validation, IAM, encryption/privacy, and monitoring. |
| AC-002 | Reviewed GitHub/HCP plan and apply identify the revision and add backups without replacing compute, altering attachment, removing protection, or opening inbound access. |
| AC-003 | Read-only inspection confirms the enabled policy selects exactly the live project volume, excluding root and unrelated volumes. |
| AC-004 | At least one naturally scheduled snapshot completes with expected source, policy attribution, timestamp, retention metadata, encryption, and private sharing state. Policy creation alone does not pass. |
| AC-005 | Retention matches the approved count; tests verify mapping and cleanup scope. If live expiration has not occurred, record that limitation and a dated follow-up check. |
| AC-006 | Tests cover fresh, stale, missing, pending, failed, wrong-volume/policy snapshots, disabled/error policy, missing target, inspection errors, and absent monitor data without false healthy results. |
| AC-007 | A notification test reaches the confirmed owner through the deployed alert path. Evidence distinguishes synthetic inputs from observed failures and records detection/delivery bounds. |
| AC-008 | Monitor failure/missing-data and return to healthy state are verified without disrupting protection. |
| AC-009 | A same-configuration follow-up pipeline plan has no unexpected changes; generated snapshots do not cause Terraform drift. |
| AC-010 | Runbook and sanitized evidence cover inspection, diagnosis, retention changes, rollback, costs, and RES-002 handoff without claiming a successful restore. |

## 8. Inputs and decisions before implementation

- Review schedule, retention, and freshness against acceptable loss of work/data.
- Supply notification email through the appropriate configuration channel and
  confirm the subscription; omit contact details from spec and evidence.
- Verify current volume, key, account, and Region from deployed outputs and
  read-only inspection rather than historical IDs.
- Resolve deployment-role permissions, including self-management restrictions.
- Select monitoring implementation and precise timing bounds. Failure events
  alone do not satisfy missing-backup detection.

## 9. Deliverables and follow-on work

After spec review, create `technical-design.md` mapping requirements to resources,
then `tasks.md` with ordered checks and deployment gates in this folder.
Implementation delivers Terraform, focused tests, operational documentation,
and `acceptance.md` with sanitized GitHub/HCP links and snapshot/alert evidence.

RES-002 proves recovery by creating and inspecting a replacement volume without
risking the live volume. RES-003 and DSH-008 can later consume backup metadata
and restore results. Database consistency, off-account protection, and production
recovery objectives require separate specifications.

## 10. References

- [Feature catalogue](../platform/features.md)
- [Recovery runbook](../../runbooks/recover-dev-host.md)
- [AWS: Snapshot lifecycle automation](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-lifecycle.html)
- [AWS: Custom policies and timing](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-ami-policy.html)
- [AWS: DLM metrics](https://docs.aws.amazon.com/ebs/latest/userguide/monitor-dlm-cw-metrics.html)
- [AWS: DLM events and best-effort delivery](https://docs.aws.amazon.com/ebs/latest/userguide/monitor-cloudwatch-events.html)
