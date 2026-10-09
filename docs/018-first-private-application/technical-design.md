# TDD-018: Minimal private application workflow

- **Status:** Draft
- **Owner:** Daniel
- **Specification:** [SPEC-018](spec.md)
- **Tasks:** [TASKS-018](tasks.md)

## Proposed approach

A user-scoped Python CLI orchestrates reviewed rootless Podman/user Quadlet
interfaces. Reuse the strict manifest validator and its isolated environment.
Keep runtime state under a platform-owned namespace on the project volume,
separate from authored manifests/source; keep disposable engine storage on the
root disk. The CLI is the documented lifecycle provider for the existing runtime
operation skill once its version, capabilities and receipt mapping are reviewed.
It is not a new daemon or privileged broker.

| Component | Proposed responsibility |
|---|---|
| CLI and bounded state/operation receipt | Resolve project, validate, serialize transitions, allocate port, report health/status/logs |
| Single Next.js/TypeScript template | Pinned container toolchain, pnpm lockfile, tests, health route, base-path support and adapted guidance |
| Per-project rootless containers/Quadlet | Dependency/build/test execution and development service with limits and loopback publication |
| Private routing adapter | Reconcile only selected owned Serve paths to healthy ports, preserving existing configuration |

Implementation chooses exact supported Node/pnpm/Next.js versions and an image
digest using primary documentation. Project commands run with project root as
container working directory, matching manifest argument-vector semantics.
Dependencies/caches are project-specific; no credential/environment material is
mounted by default. Define writable cache paths needed by Next.js separately
from source and respect forge ownership. A read-only runtime root is preferred
where compatible; verify required temporary paths rather than relaxing privileges.

## Stage 1: Hello World on the desktop

After implementation authorization, resolve the current node DNS name, healthy
rootless/tool receipts, a free high loopback port, existing Serve configuration,
operator capability and Daniel's desktop tailnet access. Check HTTPS/certificate
readiness before expecting a private HTTPS URL. A read-only status response is
not proof of write authority. If prerequisites need operator or tailnet changes,
prepare their exact scope; host configuration follows the protected pipeline.
Tailscale's general Unix operator option is broader than a Serve-only grant and
must not be enabled casually as a workaround for a denied route operation.

Pin supported container/tool/framework versions, then implement a small
Next.js/TypeScript Hello World starter on the project volume. Include its v1
manifest, health route and `/projects/hello-world/` base-path configuration. Build
and run it as forge in a bounded rootless service with loopback host publication.
Initial reviewed commands or a narrow runner are sufficient; the final CLI can
follow. Do not pass the whole platform checkout as the app build context or mount
credentials. Inspect readiness directly on loopback before publishing.

Configure only the selected owned Serve path to that backend through the
approved operator interface. Verify actual forwarding of root, asset and health
paths on the installed version; a Serve mount path alone is not proof that the
backend receives its required prefix. Use a URL target with an explicit backend
path where supported and verify semantics, rather than assuming prefix handling.
Keep the rest of Serve configuration intact and verify no active Funnel route.

Return `https://<current-node-DNS>/projects/hello-world/` using the real current
node DNS from Tailscale, not a permanent hardcoded hostname. Daniel opens it on
his desktop and confirms the content. Record local health and desktop reachability
separately. Keep the owned service available for the confirmation, then demonstrate
scoped stop/route removal while retaining app source. In stage 2 reuse the starter
and safely reconcile the prototype resources; do not overwrite or adopt unknown
projects/services. A Serve inline-text response is not an application proof.

## Lifecycle and routing

`new` refuses an occupied destination and writes the selected template/manifest.
`validate` is read-only. `start` validates, obtains the per-project lock, reserves
an available port, prepares the reviewed container/service and waits within a
fixed deadline for the declared health path. Running is not ready. Record an
operation ID and final state; on timeout/lost response reconcile that operation
instead of blindly repeating it. `stop` removes owned running resources and the
owned route while preserving project source. Repeated operations are no-ops
where already satisfied; report busy for concurrent conflicting operations.

Keep the v1 author manifest unchanged: assigned ports, image IDs, operation IDs
and route ownership belong to runtime state. Check actual port availability in
addition to the allocation registry. Document bounds and nonzero error categories
before connecting the runtime-operation skill. Limit logs by lines/time and avoid
credentials/raw environment dumps; project output is untrusted data.

The application serves its declared `/projects/<slug>/` prefix. Test and document
the Serve-to-backend path transformation; configure the target path so the app
receives that prefix, rather than assuming Serve preserves it automatically.
Verify Next.js development behavior, assets and browser-update transport through
the selected mechanism. Stage 2 implements the reusable route adapter based on
the proven first-stage behavior.
Before private route mutation, inspect existing Serve configuration and available
operator permissions. Preserve unrelated routes and refuse ownership conflicts;
never reset the entire configuration. If routing permissions or prefix forwarding
need host changes, produce a separate reviewed scoped proposal. No public Funnel
fallback or new ingress is permitted.

## Verification and boundaries

Use synthetic projects in task-owned directories. Test invalid manifests/no
execution, existing destination preservation, port conflicts, concurrent starts,
health failure/timeout reconciliation, bounds, route conflicts and scoped stop.
Demonstrate stage 1 from Daniel's actual desktop first. Then demonstrate
create/start/open/edit/test for the managed first project and concurrent operation
of the second from the same tailnet browser. Include relative assets, health,
redirects and development WebSocket/browser updates. Capture stage timings and
report observed results instead of promising an unmeasured speed target. Record live results separately
from offline tests and CI; document restart/rebuild and source retention.

Cleanup stops only owned services and routes, preserving source by default and
shared container caches. Interrupted operations retain recoverable state. No
broad image prune, recursive project deletion or extra host packages. Rollback
reverts reviewed workflow code and reconciles owned runtime state; it cannot
restore ephemeral app data and must preserve independent projects.

| Requirements | Tasks | Acceptance |
|---|---|---|
| APP-001 | T-002 | AC-001 |
| APP-002, APP-003 | T-003 | AC-002, AC-003 |
| APP-004, APP-005 | T-004 | AC-004, AC-005 |
| APP-006 | T-005 | AC-006 |
| APP-007 | T-006, T-007 | AC-007 |

Open choices for implementation review: exact toolchain pins, port range/resource
bounds, runtime-state/operation schema and installed Serve capability. Resolve
these before their dependent implementation; planning does not install anything.

## Source and feature progress

Installed Tailscale 1.104.1 help confirms background serving, path mounting and
URL targets. Official documentation describes HTTPS prerequisites, access rules
and the Unix operator option; none establishes this host's write permissions.
References checked October 9, 2026:

- [Serve CLI](https://tailscale.com/docs/reference/tailscale-cli/serve): route targets, path mount, status and scoped route removal.
- [Serve prerequisites](https://tailscale.com/docs/features/tailscale-serve): HTTPS readiness and applicable tailnet access rules.
- [Unix operator option](https://tailscale.com/docs/reference/tailscale-cli/up): daemon operation by a selected Unix user.

Record stage-specific progress against the specification's feature map. A one-off
route proof supports the first NET-101/102/103 slice, not a complete routing
manager. The CLI, second-project allocation and broader template behavior remain
unimplemented until their own tasks pass. Existing host and skill acceptance
continues in its original records; do not launch interruption tests for this plan.
