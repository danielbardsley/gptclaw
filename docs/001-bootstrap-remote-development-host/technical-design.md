# TDD-001: Bootstrap the Remote Development Host

- **Status:** Ready for implementation
- **Owner:** Daniel
- **Source:** [SPEC-001](./spec.md)
- **Implementation tasks:** [TASKS-001](./tasks.md)
- **Repository:** `danielbardsley/gptclaw`
- **Last updated:** 2026-09-05

## 1. Purpose

This document turns SPEC-001 into an implementation-ready design. It defines the secure path from a reviewed Git revision to a persistent AWS development host, and from the ChatGPT desktop app to that host through Tailscale and OpenSSH.

It covers only the first host and connection. Slack control, reusable project templates, application runtimes, previews, Expo, and production deployment remain out of scope.

The resulting host is the execution foundation for those later capabilities.
This design permits `forge` to edit repositories, run development tools, and
install unprivileged project or user dependencies. It deliberately withholds
unrestricted system administration and production AWS access; later designs
will add controlled software installation, isolated service runtimes, preview
exposure, steering files, and production promotion without weakening that
boundary.

## 2. Decisions

| ID | Decision | Reason |
|---|---|---|
| D-001 | GitHub Actions is the only Terraform client. | Every plan and apply is tied to an auditable revision. |
| D-002 | HCP workspace `gptclaw-dev-host` performs remote execution and stores state. | AWS credentials stay at the execution boundary. |
| D-003 | PRs plan; a manual dispatch from `main` applies. | Safe even without GitHub environment reviewers. |
| D-004 | HCP uses separate plan/apply AWS roles through OIDC. | Credentials are temporary and phase-specific. |
| D-005 | GitHub uses separate HCP plan/apply tokens. | PR code never receives apply capability. |
| D-006 | EC2 uses a public subnet/public IPv4 with zero security-group ingress. | Outbound services work without NAT gateway cost; the public address is not an access path. |
| D-007 | Project data uses a separate encrypted EBS volume with destruction protection. | Compute replacement cannot silently delete repositories. |
| D-008 | Tailscale uses a tagged, pre-authorized, one-use key read from Secrets Manager. | The value stays out of Git, GitHub, user data, and Terraform state. |
| D-009 | Standard OpenSSH runs over Tailscale; Tailscale SSH is disabled. | Matches ChatGPT's SSH connection model. |
| D-010 | `forge` is not a sudoer. | Project and user-scoped tooling remains available while system changes stay behind a controlled administrative path. |
| D-011 | Bootstrap uses cloud-init/systemd, not Terraform provisioners. | Terraform never needs inbound SSH. |
| D-012 | This release uses one Terraform root module. | Module extraction follows demonstrated reuse. |
| D-013 | A rendered-bootstrap change replaces compute while preserving project EBS. | Bootstrap changes take effect predictably instead of leaving declared and actual host state different. |

## 3. Architecture

### 3.1 Deployment

~~~text
Developer -> branch / pull request
    |
    v
GitHub: danielbardsley/gptclaw
    |
    | plan token or protected apply token
    v
GitHub Actions
    |
    | Terraform CLI 1.16.1
    v
HCP Terraform: gptclaw-dev-host
    |
    | OIDC, phase-specific AWS role
    v
Target AWS account (development resources only)
    +-- VPC, subnet, route, security group
    +-- IAM instance role/profile
    +-- encrypted root and persistent data volumes
    +-- EC2 instance
    +-- CloudWatch logs
    `-- Systems Manager managed node
~~~

The runner packages `infra/dev-host` and requests a remote plan or apply. Provider operations happen in HCP Terraform. GitHub receives no AWS access key.

### 3.2 Runtime

~~~text
ChatGPT desktop on Windows
    |
    | explicit alias forge-dev, OpenSSH over Tailscale
    v
forge-dev-01
    +-- sshd -> forge
    +-- Codex CLI in forge login PATH
    +-- /srv/forge/projects/gptclaw on persistent EBS
    `-- SSM Agent -> break-glass administration
~~~

ChatGPT starts the remote Codex app server through SSH. No app-server listener is exposed publicly.

## 4. Repository layout

~~~text
.github/
  dependabot.yml
  workflows/terraform-dev-host.yml
docs/
  README.md
  001-bootstrap-remote-development-host/
    spec.md
    technical-design.md
    tasks.md
infra/dev-host/
  .terraform-version
  .terraformignore
  .terraform.lock.hcl
  versions.tf
  providers.tf
  variables.tf
  locals.tf
  data.tf
  network.tf
  iam.tf
  logs.tf
  storage.tf
  compute.tf
  outputs.tf
  terraform.tfvars.example
  templates/
    cloud-init.yaml.tftpl
    bootstrap-forge.sh.tftpl
  tests/
    defaults.tftest.hcl
    security.tftest.hcl
runbooks/
  bootstrap-hcp-aws.md
  connect-chatgpt.md
  recover-dev-host.md
scripts/verify-dev-host.sh
.gitignore
~~~

The provider lock file is committed. State, plans, overrides, crash logs, and `.terraform/` are ignored. Account values do not go in a committed `terraform.tfvars`.

## 5. Terraform design

### 5.1 Versions and HCP connection

Initial pins:

- Terraform CLI and HCP workspace: `1.16.1`.
- AWS provider: `~> 6.62`; lock file pins the selected patch.
- cloud-init provider: `~> 2.4`.

The exact Terraform version appears in `.terraform-version`, `required_version`, the workflow, and HCP workspace. Dependabot proposes action/provider updates.

~~~hcl
terraform {
  required_version = "= 1.16.1"

  cloud {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.62"
    }
    cloudinit = {
      source  = "hashicorp/cloudinit"
      version = "~> 2.4"
    }
  }
}
~~~

The workflow supplies `TF_CLOUD_ORGANIZATION` and `TF_WORKSPACE=gptclaw-dev-host`. The workspace uses remote execution, has no direct VCS connection, has auto-apply disabled, and has no working-directory prefix. Terraform runs from `infra/dev-host`, which becomes the uploaded configuration root. Failed HCP initialization fails the job; local execution is not a fallback.

### 5.2 Variables

| Variable | Default/source | Validation |
|---|---|---|
| `aws_account_id` | Required HCP variable | Exactly 12 digits. |
| `aws_region` | Required HCP variable | Approved enabled region. |
| `availability_zone` | Required HCP variable | In region; immutable after data volume creation. |
| `project_name` | `gptclaw` | Naming-safe lowercase. |
| `environment` | `development` | Only `development`. |
| `instance_name` | `forge-dev-01` | Valid hostname. |
| `instance_type` | `t3.large` | Initially allowlisted to T3 general-purpose sizes. |
| `vpc_cidr` | `10.42.0.0/16` | RFC1918 CIDR. |
| `subnet_cidr` | `10.42.10.0/24` | Inside VPC CIDR. |
| `root_volume_size_gib` | `30` | Minimum 20. |
| `data_volume_size_gib` | `80` | Minimum 40; shrinking rejected. |
| `desktop_ssh_public_key` | Required HCP variable | Approved public key; private-key markers rejected. |
| `tailscale_auth_secret_arn` | Required HCP variable | Secrets Manager ARN in target account/region. |
| `tailscale_tag` | `tag:gptclaw-dev` | Starts with `tag:`. |
| `deployment_revision` | GitHub SHA | 40 lowercase hex characters. |
| `log_retention_days` | `14` | Allowed CloudWatch retention value. |

`terraform.tfvars.example` documents names and safe examples only.

### 5.3 Provider guardrails and tags

~~~hcl
provider "aws" {
  region              = var.aws_region
  allowed_account_ids = [var.aws_account_id]

  default_tags {
    tags = local.common_tags
  }
}

data "aws_caller_identity" "current" {}
~~~

A check also asserts caller account equals `var.aws_account_id`.

| Common tag | Value |
|---|---|
| `Project` | `GptClaw` |
| `Environment` | `development` |
| `ManagedBy` | `Terraform` |
| `Repository` | `danielbardsley/gptclaw` |
| `TerraformWorkspace` | `gptclaw-dev-host` |
| `Owner` | `Daniel` |
| `DeploymentRevision` | Git SHA |

### 5.4 Resources

| Address | Object | Important configuration |
|---|---|---|
| `aws_vpc.dev` | VPC | DNS support/hostnames enabled. |
| `aws_internet_gateway.dev` | Gateway | Outbound internet. |
| `aws_subnet.dev_public` | Single-AZ subnet | Public IPv4 assignment; fixed AZ. |
| `aws_route_table.dev_public` | Route table | IPv4 default route to gateway. |
| `aws_route_table_association.dev_public` | Association | Development subnet. |
| `aws_security_group.dev_host` | Security group | No ingress; initial unrestricted egress. |
| `aws_cloudwatch_log_group.dev_host` | Log group | `/gptclaw/development/forge-dev-01`, 14 days. |
| `aws_iam_role.dev_host` | EC2 role | EC2 trust only; no production role path. |
| `aws_iam_instance_profile.dev_host` | Profile | Attaches host role. |
| `aws_ebs_volume.projects` | Persistent gp3 | 80 GiB, encrypted, `prevent_destroy`. |
| `aws_instance.dev_host` | Ubuntu host | T3.large, IMDSv2, encrypted root, no EC2 key pair. |
| `aws_volume_attachment.projects` | Attachment | No forced detach. |

No Elastic IP, NAT gateway, load balancer, DNS record, or inbound security-group rule is created.

### 5.5 Network

The subnet is public only for outbound access. The instance gets a changing public IPv4 address but zero security-group ingress. That address is not an operator endpoint or Terraform output.

Initial egress is unrestricted because Ubuntu mirrors, GitHub, OpenAI, AWS APIs, Tailscale coordination/DERP, DNS, and time services use changing destinations and protocols. This bootstrap tradeoff is revisited after measuring traffic.

Tailscale may relay when direct inbound UDP is unavailable. No public UDP ingress is added for performance.

### 5.6 Compute

The AMI comes from Canonical's regional SSM parameter:

`/aws/service/canonical/ubuntu/server/noble/stable/current/amd64/hvm/ebs-gp3/ami-id`

Configuration:

- Ubuntu 24.04 LTS x86-64.
- `t3.large` default.
- 30 GiB encrypted gp3 root, deleted with instance.
- Separate project volume.
- No EC2 key pair.
- Shutdown behavior `stop`.
- IMDS enabled, tokens required, hop limit 1.
- cloud-init rendered through the cloud-init provider.
- `user_data_replace_on_change = true`.

AMI, architecture, subnet AZ, data-volume AZ, and rendered bootstrap changes are
replacement-class and require an explicit migration plan. Replacing compute is
preferred to silently accepting bootstrap drift; project data remains on the
protected EBS volume. Before any replacement, the operator must snapshot or
verify the project volume and place a fresh one-use Tailscale key in the existing
secret.

### 5.7 Persistent storage

`aws_ebs_volume.projects` is separate, encrypted with the AWS-managed EBS key, and protected with `prevent_destroy = true`.

A systemd oneshot unit:

1. Waits for the supplied EBS volume ID.
2. Resolves the Nitro NVMe device by volume ID.
3. Creates ext4 only if no filesystem signature exists.
4. Labels it `FORGE_DATA`.
5. Adds an idempotent `/etc/fstab` UUID entry.
6. Mounts at `/srv/forge`.
7. Creates `/srv/forge/projects` as `forge:forge`, mode `0750`.

Existing filesystems are never formatted. Storage ambiguity fails clearly and leaves SSM available.

### 5.8 Instance IAM

The host role receives:

- `AmazonSSMManagedInstanceCore`.
- Custom log permissions limited to its log group.
- `secretsmanager:GetSecretValue` and `DescribeSecret` on the exact Tailscale ARN.

It receives no IAM mutations, production role assumption, broad secret access, or profile changes.

The Terraform apply role may pass only the GptClaw host role. Resources use `gptclaw-dev-` names and project tags; resource/tag conditions are applied where AWS supports them.

### 5.9 Logs and outputs

CloudWatch Agent publishes cloud-init output, `/var/log/auth.log`, and bootstrap service output. Shell tracing is disabled around credentials. Retention is 14 days.

Non-secret outputs:

- `instance_id`
- `availability_zone`
- `data_volume_id`
- `cloudwatch_log_group_name`
- `ssm_start_session_command`
- `expected_tailscale_hostname`
- `deployment_revision`

## 6. Identity and bootstrap

### 6.1 One-time boundary

HCP cannot assume an AWS role until its AWS trust exists. With an existing authorized AWS identity, the owner:

1. Verifies account and region.
2. Creates/reuses the AWS OIDC provider for `https://app.terraform.io`, audience `aws.workload.identity`.
3. Creates `gptclaw-dev-hcp-plan` and `gptclaw-dev-hcp-apply`.
4. Restricts trust to exact HCP organization, project, workspace, and phase.
5. Creates/configures `gptclaw-dev-host`.
6. Stores a tagged one-use Tailscale key in Secrets Manager.
7. Creates/rotates HCP team tokens for GitHub.

`runbooks/bootstrap-hcp-aws.md` documents this. It is outside dev-host state to avoid a circular trust dependency. No EC2 resource is created manually.

### 6.2 HCP-to-AWS OIDC

Plan trust:

~~~json
{
  "StringEquals": {
    "app.terraform.io:aud": "aws.workload.identity",
    "app.terraform.io:sub": "organization:<org>:project:<project>:workspace:gptclaw-dev-host:run_phase:plan"
  }
}
~~~

Apply trust substitutes `run_phase:apply`. Organization, project, and workspace do not use wildcards.

| HCP environment variable | Value |
|---|---|
| `TFC_AWS_PROVIDER_AUTH` | `true` |
| `TFC_AWS_PLAN_ROLE_ARN` | Exact plan role ARN |
| `TFC_AWS_APPLY_ROLE_ARN` | Exact apply role ARN |

Plan gets only describe/get/list operations needed by refresh/data sources. Apply gets the EC2, EBS, VPC, IAM, Logs, tagging, and `iam:PassRole` actions required by declared resources. Permission errors are fixed by adding the smallest missing permission, never administrator access.

### 6.3 GitHub-to-HCP

This design implements SPEC-001's split GitHub-to-HCP credential boundary:

| Secret | Location | HCP permission | Job |
|---|---|---|---|
| `TF_API_TOKEN_PLAN` | Repository secret | Plan-only on workspace | PR/main plan |
| `TF_API_TOKEN_APPLY` | `development` environment | Apply on workspace | Manual apply |

Each secret is passed only to the `cli_config_credentials_token` input of `hashicorp/setup-terraform` for its job. The action writes an ephemeral Terraform CLI credential configuration; the workflow does not export the token as a general-purpose environment variable. Team-scoped tokens are preferred over personal tokens.

| GitHub variable | Value |
|---|---|
| `HCP_TERRAFORM_ORGANIZATION` | Supplied organization |
| `HCP_TERRAFORM_WORKSPACE` | `gptclaw-dev-host` |
| `TERRAFORM_VERSION` | `1.16.1` |

No AWS credential exists in this workflow. Stale AWS secrets are ignored and removed only after verifying no other workflow uses them.

### 6.4 Failure handling

| Failure | Remediation |
|---|---|
| HCP plan token 401/403 | Rotate `TF_API_TOKEN_PLAN`; do not alter AWS. |
| HCP apply token rejected | Rotate `TF_API_TOKEN_APPLY`; redispatch. |
| OIDC denied | Match organization/project/workspace/phase exactly. |
| Read API denied | Add only the required plan action. |
| Mutation denied | Add only the required apply action/resource. |
| Wrong account/region | Correct input; never relax account allowlist. |
| Tailscale key consumed early | Store new one-use key; rerun enrollment via SSM. |

## 7. GitHub workflow

### 7.1 Triggers

| Event | Ref | Behavior |
|---|---|---|
| PR changing infrastructure/workflow | PR head | Format, validate, test, speculative plan |
| Push changing those paths | `main` | Format, validate, test, speculative plan |
| Manual `plan` | Current `main` | Speculative plan |
| Manual `apply` plus confirmation `gptclaw-dev-host` | Current `main` only | Validate and remote apply |

Apply rejects non-main refs, tags, stale SHAs, and wrong confirmation. It uses the `development` environment. Required reviewers are enabled when supported; manual dispatch and exact confirmation remain mandatory.

### 7.2 Security and jobs

~~~yaml
permissions:
  contents: read
~~~

Checkout sets `persist-credentials: false`. `id-token: write` is not needed because AWS trusts HCP, not GitHub. `actions/checkout` and `hashicorp/setup-terraform` are pinned to full commit SHAs with nearby version comments; Dependabot checks weekly.

~~~text
quality
  |- terraform fmt -check -recursive
  |- terraform init -input=false
  |- terraform validate
  `- terraform test
          |
          +--> plan: terraform plan -input=false -no-color
          |
          `--> manual apply gate
                 |- ref == main
                 |- SHA == current origin/main
                 |- confirmation == gptclaw-dev-host
                 `- environment == development
                           |
                           `--> terraform apply -input=false -auto-approve
~~~

Concurrency group is `terraform-gptclaw-dev-host`; cancellation is disabled.

### 7.3 Traceability

`TF_VAR_deployment_revision` contains the exact Git SHA. Terraform tags resources and outputs it. The job summary records only Git SHA, actor, event, workspace, and HCP run URL. Plan files and plan JSON are not uploaded.

## 8. Host bootstrap

### 8.1 Cloud-init

Idempotent phases:

1. Set hostname/package defaults.
2. Install Git, curl, jq, unzip, certificates, AWS CLI, UFW, and CloudWatch Agent.
3. Verify/start SSM Agent.
4. Create `forge` without sudo.
5. Install desktop public key.
6. Write/start persistent-volume mount unit.
7. Install Tailscale stable.
8. Write/start enrollment unit.
9. Harden OpenSSH/UFW.
10. Install Codex for `forge`.
11. Start log shipping.
12. Write `/var/lib/gptclaw/bootstrap-complete.json` with the bootstrap version,
    time, status, and installed non-secret component versions only.

Phases log start/success/failure without environment dumps. Failures preserve SSM wherever possible.

### 8.2 Tailscale

Before deployment, configure tag `tag:gptclaw-dev`, ownership, and access from the owner's identity/device to that tag on TCP 22. Create a tagged, pre-authorized, non-ephemeral, one-use auth key and store exactly that value in Secrets Manager.

Terraform receives only the ARN. The host retrieves the value with its role and runs without shell tracing:

~~~text
tailscale up --auth-key=<in-memory-value> \
  --hostname=forge-dev-01 \
  --advertise-tags=tag:gptclaw-dev \
  --ssh=false
~~~

The variable is cleared. Reboots reuse node state and do not retrieve the key. Before replacement, store a fresh one-use key.

### 8.3 SSH

The SSH drop-in sets:

- `PermitRootLogin no`
- `PasswordAuthentication no`
- `KbdInteractiveAuthentication no`
- `PubkeyAuthentication yes`
- `AuthenticationMethods publickey`
- `AllowUsers forge`
- `X11Forwarding no`
- `AllowTcpForwarding local`

UFW denies incoming, allows outgoing, and permits TCP 22 only on `tailscale0`. AWS ingress remains empty. `forge` SSH directory/file modes are `0700`/`0600`.

### 8.4 Codex

The official standalone Linux installer runs as `forge` noninteractively. Bootstrap verifies:

~~~text
sudo -iu forge command -v codex
sudo -iu forge codex --version
sudo -iu forge sh -lc 'command -v codex'
~~~

The login-shell check matters because ChatGPT launches the remote app server through that shell.

Authentication is post-deployment:

1. Enter through SSM or Tailscale.
2. Switch to a `forge` login shell.
3. Confirm device-code login is enabled in ChatGPT security or workspace settings.
4. Run `codex login --device-auth` and complete the browser flow.
5. Verify `codex login status`.
6. If device-code login is unavailable, forward the standard localhost callback
   over SSH and run `codex login`; do not copy an authentication cache as the
   normal fallback.
7. If file-based credential storage is used, verify `~/.codex` is `0700` and
   credential files are `0600`.

Credentials never enter Terraform, cloud-init, Secrets Manager, Git, or evidence.

The documented fallback starts a local forward from the desktop with
`ssh -L 1455:localhost:1455 forge-dev`, then runs `codex login` in that SSH
session and completes the browser flow on the desktop.

### 8.5 GitHub from EC2

The Windows deploy key is never copied to EC2:

1. As `forge`, generate `~/.ssh/id_ed25519_gptclaw`.
2. Verify GitHub's published SSH fingerprint and create `known_hosts`.
3. Add the public key as write-enabled deploy key `GptClaw forge-dev-01`.
4. Configure a repo-specific alias with `IdentitiesOnly yes`.
5. Clone to `/srv/forge/projects/gptclaw`.
6. Verify `main` and clean status.

The EC2 private key is `0600`.

## 9. Desktop connection

Create a dedicated desktop-to-host pair, separate from both GitHub keys:

~~~text
C:\Users\danie\.ssh\id_ed25519_forge_dev
C:\Users\danie\.ssh\id_ed25519_forge_dev.pub
~~~

Only the public half enters Terraform.

~~~sshconfig
Host forge-dev
    HostName forge-dev-01
    User forge
    IdentityFile C:/Users/danie/.ssh/id_ed25519_forge_dev
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
~~~

Use the full `.ts.net` hostname if needed. Validate `ssh forge-dev`, then add it under ChatGPT **Settings -> Connections -> SSH** and select `/srv/forge/projects/gptclaw`.

## 10. Security model

| Boundary | Credential | Control |
|---|---|---|
| GitHub -> HCP | Plan/apply token | Split capability; apply secret protected |
| HCP -> AWS | OIDC identity | Exact audience/subject; short-lived STS |
| EC2 -> AWS | Instance profile | SSM, one log group, one Tailscale secret |
| Windows -> EC2 | Dedicated SSH key | Tailscale policy, UFW, public-key-only SSH |
| EC2 -> GitHub | Separate deploy key | One repo and strict file modes |
| EC2 -> OpenAI | Device-auth session | `forge`-only files |

| Threat | Controls |
|---|---|
| Internet SSH scan | Zero SG ingress; UFW limits SSH to `tailscale0`. |
| Workflow compromise | Read-only GitHub token, SHA-pinned actions, plan-only PR token, no AWS secrets. |
| HCP token theft | Workspace-scoped split tokens and rotation. |
| Cross-account apply | Account allowlist plus caller assertion. |
| HCP tenant confusion | Exact org/project/workspace/phase trust. |
| Host compromise | No production role/sudo; consumed Tailscale key; narrow role. |
| Compute replacement loss | Separate encrypted EBS and `prevent_destroy`. |
| Secret leakage | ARN only; no plan artifacts, tracing, or environment dumps. |
| Supply-chain change | Exact Terraform/action pins, provider lock file, official package sources, captured installed versions, and reviewed updates. |

## 11. Operations and recovery

### 11.1 Normal change

1. Branch and change code.
2. Review PR remote plan.
3. Merge to `main`.
4. Review main plan.
5. Dispatch `apply` with `gptclaw-dev-host`.
6. Verify GitHub, HCP, AWS, SSM, and Tailscale evidence.

No local apply is permitted.

### 11.2 Failure

- Authentication: rotate/correct the relevant identity.
- Authorization: add the narrow missing role action.
- Capacity: change instance type; do not change AZ after volume creation without migration.
- Cloud-init: inspect via SSM, repair the idempotent unit, update source.

Rerun plan after every repair.

### 11.3 Replacement/recovery

Before replacement:

1. Ensure the plan keeps `aws_ebs_volume.projects`.
2. Create/verify an EBS snapshot.
3. Store a fresh Tailscale key.
4. Quiesce project writes.
5. Apply and verify attachment, UUID, Git, SSM, Tailscale, and Codex.

Recovery creates a same-AZ volume from a verified snapshot, imports/references it through reviewed Terraform, mounts read-only for inspection, then returns it to service. Removing `prevent_destroy` requires a dedicated PR.

Codex auth and the EC2 GitHub key initially remain on root and may require reauthentication after replacement. This favors explicit authentication over silently relocating credentials.

Session Manager is the break-glass path independent of Tailscale/desktop SSH. Manual repairs are logged and reconciled into source.

## 12. Verification

### 12.1 Pull request

- `terraform fmt -check -recursive`
- `terraform init -input=false`
- `terraform validate`
- `terraform test` with mocks
- Full action SHA check
- Secret-pattern scan
- Speculative HCP plan

Tests assert zero ingress, encrypted volumes, data-volume protection, IMDSv2, no EC2 key pair, same AZ, required tags, and expected defaults.

### 12.2 Post-apply

The workflow records HCP success, outputs, account/region, and revision. Sanitized host checks:

~~~text
cloud-init status --wait
systemctl is-active amazon-ssm-agent
systemctl is-active tailscaled
tailscale status
findmnt /srv/forge
sudo -iu forge sh -lc 'command -v codex && codex --version'
sudo -iu forge git -C /srv/forge/projects/gptclaw status --short --branch
~~~

### 12.3 End to end

From ChatGPT on `forge-dev`:

1. Open `/srv/forge/projects/gptclaw`.
2. Create `connection-test.md` with hostname and UTC time.
3. Run `hostname` and `date -u`.
4. Display the diff.
5. Remove the file.
6. Confirm a clean tree.

Evidence contains statuses, resource IDs, Git SHA, GitHub run URL, and HCP run URL—not secrets or full environments.

## 13. Implementation stages

1. **Repository:** layout, ignores, versions, lock, tests, workflow skeleton.
2. **Identity:** HCP workspace, GitHub environment, split HCP tokens, AWS OIDC roles.
3. **AWS:** guardrails, network, IAM, logs, storage, EC2.
4. **Bootstrap:** cloud-init, mount, SSM, Tailscale, SSH, Codex.
5. **Plan:** repair stale credentials/read permissions.
6. **Apply:** gated manual run from `main`.
7. **Enrollment:** verify host, add EC2 GitHub key, clone, authenticate Codex.
8. **Desktop:** create separate key, alias, ChatGPT connection.
9. **Acceptance:** retain evidence and verify a no-change plan.

Each stage updates its runbook with its code.

## 14. Inputs required

| Input | Proposed | Status |
|---|---|---|
| AWS account ID | `571748613148` | Confirmed from the active AWS identity |
| AWS region | `us-east-1` | Confirmed from the active AWS configuration |
| Availability Zone | None | Required/sticky |
| HCP organization | `Bardsley` | Confirmed |
| HCP project | `gptclaw` | Created with dedicated `gptclaw-dev-host` workspace |
| HCP token capability | Separate plan/apply | Verify |
| GitHub environment reviewers | Existing plan | Verify |
| Tailscale tailnet | Existing | Required |
| Tailscale tag | `tag:gptclaw-dev` | Confirm |
| Tailscale secret ARN | None | Required |
| Desktop Tailscale enrollment | Existing tailnet | Sign-in required |
| Desktop SSH public key | Dedicated `id_ed25519_forge_dev` key | Generated locally; public half pending HCP configuration |
| ChatGPT SSH connection feature | Current desktop app | Supported by current OpenAI documentation; connection pending host deployment |
| ChatGPT device-code login | Preferred; SSH callback fallback | Verify |

These are configuration inputs, not architecture changes.

## 15. Traceability

| Requirement | Design sections |
|---|---|
| CICD-001 | 2, 7, 11.1 |
| CICD-002 | 7.1-7.3 |
| CICD-003 | 5.1, 7.2, 12.1 |
| TFC-001 | 3.1, 5.1, 6.1 |
| TFC-002 | 6.3 |
| AWS-001 | 6.1-6.2 |
| AUTH-001 | 5.3, 6.4 |
| INF-001 | 4-5 |
| INF-002 | 5.7, 11.3 |
| INF-003 | 5.8, 8.1, 11.3 |
| NET-001 | 5.4-5.5, 8.3 |
| NET-002 | 8.2, 9 |
| NET-003 | 3.2, 9 |
| ACC-001 | 5.8, 8.1-8.3 |
| ACC-002 | 8, 11.3 |
| CDX-001 | 8.4 |
| CDX-002 | 8.4 |
| GIT-001 | 8.5 |
| REM-001 | 9 |
| REM-002 | 9 |
| OBS-001 | 5.9, 7.3, 12 |

## 16. References

- [SPEC-001](./spec.md)
- [HCP Terraform CLI-driven remote runs](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run/cli)
- [HCP Terraform AWS dynamic credentials](https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/aws-configuration)
- [HashiCorp setup-terraform](https://github.com/hashicorp/setup-terraform)
- [Terraform installation](https://developer.hashicorp.com/terraform/install)
- [Terraform 1.16.1 release](https://github.com/hashicorp/terraform/releases/tag/v1.16.1)
- [Terraform AWS provider 6.62.0](https://github.com/hashicorp/terraform-provider-aws/releases/tag/v6.62.0)
- [Terraform cloud-init provider 2.4.0](https://github.com/hashicorp/terraform-provider-cloudinit/releases/tag/v2.4.0)
- [GitHub environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [Canonical current Ubuntu AMIs](https://documentation.ubuntu.com/aws/aws-how-to/instances/build-cloudformation-templates/)
- [AWS Ubuntu AMIs with SSM Agent](https://docs.aws.amazon.com/systems-manager/latest/userguide/ami-preinstalled-agent.html)
- [AWS IMDSv2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-IMDS-new-instances.html)
- [Tailscale Linux installation](https://tailscale.com/docs/install/linux)
- [Tailscale secure auth keys](https://tailscale.com/docs/features/access-control/auth-keys/how-to/secure-auth-keys)
- [OpenAI Docs: Codex CLI](https://learn.chatgpt.com/docs/codex/cli)
- [OpenAI Docs: Authentication](https://learn.chatgpt.com/docs/auth)
- [OpenAI Docs: Remote connections](https://learn.chatgpt.com/docs/remote-connections)
