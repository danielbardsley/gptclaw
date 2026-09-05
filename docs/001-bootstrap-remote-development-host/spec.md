# SPEC-001: Bootstrap the Remote Development Host

- **Status:** Draft for review
- **Owner:** Daniel
- **Implementation repository:** `git@github.com:danielbardsley/gptclaw.git`
- **Technical design:** [TDD-001](./technical-design.md)
- **Implementation tasks:** [TASKS-001](./tasks.md)
- **Last updated:** 2026-09-05

## 1. Summary

Provision one secure, persistent EC2 development host through a GitHub Actions pipeline backed by an HCP Terraform remote workspace, then connect the ChatGPT desktop app to a repository on that host over SSH. At the end of this work, the infrastructure deployment must be reproducible from the GitHub repository and a Codex task started in ChatGPT must be able to read and edit repository files, execute a harmless command on EC2, and show the resulting Git diff.

This is the first vertical slice of the development platform. It proves the remote control path before project scaffolding, application hosting, Expo, Slack, or production deployment are introduced.

## 2. Desired outcome

The owner can deploy the host by reviewing a Terraform plan generated for a pull request, merging the approved change, and approving or explicitly dispatching the GitHub Actions deployment. The resulting apply runs remotely in HCP Terraform and is traceable to the deployed Git revision.

From the ChatGPT desktop app, the owner can then select the SSH-connected EC2 project and ask Codex to:

1. Inspect the remote repository.
2. Create or edit a file in the repository.
3. Run a command on the EC2 host.
4. Display the resulting Git diff.
5. Continue the same task without switching to a separate terminal workflow.

## 3. Scope

### 3.1 Included

- Infrastructure as code for one EC2 development host.
- A GitHub Actions workflow that is the sole supported path for planning and applying the development-host infrastructure.
- A new HCP Terraform workspace at `app.terraform.io` for remote execution and state storage.
- Credential and permission preflight checks for GitHub Actions, HCP Terraform, and the target AWS account.
- A dedicated development VPC and subnet unless an existing network is deliberately selected during implementation.
- An encrypted persistent EBS volume.
- A least-privilege EC2 instance role sufficient for Systems Manager access and basic host logging.
- AWS Systems Manager Session Manager as the break-glass administration path.
- Tailscale installation and tailnet enrollment.
- SSH access over the Tailscale network.
- A dedicated, non-root Linux account named `forge`.
- Installation and authentication of Codex on the remote host.
- A persistent project root at `/srv/forge/projects`.
- Clone or initialization of the new GitHub repository under the project root.
- Connection of the ChatGPT desktop app to the EC2 host using an explicit SSH alias.
- A documented end-to-end connection test.

### 3.2 Explicitly excluded

- Slack integration.
- A custom Slack gateway or Codex SDK service.
- Rootless containers and per-project runtime isolation.
- Automated host package installation by the agent.
- Tailscale Serve or Funnel previews.
- Expo and EAS configuration.
- Application templates and new-project automation.
- Production AWS access or deployment.
- Direct Terraform applies from an owner's workstation or from the EC2 development host.
- Multi-user access.
- High availability or multiple executor instances.

The excluded items require separate specifications and must not be added opportunistically during this implementation.

## 4. Proposed defaults

These are starting assumptions, not irrevocable platform decisions.

| Setting | Proposed default |
|---|---|
| Operating system | Ubuntu 24.04 LTS, x86-64 |
| Instance size | Configurable; initial default `t3.large` |
| Storage | Configurable; initial default 80 GiB encrypted gp3 |
| Hostname | `forge-dev-01` |
| Remote Linux user | `forge` |
| Project root | `/srv/forge/projects` |
| SSH alias on the desktop | `forge-dev` |
| Normal network path | Tailscale |
| Administrative fallback | AWS Systems Manager Session Manager |
| Public inbound ports | None |
| Codex authentication | ChatGPT device-code login for the initial personal environment |
| Infrastructure repository | `danielbardsley/gptclaw` |
| Terraform code root | `infra/dev-host` |
| Terraform execution | HCP Terraform remote execution |
| HCP Terraform workspace | `gptclaw-dev-host` |
| GitHub deployment environment | `development` |

## 5. Architecture

```text
Infrastructure path

GitHub repository
        |
        | GitHub Actions: validate, plan, approved apply
        v
HCP Terraform workspace: gptclaw-dev-host
        |
        | remote execution + remote state + short-lived AWS identity
        v
AWS account: VPC, IAM, EBS, EC2

Runtime access path

ChatGPT desktop app
        |
        | OpenSSH connection to the explicit `forge-dev` alias
        | carried over Tailscale
        v
EC2: forge-dev-01
  |- sshd
  |- Codex CLI and remote app server
  |- /srv/forge/projects/gptclaw
  `- SSM Agent for break-glass administration
```

GitHub Actions orchestrates Terraform, but Terraform plans and applies execute in HCP Terraform rather than on the GitHub-hosted runner. HCP Terraform owns the state and authenticates to AWS. The Codex app-server transport must not be exposed directly to the public internet. The ChatGPT desktop app will start and manage it through SSH.

## 6. Functional requirements

### CICD-001: Pipeline-controlled infrastructure

The EC2 host and its supporting resources must be deployed from a workflow committed to `.github/workflows/`. No operator or agent may run `terraform apply` directly from a workstation or from the development host. Emergency out-of-band changes must be documented and reconciled through the pipeline immediately afterward.

### CICD-002: Plan and apply behavior

The workflow must:

- Run formatting, initialization, validation, and a speculative remote plan for pull requests that change infrastructure or workflow files.
- Never apply infrastructure from a pull-request event.
- Run an HCP Terraform remote plan and apply from the protected `development` GitHub environment after changes reach `main`.
- Run Terraform from `infra/dev-host` and use `terraform apply -auto-approve` only after the GitHub deployment gate has passed.
- Support a manually dispatched reconciliation run.
- Require an explicit deployment approval when the repository's GitHub plan supports environment reviewers; otherwise require a manual workflow dispatch with an `apply` confirmation input.
- Use a concurrency group so only one development-host deployment can run at a time.
- Publish links to the GitHub Actions run and corresponding HCP Terraform run without copying sensitive output into GitHub logs.

### CICD-003: Workflow security and reproducibility

The workflow must grant only the GitHub token permissions it needs, use a pinned Terraform CLI version, pin third-party actions to immutable commit SHAs, and fail rather than silently falling back to local Terraform execution.

### TFC-001: Dedicated HCP Terraform workspace

A new HCP Terraform workspace named `gptclaw-dev-host` must be created in the owner's existing HCP Terraform organization. The workspace must:

- Use remote execution rather than local execution.
- Retain Terraform state and run history in HCP Terraform.
- Be dedicated to this development host and its supporting resources.
- Use the CLI-driven workflow without a direct HCP Terraform VCS connection, so GitHub Actions remains the sole run initiator.
- Execute from the root of the configuration archive uploaded by GitHub Actions from `infra/dev-host`.
- Disable HCP Terraform auto-apply; apply is initiated only by the gated GitHub Actions job.
- Prevent overlapping applies.
- Not share state with any production workspace.

The organization name remains an implementation input. Workspace creation is an explicit bootstrap action and may be completed once through the HCP Terraform UI or API before the first pipeline run.

### TFC-002: GitHub-to-HCP authentication

GitHub Actions must authenticate to `app.terraform.io` using a narrowly scoped HCP Terraform team or service-account token stored as the `TF_API_TOKEN` secret in the protected `development` GitHub environment. The token must never be committed, printed, or stored on the EC2 host.

### AWS-001: HCP-to-AWS authentication

HCP Terraform must authenticate to the target AWS account. The preferred implementation is HCP Terraform dynamic provider credentials using an AWS IAM OIDC trust and separate least-privilege plan and apply roles. Static AWS access keys are permitted only as a documented temporary bootstrap fallback; if used, they must be rotated, stored as sensitive HCP Terraform workspace environment variables, and removed after dynamic credentials are working.

Long-lived AWS credentials must not be copied into Terraform files, Terraform state, GitHub workflow files, or GitHub logs. GitHub-hosted runners do not require AWS credentials when HCP Terraform performs the remote run.

### AUTH-001: Credential and permission preflight

Existing GitHub credentials must be treated as potentially stale. Before provisioning resources, the implementation must verify:

- The GitHub Actions secret can access the intended HCP Terraform organization and workspace.
- The HCP Terraform run identity can authenticate to the intended AWS account.
- The plan identity can read the required AWS metadata.
- The apply identity has only the permissions needed to create the resources in this specification.
- The observed AWS account ID and region match the approved inputs.

Authentication or authorization failures must stop the run before an apply. Credentials and policies may be repaired iteratively, but permission expansion must be deliberate, least-privilege, and recorded without exposing secret values.

### INF-001: Reproducible provisioning

The EC2 host and its supporting AWS resources must be defined as Terraform code beneath `infra/dev-host`. Re-running the GitHub Actions workflow must not replace the instance unexpectedly when no relevant setting has changed.

### INF-002: Persistent encrypted storage

The project filesystem must reside on encrypted EBS storage. Terminating or replacing compute must not silently destroy project data. The implementation must document the selected EBS deletion policy and recovery procedure.

### INF-003: Administrative recovery

The host must register with AWS Systems Manager and permit an authorized AWS administrator to open a Session Manager shell without an SSH key or public inbound rule.

### NET-001: No public inbound access

The instance security group must contain no public inbound rules. In particular, TCP port 22 must not be open to `0.0.0.0/0` or `::/0`.

### NET-002: Private SSH path

The host must join the owner's Tailscale network and be reachable from the ChatGPT desktop machine using its Tailscale address or MagicDNS name. SSH must be usable through that path.

### NET-003: No direct app-server exposure

No Codex app-server WebSocket listener may be exposed on a public interface. Remote Codex access must be initiated through SSH.

### ACC-001: Dedicated user

Normal remote work must run as the `forge` user. The account must:

- Own `/srv/forge/projects`.
- Use SSH key authentication.
- Have no password-based SSH login.
- Have no unrestricted passwordless `sudo` capability.
- Be unable to assume a production AWS role.

### ACC-002: Host administration boundary

System provisioning is performed through infrastructure bootstrap or an explicit administrator session. During this phase, Codex may request a missing host package but must not install it through unrestricted privilege escalation.

### CDX-001: Codex installation

The current supported Codex CLI must be installed so that `codex` is present in the `forge` user's login-shell `PATH`.

### CDX-002: Codex authentication

Codex must be authenticated on the remote host using ChatGPT device-code authentication. Cached authentication material must:

- Be readable only by the `forge` user.
- Never be committed to Git.
- Never be copied into a project directory.
- Be treated as a secret during backup and troubleshooting.

### GIT-001: Repository availability

The GitHub repository `git@github.com:danielbardsley/gptclaw.git` must be cloned beneath `/srv/forge/projects`. The default branch must be checked out and `git status` must succeed as the `forge` user.

### REM-001: Desktop SSH configuration

The desktop running ChatGPT must contain a concrete SSH host alias similar to:

```sshconfig
Host forge-dev
    HostName <tailscale-hostname>
    User forge
    IdentityFile <private-key-path>
    IdentitiesOnly yes
```

Wildcard-only SSH entries do not satisfy this requirement.

### REM-002: ChatGPT project connection

The EC2 host must appear under **Settings -> Connections -> SSH** in the ChatGPT desktop app, and the remote repository folder must be selectable as a project.

### OBS-001: Bootstrap evidence

The implementation must retain non-secret evidence showing:

- Infrastructure provisioning succeeded.
- SSM reports the host as managed.
- Tailscale reports the host as connected.
- `ssh forge-dev` succeeds from the desktop.
- `codex login status` reports an authenticated session.
- The ChatGPT desktop app can operate on the remote repository.

Secrets, access tokens, device codes, private keys, and complete environment dumps must not appear in the evidence.

## 7. Security requirements

- EC2 receives no production deployment permissions.
- AWS credentials used by Terraform must come from the HCP Terraform workspace identity, preferably through short-lived OIDC credentials.
- AWS credentials used by applications on EC2 must come from an instance role, not stored access keys.
- The GitHub Actions runner must not receive AWS credentials when the Terraform run executes remotely in HCP Terraform.
- The HCP Terraform API token must be stored only as a protected GitHub environment secret and must be rotated if the existing value is stale or its scope is excessive.
- Terraform state must remain in HCP Terraform and must never be committed to Git.
- Saved plan files must not be committed or exposed as public workflow artifacts.
- The instance role follows least privilege and is limited to resources needed by this host.
- SSH password authentication and direct root login are disabled.
- The private SSH key remains on the owner's desktop and is not committed.
- Tailscale enrollment credentials are not written to Terraform state, source control, shell history, or logs.
- Codex authentication files remain outside project workspaces.
- The host firewall permits SSH through the Tailscale interface and does not create a public SSH path.
- Host bootstrap output is reviewed for accidental secret disclosure before it is retained.
- Workflow logs and HCP Terraform run output are reviewed for accidental secret disclosure before being retained as implementation evidence.

## 8. Implementation sequence

1. Confirm the HCP Terraform organization, target AWS account ID, region, and development naming conventions.
2. Create the `gptclaw-dev-host` HCP Terraform workspace in remote-execution mode.
3. Configure HCP Terraform access to AWS, preferring OIDC-based dynamic provider credentials with separate plan and apply roles.
4. Create the protected `development` GitHub environment and add or rotate its `TF_API_TOKEN` secret.
5. Add Terraform code beneath `infra/dev-host` and the deployment workflow beneath `.github/workflows/`.
6. Run the credential preflight and repair stale credentials or insufficient permissions without placing credentials in source control.
7. Open a pull request and obtain a successful validation and speculative HCP Terraform plan.
8. Merge the reviewed change to `main`, approve or manually dispatch the `development` deployment, and let the GitHub Actions workflow trigger the HCP Terraform apply.
9. Confirm the successful GitHub Actions run, HCP Terraform run, remote state, and expected AWS account and region.
10. Confirm SSM access before configuring any alternative access path.
11. Install Tailscale and enroll the host without placing the enrollment secret in Terraform state.
12. Create and harden the `forge` account.
13. Install Codex and confirm it is on the login-shell `PATH`.
14. Authenticate Codex with `codex login --device-auth`.
15. Clone `danielbardsley/gptclaw` beneath `/srv/forge/projects`.
16. Add the `forge-dev` alias to the desktop SSH configuration and verify normal SSH access.
17. Add the SSH host and remote project folder in the ChatGPT desktop app.
18. Run the acceptance test and retain sanitized evidence with links to the GitHub and HCP Terraform runs.

## 9. Acceptance test

The work is complete only when all of the following pass:

- [ ] The `gptclaw-dev-host` workspace exists in the approved HCP Terraform organization and uses remote execution.
- [ ] Terraform state exists only in HCP Terraform and is not present in the Git repository.
- [ ] A pull request produces formatting and validation results plus a speculative HCP Terraform plan, with no apply.
- [ ] A protected or explicitly confirmed GitHub Actions run from `main` produces the successful HCP Terraform apply.
- [ ] The EC2 instance was created from committed Terraform code by that pipeline; no local `terraform apply` was used.
- [ ] The GitHub Actions and HCP Terraform run records identify the same revision.
- [ ] The deployment targets the approved AWS account ID and region.
- [ ] The active HCP-to-AWS identity is least-privilege; dynamic credentials are used or the temporary static-credential exception is documented.
- [ ] No AWS access key, HCP Terraform token, Terraform state, or saved plan is committed or exposed in logs.
- [ ] The instance security group has no public inbound rule.
- [ ] An authorized administrator can connect through Session Manager.
- [ ] The desktop can resolve and reach `forge-dev` over Tailscale.
- [ ] `ssh forge-dev` opens a shell as the `forge` user.
- [ ] `codex` is available in that user's non-interactive login-shell `PATH`.
- [ ] Codex is authenticated without storing credentials in the repository.
- [ ] ChatGPT can open the remote repository as a project.
- [ ] From a remote Codex chat, ChatGPT can create `connection-test.md` containing the remote hostname and current UTC timestamp.
- [ ] The same chat can run a harmless verification command on EC2.
- [ ] ChatGPT displays the new file in the remote Git diff.
- [ ] Removing `connection-test.md` returns the repository to a clean state.
- [ ] The implementation records setup and recovery instructions without recording secrets.
- [ ] Re-running the deployment workflow with no code or variable changes produces no infrastructure changes.

## 10. Required inputs before implementation

- AWS account ID and target region.
- An authorized bootstrap path for establishing HCP Terraform's AWS trust and least-privilege plan/apply roles.
- HCP Terraform organization name and permission to create the `gptclaw-dev-host` workspace.
- A valid HCP Terraform team or service-account token for the GitHub `development` environment; any existing token is assumed stale until verified.
- Confirmation of whether GitHub environment required reviewers are available for this repository plan; otherwise the workflow will use explicit manual dispatch confirmation.
- GitHub repository `danielbardsley/gptclaw` with `main` as the default branch.
- Tailscale tailnet and desired device tag, if tags are used.
- Public half of the desktop SSH key.
- Confirmation that **Settings -> Connections -> SSH** is available in the owner's ChatGPT desktop app.

## 11. Deliverables

- Terraform source beneath `infra/dev-host`.
- GitHub Actions validation, plan, and deployment workflow.
- Configured `gptclaw-dev-host` HCP Terraform remote workspace.
- Least-privilege HCP-to-AWS authentication configuration.
- GitHub `development` environment configuration and secret inventory containing names and scopes, never values.
- Non-secret bootstrap configuration.
- Remote-host setup and recovery runbook.
- Desktop SSH configuration example.
- Sanitized acceptance-test record.
- Links between the deployed Git revision, GitHub Actions run, and HCP Terraform run.
- A working ChatGPT-to-EC2 remote project connection.

## 12. Follow-on specifications

Completing this specification should be followed by separate specs for:

1. Remote development runtime and controlled software installation.
2. Steering files, project specifications, and reusable templates.
3. Private web-service previews through Tailscale Serve.
4. Expo development and EAS preview workflows.
5. GitHub pull-request and production-promotion workflow.
6. Optional Slack control adapter.

## 13. References

- [OpenAI: Remote connections](https://learn.chatgpt.com/docs/remote-connections)
- [OpenAI: Authentication](https://learn.chatgpt.com/docs/auth)
- [AWS: Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [AWS: IAM roles for Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
- [HCP Terraform: Remote operations](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run/remote-operations)
- [HCP Terraform: CLI-driven remote runs](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run/cli)
- [HCP Terraform: Dynamic provider credentials](https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials)
- [HashiCorp: Setup Terraform GitHub Action](https://github.com/hashicorp/setup-terraform)
- [GitHub: Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [Tailscale: Install Tailscale on Linux](https://tailscale.com/docs/install/linux)
