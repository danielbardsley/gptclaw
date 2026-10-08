# SPEC-016 acceptance evidence

- **Status:** Fresh-host enrollment, bootstrap and private access verified; owner acceptance pending
- **Owner:** Daniel
- **Date:** 2026-10-08 (America/New_York)
- **Specification:** [SPEC-016](spec.md)
- **Design:** [TDD-016](technical-design.md)
- **Tasks:** [Tasks](tasks.md)
- **Branch:** `codex/tailscale-workload-identity`

## Criteria

| Criterion | State | Evidence / remaining work |
|---|---|---|
| AC-001 | passed locally | 11 offline enrollment tests cover success, retry, version/config/state/tag failures, timeout, credential isolation and migration; rendered helper/no-key/payload assertions pass. |
| AC-002 | passed | Local IAM bounds and account-stack tests pass. October 8 protected account plan/apply and development-host plan retain deployment identities and project disk; see run evidence below. |
| AC-003 | verified | October 8 fresh host enrolled automatically; expected online/tag state, SSM and authenticated private SSH verified below. |
| AC-004 | verified | Successful bootstrap/profile/rootless receipts and preserved project filesystem/ownership verified below. Full SYS-001 fixture/reboot acceptance remains separate. |

## Executed verification

- `./scripts/check-repository.sh` with the existing isolated manifest environment:
  passed, including all existing suites and 11 federation tests.
- Terraform 1.16.1 `fmt`, `validate`, `test` in `infra/dev-host`: passed,
  24 tests, mocked AWS and real local cloud-init rendering; user-data size passes.
- Terraform 1.16.1 backend-free, read-only-lock initialization, validation and
  tests in `infra/tailscale-federation`: passed, 2 mocked AWS tests.
- The first account-root initialization rejected an unrelated copied cloud-init
  lock entry; removed that unused entry while retaining the existing signed AWS
  provider selection/checksums, then read-only initialization passed.
- `bash -n` for the repository checker and bootstrap template: passed.
- Git whitespace checks: passed.
- Source inspection confirmed Tailscale's JSON status mode returns successfully
  for a not-yet-enrolled node. Documentation establishes >=1.94 audience discovery
  and persistent/preauthorized client-ID parameters; no client enrollment was run.

During the October 1 implementation checks, no local package install, token
request, AWS mutation or external trust write was performed. Mock test blocks named `apply` do not provision AWS resources. No
credentials, live tokens, state or plans are included in this evidence.

## Remaining setup

Follow [the runbook](../../runbooks/manage-tailscale-federation.md) for the
recovery readiness and protected development-host apply. The protected remote plan
now confirms Terraform 1.16.5. Preserve the empty development working directory
and disabled auto-apply. Tailnet Lock is disabled on the connected host's tailnet;
confirm recovery point, maintenance window and rollback readiness before replacement.
No host replacement or actual automatic enrollment has occurred in this setup.
Delivered status is not claimed.

## Review and CI

[PR #28](https://github.com/danielbardsley/gptclaw/pull/28) contains implementation
revision `04ed5424d7ab5db3865e51cae332ce1da2f33efe`.
Both [development CI](https://github.com/danielbardsley/gptclaw/actions/runs/36821074386)
and [account-setup CI](https://github.com/danielbardsley/gptclaw/actions/runs/36821074416)
passed for that revision. Protected plan/apply jobs were skipped for these PR runs;
CI did not establish issuer setup or change AWS infrastructure.

## Account and trust setup — October 8, 2026 (America/New_York)

Reviewed/deployed source: `ce5b81438e9092bca050be42c0450facc255a8f7`, including
merged [Terraform 1.16.5 PR #31](https://github.com/danielbardsley/gptclaw/pull/31).
Daniel reported that outbound federation had not previously been enabled.

- [Protected plan #7](https://github.com/danielbardsley/gptclaw/actions/runs/37732155358)
  initially failed because the HCP `aws_account_id` input was marked sensitive,
  which propagated to the intentionally non-secret subject output. Recreating
  only that input as a non-sensitive Terraform string fixed the failure.
- The corrected [HCP plan](https://app.terraform.io/app/Bardsley/gptclaw-tailscale-federation/runs/run-XE4xkcSuXbUxxtiJ)
  passed: only `aws_iam_outbound_web_identity_federation.tailscale`, 1 addition,
  0 changes, 0 deletions. GitHub quality checks passed; environment review retained.
- [Protected apply #8](https://github.com/danielbardsley/gptclaw/actions/runs/37733151298)
  and its [HCP run](https://app.terraform.io/app/Bardsley/gptclaw-tailscale-federation/runs/run-n2auPLMfb7VaYwpq)
  succeeded: 1 added, 0 changed, 0 destroyed. No compute or storage change.
- The isolated federation workspace uses Terraform 1.16.5, remote execution,
  `infra/tailscale-federation`, disabled auto-apply, and no inherited variable
  sets or dynamic credential connections. GitHub `federation-bootstrap` permits
  only `main`, requires Daniel's review and contains both HCP token secrets.
- Browser verification confirmed the Tailscale OIDC trust on `bardsley.org.uk`:
  issuer `https://a124dc86-7fee-4e8e-a98d-640682d5143c.tokens.sts.global.api.aws`,
  exact subject `arn:aws:iam::571748613148:role/gptclaw-dev-host`, only Auth Keys
  write (`auth_keys`), only `tag:gptclaw-dev`, and no custom claims.
- Non-secret client ID `TA5NpyzWWE11CNTRL-kbMEFD4qMH11CNTRL` was saved as
  `tailscale_federation_client_id` in `gptclaw-dev-host` (Terraform string,
  HCL off, non-sensitive). Audience is derived by code as `api.tailscale.com/`
  followed by that client ID. Actual token exchange remains untested.

### Closed one-time credential exception

Owner: Daniel. Scope: this isolated account-federation setup attempt only.
Reason: Daniel supplied a long-lived development-account key with broader
permissions and explicitly authorized using it to finish the setup, followed by
revocation. Expiry: immediately after the setup attempt; no standing exception.
Before pipeline execution, both credential inputs were verified as sensitive
HCP environment variables after correcting their initial category/name/flags. Browser verification after the successful apply confirmed deletion of
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`; no session token existed.
Daniel subsequently confirmed revocation in AWS (owner report, not independently
verified). No credential values are retained in this record. HCP API tokens are
separate pipeline credentials and were preserved.

No local AWS mutation, host replacement, reboot/logout acceptance, or rollback
drill was performed. Historical local test evidence above remains unchanged.

## Development-host plan — October 8, 2026 (UTC)

- [Protected plan #97](https://github.com/danielbardsley/gptclaw/actions/runs/37735107049)
  passed at `ce5b81438e9092bca050be42c0450facc255a8f7`; quality checks also
  passed and the apply job was skipped. The [HCP speculative run](https://app.terraform.io/app/Bardsley/gptclaw-dev-host/runs/run-og2PTtwN2Z2UHEoM)
  reports Terraform 1.16.5 and **2 additions, 14 updates, 2 deletions**.
- Only `aws_instance.dev_host` and `aws_volume_attachment.projects` are replaced.
  `aws_ebs_volume.projects` (`vol-0f53005235c1e39f3`) has only revision-tag
  updates; its existing attachment reports `delete_on_termination=false`.
  Deployment identities have no planned changes. Thirteen in-place updates are
  revision tags; the remaining update is the host runtime IAM policy.
- Host runtime IAM removes Secrets Manager reads and adds `sts:GetWebIdentityToken`
  for the exact configured audience, nonempty audience, `us-east-1`, and at most
  300 seconds. EC2-only host trust remains unchanged. The legacy secret version
  is forgotten with `destroy=false`; the secret container is retained.
- Terraform warns that the obsolete `tailscale_auth_key` HCP input is undeclared.
  Remove obsolete key/counter inputs without reading their values after rollback
  preparation. Rollback requires reviewed code and a fresh one-use key/counter;
  the old key is not a usable fallback.
- The browser could not determine Tailnet Lock status. The installed client's
  read-only `tailscale lock status` then explicitly reported **NOT enabled**.
- Read-only `findmnt` reports `/srv/forge` as ext4 with filesystem UUID
  `680fdc21-378e-466b-8b3f-8fa947eabc8d`; `id -u` reports forge UID 1002.
  Retain this baseline for post-replacement checks. This does not prove backup
  freshness, restored data, or post-replacement ownership.

No apply was dispatched. A suitable completed DLM snapshot, quiesced writes,
maintenance readiness and independent SSM recovery access remain required.
The AWS console redirected TinyFish to sign-in during read-only backup
inspection. No current snapshot metadata was obtained; AWS access is the next
operator action. This is not evidence that snapshots are absent.

### Backup inspection and AWS CLI preference follow-up

Daniel saved an AWS browser session, then instructed that all AWS work use the
CLI. Repository guidance now records that preference; infrastructure mutations
remain on the protected pipeline. No further AWS browser checks will be started.
The already-running read-only browser check completed after a cancellation
request was rejected by automatic approval review (the connector requires an
explicit stop instruction).

That browser reported completed snapshot `snap-0022f6fe12c59fe58` for
`vol-0f53005235c1e39f3`, starting October 7, 2026 at 23:16:36 EDT
(October 8 at 03:16:36 UTC), encrypted with source-volume key
`80089d26-3dc7-46ef-8982-e41f1d5163f7`, and private with no listed sharing accounts.
Its description names DLM policy `policy-0915f5294ae69132a`; the policy tag and
actual policy state were not independently extracted. CLI confirmation and
adequacy for subsequent project writes remain pending; no restore was tested.

AWS CLI v2 is already declared in `infra/dev-host/host-tools.json` and has an
installation/verification adapter in `infra/dev-host/lib/host_tools.py`.
Read-only `namei -l /usr/local/bin/aws` found the existing symlink but also
root-owned `/usr/local/aws-cli` with mode 750, preventing forge from traversing
the installed CLI tree. No live permissions or packages were changed. CLI access
needs a reviewed repair or approved user-scoped setup before backup verification.

## Fresh-host enrollment verified - October 8, 2026

[PR #33](https://github.com/danielbardsley/gptclaw/pull/33) repaired absent-package
classification. [PR #34](https://github.com/danielbardsley/gptclaw/pull/34) repaired
the bootstrap storage-parent ownership that blocked Podman before Tailscale.
Final deployed source: `6d90105136de55f7932c7e6857ba0bf6415db249`.

The [protected plan](https://github.com/danielbardsley/gptclaw/actions/runs/37845606105)
passed: two additions, thirteen revision-tag updates, two deletions. Only compute
and its attachment were replaced; protected project storage was retained.
The [protected apply](https://github.com/danielbardsley/gptclaw/actions/runs/37846268276)
succeeded with the same counts. Daniel authorized that replacement and subsequent
host debugging; Terraform plans/applies remained exclusively in CI/CD.

Post-apply verification observed successful bootstrap completion, passing
rootless and host-tool receipts, and matching deployment-revision provenance.
The rootless phase passed before Tailscale enrollment, and subsequent hardening,
logging, policy and agent-installation phases completed. Tailscale reported
Running, online, and the exact expected tag. The new instance enrolled through
the installed AWS workload-identity bootstrap helper without a manually supplied
auth key or interactive enrollment login.

Desktop Tailscale ping returned two relay pongs. TCP 22 and authenticated private
SSH succeeded. SSH host identity was verified against the public key obtained
through SSM; the temporary known-hosts file was removed. Independent SSH checks
confirmed the original project filesystem identity and expected ownership, plus
the corrected engine-storage-parent ownership. The desktop SSH alias still needs
the replacement's current DNS name; no permanent local SSH configuration or old
tailnet-device record was changed during verification.

Connection addresses, cloud resource identifiers, HCP run links and detailed
host metadata are omitted from this new public evidence summary. No tokens,
credentials, Terraform state/plans or raw authentication logs are included.

These observations verify SPEC-016 enrollment and receipt/storage checks.
Final owner acceptance, full SYS-001 container/logout/reboot/cleanup scenarios
and any post-replacement agent reauthentication/deploy-key recovery remain
separate. No broader feature Delivered status or executed rollback is claimed.
