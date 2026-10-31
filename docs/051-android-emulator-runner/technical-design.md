# Android runner technical design

Owner: project owner. Date: 2026-10-30. Runner deployed; first-boot recovery pending.
[Specification](spec.md) · [Tasks](tasks.md)

Add separate compute in `infra/dev-host` using the existing subnet, zero-ingress
security group and development instance profile. The profile grants SSM and
audience-bound Tailscale federation, not project-volume or repository access.
Fresh federation enrollment uses a distinct hostname, `forge-android-01`, with
the existing `tag:gptclaw-dev` trust/ACL. The runner consequently shares that
development tag's access; a production or general multi-tenant runner is outside
scope. No new deployment-role permissions or self-management are proposed.

The Ubuntu image remains the current Canonical Noble x86_64 source. Explicit
`cpu_options.nested_virtualization = "enabled"` and M7i provide KVM; changing an
AMI alone cannot supply the missing CPU virtualization extensions. The existing
host's AMI/bootstrap/lifecycle guards and EBS resources stay untouched.

Separate cloud-init creates `forge`, installs distribution support libraries,
hardens SSH/firewall and configures KVM membership, the pinned Tailscale binaries,
and the existing federation helper. Its own checksum-pinned Android setup runs
as forge. No copied host credentials, backend containers or data-volume mounting.
Use a dedicated public SSH key for this task alongside the existing desktop
public key; private key material stays outside the repository. Connect from the
development host over Tailscale; ADB and emulator consoles stay loopback-only.

The runner does not need a GPU: use SwiftShader graphics with KVM CPU acceleration.
Keep 2 guest CPUs and 3 GiB guest RAM, enough host headroom for rendering. The
headless process is a systemd service as forge. SDK archives are immutable URLs
with SHA256 checks; package notices/licenses are retained. The project owner
explicitly accepted Android SDK terms for this runner on 2026-10-30; bootstrap
records that scoped acceptance and starts the fixture after installation.

An independent four-hour boot timer stops the emulator cleanly then shuts down
the instance (`instance_initiated_shutdown_behavior = "stop"`). An explicit
Terraform instance-state resource and protected workflow input control subsequent
start/stop; default dispatch state is stopped. A running apply is deliberate and
may restart an auto-stopped runner. Storage/IPv4 charges are separate; this timer
is not a hard AWS billing cap. No new recurring automation service is introduced.

## Verification and operation

Local gates: pinned Terraform format/validate/test with mocked AWS and real local
cloud-init rendering; offline bootstrap tests; existing repository checker and
whitespace checks. Checksum-pin and path-safe archive extraction tests use tiny
synthetic archives, not cloud calls. Existing Terraform/provider pins remain.
These infrastructure conventions apply; application starter standards and app
tests do not substitute for infrastructure checks.

After review/merge, dispatch a protected remote plan and inspect resource actions:
no replacement/destruction of existing resources, no project-volume changes, no
IAM expansion. Dispatch apply with runner state running. Preserve revision and
GitHub/HCP links. Verify cloud-init, KVM access, tailnet reachability and SSH as
forge; confirm ADB listeners are loopback. Capture real boot/app
screenshots. Then stop/start through the same workflow and verify retained
synthetic fixture data. Distinguish local, CI, deployment and app evidence.

Rollback: stop the new runner through Terraform. Keep its encrypted disk for
diagnosis; removal/replacement needs a reviewed change to its destruction guard.
Do not alter or detach the development host's project volume. Restore source
with a targeted PR, preserving subsequent unrelated changes.

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| ER-01,02 | Separate protected Terraform compute/state; existing pipeline | T1,T3,T5 | AC-01,02 |
| ER-03,04 | Minimal cloud-init, pinned artifacts, forge/KVM, private access | T2,T3,T4 | AC-02,03 |
| ER-05 | Independent disk, stop timer and protected state input | T2,T3,T5 | AC-02,05 |
| ER-06 | Actual Android interaction and private backend test | T5,T6 | AC-03,04 |

Sources: [AWS nested virtualization](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/amazon-ec2-nested-virtualization.html),
[Android acceleration](https://developer.android.com/studio/run/emulator-acceleration).

## First-boot recovery proposal (October 31)

The initial runner failed at SSH validation before Tailscale installation because
`/run/sshd` was absent. The corrected template creates it explicitly and uses
cloud-init's supported `sudo: null` value. Local tests reproduce the missing
directory and safe retry without running privileged commands.

The owner requested recovery through automatic machine setup rather than manual
SSM commands. A proposed one-time exception to **this runner's** destruction and
user-data-drift guards enables Terraform replacement with corrected cloud-init.
It is not yet approved for publication, merge or deployment. Create-before-destroy
keeps the failed instance until EC2 creation succeeds; bootstrap still requires
live verification. The failed runner's own root disk will be deleted. The existing
development host and project-volume guards remain unchanged. No IAM expansion.
Restore the runner guards immediately after the single approved replacement,
before any subsequent apply. See the [recovery procedure](../../runbooks/android-emulator-runner.md).
