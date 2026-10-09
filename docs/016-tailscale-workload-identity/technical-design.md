# TDD-016: AWS-to-Tailscale federation

- **Status:** Authorized implementation
- **Specification:** [SPEC-016](spec.md)
- **Tasks:** [Tasks](tasks.md)

AWS account outbound federation is a separate account-wide prerequisite, not an
inbound AWS OIDC provider or change to the EC2 assume-role trust. A separate
`infra/tailscale-federation` root and protected manual workflow own its
`aws_iam_outbound_web_identity_federation` resource with `prevent_destroy`.
A dedicated HCP workspace and scoped operator credential are needed once; never
reuse production credentials or broaden the normal apply role. If already
managed elsewhere, consume its existing issuer and do not adopt it blindly.

After enabling the issuer, Daniel configures Tailscale trust for that exact URL,
subject `arn:aws:iam::<account>:role/gptclaw-dev-host`, write `auth_keys` scope and
only `tag:gptclaw-dev`. Non-secret client ID/audience become development HCP inputs.
The host gets `sts:GetWebIdentityToken` with all audiences constrained to the
configured value, nonempty audience, maximum 300 seconds and configured Region.
Tailscale >=1.94 performs native token discovery and exchange. Request a persistent
preauthorized tag-owned node (`ephemeral=false&preauthorized=true`), avoiding both
offline garbage collection and recurring device approval. Bootstrap invokes
it through a bounded helper with no token output; no extra SDK/runtime is added.

Retain the protected legacy Secrets Manager container and existing deployment
policy permissions to avoid identity maintenance or deletion during migration.
Forget only the write-only secret-version resource with a declarative removed
block and `destroy=false`. Remove auth-key variables/counter and the host's secret
read grant. Rollback requires reviewed code and a fresh key/version, never silently
reusing the retired one. Account issuer teardown is outside routine rollback.

Offline fixtures cover old client, invalid input, token/enrollment command failure,
wrong state/tag and correct enrollment; Terraform checks exact IAM bounds and
rendered helper, size, no-key inputs and storage protection. Remote bootstrap-stack
plan must show only account federation; development plan must preserve identities
and disk. Daniel reports successful replacement and Tailscale connection on October 9;
actual deployed receipts and the full enrollment criteria remain pending verification.

Sources checked October 1, 2026:
- [Tailscale federation](https://tailscale.com/docs/features/workload-identity-federation?tab=aws)
- [AWS setup](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound_getting_started.html)
- [AWS claims](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound_token_claims.html)
- [Pinned AWS provider resource](https://github.com/hashicorp/terraform-provider-aws/blob/v6.63.0/website/docs/r/iam_outbound_web_identity_federation.html.markdown)

All requirements map to the implementation/tests above and tasks T-001–T-004;
AC-003/AC-004 require live operator evidence and cannot pass from local tests.
