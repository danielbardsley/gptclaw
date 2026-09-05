# Bootstrap HCP Terraform, AWS trust, and GitHub

This runbook creates the one-time trust anchors required before the development
host pipeline can run. It does not create EC2, VPC, EBS, or runtime IAM
resources manually. Those resources are owned exclusively by Terraform in the
`gptclaw-dev-host` workspace.

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

## 3. Establish HCP-to-AWS OIDC trust

The reviewed bootstrap resources are defined in
`bootstrap/aws/hcp-terraform.yaml`. Deploy that stack from an authorized AWS
administrator session in the approved region:

```sh
aws cloudformation deploy \
  --region us-east-1 \
  --stack-name gptclaw-hcp-bootstrap \
  --template-file bootstrap/aws/hcp-terraform.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

The stack creates the OIDC provider, phase-specific plan/apply roles, and an
empty retained Secrets Manager secret. It does not create the development VPC,
EC2 host, EBS project volume, or host runtime role.

Create or reuse the AWS IAM OIDC provider with:

- Provider URL: `https://app.terraform.io` without a trailing slash
- Audience: `aws.workload.identity`

Create two roles:

- `gptclaw-dev-hcp-plan`
- `gptclaw-dev-hcp-apply`

Each trust policy must use `sts:AssumeRoleWithWebIdentity`, match the audience,
and match the exact HCP organization, project, workspace, and run phase:

```json
{
  "StringEquals": {
    "app.terraform.io:aud": "aws.workload.identity",
    "app.terraform.io:sub": "organization:<ORG>:project:<PROJECT>:workspace:gptclaw-dev-host:run_phase:<plan-or-apply>"
  }
}
```

The plan role receives only the read operations needed for refresh and data
sources. The apply role receives only the EC2, EBS, VPC, IAM, Logs, tagging, and
`iam:PassRole` operations required by `infra/dev-host`; `iam:PassRole` must be
restricted to the GptClaw EC2 role. Add a denied permission only after a failed
run identifies the exact missing action and resource.

Static AWS access keys are not a fallback.

## 4. Configure HCP workspace variables

Environment variables:

| Name | Value |
|---|---|
| `TFC_AWS_PROVIDER_AUTH` | `true` |
| `TFC_AWS_PLAN_ROLE_ARN` | Exact plan-role ARN |
| `TFC_AWS_APPLY_ROLE_ARN` | Exact apply-role ARN |

Terraform variables:

- `aws_account_id`
- `aws_region`
- `availability_zone`
- `desktop_ssh_public_key`
- `tailscale_auth_secret_arn`

The workflow supplies `deployment_revision`; the remaining variables have safe
defaults documented in `infra/dev-host/terraform.tfvars.example`.

## 5. Prepare Tailscale enrollment

In the tailnet policy:

1. Assign an owner for `tag:gptclaw-dev`.
2. Permit only the approved owner identity or desktop device to reach that tag
   on TCP 22.
3. Create a tagged, pre-authorized, non-ephemeral, one-use auth key.
4. Store only the key value in an AWS Secrets Manager secret in the target
   account and region.
5. Record the secret ARN, never the value.

Create a fresh one-use key immediately before initial creation or instance
replacement. The host consumes the value once and retains Tailscale node state
on reboot.

## 6. Configure GitHub

Create HCP team or service-account tokens with workspace-specific permissions:

| GitHub location | Name | Capability |
|---|---|---|
| Repository secret | `TF_API_TOKEN_PLAN` | Queue/read plans only |
| `development` environment secret | `TF_API_TOKEN_APPLY` | Queue/apply runs |

Create repository variables:

| Name | Value |
|---|---|
| `HCP_TERRAFORM_ORGANIZATION` | Approved organization |
| `HCP_TERRAFORM_WORKSPACE` | `gptclaw-dev-host` |
| `TERRAFORM_VERSION` | `1.16.1` |

Configure required reviewers on the `development` environment when the GitHub
plan supports them. The exact manual confirmation remains mandatory either way.

## 7. Preflight

Before merging the implementation pull request, confirm:

- The plan token can queue a speculative run only in `gptclaw-dev-host`.
- The plan phase assumes `gptclaw-dev-hcp-plan` in the approved account.
- The plan reports the approved region and fixed availability zone.
- The apply token is unavailable to pull-request jobs.
- No AWS credential is configured in GitHub Actions.
- HCP auto-apply remains disabled.

Retain links to the GitHub and HCP runs. Do not retain raw credentials or full
environment output.
