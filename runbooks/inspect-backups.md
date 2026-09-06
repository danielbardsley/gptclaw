# Inspect and operate project-volume backups

RES-001 uses DLM for encrypted project-volume snapshots and count retention.
There are no failure notifications, alarms, or freshness checks. DLM may fail
silently. Use manual inspection when diagnosing or preparing a recovery.

Run AWS CLI reads below with an authorized operator identity, not new privileges
on the development host. All infrastructure changes still use reviewed code,
GitHub Actions, and HCP Terraform. Never run a local apply or direct AWS
snapshot/volume mutation.

## Discover the policy and target

Read the non-secret `project_backup` output in the latest applied HCP run. It
contains policy ID/ARN, volume ID, enabled state, interval, UTC start time,
retention count, and selector. Outputs describe applied configuration; confirm
actual AWS state with these reads.

Set the following to the current approved values, not historical acceptance IDs:

~~~sh
backup_region='us-east-1'
backup_policy_id='<project_backup.policy_id>'
backup_volume_id='<project_backup.volume_id>'

aws sts get-caller-identity --query '{Account:Account,Arn:Arn}'
aws dlm get-lifecycle-policy --region "$backup_region" \
  --policy-id "$backup_policy_id" \
  --query 'Policy.{Id:PolicyId,State:State,Status:StatusMessage,Role:ExecutionRoleArn,Details:PolicyDetails}'
aws ec2 describe-volumes --region "$backup_region" \
  --filters 'Name=tag:GptClawBackup,Values=development-projects' \
  --query 'Volumes[].{Id:VolumeId,Encrypted:Encrypted,Key:KmsKeyId,AZ:AvailabilityZone,Attachments:Attachments[].{Instance:InstanceId,State:State}}'
~~~

The matching set must contain exactly the current project volume. Verify its
encryption and attachment; the root volume and unrelated volumes must not match.
Do not propagate the active selection tag to restored/test volumes.

## Inspect recovery points

~~~sh
aws ec2 describe-snapshots --region "$backup_region" --owner-ids self \
  --filters "Name=volume-id,Values=$backup_volume_id" \
            "Name=tag:aws:dlm:lifecycle-policy-id,Values=$backup_policy_id" \
  --query 'sort_by(Snapshots, &StartTime)[].{Id:SnapshotId,State:State,Start:StartTime,Encrypted:Encrypted,Key:KmsKeyId,Volume:VolumeId}'

aws ec2 describe-snapshots --region "$backup_region" --owner-ids self \
  --filters "Name=volume-id,Values=$backup_volume_id" \
            "Name=tag:aws:dlm:lifecycle-policy-id,Values=$backup_policy_id" \
  --query "sort_by(Snapshots[?State=='completed'], &StartTime)[-1].{Id:SnapshotId,Start:StartTime,Encrypted:Encrypted,Key:KmsKeyId,Volume:VolumeId}"
~~~

A null latest result means no completed recovery point was found. A pending
snapshot is not usable acceptance evidence. Calculate age from the UTC start
timestamp, not the time the command was run. Inspect the chosen snapshot's
sharing permissions without exposing contents:

~~~sh
backup_snapshot_id='<completed snapshot ID>'
aws ec2 describe-snapshot-attribute --region "$backup_region" \
  --snapshot-id "$backup_snapshot_id" --attribute createVolumePermission \
  --query CreateVolumePermissions
~~~

The permissions list must be empty. Confirm the snapshot's key matches the
source volume key. A completed snapshot is not a tested restore; use the
RES-002 workflow before claiming recovery was proven.

## Scheduling and retention

Defaults are daily at 03:00 UTC and seven retained snapshots. DLM may start
within an hour of the scheduled time, and completion is asynchronous. Policy
creation does not create an immediate completed snapshot.

Review changes to `backup_interval_hours`, `backup_start_time_utc`, and
`backup_retention_count` through the pipeline. Lower retention can remove older
recovery points. Count retention does not guarantee seven calendar days or cap
changed bytes and cost. Record observed expiration or a dated follow-up after
at least eight daily runs; keep the owner and limitation visible in acceptance.

Snapshot storage is incremental. Use the account's billing/cost views and
policy-attributed inventory for usage; do not estimate billed storage by adding
each snapshot's logical volume size.

## Diagnose silently failed backups

Inspect policy state/status, selector matches, snapshot state, and the DLM
execution role's inline policies. Check the latest GitHub/HCP run and current
Region/account before changing anything. Repair exact IAM/tag/configuration
issues through reviewed Terraform. Do not expand the host role or remove
snapshot ownership conditions to work around a denial.

The role's creation policy must exist before the DLM policy, and the scoped
lifecycle policy must be attached before the first schedule. If a first run
occurs before deployment finishes, inspect the outcome and await the next
scheduled run after a pipeline repair. Do not claim acceptance from mock tests.

## Disable, replace, or roll back

Set `backup_policy_enabled=false` through a reviewed pipeline change to disable
new runs without deleting the volume or policy. Record disablement explicitly;
no notification will announce lost protection. Preserve existing snapshots.

Disabling or deleting a custom DLM policy stops lifecycle management. Removing
the source selection tag also stops management of its snapshots. Inventory
retained snapshots and account for ongoing storage cost. Re-enabling may resume
retention cleanup; review old recovery points before doing so.

A replacement policy gets a new ID and does not adopt the old policy's
snapshots. Record the old ID and inventory first. Do not import old snapshots
merely to destroy them or delete them using the CLI. Any later cleanup requires
a separately reviewed inventory and pipeline procedure.

Never detach, replace, reformat, or remove `prevent_destroy` from the project
volume as backup rollback. Recovery-volume creation and attachment belong to
the reviewed [restore procedure](./recover-dev-host.md), not this feature.

## Evidence

Retain deployed revision, GitHub/HCP links, account/Region, actual policy/volume
IDs, completed snapshot metadata, private/encrypted verification, retention
observations, and a same-revision no-change plan. Exclude credentials, state,
saved plans, filesystem contents, or environment dumps.
