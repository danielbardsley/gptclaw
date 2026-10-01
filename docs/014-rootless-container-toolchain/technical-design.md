# TDD-014: Rootless Container Toolchain

- **Status:** Draft proposal
- **Owner:** Daniel
- **Last updated:** 2026-10-01 (America/New_York)
- **Specification:** [SPEC-014](spec.md)
- **Tasks:** [TASKS-014](tasks.md)

## Existing components and proposed approach

[AMI selection](../../infra/dev-host/data.tf) uses Ubuntu Noble amd64.
[Compute](../../infra/dev-host/compute.tf) renders
[bootstrap](../../infra/dev-host/templates/bootstrap-forge.sh.tftpl) into
[cloud-init](../../infra/dev-host/templates/cloud-init.yaml.tftpl), with
`user_data_replace_on_change = true`. Bootstrap already separates user creation,
project-volume mounting and completion. Add a bounded toolchain phase after
identity/storage readiness and before completion. Do not turn a provisioning
change into a local installer for the active host.

Prefer Ubuntu distribution packages for Podman and the necessary namespace,
network and storage helpers. Resolve the actual package versions and dependencies
against the target release before coding; record an explicit supported baseline
and installed versions rather than assuming current upstream documentation
matches distro binaries. No floating upstream install script or automatic image
updates are proposed. Keep Terraform/provider pins in their existing sources.

The [upstream rootless tutorial](https://github.com/podman-container-tools/podman/blob/main/docs/tutorials/rootless_tutorial.md)
and [Podman manual](https://docs.podman.io/en/stable/markdown/podman.1.html)
describe subordinate mappings and user storage. Review the manual for the selected
version when choosing helpers. Inventory existing `forge` UID/GID and subordinate
ranges; select and record a collision-free allocation, preserving it across host
replacement. Refuse conflicting existing allocation or configuration before
writing. Do not infer that `useradd` chose a reproducible mapping.

Proposed graph storage is beneath `/home/forge/.local/share/containers`, on the
root disk, with runtime state beneath the user runtime directory. Verify actual
resolved paths and driver; reject silent fallback to another persistent location.
Keep `/srv/forge/projects` as project storage. Use only a task-owned synthetic
bind mount to prove ownership behavior. Root disk loss requires repulling images
and rebuilding containers; this slice creates no persistent application volume.

Select and verify a rootless network backend supported by the chosen package
set. The acceptance container uses explicit `127.0.0.1` publication on a free
high port; port conflicts fail without killing the existing listener. Test DNS,
outbound access and private binding separately. Do not install proxy routes or
claim loopback publication enforces a cross-project security boundary.

Enable lingering for `forge` through reviewed bootstrap and verify the user
manager and runtime directory are available without an interactive shell.
Place the opt-in fixture definition in the supported rootless Quadlet search
path, with activation in its source definition, restart limits and resource
limits. The [Quadlet documentation](https://docs.podman.io/en/v4.8.3/markdown/podman-systemd.unit.5.html)
describes cgroup v2 requirements and generator-managed activation; verify all
used keys against the chosen installed version. Use user-manager status and
journal access for diagnostics; do not enable a rootful engine API socket.

For this first slice, user configuration on the root disk survives reboot but
must be recreated from reviewed source after replacement. Future RUN-002 defines
project-service reconstruction and lifecycle interfaces. Acceptance fixture
installation is explicit and temporary, not an always-on bootstrap service.

## Planned changes

| Component | Responsibility | Requirements |
|---|---|---|
| Bootstrap template and narrowly scoped helper, if needed | Package declaration, identity conflict checks, managed configuration, linger, capability checks and completion metadata | RCT-001–RCT-006 |
| Terraform rendering and tests | Wire any reviewed inputs; prove rendered phase ordering and unchanged safeguards using synthetic values | RCT-001, RCT-002, RCT-006 |
| Isolated script tests | Exercise idempotency and failure paths without modifying host users, packages or systemd | RCT-001–RCT-003, RCT-006 |
| Synthetic fixture and scoped verification script | Build/run, mapping, bind mount, network, Quadlet/restart and cleanup scenarios | RCT-002–RCT-005, RCT-007 |
| New toolchain runbook and recovery-runbook links | Inspect, install/remove fixture, capacity checks, logout/reboot evidence, replacement and rollback | RCT-003–RCT-007 |
| Initiative acceptance record | Distinguish tests, deployment and owner acceptance for every criterion | RCT-007 |

## Failure, rollout and rollback

Fail before a success marker if required tools, mappings, driver, generator or
user manager cannot be verified. Preserve unknown configuration and report the
specific conflict. Avoid environment dumps and unrestricted engine diagnostics
that could include credentials. Install no private registry credentials.

Offline tests cannot establish kernel, network or systemd behavior. Follow the
[replacement runbook](../../runbooks/recover-dev-host.md): review the protected
pipeline plan, check the recovery point and maintenance window, quiesce project
writes, then apply only with explicit deployment authorization. Verify SSM,
private SSH, project UUID/ownership and existing safeguards after replacement.
Acceptance images and helper binaries must have a recorded source and version;
network-dependent probes run only during authorized host acceptance.

Observe logout and reboot from an approved independent operator session, without
starting a `forge` login before verifying boot startup. Stop fixture writes before
replacement; regenerate the fixture afterward and verify preserved synthetic
source. Failure blocks acceptance and normal fixture use; it does not justify
changing security controls. Remove only owned fixture resources afterward.

Rollback uses a reviewed revert and the same protected pipeline, potentially
replacing compute again. Preserve the project disk and mappings. Do not downgrade
an existing engine store in place or run global prune/reset commands. Record
whether rollback was exercised or only reviewed. Broader restore drills remain
RES-002 work.

## Traceability and unresolved choices

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| RCT-001 | Declared packages and capability/completion checks | T-002, T-003, T-005 | AC-001 |
| RCT-002 | Stable identity allocation and conflict checks | T-002, T-003, T-004, T-005 | AC-002, AC-003 |
| RCT-003 | Explicit disposable storage and mount ownership | T-002, T-003, T-004, T-006 | AC-003 |
| RCT-004 | Rootless network and loopback fixture | T-002, T-004, T-006 | AC-004 |
| RCT-005 | Linger, Quadlet source activation and restart bounds | T-003, T-004, T-006 | AC-005 |
| RCT-006 | Conflict-safe provisioning and pipeline recovery | T-003, T-005, T-006 | AC-006 |
| RCT-007 | Scoped fixture, runbook and evidence | T-004, T-006, T-007 | AC-007 |

Daniel owns scope approval and the storage policy. The implementer owns version,
backend, mapping and image selection at T-002, providing evidence before changes.
Daniel owns the maintenance window and deployment decision at T-006. Planning
and review can proceed with these choices explicitly pending; no host capability
or deployed verification is claimed by this design.
