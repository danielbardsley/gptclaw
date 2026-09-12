# RES-001 deployment attempt — 2026-09-12

Status: prerequisite and feature deployed; naturally scheduled snapshot
acceptance pending. No manual snapshot was created.

## Authorization and authentication

The owner explicitly authorized a one-time exception to the short-lived-session
maintenance procedure: use the existing authorized IAM user credentials only
in sensitive HCP environment variables. No new IAM credential was created.
The account and Region were verified as `571748613148` / `us-east-1`.
HCP auto-apply remained off and no inherited variable sets were present.

After the plan, both temporary credentials were deleted and
`TFC_AWS_PROVIDER_AUTH=true` restored. The original phase-specific plan and
apply role ARNs were preserved. Cleanup verified zero static AWS credential
variables. The local Terraform login was preserved.

## Prerequisite result

- Main revision: `f8913f1e79731eb803d7055ac836e427f48fb9a9`.
- [Protected GitHub plan #40](https://github.com/danielbardsley/gptclaw/actions/runs/34719133973): succeeded, including quality checks.
- [HCP plan](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-Fr97gsbdknVd4DJQ).
- Result: **0 to add, 14 to change, 0 to destroy**.
- Two changes are the prerequisite HCP inline policies. Twelve additional
  resource updates change only `DeploymentRevision` tags from `ca52f89…` to
  `f8913f1…`, including the host, its root-volume tags, and project volume.
- No replacement, attachment, encryption, storage-size, or host configuration
  change is proposed by those twelve resource updates.
- The committed pipeline supplies the current Git commit as
  `deployment_revision`; provider default tags propagate that value.

The maintenance runbook requires only two inline-policy changes. The apply was
therefore withheld. PR #4 remains unmerged and live acceptance remains pending.
Proceeding requires an explicit decision about the additional tag-only updates
or a reviewed code change to preserve tags during maintenance. No targeting or
pipeline-gate bypass was used.

### Authorized continuation

The owner subsequently explicitly approved the twelve additional tag-only
updates alongside the two policy changes. The same main revision was verified.
The existing credentials were temporarily configured again for this maintenance
apply only, then removed immediately after success.

- [GitHub apply #42](https://github.com/danielbardsley/gptclaw/actions/runs/34719441471).
- [HCP apply](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-JpBLUBdNJJhCFFJE).
- Result: 0 added, 14 changed, 0 destroyed.
- Cleanup: zero static AWS credential variables; OIDC enabled; original
  phase-specific role ARNs preserved.
- [Post-apply OIDC plan #43](https://github.com/danielbardsley/gptclaw/actions/runs/34719608351): succeeded, no changes.
- [HCP no-change verification](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-NSkiDND3mwXgV7d9).

### Live safety baseline

Project volume `vol-0f53005235c1e39f3`: encrypted 80 GiB gp3 in us-east-1a,
attached at `/dev/sdf` to running host `i-02872b301f0d44218`, with
DeleteOnTermination=false. Root volume: `vol-04876aac2f3e06baf`.
The AWS-managed encryption key `80089d26-3dc7-46ef-8982-e41f1d5163f7` is enabled.
SSM is Online; security group `sg-0dea31b346a469de2` has no inbound rules.
The project-volume Terraform prevent_destroy remains configured. EC2 API
termination protection was already false; no change to that baseline was made.
Tailscale SSH as `forge` succeeds, SSH is active, and `/srv/forge` is mounted
as ext4 from `/dev/nvme1n1`.

### Feature review and merge

PR #4 was rechecked: expected head `67c01ad6639f0d37142b802ca7c61eff74bba776`,
mergeable, targeting main, with passing CI run #36. Code review confirmed the
dedicated selector, daily 03:00 UTC schedule, retention seven, exact source-volume
creation permission, and policy-attributed cleanup, without monitoring resources.
After prerequisite/OIDC verification it was merged at
`ca4305966500e9824ae8f6305594f10d046ce515`.
[Feature plan #45](https://github.com/danielbardsley/gptclaw/actions/runs/34719743206)
/ [HCP plan](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-WBgbvkdkfvF5t6MD)
proposed four additions, fourteen updates and no destruction. Twelve updates
were the expected revision tags (plus the source-volume selector). The unchanged
HCP policy documents were deferred for recalculation, not new permission changes.

### Feature deployment and live checks

- [GitHub apply #46](https://github.com/danielbardsley/gptclaw/actions/runs/34719893951)
  / [HCP apply](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-BgbfbBhsgrse2ZQf):
  **4 added, 12 changed, 0 destroyed**. The two HCP policy documents resolved
  without mutation.
- CloudTrail CreateLifecyclePolicy at `2026-09-12T21:27:29Z` identifies
  `arn:aws:sts::571748613148:assumed-role/gptclaw-dev-hcp-apply/terraform-run-BgbfbBhsgrse2ZQf`,
  with no error, creating `policy-0915f5294ae69132a`.
- The policy is ENABLED, VOLUME/CLOUD targeted, selecting
  `GptClawBackup=development-projects`. Schedule `projects-daily` is every 24
  hours at 03:00 UTC, count retention seven, copy_tags=false, no sharing/copy/
  scripts. Only the five reviewed non-secret snapshot tags are configured.
- Actual selector match: exactly `vol-0f53005235c1e39f3`, excluding root volume.
  Its 80 GiB gp3 size, encryption key, attachment timestamp, and
  DeleteOnTermination=false are unchanged.
- The DLM role's creation policy limits source creation to the exact project
  volume ARN; existing-snapshot tagging/deletion requires this policy ID.
  Both inline policies and the scoped DLM trust were read back and verified.
- Host `i-02872b301f0d44218` remains running with the same AMI/type and both
  original attachments. Security group inbound rules remain empty, SSM Online,
  Tailscale SSH works and `/srv/forge` remains mounted.
- [GitHub follow-up plan #47](https://github.com/danielbardsley/gptclaw/actions/runs/34720055891)
  / [HCP follow-up plan](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-LMVVu3bSND81oCsd):
  finished, has-changes=false, 0 add/change/destroy, same deployed revision.

### Pending acceptance and retention

Immediate policy-attributed snapshot inventory was empty. First scheduled
start window is 2026-09-13 03:00–04:00 UTC; completion is asynchronous.
Do not mark AC-004 complete until a natural snapshot is completed and metadata,
source, policy attribution, encryption/key and private permissions are checked.
Repeat the same-configuration pipeline plan after the snapshot exists.

Daniel owns the permitted retention follow-up on 2026-09-21, after at least
eight daily runs. No expiry or restore has been proven.
The local acceptance follow-up `complete-res-001-snapshot-acceptance` runs at
00:15 America/New_York daily and must stop once acceptance is complete. It is
an acceptance checkpoint, not an AWS monitoring/notification component.

## OIDC restoration verification

[Protected GitHub plan #41](https://github.com/danielbardsley/gptclaw/actions/runs/34719255725)
was dispatched after cleanup. The remote speculative plan succeeded under the
restored OIDC configuration, again reporting 0 to add, 14 to change, 0 to
destroy. [HCP verification run](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-1xpfULFGDxNy6URY).
This verifies restored planning access, not prerequisite deployment or a
no-change result. Apply-phase identity verification remains pending.
