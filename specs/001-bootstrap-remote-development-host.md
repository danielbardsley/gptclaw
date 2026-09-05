# SPEC-001: Bootstrap the Remote Development Host

**Status:** Draft for review  
**Owner:** Daniel  
**Implementation repository:** To be supplied  
**Last updated:** 2026-09-05

## 1. Summary

Provision one secure, persistent EC2 development host and connect the ChatGPT desktop app to a repository on that host over SSH. At the end of this work, a Codex task started in ChatGPT must be able to read and edit repository files, execute a harmless command on EC2, and show the resulting Git diff.

This is the first vertical slice of the development platform. It proves the remote control path before project scaffolding, application hosting, Expo, Slack, or production deployment are introduced.

## 2. Desired outcome

From the ChatGPT desktop app, the owner can select an SSH-connected EC2 project and ask Codex to:

1. Inspect the remote repository.
2. Create or edit a file in the repository.
3. Run a command on the EC2 host.
4. Display the resulting Git diff.
5. Continue the same task without switching to a separate terminal workflow.

## 3. Scope

### 3.1 Included

- Infrastructure as code for one EC2 development host.
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

## 5. Architecture

```text
ChatGPT desktop app
        |
        | OpenSSH connection to the explicit `forge-dev` alias
        | carried over Tailscale
        v
EC2: forge-dev-01
  |- sshd
  |- Codex CLI and remote app server
  |- /srv/forge/projects/<repository>
  `- SSM Agent for break-glass administration
```

The Codex app-server transport must not be exposed directly to the public internet. The ChatGPT desktop app will start and manage it through SSH.

## 6. Functional requirements

### INF-001: Reproducible provisioning

The EC2 host and its supporting AWS resources must be defined as code. Reapplying the infrastructure configuration must not replace the instance unexpectedly when no relevant setting has changed.

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

The GitHub repository supplied by the owner must be cloned beneath `/srv/forge/projects`. The default branch must be checked out and `git status` must succeed as the `forge` user.

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
- AWS credentials must come from an instance role, not stored access keys.
- The instance role follows least privilege and is limited to resources needed by this host.
- SSH password authentication and direct root login are disabled.
- The private SSH key remains on the owner's desktop and is not committed.
- Tailscale enrollment credentials are not written to Terraform state, source control, shell history, or logs.
- Codex authentication files remain outside project workspaces.
- The host firewall permits SSH through the Tailscale interface and does not create a public SSH path.
- Host bootstrap output is reviewed for accidental secret disclosure before it is retained.

## 8. Implementation sequence

1. Add the infrastructure code and configuration variables to the GitHub repository.
2. Provision networking, IAM, security group, encrypted EBS, and the EC2 instance.
3. Confirm SSM access before configuring any alternative access path.
4. Install Tailscale and enroll the host without placing the enrollment secret in Terraform state.
5. Create and harden the `forge` account.
6. Install Codex and confirm it is on the login-shell `PATH`.
7. Authenticate Codex with `codex login --device-auth`.
8. Clone the GitHub repository beneath `/srv/forge/projects`.
9. Add the `forge-dev` alias to the desktop SSH configuration and verify normal SSH access.
10. Add the SSH host and remote project folder in the ChatGPT desktop app.
11. Run the acceptance test and retain sanitized evidence.

## 9. Acceptance test

The work is complete only when all of the following pass:

- [ ] The EC2 instance was created from committed infrastructure code.
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

## 10. Required inputs before implementation

- AWS account and target region.
- AWS identity or profile authorized to provision the development resources.
- GitHub repository URL and default branch.
- Tailscale tailnet and desired device tag, if tags are used.
- Public half of the desktop SSH key.
- Confirmation that **Settings -> Connections -> SSH** is available in the owner's ChatGPT desktop app.

## 11. Deliverables

- Infrastructure-as-code source.
- Non-secret bootstrap configuration.
- Remote-host setup and recovery runbook.
- Desktop SSH configuration example.
- Sanitized acceptance-test record.
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
- [Tailscale: Install Tailscale on Linux](https://tailscale.com/docs/install/linux)

