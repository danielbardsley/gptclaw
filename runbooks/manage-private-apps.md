# Develop private web applications

[SPEC-018](../docs/018-first-private-application/spec.md) defines this initial
single-service Next.js workflow. Run as forge. Node/pnpm and project commands run
inside rootless containers; no host language package installation is needed.
The projects share forge's identity: these controls are not a security boundary
between hostile projects.

## Runner and prerequisites

From the GptClaw checkout, prepare the existing isolated manifest environment if
it does not exist, then use `scripts/gptclawctl`. Its `--version` reports the
provider version/capabilities and receipt schema. After ingress setup a stable
snapshot launcher is available at:

```text
/srv/forge/projects/.gptclaw-runtime/v1/gptclawctl
```

The installed snapshot includes code, schema and template, independent of Git
branch switches. It uses the prepared repository Python environment. Preserve
that environment; do not delete it while services depend on it. Provider updates
reconcile owned files/checksums; an unknown unit, drop-in, route or launcher is a
conflict, not permission to overwrite it.

## One-time private ingress

The unprivileged router listens only on `127.0.0.1:18079`. The operator uses the
existing approved SSM access to configure exactly the owned apps prefix after
router health is verified. Do not grant forge general Tailscale operator rights
as a workaround for a denied Serve operation.

```sh
sudo tailscale serve --bg --https=443 --set-path=/projects/ http://127.0.0.1:18079/projects/
```

Keep unrelated Serve entries. Before applying the prefix, inspect configuration
and require that this path is empty or already points to this backend, and that
Funnel is off. HTTPS/tailnet prerequisites need their scoped owner consent. A
successful read-only status call does not establish write authority.

For the initial verified Hello World prototype only, remove its more-specific
route after the shared prefix works:

```sh
sudo tailscale serve --https=443 --set-path=/projects/hello-world/ off
```

Require its existing target to match the known prototype backend first. No Serve
reset, unrelated route removal, sudo/IAM grant or infrastructure mutation is part
of this setup. After this one-time private prefix, CLI start/stop controls only
its own application mappings through the loopback router without sudo.

## Create and use an app

Use the source runner from repository root, or substitute the stable launcher:

```sh
scripts/gptclawctl new my-app
scripts/gptclawctl validate --project-root /srv/forge/projects/my-app
scripts/gptclawctl start --project-root /srv/forge/projects/my-app
scripts/gptclawctl status --project-root /srv/forge/projects/my-app
scripts/gptclawctl logs --project-root /srv/forge/projects/my-app --lines 40
scripts/gptclawctl test --project-root /srv/forge/projects/my-app
scripts/gptclawctl restart --project-root /srv/forge/projects/my-app
scripts/gptclawctl stop --project-root /srv/forge/projects/my-app
```

`new` refuses existing destinations and writes a valid v1 manifest, provider
marker, pinned starter and adapted guidance. Read that project's guidance before
editing. The first `start` enforces the [dependency policy](manage-project-dependencies.md),
installs from the frozen lockfile with hooks/version downloads disabled and runs the manifest
build vector, then starts the development service and waits for declared health.
Dependency preparation/build is reused on later starts until its lock/toolchain
fingerprint changes. Development source edits update Next.js without hand-editing
host units. The returned private URL uses the actual current node DNS name.

`stop` revokes this project's mapping, stops/removes its owned service/container
and activation source, and preserves project files, dependencies and shared
images. Another app is unaffected. The shared ingress service and private prefix
remain available for subsequent apps; they are platform resources, not a
per-project route to delete. Stop does not archive or delete project data.

Runtime state is in `.gptclaw-runtime/v1`, separate from manifests. Source and
project-local build/dependency caches live on the retained project volume;
container images live on the disposable root disk. No managed persistent
application data or databases are provided. Do not put credentials in source or
logs. This slice refuses common project environment/authentication files; it
mounts no home/credential directory. That is not comprehensive secret detection.

## Provider contract and recovery

- Target: absolute non-symlink project root under `/srv/forge/projects`, valid
  manifest v1 and `nextjs-v1` marker. IDs are stable lowercase slugs; duplicate
  IDs pointing to different roots fail. Only the approved single-web slice is supported.
- Ports: stable reservations in 18080–18179, plus actual availability checks.
  Services publish exclusively on loopback. A stopped project's reservation is
  retained for its next start; no port/interface is taken from another process.
- Resources: each app/job has 1 CPU, 1536 MiB and 256 PIDs; the router has 192 MiB,
  50% CPU, 64 tasks and 16 request workers. HTTP request/response bodies are capped
  at 2 MiB; upstream requests have 15-second bounds and development WebSockets a
  120-second idle bound. This is not a general streaming/API ingress yet.
- Lifecycle mutation receipts (start/stop/restart/test): `operation_id`, selected `project`, state, change flag and
  duration. A never-started stop can be a no-op without an operation ID. Start waits up to 120 seconds after service start for HTTP health;
  individual scoped build/job commands are limited to 300 seconds. Ready does
  not substitute for Daniel's desktop check. Route state/URL are separate; an
  operator-required route is a partial outcome, with no invented URL.
- Concurrency: per-project nonblocking locks; a brief registry lock protects
  allocation. Conflicting operations report busy without stealing/cancelling.
  Stop refuses an unresolved owned job; unknown job outcomes are preserved.
- Reconciliation: on lost output/timeout call status for the same root and use
  its stored operation ID, last operation/error, job-busy and observed health.
  Do not blindly repeat a mutation. Restart intentionally records stop/start
  transitions and a new final operation ID, even if the app was initially ready.
- Logs: only the selected owned service, up to 200 lines from the last hour,
  bounded captured output and a 32 KiB returned excerpt. Common credential
  patterns are redacted; project authors must still avoid logging secrets.
- Results: JSON; exit 0 for the reported successful/observed outcome, 1 for
  validation/conflict/busy/failed/partial-route outcomes and 2 for usage/setup or
  unreconciled internal failure. Validation remains observation-only.

On conflict inspect only named metadata and owned bounded logs. Do not reset
Podman, prune shared images, disable protections, alter unknown units/drop-ins or
broaden IAM/sudo/daemon permissions. Source changes and provider upgrades use the
repository PR workflow; any needed privileged host configuration follows the
protected infrastructure pipeline. Existing full host acceptance remains in
SPEC-014/015/016; this workflow does not run logout, reboot or replacement tests.

## Dependency changes

Provider 1.1.0 adds typed `deps status/install/add/update/remove/recover` operations.
Use [the dependency runbook](manage-project-dependencies.md) for exact packages,
source/lock review, stopped-target mutations, frozen repair and operation-ID
reconciliation. Runtime operations must not be substituted for dependency-policy
exceptions; startup/test preparation uses the same validator and policy fingerprint.

Provider 1.2.0 adds [project-selected toolchains](manage-project-toolchains.md).
New apps declare the exact reviewed Node/pnpm profile; legacy apps retain a fixed
selection. The resolver supplies the same image to dependencies/build/test/start.
