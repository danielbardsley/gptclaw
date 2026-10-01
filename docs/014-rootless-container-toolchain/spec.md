# SPEC-014: Rootless Container Toolchain

- **Status:** Draft; awaiting Daniel's review
- **Owner:** Daniel
- **Feature catalogue:** SYS-001
- **Last updated:** 2026-10-01 (America/New_York)
- **Design:** [TDD-014](technical-design.md)
- **Tasks:** [TASKS-014](tasks.md)
- **Context:** [Architecture](../platform/architecture.md), sections 10, 11 and 14;
  [feature catalogue](../platform/features.md)

## Outcome and authorization

Give `forge` a declared, repeatable Podman foundation that can build and run a
synthetic container without privileged runtime access, and keep an explicitly
configured user service running across logout and host reboot. This enables
later work toward the first privately accessible web application.

Daniel requested the SYS-001 specification. Drafting is authorized; specification
approval, implementation, host replacement, and deployed acceptance are pending.
This document does not authorize installation or deployment.

## Scope and current baseline

Include host provisioning for Podman and its rootless prerequisites, subordinate
IDs, container networking and storage, the Quadlet generator, the `forge` user
manager and lingering, a synthetic acceptance fixture, and operational recovery
instructions. Include only host packages needed for this capability.

The committed bootstrap creates `forge`, mounts protected ext4 storage at
`/srv/forge`, and installs existing host tools. It does not declare Podman or
Quadlet. This is source evidence, not an inventory of the running host. The AMI
source selects Ubuntu Noble amd64; user-data changes replace the instance and
its disposable root disk. Existing projects survive on the separate volume.

Exclude language toolchains (SYS-002), general dependency policy (SYS-003), a
whole-host tool profile (SYS-004), a privileged broker, shared caches, product
scaffolding, manifest execution, `gptclawctl`, routing, public exposure, production,
and application databases or secrets. RUN-002 owns the future project lifecycle
contract, reconciliation and managed service policy; SYS-001 proves only the
underlying user-service mechanism with a disposable fixture. PRJ-001 remains a
metadata contract and is not executed by this feature.

## Requirements

### RCT-001: Declared and verifiable installation

Provision the supported Podman package set and required helpers through committed
bootstrap code and the protected GitHub Actions/HCP Terraform pipeline. Record
the selected package source, supported version baseline, actual versions and
capabilities in sanitized evidence. Verify rootless execution, storage/network
backends, cgroup v2 and Quadlet availability; a package being installed is not
sufficient. Missing prerequisites must fail the toolchain phase and prevent a
successful bootstrap completion marker. Do not silently fetch an alternative
installer or relax security controls.

### RCT-002: Stable unprivileged identity

Run containers as `forge` without sudo, privileged containers, host engine socket
access, or membership in a root-equivalent group. Declare non-overlapping
subordinate UID/GID ranges sufficient for ordinary multi-user images. Preserve
existing mappings and project ownership across reruns and replacement; detect
conflicts before changes, stop with actionable diagnostics, and never repair
conflicts by recursively changing ownership or resetting container storage.
Rootless execution does not establish isolation between projects sharing `forge`.

### RCT-003: Deliberate storage and data boundaries

Declare graph storage and ephemeral runtime storage separately. Proposed initial
policy: images, writable layers and engine metadata live on the disposable root
disk; project source stays on the protected project volume. No durable application
data is supported by this slice. Document capacity inspection and loss/rebuild
behavior on replacement. A synthetic bind-mount test must leave files usable by
`forge`. Never prune unrelated objects, relocate existing storage automatically,
or treat project files as disposable container cache. Unexpected pre-existing
storage requires an inventoried migration decision before changes.

### RCT-004: Private networking

Support image retrieval, container DNS and outbound connectivity using the
selected rootless networking backend. Publish fixture HTTP traffic only on an
explicit loopback address and unprivileged available port. Verify the listener
and lack of access through a non-loopback host address. Do not modify ingress,
Tailscale routing, privileged-port policy or host firewall policy. This binding
convention is not a sandbox against arbitrary commands by `forge`.

### RCT-005: Quadlet and user-service persistence

Provide working rootless Quadlet generation and a persistent `forge` user manager.
An explicitly installed synthetic unit must start, stop, report status and logs,
restart after a deliberate process failure within bounded limits, remain active
after the last login session ends, and start after reboot before a new `forge`
login. Its definition must express boot activation; generated service files are
not the source of truth. Ordinary containers are not implicitly made persistent.

### RCT-006: Safe provisioning and recovery

Make managed configuration repeatable and preserve unknown user configuration.
Report configuration conflicts and prerequisite failures without claiming success.
Do not broaden sudo, IAM or deployment-role permissions, disable host protections,
or replace the reviewed host policy. Before deployment, review the replacement
plan, quiesce writes, verify an adequate recovery point and record the approved
maintenance window using the existing recovery runbook. Rollback must use a
reviewed code revision and the protected pipeline, preserve the project volume,
and document that reverting code does not recover a terminated root disk.

### RCT-007: Evidence and operational handover

Provide a narrow runbook and synthetic, digest-pinned acceptance fixture with
bounded CPU/memory, bounded retries and task-owned names/paths. Record exact
revision, package versions, commands/results, CI and deployment references,
limitations and owner acceptance without credentials or environment dumps.
Cleanup must stop and remove only fixture units, containers and owned data,
including boot activation. Separate local tests from actual host acceptance.

## Acceptance criteria

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| AC-001 | Rendered-bootstrap tests verify package/configuration ordering, prerequisite failure and completion gating; deployed capability checks identify versions, rootless mode, cgroup v2, generator and selected backends. | RCT-001 |
| AC-002 | Synthetic build/run succeeds as unprivileged `forge`; mapping checks prove no overlap and stable identity on rerun; conflicting mappings fail without mutation; no new privilege grants appear in the reviewed diff. | RCT-002 |
| AC-003 | Observed graph/run paths match policy; synthetic project bind-mount writes remain usable by `forge`; conflict fixtures preserve existing storage; replacement verification preserves project filesystem UUID, ownership and synthetic source while container cache is rebuilt. | RCT-002, RCT-003 |
| AC-004 | Digest-pinned image retrieval and DNS/outbound probes succeed; HTTP responds on loopback, listener inspection shows no wildcard/other-interface binding and a non-loopback probe fails; ingress configuration is unchanged. | RCT-004 |
| AC-005 | Fixture status/logs and deliberate crash demonstrate bounded restart; an independent observer verifies continued operation after all `forge` sessions close and after reboot before `forge` logs in. Record boot/session evidence. | RCT-005 |
| AC-006 | Tests cover repeat configuration, unknown-config conflict and missing prerequisites; reviewed deployment plan retains protected volume and identities; operator records recovery-point check, authorized replacement and post-replacement access/data checks. Rollback procedure is reviewed, with unexecuted rollback explicitly labeled. | RCT-006 |
| AC-007 | Fixture cleanup removes its listener and boot activation without changing unrelated workloads/files; runbook, CI/deployment evidence and criterion-by-criterion acceptance record are reviewed by Daniel. | RCT-007 |

## Decisions and completion

Daniel reviews the proposed disposable engine storage policy and deployment
window. Before implementation, the implementer must inventory non-secret host
identity/storage metadata and resolve exact distro package versions, rootless
network/storage backends, subordinate ranges and fixture image digest against
the target environment. These are implementation gates, not claims of installed
capability. If Noble's supported packages cannot meet the requirements, return a
specific source/version proposal for review rather than expanding host policy.

Deliver implementation, tests, fixture, runbook and an acceptance record in this
initiative. Mark SYS-001 Delivered only after merged implementation and passing
host criteria accepted by Daniel. Local tests or merging these plans alone do
not constitute runtime acceptance.
