# SPEC-016 acceptance evidence

- **Status:** Account issuer and Tailscale trust configured; host deployment and acceptance pending
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
| AC-003 | pending | Issuer and exact-role trust configured October 8; fresh-host enrollment and SSM/private access remain pending. |
| AC-004 | pending | Existing Podman/profile tests pass; actual package receipts, private access and preserved storage must be checked after replacement. |

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
