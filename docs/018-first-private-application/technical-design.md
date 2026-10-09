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

The application serves its declared `/projects/<slug>/` prefix directly; the
Serve adapter preserves that prefix. Verify actual Next.js development behavior,
assets and browser-update transport through the selected routing mechanism.
Before private route mutation, inspect existing Serve configuration and available
operator permissions. Preserve unrelated routes and refuse ownership conflicts;
never reset the entire configuration. If routing permissions or prefix forwarding
need host changes, produce a separate reviewed scoped proposal. No public Funnel
fallback or new ingress is permitted.

## Verification and boundaries

Use synthetic projects in task-owned directories. Test invalid manifests/no
execution, existing destination preservation, port conflicts, concurrent starts,
health failure/timeout reconciliation, bounds, route conflicts and scoped stop.
Then demonstrate create/start/open/edit/test for the first project and concurrent
operation of the second from a tailnet browser. Record live results separately
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

Open choices for implementation review: exact toolchain pins, port range/resource
bounds, runtime-state/operation schema and installed Serve capability. Resolve
these before their dependent implementation; planning does not install anything.
