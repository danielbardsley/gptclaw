# Manage the rootless container toolchain

[SYS-001](../docs/014-rootless-container-toolchain/spec.md) adds the declared Podman
foundation through [SYS-004's tool profile](../infra/dev-host/host-tools.json).
It does not implement project lifecycle commands, private routing or public access.

## Deployment is IaC-only

Merging a PR runs quality checks; it does **not** apply Terraform. The existing
[workflow](../.github/workflows/terraform-dev-host.yml) requires a manual dispatch
on `main` with `operation: plan` or `operation: apply`. An apply requires the
`gptclaw-dev-host` confirmation and the existing development environment gates.
Terraform runs in HCP, with AWS changes made by the reviewed deployment role.
No local installation, local Terraform apply or ad hoc sudo is part of this feature.

The [bootstrap helper](../infra/dev-host/lib/rootless.py) is embedded in cloud-init
from the same reviewed checkout. It refuses provisioning from a source checkout.
Cloud-init calls it during instance creation. It is not an agent runtime command.
Changing bootstrap/user data replaces compute; it does not install tools on the
running host when Git is pulled. Follow [host recovery](recover-dev-host.md):
review the protected plan and adequate recovery point, quiesce project writes,
obtain Daniel's concrete replacement authorization/window, and verify private
access and the protected filesystem after replacement. The deployment-policy rendering repair is merged. Enrollment now uses
[workload identity federation](manage-tailscale-federation.md); complete its one-time
account issuer and Tailscale trust setup before the protected host plan/apply.
The old manual key/counter step is superseded. Review recovery readiness and
require the plan to retain the project volume and HCP identities.


## Declared baseline and boundaries

| Setting | Reviewed selection |
|---|---|
| OS/package source | Ubuntu Noble amd64, official configured Ubuntu repositories through SYS-004. |
| Podman | Runtime 4.9.x; inspected candidate `4.9.3+ds1-1ubuntu0.2`. Distribution patch updates allowed; a different minor/major runtime fails capability verification. |
| Explicit prerequisites | `uidmap`, `slirp4netns`, `fuse-overlayfs`, `netavark`, `aardvark-dns`, `dbus-user-session`, `crun`, `libpam-systemd`; dependencies remain package-manager-owned. |
| Host identity | `forge` UID/GID 1002, matching the observed host and project ownership. |
| Subordinate mappings | `forge:231072:65536` in both `/etc/subuid` and `/etc/subgid`, preserving the observed allocation. |
| Runtime/cgroups | `crun`, cgroup v2 and the user systemd manager. |
| Network | Netavark backend, slirp4netns for rootless networking. Fixture publication is explicit IPv4 loopback only. |
| Storage | Overlay with `/usr/bin/fuse-overlayfs`; graph root `/home/forge/.local/share/containers/storage`; run root `/run/user/1002/containers`. |
| User persistence | Linger for `forge`; user manager started during bootstrap. Only explicitly activated Quadlets start at boot. |

The subordinate range contains 65536 IDs, from 231072 through 296607 inclusive.
Preflight rejects collisions with other users, groups or allocations, differing
`forge` identity/mappings and privileged group memberships. It checks both mapping
files before writing either and disables automatic range allocation when creating
`forge`. It never renumbers existing users or recursively changes project ownership.
Partial provisioning can be retried only with unchanged valid configuration.

Before package installation, bootstrap masks six system-level units declared in
the helper (API socket/service, auto-update service/timer, restart and transient
cleanup). This counters Noble's package default of enabling those services.
Unknown unit overrides, existing engine binaries or rootful storage without the
matching management marker fail preflight. The package helper preserves these
administrator-owned masks; bootstrap verifies masked/inactive state afterward.
No such masks have been installed on the current host during implementation.

Managed user files are `~/.config/containers/storage.conf` and `containers.conf`.
Unknown files at those paths, config overrides, symlinks, changed policy markers
or unrecorded nonempty engine storage block provisioning rather than being
removed or migrated. `/var/lib/gptclaw/rootless-policy.json` records managed intent
before the first engine probe, allowing a failed first probe to be retried without
misidentifying its initialized storage as an unrelated store.

The graph store is disposable root-disk state: images, writable layers, local
named volumes and generated fixture services are not preserved by replacement.
This slice supports no durable application data. Project source remains under
`/srv/forge/projects` on the protected volume. Inspect capacity with `df -h` and,
once deployed, `podman system df` as `forge`; do not use global prune/reset as a
repair step. Never move a store or change mappings while retaining its files
without a separately reviewed migration.

Rootless containers share `forge`'s host identity. These conventions are not a
security boundary between projects or enforcement against arbitrary commands by
that user. This feature grants no new sudo/IAM rights, opens no engine socket,
changes no ingress or kernel/AppArmor policy, and does not configure production.
SYS-004's existing channel exceptions still expire after November 1, 2026
(America/New_York); deployment must respect that independent gate.

## Bootstrap verification and diagnosis

Configuration follows account creation and successful mounting of `/srv/forge`.
The helper checks the installed binaries/generator, cgroup v2, intended filesystems,
linger, the user bus, rootless Podman information, UID/GID namespace maps and
Quadlet generation. Engine/namespace probes run as `forge` with a minimal explicit
user-manager environment. They neither pull an image nor start an application.
Failure prevents bootstrap success and retains an actionable bounded error.

`/var/lib/gptclaw/rootless-toolchain.json` records the capability result and storage/
identity policy. Read it together with the SYS-004 receipt and bootstrap marker
for the deployment revision and actual package versions. Check the approved
revision against the protected pipeline, not the current Git checkout alone.

Read-only diagnosis after deployment:

```sh
cat /var/lib/gptclaw/rootless-toolchain.json
cat /var/lib/gptclaw/host-tools.json
cat /var/lib/gptclaw/bootstrap-complete.json
loginctl show-user forge -p Linger -p RuntimePath
systemctl --user status
podman version
podman info --format '{{.Host.Security.Rootless}} {{.Host.CgroupsVersion}} {{.Host.NetworkBackend}}'
podman unshare cat /proc/self/uid_map
podman unshare cat /proc/self/gid_map
```

Do not publish unrestricted engine information, environment dumps or credential
files. If namespace, mount or AppArmor checks fail, record the narrow failure and
return to reviewed code; do not disable host protections or substitute rootful
containers. A successful package install alone does not pass SYS-001 acceptance.

## Explicit synthetic acceptance fixture

Only run this after an authorized deployment, as `forge`, from the repository.
It builds a minimal HTTP fixture from Alpine 3.22.2 pinned to an amd64 manifest
digest. It uses only a copied Containerfile and synthetic files; it never sends
the GptClaw checkout as a container build context. It pulls the public image,
checks DNS/outbound HTTPS to `example.com`, tests a keep-id bind write and starts
one bounded user Quadlet. No secrets or production data are needed.

```sh
python3 scripts/rootless-fixture.py start --port 18081
```

The script prints its unique directory under `/srv/forge/projects` before work.
Retain that printed path for subsequent commands; do not replace it with a real
project directory. If the selected port is occupied, choose another high port;
never stop its existing listener. The image, container, probe and Quadlet use a
unique name/ownership label. Failures retain the directory for scoped cleanup.

```sh
python3 scripts/rootless-fixture.py check --directory /srv/forge/projects/PRINTED-FIXTURE-NAME --non-loopback HOST-PRIVATE-IPV4
python3 scripts/rootless-fixture.py crash --directory /srv/forge/projects/PRINTED-FIXTURE-NAME
```

Use an actual non-loopback IPv4 address assigned to the host. The check verifies
an HTTP token, exact loopback listener and failed connection via that address.
`crash` kills only the labeled fixture and verifies systemd restarts it. The
Quadlet has CPU/memory/PID limits, three starts per minute, bounded mount waiting,
read-only container root, keep-id, no added capabilities and no image auto-update.
The boot source is its `.container` file with `WantedBy=default.target`; do not
try to enable the generated transient `.service` as a persistent source file.

Logout/reboot acceptance needs an independent operator session (for example the
existing approved SSM recovery session). Record all `forge` sessions closing and
confirm the user manager/fixture stays active without opening another `forge`
login. For reboot, obtain a maintenance window, reboot through the reviewed
operator path and check the fixture before any new `forge` login. Record boot ID,
service status and listener/HTTP evidence; a later interactive login is not proof
of boot activation. The fixture waits up to 120 seconds for the project mount
before starting; missing mounts fail rather than using an empty root-disk path.
Do not trigger reboot or replacement from the fixture script.

For authorized replacement acceptance, record the project filesystem UUID,
synthetic source hashes and ownership first. Remove/stop runtime fixture resources
before quiescing writes, retaining the desired synthetic source evidence for the
operator's preservation check. After replacement verify those same files and
filesystem identity; explicitly rebuild/reinstall a fresh fixture from reviewed
source. Root-disk images and user Quadlets must be recreated. This is separate
from a snapshot restore drill.

Cleanup:

```sh
python3 scripts/rootless-fixture.py cleanup --directory /srv/forge/projects/PRINTED-FIXTURE-NAME
```

Cleanup checks labels and the unit digest before stopping/removing the owned
resources. It removes its activation source and regenerates user units, its built
image tag and known synthetic files, then checks that the listener is gone.
Changed units or unexpected files stop cleanup for inspection; no broad deletion,
image prune or engine reset occurs. The shared digest-pinned base image/cache is
retained so unrelated workloads cannot lose it. Export sanitized evidence before
cleanup. Use only the task-owned names when recovering an interrupted fixture.

## Recovery and acceptance

A reviewed revert through GitHub Actions/HCP Terraform is the rollback path; it
may replace compute again. Preserve the project volume and identity protections.
Older pre-SYS-001 bootstrap code allocated `forge` dynamically: any rollback must
retain the reviewed UID/GID allocation or explicitly prove the old code will
recreate the same identity before attaching project data. Do not blindly revert
identity preservation or chown persistent data to compensate. Check older package
availability and SYS-004 exception expiry before attempting rollback.

The [acceptance record](../docs/014-rootless-container-toolchain/acceptance.md)
separates local mocks and generator parsing from actual host behavior. Mark
Delivered only after merged implementation, authorized deployed checks and
Daniel's acceptance. Current implementation does not prove DNS/HTTP, actual
container execution, logout persistence, reboot startup or replacement recovery.

References: [Podman 4.9.3 Quadlet](https://docs.podman.io/en/v4.9.3/markdown/podman-systemd.unit.5.html),
[Ubuntu Noble Podman](https://packages.ubuntu.com/en/noble/podman).
