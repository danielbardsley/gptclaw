# Bootstrap HCP Terraform, AWS trust, and GitHub

This runbook bootstraps the trust required by the development-host pipeline.
Every AWS mutation—including the OIDC provider, deployment roles, Tailscale
secret, EC2, VPC, EBS, and runtime IAM—is made by committed Terraform through
GitHub Actions and the `gptclaw-dev-host` HCP workspace. No AWS console, CLI, or
local Terraform mutation is permitted.

Do not record token values, Tailscale keys, AWS access keys, device codes, or
complete environment dumps while following this runbook.

## Required values

| Value | Requirement |
|---|---|
| AWS account ID | Explicitly approved 12-digit target |
| AWS region | Explicitly approved region |
| Availability Zone | Fixed before the project volume is created |
| HCP organization | Existing organization at `app.terraform.io` |
| HCP project | Existing project or a new `gptclaw` project |
| HCP workspace | `gptclaw-dev-host` |
| Tailscale tag | `tag:gptclaw-dev` unless deliberately changed |
| Desktop SSH public key | Dedicated key; never the private half |

## 1. Verify the bootstrap identity

Use an already-authorized AWS administrator session and confirm the account and
region before making changes:

```sh
aws sts get-caller-identity
aws configure get region
```

Stop if either value differs from the approved input. Do not make the Terraform
apply role an administrator.

## 2. Create the HCP Terraform workspace

In the approved HCP organization and project, create `gptclaw-dev-host` with:

- Execution mode: **Remote**
- Workflow: **CLI-driven**, with no VCS connection
- Auto apply: **Off**
- Working directory: blank
- Terraform version: `1.16.1`

If HCP does not yet offer `1.16.1`, select one supported `1.16.x` version and
update `.terraform-version`, `versions.tf`, the workflow variable, and all
planning documents in the same pull request.

## 3. Bootstrap HCP-to-AWS trust through the pipeline

Add the existing authorized AWS credential to the HCP workspace only as
sensitive environment variables:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Do not add them to GitHub, Terraform input variables, local files, or shell
history. The credential exists only to authorize the first GitHub-triggered HCP
apply. `infra/dev-host/hcp_identity.tf` creates the OIDC provider and two roles:

- `gptclaw-dev-hcp-plan`
- `gptclaw-dev-hcp-apply`

Their trust uses `sts:AssumeRoleWithWebIdentity`, the sole audience
`aws.workload.identity`, and the exact HCP organization, project, workspace, and
run phase:

```json
{
  "StringEquals": {
    "app.terraform.io:aud": "aws.workload.identity",
    "app.terraform.io:sub": "organization:<ORG>:project:<PROJECT>:workspace:gptclaw-dev-host:run_phase:<plan-or-apply>"
  }
}
```

The plan role receives only refresh/data-source reads. The apply role receives
the declared EC2, EBS, VPC, host-IAM, Logs, secret, tagging, and scoped
`iam:PassRole` operations. It cannot modify itself, the plan role, or the OIDC
provider. All three identities and their policies have destruction protection.

After the first successful apply, configure the dynamic variables in section 4
and delete both static AWS variables. A later OIDC or deployment-policy change
requires temporarily restoring an authorized bootstrap credential, but the
change must still flow through pull request, GitHub Actions, and HCP Terraform.

## 4. Configure HCP workspace variables

Before the first apply, the only AWS environment variables are the two sensitive
bootstrap variables from section 3. After that apply, add:

| Name | Value |
|---|---|
| `TFC_AWS_PROVIDER_AUTH` | `true` |
| `TFC_AWS_PLAN_ROLE_ARN` | Exact plan-role ARN |
| `TFC_AWS_APPLY_ROLE_ARN` | Exact apply-role ARN |

Then delete `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` before queuing the
OIDC verification plan.

Terraform variables:

- `aws_account_id`
- `aws_region`
- `availability_zone`
- `desktop_ssh_public_key`
- `tailscale_auth_key` (sensitive)

`tailscale_auth_key` is an ephemeral Terraform variable and is written through
the AWS provider's write-only secret argument, so its value is not stored in
Terraform state. Set `tailscale_auth_key_version` to `1`; increment it whenever
the key is rotated.

The workflow supplies `deployment_revision`; the remaining variables have safe
defaults documented in `infra/dev-host/terraform.tfvars.example`.

## 5. Prepare Tailscale enrollment

In the tailnet policy:

1. Assign an owner for `tag:gptclaw-dev`.
2. Permit only the approved owner identity or desktop device to reach that tag
   on TCP 22.
3. Create a tagged, pre-authorized, non-ephemeral, one-use auth key.
4. Store the key only in the sensitive HCP Terraform variable
   `tailscale_auth_key`.
5. Let the first pipeline apply create the AWS Secrets Manager secret and write
   its value without persisting that value in Terraform state.

Create a fresh one-use key immediately before initial creation or instance
replacement. The host consumes the value once and retains Tailscale node state
on reboot.

## 6. Configure GitHub

HCP Terraform Free exposes only the owners team. Create two short-lived owners
team tokens for independent rotation, then store both only in the protected
GitHub `development` environment:

| GitHub location | Name | Capability |
|---|---|---|
| `development` environment secret | `TF_API_TOKEN_PLAN` | Manual `main` plan |
| `development` environment secret | `TF_API_TOKEN_APPLY` | Manual `main` apply |

Both tokens have owner capability on the Free tier. Never store either as a
repository secret or expose either to pull-request jobs.

Create repository variables:

| Name | Value |
|---|---|
| `HCP_TERRAFORM_ORGANIZATION` | Approved organization |
| `HCP_TERRAFORM_WORKSPACE` | `gptclaw-dev-host` |
| `TERRAFORM_VERSION` | `1.16.1` |

Configure required reviewers on the `development` environment when the GitHub
plan supports them. The exact manual confirmation remains mandatory either way.

## 7. Preflight

Before the first apply, confirm:

- The plan token is present only in the GitHub `development` environment; its
  owners-team scope is an accepted HCP Free limitation.
- The temporary bootstrap AWS variables are sensitive HCP environment variables.
- The plan reports the approved region and fixed availability zone.
- The apply token is unavailable to pull-request jobs.
- No AWS credential is configured in GitHub Actions.
- HCP auto-apply remains disabled.

After the first apply, confirm:

- HCP reports the output ARNs for `gptclaw-dev-hcp-plan` and
  `gptclaw-dev-hcp-apply`.
- Both static AWS variables have been deleted from HCP.
- A new GitHub-triggered plan assumes `gptclaw-dev-hcp-plan` and reports no
  infrastructure changes.
- The apply phase assumes `gptclaw-dev-hcp-apply` only after the GitHub gate.

Retain links to the GitHub and HCP runs. Do not retain raw credentials or full
environment output.
