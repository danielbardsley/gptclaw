# Configure automatic Tailscale enrollment

[Specification](../docs/016-tailscale-workload-identity/spec.md) ·
[Design](../docs/016-tailscale-workload-identity/technical-design.md)

This replaces the recurring fresh-key step. Account setup and tailnet trust are
one-time prerequisites; later EC2 replacements authenticate automatically through
the instance role. No reusable auth key or OAuth secret is introduced. A merged
PR is not evidence of configured trust or a successfully enrolled host.

## 1. Establish the AWS account issuer through IaC

Use the independent root [infra/tailscale-federation](../infra/tailscale-federation/main.tf)
and workflow **Terraform Tailscale account federation**. It never manages compute,
project storage, HCP roles or inbound OIDC trust.

Create a CLI-driven HCP workspace named `gptclaw-tailscale-federation` in the
existing organization. Use Terraform 1.16.1 and working directory
`infra/tailscale-federation`. Set `aws_account_id` to the approved development
account. Configure GitHub environment `federation-bootstrap` with required
reviewers when available and the existing scoped HCP plan/apply token mechanism
(`TF_API_TOKEN_PLAN`, `TF_API_TOKEN_APPLY`). Keep HCP auto-apply disabled. The workflow
fixes its workspace name; never point it at the development host workspace.

The operator needs a separately authorized short-lived AWS session permitting
`iam:GetOutboundWebIdentityFederationInfo`, `iam:EnableOutboundWebIdentityFederation`
and `sts:GetCallerIdentity`. These account-level operations require wildcard
resource scope; limit the session to this account and those operations, with no
IAM role/policy administration or disable permission. Supply it only as sensitive
HCP environment variables in this isolated workspace, using the reviewed
credential-handling rules in [the bootstrap runbook](bootstrap-hcp-aws.md).
Do not borrow production credentials, put credentials in GitHub or this host,
or expand `gptclaw-dev-hcp-apply`. Authorization to deploy is not evidence that
such an operator session is currently available.

First inspect whether an issuer already exists and which state owns it. If owned
elsewhere, reuse that owner's issuer output and skip this stack. If enabled but
unmanaged, set `adopt_existing_issuer=true` only after that ownership review; the
committed import block adopts it without disabling/re-enabling it.

Dispatch `plan` from `main`. It must show only creation/import of the account
issuer; stop on any other resource. Dispatch `apply` with confirmation
`gptclaw-tailscale-federation`. Retain run links and the non-secret `issuer_url`
and `tailscale_subject` outputs. Remove the temporary AWS session variables on
success or failure; do not leave standing administrator credentials in HCP.
Issuer deletion is prevented because it could affect other account consumers.
No local Terraform apply or direct AWS enable command is part of this procedure.

## 2. Configure the Tailscale trust once

In Tailscale **Trust credentials → Credential → OpenID Connect**, create:

| Field | Required value |
|---|---|
| Issuer | Exact `issuer_url` from the account setup output; choose Custom if needed. |
| Subject | Exact `tailscale_subject`, `arn:aws:iam::<account>:role/gptclaw-dev-host`; no wildcard role/account/session pattern. |
| Scope | Auth Keys write (`auth_keys`) only. |
| Tags | Only `tag:gptclaw-dev`; ensure tag ownership permits this assignment. |
| Audience | Use Tailscale's generated `api.tailscale.com/<client-id>`. |

The client requests a persistent node (`ephemeral=false`) and preauthorization
(`preauthorized=true`) within this explicitly trusted tag, so device approval does
not become a recurring manual step. Do not add general device-administration or
production tags. If Tailnet Lock requires signatures, resolve that prerequisite
before replacement; do not disable protections to make enrollment
pass. Native federation setup here has not been tested against this tailnet yet.

Copy the non-secret client ID into the development HCP workspace Terraform input
`tailscale_federation_client_id`. The audience is derived in code. Remove obsolete
`tailscale_auth_key` and `tailscale_auth_key_version` HCP inputs/overrides after
preparing rollback; never copy their values into evidence. Nothing requires a new
manual enrollment key for the federation deployment.

## 3. Deploy and verify the host

Use **Terraform development host**, `main`, `plan`. Confirm:

- Existing project volume and deployment identities are preserved.
- Host runtime IAM replaces secret reads with `sts:GetWebIdentityToken`, limited
  to the exact audience, `us-east-1` and at most 300 seconds.
- The old write-only secret-version resource is forgotten with `destroy=false`;
  its value and protected secret container are not deleted. Existing HCP policy
  permissions remain unchanged to avoid a self-management migration.
- Compute/attachment replacement is expected; no account issuer resource appears
  in this stack. Required client ID is real and external trust already exists.

Review the recovery point and quiesce project writes using
[host recovery](recover-dev-host.md). Dispatch the existing confirmed apply.
Cloud-init installs the declared profile (including Podman), then runs the
bootstrap-only enrollment helper using the native Tailscale >=1.94 flags.
Tokens are handled internally by the client; helper output never copies command
output or exception text. It does not modify the host's EC2-only trust policy.

After replacement, verify SSM first, then private SSH/Tailscale access, original
filesystem UUID/ownership, and the profile/rootless/bootstrap receipts described
in [the rootless runbook](manage-rootless-toolchain.md). Confirm the expected
online tag-owned node in Tailscale and record sanitized version/state evidence.
Do not publish raw tokens, credential files or unrestricted status/log dumps.
The acceptance check must prove a fresh host joined without a manually supplied
key; existing-node retry tests alone are insufficient.

## Failure and rollback

On enrollment failure bootstrap remains incomplete. Inspect the client version,
account issuer enablement, exact subject/audience/tag, host IAM and network access.
Use SSM for diagnosis; repair through reviewed code and the pipeline. Never print
token exchange traffic, fall back to the old key or broaden the audience/subject.
The helper's version check fails before enrollment when Tailscale is too old.

A reviewed rollback may restore the previous key-based bootstrap, but requires a
fresh one-use key and a rotation version greater than the previously applied
counter. The preserved old key is not a valid fallback. Preserve the account
issuer and external consumers; trust revocation/issuer teardown requires separate
scope review. Reauthenticate Codex and recreate the host deploy key after root-disk
replacement as described in the recovery runbook.

References: [Tailscale federation](https://tailscale.com/docs/features/workload-identity-federation?tab=aws),
[AWS outbound setup](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound_getting_started.html),
[AWS claims](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound_token_claims.html).
