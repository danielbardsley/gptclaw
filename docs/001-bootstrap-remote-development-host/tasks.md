# TASKS-001: Bootstrap the Remote Development Host

- **Status:** Not started
- **Owner:** Daniel
- **Specification:** [SPEC-001](./spec.md)
- **Technical design:** [TDD-001](./technical-design.md)
- **Last updated:** 2026-09-05

## How to use this list

Work through the phases in order. A later phase may start only when its stated
entry gate is satisfied. Tasks marked **Operator** require an account owner or
interactive desktop action; tasks marked **Repository** produce reviewed files
in this repository. Never paste secret values into this document, issues,
commits, workflow logs, or acceptance evidence.

A task is complete when its change is reviewed, its checks pass, supporting
documentation is updated, and no secret or generated Terraform artifact is
present in Git.

This task list ends when ChatGPT can safely edit files and run commands on the
remote host. Controlled system-software installation, rootless application
services, Tailscale and Expo previews, reusable steering files, production AWS
promotion, and Slack control remain follow-on work; this implementation must
preserve a secure path to add them.

## Phase 0 — Confirm inputs and safety boundaries

**Entry gate:** None.

- [ ] **0.1 Operator — Confirm the target environment inputs.** Record the AWS
  account ID, AWS region, fixed availability zone, HCP Terraform organization,
  HCP project, and Tailscale tailnet in an approved administrative location.
- [ ] **0.2 Operator — Confirm repository controls.** Verify `main` is the
  default branch and determine whether the GitHub plan supports required
  reviewers on the `development` environment.
- [ ] **0.3 Operator — Confirm the desktop connection capability.** Verify the
  ChatGPT desktop app exposes **Settings -> Connections -> SSH**.
- [ ] **0.4 Operator — Create a dedicated desktop-to-host SSH key pair.** Keep
  the private key on the desktop and make only the public key available as an
  HCP Terraform input.
- [ ] **0.5 Operator — Confirm Tailscale policy inputs.** Approve the hostname
  `forge-dev-01`, tag `tag:gptclaw-dev`, and the identity or device permitted to
  reach tagged hosts on TCP 22. Confirm the ChatGPT desktop machine is already
  authenticated to the same tailnet.
- [ ] **0.6 Operator — Confirm the Codex login path.** Enable device-code login
  in ChatGPT security or workspace settings, or verify that the desktop can use
  SSH local port forwarding for the supported browser callback fallback.
- [ ] **0.7 Repository — Record non-secret implementation decisions.** Update
  the spec or design if any approved input changes an architectural default.

**Exit gate:** Every required input has an owner and a confirmed value; no
secret value has been committed.

## Phase 1 — Establish the repository foundation

**Entry gate:** Phase 0 complete.

- [ ] **1.1 Repository — Create the planned source layout.** Add
  `.github/workflows`, `infra/dev-host/templates`, `infra/dev-host/tests`,
  `runbooks`, and `scripts`.
- [ ] **1.2 Repository — Add Terraform ignore rules.** Exclude `.terraform/`,
  state files, saved plans, crash logs, override files, and local variable files
  while retaining `terraform.tfvars.example` and `.terraform.lock.hcl`.
- [ ] **1.3 Repository — Pin the toolchain.** Confirm HCP Terraform supports
  Terraform `1.16.1`, then set that version, AWS provider `~> 6.62`, and
  cloud-init provider `~> 2.4` in every documented location. If HCP does not yet
  support `1.16.1`, choose one supported `1.16.x` version and update the spec,
  design, tasks, workflow, workspace, and `.terraform-version` together.
- [ ] **1.4 Repository — Configure dependency updates.** Add weekly Dependabot
  checks for GitHub Actions and Terraform providers.
- [ ] **1.5 Repository — Add safe example configuration.** Create
  `terraform.tfvars.example` containing variable names and non-sensitive sample
  values only.
- [ ] **1.6 Repository — Document local validation commands.** Include format,
  initialization, validation, and test commands; state explicitly that local
  `terraform apply` is unsupported.

**Exit gate:** The planned directory structure, version pins, and ignore rules
are committed and a secret scan finds no credentials or Terraform artifacts.

## Phase 2 — Bootstrap HCP Terraform, AWS trust, and GitHub controls

**Entry gate:** Phases 0–1 complete. An existing authorized AWS identity and
HCP Terraform administrator are available for one-time setup.

- [ ] **2.1 Operator — Create the HCP Terraform workspace.** Create
  `gptclaw-dev-host` in the approved project with remote execution, no VCS
  connection, no working-directory prefix, auto-apply disabled, and Terraform
  `1.16.1`.
- [ ] **2.2 Operator — Create or verify the HCP AWS OIDC provider.** Use issuer
  `https://app.terraform.io` and audience `aws.workload.identity`.
- [ ] **2.3 Operator — Create the HCP plan role.** Restrict trust to the exact
  organization, project, workspace, and `run_phase:plan`; grant only the read
  actions needed for refresh and data sources.
- [ ] **2.4 Operator — Create the HCP apply role.** Restrict trust to the exact
  organization, project, workspace, and `run_phase:apply`; grant only the
  resource mutations required by this design and limit `iam:PassRole` to the
  GptClaw host role.
- [ ] **2.5 Operator — Configure dynamic AWS credentials in HCP.** Set
  `TFC_AWS_PROVIDER_AUTH`, `TFC_AWS_PLAN_ROLE_ARN`, and
  `TFC_AWS_APPLY_ROLE_ARN` as workspace environment variables.
- [ ] **2.6 Operator — Configure HCP Terraform variables.** Add the approved
  account, region, availability zone, desktop SSH public key, Tailscale secret
  ARN, and other non-default inputs. Mark sensitive values appropriately.
- [ ] **2.7 Operator — Create separate HCP tokens.** Create or rotate a
  workspace-scoped plan token and apply-capable token, preferring team or
  service-account tokens over personal tokens.
- [ ] **2.8 Operator — Configure GitHub Actions settings.** Add
  `TF_API_TOKEN_PLAN` as a repository secret; create the protected
  `development` environment and add `TF_API_TOKEN_APPLY` there.
- [ ] **2.9 Operator — Configure GitHub variables.** Add
  `HCP_TERRAFORM_ORGANIZATION`, `HCP_TERRAFORM_WORKSPACE`, and
  `TERRAFORM_VERSION` with the approved values.
- [ ] **2.10 Operator — Configure the deployment gate.** Enable required
  reviewers when supported; retain manual dispatch and exact workspace-name
  confirmation in all cases.
- [ ] **2.11 Operator — Prepare Tailscale enrollment.** Configure tag ownership
  and TCP 22 access, create a tagged pre-authorized non-ephemeral one-use key,
  and store it in AWS Secrets Manager.
- [ ] **2.12 Repository — Write `runbooks/bootstrap-hcp-aws.md`.** Document the
  one-time trust boundary, configuration names, validation steps, rotation, and
  least-privilege repair process without recording secret values.

**Exit gate:** HCP can obtain the intended plan/apply AWS identities, GitHub has
separate HCP credentials, the Tailscale secret exists, and the observed account
and region match the approved inputs.

## Phase 3 — Implement and test the Terraform configuration

**Entry gate:** The HCP workspace and identity names are known.

- [ ] **3.1 Repository — Implement Terraform and provider configuration.** Add
  `versions.tf`, `providers.tf`, the HCP `cloud {}` block, exact CLI constraint,
  provider constraints, account allowlist, and default tags.
- [ ] **3.2 Repository — Implement validated inputs and locals.** Add every
  variable from TDD section 5.2, validation rules, common names, common tags,
  and deployment-revision handling.
- [ ] **3.3 Repository — Add account and AMI data sources.** Assert the caller
  account and resolve the Canonical Ubuntu 24.04 x86-64 gp3 AMI from its regional
  SSM parameter.
- [ ] **3.4 Repository — Implement networking.** Create the VPC, internet
  gateway, fixed-AZ public subnet, route table, association, and a host security
  group with zero ingress and initial unrestricted egress.
- [ ] **3.5 Repository — Implement logging.** Create the host CloudWatch log
  group with the configured retention and resource tags.
- [ ] **3.6 Repository — Implement the host IAM boundary.** Create the EC2 role
  and instance profile with SSM access, log permissions limited to the host log
  group, and read access limited to the exact Tailscale secret ARN.
- [ ] **3.7 Repository — Implement persistent storage.** Create the encrypted
  gp3 project volume in the fixed availability zone, apply `prevent_destroy`,
  and attach it without forced detach.
- [ ] **3.8 Repository — Implement compute.** Create the Ubuntu instance with no
  EC2 key pair, encrypted 30 GiB root disk, IMDSv2 required, hop limit 1,
  shutdown behavior `stop`, rendered cloud-init, and
  `user_data_replace_on_change = true`. Treat a rendered-bootstrap change as an
  expected, reviewable instance replacement while preserving the project EBS
  volume.
- [ ] **3.9 Repository — Implement non-secret outputs.** Output only the
  instance ID, availability zone, project volume ID, log-group name, SSM command,
  expected Tailscale hostname, and deployment revision.
- [ ] **3.10 Repository — Add Terraform tests.** Test defaults, input rejection,
  account guardrails, zero ingress, encrypted volumes, project-volume
  protection, IMDSv2, absence of an EC2 key pair, same-AZ placement, tags, and
  expected outputs.
- [ ] **3.11 Repository — Initialize providers and commit the lock file.** Run
  initialization through the intended HCP configuration and commit the reviewed
  `.terraform.lock.hcl`; do not commit state or a plan.

**Exit gate:** `terraform fmt -check -recursive`, `terraform validate`, and
`terraform test` pass, and tests enforce all material infrastructure controls.

## Phase 4 — Implement the idempotent host bootstrap

**Entry gate:** Terraform resource interfaces and volume identifiers are
stable.

- [ ] **4.1 Repository — Create the cloud-init template.** Make phases
  idempotent and log phase start, success, and failure without dumping the
  environment.
- [ ] **4.2 Repository — Install base services.** Install Git, curl, jq, unzip,
  certificates, AWS CLI, UFW, CloudWatch Agent, Tailscale, and required support
  packages; verify or start SSM Agent.
- [ ] **4.3 Repository — Create and constrain `forge`.** Create the non-root
  account without password login or unrestricted passwordless sudo, install the
  desktop public key, and enforce SSH directory and file modes.
- [ ] **4.4 Repository — Implement persistent-volume mounting.** Resolve the
  Nitro device by EBS volume ID, format only when no filesystem exists, label it
  `FORGE_DATA`, persist its UUID in `/etc/fstab`, mount `/srv/forge`, and create
  `/srv/forge/projects` as `forge:forge` mode `0750`.
- [ ] **4.5 Repository — Implement one-time Tailscale enrollment.** Retrieve the
  key directly from the exact Secrets Manager ARN, keep it out of Terraform
  state and logs, enroll with the approved hostname/tag, clear the value, and
  reuse node state on reboot.
- [ ] **4.6 Repository — Harden SSH and the host firewall.** Disable root,
  password, and keyboard-interactive login; allow only `forge` with public-key
  authentication; restrict forwarding to local forwarding; permit TCP 22 only
  on `tailscale0` in UFW.
- [ ] **4.7 Repository — Install Codex for `forge`.** Use the official
  noninteractive installation path and verify `codex` is available in both the
  interactive and non-interactive login-shell `PATH`.
- [ ] **4.8 Repository — Configure log shipping.** Send cloud-init, bootstrap,
  and authentication logs to the dedicated CloudWatch log group without
  capturing credentials.
- [ ] **4.9 Repository — Publish sanitized bootstrap status.** Write
  `/var/lib/gptclaw/bootstrap-complete.json` with bootstrap version, time,
  status, and installed non-secret component versions only.
- [ ] **4.10 Repository — Test rerun and failure behavior.** Confirm bootstrap
  can safely rerun, never reformats an existing filesystem, and leaves SSM
  usable when storage or enrollment fails.

**Exit gate:** Bootstrap is deterministic, idempotent, secret-safe, and exposes
no public administration path.

## Phase 5 — Implement the GitHub Actions delivery pipeline

**Entry gate:** Terraform validation and bootstrap tests pass locally without
an apply.

- [ ] **5.1 Repository — Add the workflow triggers.** Run quality and remote
  speculative plan jobs for relevant pull requests, pushes to `main`, and manual
  plan dispatches; allow apply only through manual dispatch from current `main`.
- [ ] **5.2 Repository — Enforce minimal workflow permissions.** Set
  `contents: read`, disable persisted checkout credentials, and do not request a
  GitHub OIDC token because AWS authentication occurs in HCP Terraform.
- [ ] **5.3 Repository — Pin third-party actions.** Pin checkout and Terraform
  setup actions to full immutable commit SHAs with nearby release comments.
- [ ] **5.4 Repository — Implement the quality job.** Run format checking,
  remote initialization, validation, Terraform tests, action-pin checks, and a
  secret-pattern scan.
- [ ] **5.5 Repository — Implement the plan job.** Use only
  `TF_API_TOKEN_PLAN`, fail if HCP remote execution cannot initialize, and run a
  speculative plan without saving or uploading plan artifacts.
- [ ] **5.6 Repository — Implement the apply gate.** Require the
  `development` environment, current `main`, a non-stale SHA, and exact
  confirmation `gptclaw-dev-host` before using `TF_API_TOKEN_APPLY`.
- [ ] **5.7 Repository — Implement the remote apply.** Run
  `terraform apply -input=false -auto-approve` only after the GitHub deployment
  gate and fail instead of falling back to local execution.
- [ ] **5.8 Repository — Serialize deployments.** Use concurrency group
  `terraform-gptclaw-dev-host` with cancellation disabled.
- [ ] **5.9 Repository — Add revision traceability.** Pass the exact 40-character
  Git SHA as `TF_VAR_deployment_revision` and summarize only the actor, event,
  workspace, revision, and HCP run URL.

**Exit gate:** Pull-request events cannot apply; only a current, confirmed
`main` dispatch through the protected environment can apply.

## Phase 6 — Qualify the deployment through a pull request

**Entry gate:** Phases 1–5 are implemented on a feature branch.

- [ ] **6.1 Repository — Open the implementation pull request.** Link SPEC-001,
  TDD-001, and this task list; describe all one-time external configuration.
- [ ] **6.2 Operator — Verify the credential preflight.** Confirm the plan token
  can reach the intended HCP organization/workspace and the plan role sees the
  approved AWS account and region.
- [ ] **6.3 Operator — Repair stale credentials narrowly.** Rotate the failed
  token or add only the smallest missing AWS read permission; never broaden to
  administrator access.
- [ ] **6.4 Operator — Review the speculative plan.** Confirm expected resource
  count/types, zero security-group ingress, encrypted storage, protected project
  volume, intended account/region/AZ, and no secret-bearing output.
- [ ] **6.5 Operator — Merge only after all checks pass.** Preserve the final
  reviewed HCP plan link and merged Git revision.

**Exit gate:** The reviewed pull request is merged to `main`; no infrastructure
has yet been applied from a pull-request event.

## Phase 7 — Apply and verify the AWS development host

**Entry gate:** The implementation revision is on current `main` and the apply
role is configured.

- [ ] **7.1 Operator — Refresh enrollment and run the protected manual apply.**
  For a replacement, first verify a current project-volume snapshot and confirm
  the plan retains the existing EBS volume. Store a fresh one-use Tailscale key
  in the existing secret immediately before an initial creation or replacement.
  Enter the exact workflow confirmation, approve the `development` environment
  when applicable, and let GitHub Actions initiate the remote apply.
- [ ] **7.2 Operator — Repair apply permissions narrowly if required.** Add only
  the denied action/resource needed by the declared plan, rerun the plan, and
  redispatch; do not perform manual resource creation.
- [ ] **7.3 Operator — Verify deployment provenance.** Confirm GitHub and HCP run
  records identify the same Git revision, workspace, AWS account, and region.
- [ ] **7.4 Operator — Verify the AWS controls.** Confirm no security-group
  ingress, encrypted root/data volumes, project-volume deletion protection,
  IMDSv2 enforcement, intended instance profile, and absence of an EC2 key pair.
- [ ] **7.5 Operator — Verify SSM first.** Establish a Session Manager shell and
  inspect cloud-init/bootstrap status before relying on Tailscale or SSH.
- [ ] **7.6 Repository — Add `scripts/verify-dev-host.sh`.** Check cloud-init,
  SSM Agent, Tailscale, mounted storage, Codex path/version, repository status,
  and sanitized bootstrap status without printing credentials.
- [ ] **7.7 Operator — Run the host verification script.** Retain sanitized
  results and relevant GitHub/HCP run links.

**Exit gate:** Pipeline-created infrastructure is healthy, SSM works, and all
AWS security/storage assertions pass.

## Phase 8 — Complete host enrollment and repository access

**Entry gate:** Phase 7 complete and Session Manager access is confirmed.

- [ ] **8.1 Operator — Verify Tailscale enrollment.** Confirm
  `forge-dev-01` appears with the approved tag and is reachable only according
  to the tailnet policy; replace the one-use secret if it was consumed early.
- [ ] **8.2 Operator — Verify hardened SSH.** Confirm public-key login works as
  `forge` over Tailscale and that root, password, and public-network SSH paths do
  not work.
- [ ] **8.3 Operator — Create the EC2-to-GitHub key as `forge`.** Generate a
  separate key on the host, verify GitHub's published host fingerprint, and add
  its public half as the write-enabled deploy key `GptClaw forge-dev-01`.
- [ ] **8.4 Operator — Clone the repository.** Use a repository-specific SSH
  alias with `IdentitiesOnly yes`, clone to
  `/srv/forge/projects/gptclaw`, select `main`, and confirm a clean worktree.
- [ ] **8.5 Operator — Authenticate Codex as `forge`.** Prefer
  `codex login --device-auth`. If it is unavailable, use the documented SSH
  localhost-forwarding browser callback; do not copy a local authentication
  cache as the normal fallback. Verify login status and, when file-based
  credential storage is used, enforce `0700`/`0600` permissions.
- [ ] **8.6 Operator — Verify non-interactive Codex startup.** Confirm ChatGPT's
  SSH launch context finds `codex` without loading credentials from the
  repository or a globally readable file.

**Exit gate:** The host is privately reachable, has repository write access,
and Codex is authenticated under the constrained `forge` identity.

## Phase 9 — Connect ChatGPT and run the end-to-end acceptance test

**Entry gate:** Phase 8 complete and the desktop is connected to the same
Tailscale network.

- [ ] **9.1 Operator — Add the desktop SSH alias.** Configure `forge-dev` with
  the Tailscale hostname, user `forge`, dedicated desktop key,
  `IdentitiesOnly yes`, and keepalive settings.
- [ ] **9.2 Operator — Verify desktop SSH.** Run `ssh forge-dev`; confirm the
  session is `forge`, lands on the intended host, and reaches no public SSH
  endpoint.
- [ ] **9.3 Operator — Add the ChatGPT SSH connection.** Register `forge-dev` in
  the desktop app and open `/srv/forge/projects/gptclaw` as the remote project.
- [ ] **9.4 Operator — Exercise remote filesystem access.** From one remote
  Codex task, create `connection-test.md` containing the remote hostname and
  current UTC timestamp.
- [ ] **9.5 Operator — Exercise remote command execution.** In the same task,
  run harmless hostname/time verification and display the resulting Git diff.
- [ ] **9.6 Operator — Restore the repository.** Remove `connection-test.md` and
  confirm the remote worktree is clean.

**Exit gate:** ChatGPT can manipulate files, execute commands, and show Git
changes on the EC2 host through the private SSH connection.

## Phase 10 — Prove repeatability and hand off operations

**Entry gate:** The end-to-end acceptance test passes.

- [ ] **10.1 Operator — Prove idempotence.** Run a new pipeline plan without
  code or variable changes and confirm it reports no infrastructure changes.
- [ ] **10.2 Repository — Write `runbooks/connect-chatgpt.md`.** Document key
  creation, Tailscale prerequisites, SSH alias setup, ChatGPT connection, Codex
  authentication, and troubleshooting without secret values.
- [ ] **10.3 Repository — Write `runbooks/recover-dev-host.md`.** Document SSM
  break-glass access, snapshot validation, same-AZ volume recovery, fresh
  Tailscale enrollment, instance replacement, GitHub key recreation, Codex
  reauthentication, and reconciliation through Terraform.
- [ ] **10.4 Operator — Test the documented recovery entry points.** Confirm an
  authorized operator can find the SSM session command, volume/snapshot IDs,
  log group, and exact pipeline workflow without relying on undocumented local
  knowledge.
- [ ] **10.5 Repository — Create a sanitized acceptance record.** Record pass or
  fail for every SPEC-001 acceptance criterion plus resource IDs, deployment
  revision, and GitHub/HCP run URLs; include no tokens, keys, environment dumps,
  or saved plans.
- [ ] **10.6 Repository — Close the implementation.** Mark this task list and
  SPEC-001 complete only after all acceptance criteria pass and the final
  worktree and no-change plan are clean.

**Exit gate:** The platform is reproducible, documented, recoverable, and every
SPEC-001 acceptance criterion has retained sanitized evidence.

## Requirement traceability

| Requirement | Primary tasks |
|---|---|
| CICD-001 | 1.6, 5.1–5.9, 6.1–6.5, 7.1 |
| CICD-002 | 5.1, 5.4–5.9, 6.4, 7.1 |
| CICD-003 | 1.3–1.4, 5.2–5.5 |
| TFC-001 | 2.1, 3.11, 5.5, 7.3 |
| TFC-002 | 2.7–2.10, 5.5–5.7 |
| AWS-001 | 2.2–2.6, 6.2–6.3, 7.2 |
| AUTH-001 | 0.1, 2.2–2.10, 6.2–6.4, 7.2–7.3 |
| INF-001 | 3.1–3.11, 5.1–5.9, 10.1 |
| INF-002 | 3.7–3.10, 4.4, 7.4, 10.3 |
| INF-003 | 3.6, 4.2, 7.5, 10.3–10.4 |
| NET-001 | 3.4, 3.10, 4.6, 7.4, 8.2 |
| NET-002 | 2.11, 4.5–4.6, 8.1–8.2, 9.1–9.2 |
| NET-003 | 3.4, 4.6, 9.1–9.3 |
| ACC-001 | 3.6, 4.3–4.4, 4.6–4.7, 8.2–8.6 |
| ACC-002 | 2.4, 3.6, 4.3, 7.5, 10.3 |
| CDX-001 | 4.7, 7.6–7.7, 8.6 |
| CDX-002 | 0.6, 8.5–8.6, 10.2 |
| GIT-001 | 8.3–8.4, 9.3–9.6 |
| REM-001 | 0.4, 9.1–9.2, 10.2 |
| REM-002 | 0.3, 9.3–9.6 |
| OBS-001 | 3.5, 3.9, 4.1, 4.8–4.9, 5.9, 7.3–7.7, 10.5 |
