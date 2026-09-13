# ACCEPTANCE-002: Automated EBS Snapshots

- **Status:** Accepted on 2026-09-13; retention-expiry follow-up recorded
- **Owner:** Daniel
- **Specification:** [SPEC-002](./spec.md)
- **Deployment:** [sanitized deployment evidence](./deployment-attempt-2026-09-12.md)
- **Deployed revision:** `ca4305966500e9824ae8f6305594f10d046ce515` ([merged PR #4](https://github.com/danielbardsley/gptclaw/pull/4))
- **Account / Region:** `571748613148` / `us-east-1`

## Active acceptance criteria

| Criterion | Result and evidence |
|---|---|
| AC-001 | Passed. The protected quality job passed formatting, validation, repository checks and all 15 Terraform tests, including the post-snapshot rerun below. |
| AC-002 | Passed. Protected prerequisite and feature plan/apply links are in the deployment record. Feature apply added four backup resources, updated twelve resource tags, destroyed nothing, and used the normal HCP OIDC apply role. No replacement or attachment/key/protection/inbound-access change. |
| AC-003 | Passed. Enabled DLM policy `policy-0915f5294ae69132a` selects exactly `vol-0f53005235c1e39f3` through `GptClawBackup=development-projects`. Root volume is excluded. Read-only verification repeated on 2026-09-13. |
| AC-004 | Passed. The naturally scheduled completed snapshot below has the expected source, service/policy/schedule attribution, timestamp, metadata, encryption/key and private sharing state. |
| AC-005 | Passed with the specification's permitted limitation. Configured retention is seven; tests cover mapping and policy-attributed cleanup. Live expiry has not occurred. Daniel owns the dated 2026-09-21 follow-up below. |
| AC-009 | Passed. After the service-created snapshot completed, the original protected plan was rerun at the deployed revision and reported no changes. No apply was dispatched during acceptance. |
| AC-010 | Passed. [Inspection/operations](../../runbooks/inspect-backups.md) and [recovery handoff](../../runbooks/recover-dev-host.md) cover diagnosis, retention changes, rollback, costs and RES-002, without claiming a tested restore. |

## Naturally scheduled snapshot

Read-only checks at approximately 2026-09-13 04:15–04:18 UTC confirmed:

- Snapshot: `snap-01b934e8e05f1018b`, state `completed`.
- Start: `2026-09-13T03:04:39.929Z`, within the first scheduled window.
- Source: `vol-0f53005235c1e39f3`.
- Policy tag: `aws:dlm:lifecycle-policy-id=policy-0915f5294ae69132a`.
- Schedule tag: `aws:dlm:lifecycle-schedule-name=projects-daily`.
- Service tag: `dlm:managed=true`.
- Reviewed metadata: `Project=GptClaw`, `Repository=danielbardsley/gptclaw`,
  `BackupSet=development-projects`, `Environment=development`,
  `RetentionClass=daily`.
- Encrypted: true. Snapshot and source use
  `arn:aws:kms:us-east-1:571748613148:key/80089d26-3dc7-46ef-8982-e41f1d5163f7`.
- `createVolumePermission` is an empty list: no public or cross-account sharing.
- CloudTrail CreateSnapshot at `2026-09-13T03:04:40Z` records
  `invokedBy=dlm.amazonaws.com`, issuer
  `arn:aws:iam::571748613148:role/gptclaw-dev-projects-backup`, the exact snapshot
  and source IDs, and no error. No manual snapshot was created.
- Source attachment remains attached to `i-02872b301f0d44218` at `/dev/sdf`,
  with the original attachment time and DeleteOnTermination=false.

## Post-snapshot pipeline verification

- [GitHub run #47, attempt 2](https://github.com/danielbardsley/gptclaw/actions/runs/34720055891/attempts/2): success.
- [HCP run](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-CZtGQpvRGCWFKPdT): no changes at 2026-09-13 04:18:50 UTC.
- Revision remains `ca4305966500e9824ae8f6305594f10d046ce515`.

Current main contains newer unrelated work. Rerunning the existing protected
plan preserved the original main ref, revision, workflow, quality job and
protected environment instead of changing inputs or deploying later work.
The GitHub CLI was used; no browser, local apply, credential reconfiguration,
direct AWS mutation, state dump or saved plan was needed.

## Limitations and retention follow-up

Daniel will inspect policy-attributed snapshot inventory and expiry on
**2026-09-21**, after at least eight daily schedules. Record whether count-based
cleanup has operated, allowing for pending snapshots and actual successful
runs. Do not delete snapshots manually to manufacture retention evidence.
One completed snapshot does not establish seven days of coverage or prove
expiry, application consistency, restoration, or recovery time. Restore remains
RES-002. Silent DLM failures are accepted; no monitoring or notifications exist.

The local acceptance follow-up can now be paused; it is not an ongoing backup
freshness monitor. No new AWS resources were changed during acceptance.
