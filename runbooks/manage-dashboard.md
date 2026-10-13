# Operate the private projects dashboard

The dashboard is platform tooling from [SPEC-027](../docs/027-dashboard-project-inventory/spec.md),
[SPEC-028](../docs/028-dashboard-live-service-status/spec.md) and
[SPEC-029](../docs/029-dashboard-project-links/spec.md). Source is reviewed in
`platform/dashboard/`; installed assets live separately on the project volume under
`/srv/forge/platform`. Operate as forge through `scripts/manage_dashboard.py` using
the prepared isolated manifest interpreter. This does not manage project data.

## Build and prepare

The approved base directory must already exist with forge ownership and mode 0700.
The existing project-volume mount root is owned by root; forge does not create or
change permissions on it. If `/srv/forge/platform` is absent, the existing operator
must provision only this new application directory after reviewing this runbook:

```sh
test ! -e /srv/forge/platform && test ! -L /srv/forge/platform && sudo install -d -m 0700 -o forge -g forge /srv/forge/platform
```

First verify the expected project volume is mounted at `/srv/forge`. If the path exists
with unexpected ownership, links or contents, inspect it rather than overwrite it.
This is scoped operational allocation on the existing protected project volume: it
changes no AWS resource, mount, identity, deletion protection or host access control.
No forge privilege or parent-directory permission change is granted. Preserve the
existing reviewed operator path and infrastructure gates; do not run unrestricted
sudo or use an AWS configuration workaround.

Use the reviewed Node/pnpm profile in [the toolchain registry](../config/toolchains/v1.json),
with the immutable `templates/apps/node-toolchain` recipe if the matching image is
not already installed. Do not install host Node, pnpm or Python packages.

Inside the reviewed rootless container, mount only `platform/dashboard` at `/workspace`,
use `/workspace` as working directory, set `NEXT_TELEMETRY_DISABLED=1`, finite CPU,
memory/PID limits, and run:

```sh
pnpm install --frozen-lockfile --ignore-scripts --no-runtime --pm-on-fail=error --ignore-pnpmfile --registry=https://registry.npmjs.org/
pnpm test
pnpm typecheck
pnpm build
```

The build creates standalone Node assets and static files in ignored `.next/` output.
Keep caches/build files on the project volume; the host root volume is capacity-limited.
No starter demo UI, demo API or application database is included. The two API reads
are `/dashboard/api/health/` and `/dashboard/api/snapshot/`.

```sh
/srv/forge/projects/gptclaw/.venv-manifest/bin/python -B scripts/manage_dashboard.py prepare
```

Preparation validates the standalone assets, records their hashes, freezes the exact
local image ID and provider snapshot/interpreter, and creates an immutable release in
`/srv/forge/platform/releases/<sha256>/`. The `run/` socket directory is mode 0700.
Unknown existing files/unsafe ownership/symlinks are refused, and failed owned stages
are retained for inspection. Project manifests, data and existing routes are untouched.

## Install and start the owned services

After review and relevant checks, use the prepared release identity:

```sh
/srv/forge/projects/gptclaw/.venv-manifest/bin/python -B scripts/manage_dashboard.py start --release <sha256>
/srv/forge/projects/gptclaw/.venv-manifest/bin/python -B scripts/manage_dashboard.py status
```

This serializes dashboard operations and owns only:

- `~/.config/systemd/user/gptclaw-dashboard-collector.service`
- `~/.config/containers/systemd/gptclaw-dashboard.container`
- `/srv/forge/platform/owner.json`, immutable releases and the owned socket namespace

The collector runs as forge from a versioned provider snapshot, using the prepared
Python environment. The frontend uses a rootless container publishing only
`127.0.0.1:18200:3000`. Its only host mounts are immutable frontend assets and the
read-only collector socket directory. It receives no project/runtime credential
store or Podman socket. Both services have finite resource limits and restart policy.
Unknown/drifted units or systemd drop-ins block lifecycle changes. Keep the prepared
Python environment while the collector depends on it.

Collector observations and transitions are in memory. Socket lifecycle receipts
record only an inode/device pair; a restart may replace a socket only after proving
its exact owned stale inode under an exclusive lock. An unknown or live socket is
preserved for inspection. This is accidental-exposure protection within the shared
forge account, not isolation from malicious code running as the same user.

## Private Serve route: operator step

Forge does not receive Tailscale administration or new sudo rights. Inspect the
existing Serve configuration through the established operator path. Require that
`/dashboard/` is absent or already targets this exact backend, preserve `/projects/`
and every unrelated handler, and require Funnel off. First prove the frontend is
healthy locally, sending the configured tailnet Host header:

```sh
curl --fail --header 'Host: <forge-dev-tailnet-host>' http://127.0.0.1:18200/dashboard/api/health/
```

Only the existing authorized operator configures the reviewed owned path:

```sh
sudo tailscale serve --bg --https=443 --set-path=/dashboard/ http://127.0.0.1:18200/dashboard/
```

This runbook supplies a scoped procedure, not a new permission grant. Keep the existing
operator/infrastructure gates. Do not reset Serve, change EC2 configuration directly,
broaden permissions after denial or enable Funnel. Capture sanitized configuration
and HTTPS/browser evidence. The dashboard URL is
`https://<forge-dev-tailnet-host>/dashboard/`; it is useful only from the tailnet.

The frontend checks the configured Host/Origin, browser fetch site, request path and
read method. Arbitrary root paths, URL overrides, mutation methods and cross-origin
reads are rejected. A successful loopback probe does not establish owner desktop
access; that requires the owner's tailnet browser acceptance.

## Inventory metadata and freshness

Optional `metadata.json` is maintained through reviewed operator edits, never through
a dashboard write endpoint. Use forge ownership, mode 0600 and this versioned shape:

```json
{"schema_version":1,"projects":[{"root":"/srv/forge/projects/example","id":"example","owner":"Project owner","repository":"https://github.com/example/project"}]}
```

Bind entries to the exact canonical root and validated ID. Use only non-secret labels
and canonical credential-free HTTPS GitHub URLs. Missing data shows “Not recorded”;
invalid registries cannot replace project identity. Do not populate metadata by reading
Git credential/configuration or broker secret stores. The registry is bounded to 256
entries/128 KiB. The scan is bounded to 256 immediate directory candidates, 4096 entries,
10 seconds and a 1 MiB public response. Discovery does not execute repository code.
Snapshots refresh at 30 seconds and become stale after 60 seconds without success.
Documentation labels check safe file presence only, not prose quality.

## Stop, rollback and recovery

```sh
/srv/forge/projects/gptclaw/.venv-manifest/bin/python -B scripts/manage_dashboard.py stop
/srv/forge/projects/gptclaw/.venv-manifest/bin/python -B scripts/manage_dashboard.py rollback
```

Stop only the two owned services. Rollback selects the recorded previous immutable
release and verifies assets/unit ownership before activation; it never modifies project
runtimes, sources, metadata, databases or public previews. Preserve releases and registry
for recovery. If an interrupted installation leaves unknown unit/receipt state, inspect
it through review rather than overwrite it. To remove the private dashboard route, the
operator must first verify that its current target matches the owned backend; remove
only that handler and preserve all others. Never reset Serve or delete project data.

## Enable the reviewed status and links increments

The default release enables inventory only. After its foundation is verified, prepare
and activate the reviewed status increment with `--with-status`; enable the link
increment with `--with-links` (which also enables status). Exact feature flags are
frozen in the release descriptor and included in its identity. The collector exports
a fixed full snapshot; browser reads never spawn project observations.

Provider 1.9.0 adds `gptclawctl observe --project-root <owned-root>` with observation
and route schema 1. It remains read-only: ownership/readiness checks precede metadata
projection, native calls are allowlisted, receipt writes are refused and no snapshot
publication occurs from observation. Clean preloaded forkserver workers collect at
most four projects concurrently, bounded by available CPUs, with at most three component-read threads per group
and a four-second project deadline. Twenty projects form a bounded collection window;
larger inventories rotate windows and show capacity/freshness limitations. Status
becomes stale after 30 seconds; first-observed and change-detected labels do not
promise exact unseen event times. Uptime/counters describe the current instance.

Private app/docs links require fresh ready publication and exact observed route
capability. The provider verifies only fixed owned docs paths with a bounded private
GET; the pure link layer never crawls URLs. Repository links use validated metadata
and the browser's GitHub authentication. Log-viewer/preview-registry adapters remain
unavailable until their separately accepted prerequisites exist. No logs endpoint,
Funnel operation or public preview is added by these feature switches.
