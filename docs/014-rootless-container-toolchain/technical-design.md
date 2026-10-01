# TDD-014: Rootless Container Toolchain

- **Status:** Implemented for review; not deployed
- **Owner:** Daniel
- **Last updated:** 2026-10-01 (America/New_York)
- **Specification:** [SPEC-014](spec.md)
- **Tasks:** [TASKS-014](tasks.md)
- **Evidence:** [Acceptance status](acceptance.md)

## Baseline and selected implementation

SYS-004 is merged in [PR #25](https://github.com/danielbardsley/gptclaw/pull/25).
Its [tool profile](../../infra/dev-host/host-tools.json) now declares nine SYS-001
packages: Podman, uidmap, slirp4netns, fuse-overlayfs, netavark, aardvark-dns,
dbus-user-session, crun and libpam-systemd. Existing adapters install/verify them
through the same distribution-maintained Ubuntu Noble policy. No alternate
repository, floating installer, local installation or privilege broker is added.

Read-only discovery on October 1 found Podman absent, cgroup v2 available,
`forge` UID/GID 1002, subordinate start 231072/count 65536, no user container
configuration/storage and linger disabled. `/home/forge` is on the root ext4
filesystem; `/srv/forge/projects` is on the separately mounted ext4 project disk.
These observations select fixed identities and a clean first-install path; they
do not prove runtime capability after deployment.

Observed package candidates: Podman `4.9.3+ds1-1ubuntu0.2`, uidmap
`1:4.13+dfsg1-4ubuntu3.2`, slirp4netns `1.2.1-1build2`, fuse-overlayfs `1.13-1`,
netavark `1.4.0-4`, aardvark-dns `1.4.0-5`, crun `1.14.1-1`. Distro updates are
permitted within the declared source policy; a runtime outside Podman 4.9.x fails
the capability gate. Actual installed package versions are recorded by SYS-004.

## Bootstrap and identity

[Compute](../../infra/dev-host/compute.tf) embeds the standalone
[rootless helper](../../infra/dev-host/lib/rootless.py) in
[cloud-init](../../infra/dev-host/templates/cloud-init.yaml.tftpl) as
`/usr/local/libexec/gptclaw-rootless`. It remains inside the module upload boundary
and the same reviewed deployment revision. Source-checkout provisioning is refused;
only the installed helper running as root can configure the host. This guard is
not a security boundary against an administrator changing code.

Before installing packages, bootstrap prepares administrator-owned system unit
masks for Podman's API socket/service, auto-update service/timer, restart and
transient cleanup services. Noble's inspected maintainer script otherwise enables
these units. Unknown overrides, an unrecorded existing engine or rootful storage
block preparation; known masks are preserved on repeat. Configuration verifies
all six system units remain masked and inactive after package installation.
The separate rootless user manager and explicitly selected Quadlets remain usable.

The [bootstrap](../../infra/dev-host/templates/bootstrap-forge.sh.tftpl) then installs
profile packages and invokes identity setup before the existing `forge` account
configuration. Both subordinate files and account/group collisions are checked
before identity/mapping writes. New `forge` creation explicitly uses UID/GID 1002
and disables automatic subordinate allocation. Matching entries are retained;
missing mappings are appended while unrelated entries are preserved. Different
mappings, real-account collisions, privileged group membership and an unowned
pre-existing home fail without renumbering or recursive chown.

After the existing protected-volume mount succeeds, configuration checks the
expected root/project filesystem locations, required binaries, generator and
cgroup v2. It refuses unknown user configuration, override files, symlinks,
changed policy markers and unrecorded nonempty engine storage. Only absent
managed directories/files are created, with `forge` ownership. A root-owned
intent marker precedes engine initialization so interrupted probes can be retried
without treating their new store as unreviewed legacy storage.

## Runtime foundation

| Concern | Mechanism |
|---|---|
| Storage | User `storage.conf`: overlay with fuse-overlayfs, graph root `/home/forge/.local/share/containers/storage`, run root `/run/user/1002/containers`. |
| Engine/network | User `containers.conf`: crun, systemd cgroups, netavark backend and explicit slirp4netns rootless networking. |
| Persistence | Bootstrap enables linger for `forge`, starts `user@1002.service` and verifies the user manager via its runtime bus. No application unit is installed by bootstrap. |
| Capability gate | As `forge`, inspect sanitized Podman fields, prove actual UID/GID namespace maps with `podman unshare`, and invoke Quadlet in an isolated dry-run directory. No image pull occurs during these probes. |
| Receipt | `/var/lib/gptclaw/rootless-toolchain.json` records policy/configuration digest, identity, selected storage/network/runtime, Podman version and observation time. Read together with SYS-004's deployment-revision receipt. |
| Completion | Final rootless verification precedes host-tool receipt and bootstrap success. Errors remove stale capability/completion receipts. |

User probes use a minimal environment with explicit home, runtime directory and
bus address. No rootful workload, API socket, ingress, Tailscale publication, sudo
permission, IAM permission or kernel/AppArmor relaxation is introduced. Rootless
mode does not separate projects that share `forge`.

Images, writable layers and any engine-local volumes are disposable root-disk
state. Persistent application data is unsupported by this slice. Project source
stays on the existing protected volume. User Quadlets survive reboot but must be
reconstructed from reviewed source after compute replacement; RUN-002 owns future
managed project lifecycle and reconstruction.

## Synthetic acceptance fixture

The [Containerfile](../../examples/rootless-toolchain/Containerfile) uses Alpine
3.22.2's Linux/amd64 manifest digest
`sha256:85f2b723e106c34644cd5851d7e81ee87da98ac54672b29947c052a45d31dc2f`.
The digest was resolved from the public registry; no image was pulled or run
locally. Only the Containerfile is copied into the eventual build context.

[Fixture tooling](../../scripts/rootless-fixture.py) is explicit and unprivileged,
separate from bootstrap and offline CI. It creates unique synthetic data, image,
container and unit names with ownership labels. It tests a keep-id bind write,
DNS and outbound HTTPS, then starts the
[Quadlet](../../examples/rootless-toolchain/fixture.container.in) with explicit
loopback HTTP publication. CPU, memory, PID, restart and startup limits apply.
The generated unit source declares boot activation and waits up to 120 seconds
for the project mount; it cannot quietly start against the unmounted directory.

Checks verify the HTTP token, exact listener and rejection through an actual
non-loopback address assigned to the host. The crash test targets only the owned
fixture and waits for a systemd restart. Cleanup requires matching labels and
unit digest, removes only known resources/data and verifies listener removal;
unknown files or engine errors stop cleanup. Shared base images/cache are retained.
Logout, pre-login reboot checks and replacement/rebuild evidence require the
independent operator steps in the [runbook](../../runbooks/manage-rootless-toolchain.md).

## Verification, deployment and recovery

[Offline tests](../../scripts/tests/test_rootless_toolchain.py) use synthetic
accounts/files and fake commands. They cover collisions, stable repeated identity,
config/storage conflicts, capability failures, user-probe environment and scoped
fixture cleanup. The existing SYS-004 suite continues to validate the expanded
profile. [Terraform tests](../../infra/dev-host/tests/rootless.tftest.hcl) mock AWS
and use real local cloud-init to check ordering, exact embedded bytes, replacement
wiring and the unchanged EC2 payload limit. Remaining script payloads use literal
YAML inside the compressed cloud-init envelope to avoid redundant base64 expansion.

The Ubuntu Podman package was downloaded to a task-owned temporary directory,
verified against apt metadata SHA-256
`e5c1c37e387ed14c352a744a75fbb79fb2f82573ca7bf36886e3b7333fc9ef1a`, and extracted
without installation. Its actual Quadlet binary parsed the fixture in dry-run
mode. This verifies generator syntax, not container/systemd runtime behavior.

Merges trigger quality checks only. Deployment remains an explicitly dispatched,
protected GitHub Actions -> HCP Terraform -> AWS operation. Before replacement,
review the plan/recovery point, quiesce writes and obtain Daniel's authorization
and maintenance window. Verify SSM/private SSH, original filesystem UUID, project
ownership and capability receipts after replacement; then run host acceptance.

Rollback uses reviewed code and the same pipeline, preserving the project disk
and identity. A revert to pre-SYS-001 dynamic user allocation must retain/prove
UID/GID 1002 before reuse of protected data; never compensate with recursive chown.
Check old package availability and SYS-004 exception expiry. Do not downgrade an
existing store, reset the engine or restore an entire user home. Rollback review
is distinct from an executed drill, and broader snapshot restore remains RES-002.

## Traceability

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| RCT-001 | SYS-004 packages, prerequisite checks and completion gate | T-002, T-003, T-005 | AC-001 |
| RCT-002 | Fixed observed IDs, collision checks and real namespace probes | T-002, T-003, T-004, T-005 | AC-002, AC-003 |
| RCT-003 | Explicit disposable storage, conflict refusal, keep-id fixture | T-002, T-003, T-004, T-006 | AC-003 |
| RCT-004 | Rootless backend and loopback/DNS/outbound fixture checks | T-002, T-004, T-006 | AC-004 |
| RCT-005 | Linger, user manager and bounded opt-in Quadlet | T-003, T-004, T-006 | AC-005 |
| RCT-006 | Conflict-safe bootstrap and protected recovery procedure | T-003, T-005, T-006 | AC-006 |
| RCT-007 | Scoped fixture/runbook and separate acceptance record | T-004, T-006, T-007 | AC-007 |

Version-matched sources: [Podman 4.9.3 Quadlet](https://docs.podman.io/en/v4.9.3/markdown/podman-systemd.unit.5.html),
[containers.conf](https://github.com/containers/common/blob/v0.57.4/docs/containers.conf.5.md),
[storage configuration](https://github.com/containers/storage/blob/v1.51.0/docs/containers-storage.conf.5.md),
[Ubuntu Noble Podman](https://packages.ubuntu.com/en/noble/podman).
