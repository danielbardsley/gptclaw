# Recover or replace the development host

Project data lives on a separate protected EBS volume. Compute, Codex
authentication, and the EC2-to-GitHub key are replaceable. All infrastructure
reconciliation must run through GitHub Actions and HCP Terraform.

## Break-glass access

Use the `ssm_start_session_command` Terraform output or the AWS console to open
a Systems Manager Session Manager shell. SSM is the first recovery path when
Tailscale, SSH, or Codex is unavailable.

Inspect without printing secrets:

```sh
cloud-init status --long
systemctl status gptclaw-bootstrap.service
journalctl -u gptclaw-bootstrap.service --no-pager
cat /var/lib/gptclaw/bootstrap-complete.json
findmnt /srv/forge
```

Do not print the Tailscale secret or dump the process environment.

## Planned instance replacement

1. Quiesce writes beneath `/srv/forge/projects`.
2. Confirm the Terraform plan retains `aws_ebs_volume.projects` and changes only
   the expected compute/attachment resources.
3. Create and verify an EBS snapshot of the project volume.
4. Store a fresh tagged one-use Tailscale auth key in the existing Secrets
   Manager secret.
5. Merge the reviewed change to `main`.
6. Manually dispatch the `apply` operation with confirmation
   `gptclaw-dev-host` and complete the environment approval when configured.
7. Verify SSM before Tailscale and SSH.
8. Verify the original filesystem UUID, `/srv/forge/projects`, ownership, Git
   status, Tailscale identity, and Codex executable.
9. Recreate the EC2-to-GitHub deploy key and reauthenticate Codex if the root
   volume was replaced.

Removing `prevent_destroy` from the project volume requires a dedicated pull
request and explicit data-destruction review.

## Restore from snapshot

1. Select a verified snapshot and create a gp3 encrypted volume in the same
   availability zone as the replacement instance.
2. Represent the recovered volume in reviewed Terraform configuration and
   import it into the HCP Terraform state before attachment.
3. Mount it read-only through an administrator session and inspect the expected
   filesystem and repositories.
4. Return it to normal service only after validation.
5. Re-run the protected pipeline and retain GitHub/HCP run links.

Do not create a long-lived manual attachment or other infrastructure drift. Any
emergency change must be reconciled into Terraform immediately.

## Common failures

| Failure | Response |
|---|---|
| HCP token rejected | Rotate only the failed plan or apply token. |
| AWS OIDC denied | Correct the exact organization/project/workspace/phase trust. |
| AWS permission denied | Add only the specific required action/resource and re-plan. |
| Wrong account or region | Correct inputs; never relax the provider allowlist. |
| Tailscale key expired or consumed | Store a fresh one-use key and rerun the enrollment service through SSM. |
| Project volume not found | Confirm attachment and Nitro by-id link; never format an ambiguous device. |
| Codex missing from login `PATH` | Re-run the official installer as `forge` and verify `sh -lc 'command -v codex'`. |
