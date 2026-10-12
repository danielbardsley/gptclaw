# TDD-027: Private dashboard foundation and inventory adapter

- **Status:** Proposed — no implementation or deployment performed
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-027](spec.md) · **Tasks:** [TASKS-027](tasks.md)

## Approach and existing interfaces

Keep the platform application under `/srv/forge/platform`, with reviewed source and
release provenance established during implementation. Do not add a product runtime to
the GptClaw infrastructure checkout or pass this platform path to the current project
lifecycle provider: `scripts/private_apps.py:target` only accepts project roots below
`/srv/forge/projects` and rejects the provider checkout itself.

Use a Next.js/TypeScript frontend in a rootless container and a small trusted Python
observation process running as forge. Reuse the prepared manifest validation environment
and import the installed, versioned validator; never import modules from a discovered
project. Proposed local transport is a forge-owned Unix-domain socket with a fixed
inventory read protocol, mounted into the frontend container. The frontend needs no
project-volume, credential-store, Podman socket or host filesystem mount. Do not add
host packages or a database. Pin frontend dependencies/profile from the reviewed
[web toolchain](../020-pinned-language-toolchains/spec.md) and dependency policy.

The observation process is trusted host tooling with forge's permissions, not isolation
from malicious code also running as forge. Socket permissions and narrow operations
reduce accidental exposure; they do not create a new user security boundary. Frontend
requests map fixed endpoints to typed reads; the browser cannot choose host paths.

## Discovery and projection

Proposed collector budgets: at most 256 immediate owned non-hidden directory candidates,
10 seconds per scan, one concurrent scan, a 30-second snapshot reuse interval, and a
1 MiB serialized response limit. If a budget is exceeded, mark the snapshot incomplete
and report truncation; never describe the visible rows as exhaustive. Sort candidate
names before processing and check the deadline between bounded filesystem operations.
Keep the last successful snapshot in memory only. Mark it stale after 60 seconds
without a successful refresh. Budget choices must be confirmed against synthetic and
live inventory size; later changes require documented bounds, not silent unlimited scans.

Use directory-descriptor/no-follow lookup from the configured root, ownership checks
and the complete `scripts/project_manifest.py:validate_project` contract. Detect unsafe
entries before reading. Limit inspection to each immediate project's manifest and
safe existence checks for README.md/docs/README.md. Use a platform-generated opaque
row key bound to canonical root and manifest ID, rather than accepting a root string
from the browser. For duplicate IDs, return conflict rows and suppress runtime lookup.
Do not recursively count group components or discover worktrees in this initial slice.

Proposed versioned inventory response contains `schema_version`, snapshot ID,
`observed_at`, `last_success_at`, freshness/completeness, bounded diagnostics and rows.
Rows include opaque key, ID, name, kind, declared components, relative location,
manifest version, runtime-support state, optional repository/owner and documentation
presence states. Map errors to fixed codes/messages. Do not forward raw validator,
provider or filesystem output. Every projection is field-allowlisted and length-bounded.
Use one shared row key/identity contract for SPEC-028 and SPEC-029.

Optional owner/repository data comes from a small forge-owned platform registry, keyed
by canonical root plus validated ID. Proposed limits are 256 entries, 100 characters
for owner labels and canonical credential-free HTTPS GitHub repository identities.
Do not inspect `.git/config`, call Git or read broker credential/configuration stores.
Absent registry data remains “Not recorded”. A stale or mismatched entry never adopts
or retargets a directory. Version and validate registry data independently of project
schemas; populated metadata needs reviewed provenance and explicit owner maintenance.
No registry-edit endpoint is supplied by the dashboard.

## Hosting and failures

Provide a dedicated owned user service/Quadlet for the frontend and a reviewed user
service for the collector. Final unit names, source packaging, socket mount and finite
resource limits are implementation decisions to record before installation. Reuse
existing reviewed toolchains; inspect actual version/capability sources rather than
invent pins. A proposed `/dashboard/` Serve path targets only the loopback frontend;
it is separate from the existing `/projects/` ingress. Require an empty or known-owned
route, preserve unrelated handlers, verify Funnel off and use the operator path if
Serve configuration requires privileges. No AWS/IAM change is implied.

Return safe partial results for invalid candidates and a distinct global unavailable
state for root/collector failures. Ignore unexpected registry properties. Escape all
text in the frontend; do not render repository Markdown/HTML. Validate allowed host,
origin and methods at the HTTP boundary; deny cross-origin browser access and avoid
caching inventory in shared/public intermediaries. No arbitrary request-to-command
translation, telemetry/history store or writable project mount is needed.

## Components and changes

| Component | Planned responsibility | Requirement IDs |
|---|---|---|
| Trusted platform inventory adapter | Bounded safe discovery, validation, metadata projection, row identities and snapshot freshness | INV-001/002/003/005 |
| Versioned local read interface | Fixed requests, output allowlist, socket ownership and request bounds | INV-003/004 |
| Rootless Next.js dashboard | Accessible inventory, diagnostics and honest empty/stale states | INV-002/005 |
| Platform service packaging and runbook | Pinned releases, private lifecycle, route ownership and rollback | INV-004 |

## Verification, rollout and rollback

Use task-owned synthetic fixtures and execution/network spies for AC-001/002/003.
Exercise empty scans, malformed registries, duplicate IDs, partial permissions, limits,
collector loss/recovery and frontend escaping. API tests cover methods, paths, host and
origin validation. If a starter is used, remove demo routes/content/tests outside the
inventory scope and inspect rendered UI and exposed routes against the specification.

Run repository checks for changed tooling, frontend dependency/build/type checks and
relevant behavioral/accessibility checks. Record exact executed commands and results;
no dashboard stack command exists yet. After reviewed implementation, verify installed
source/profile parity, forge identity, listeners/socket/mounts, route ownership and
Funnel off. Obtain owner desktop-browser acceptance separately from CLI probes.

Deploy inventory first, then the separate status and link increments. On failure stop
only owned dashboard services and revert their reviewed release/route changes. Preserve
project services, sources, metadata registry, runtime receipts and databases. Remove an
owned Serve path only after checking its current target; never reset Serve. No project
manifest/data migration is needed. Record rollback behavior and any operator handoff.

## Traceability and remaining decisions

| Requirement | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| INV-001 | Bounded validated discovery and conflict keys | T-002 | AC-001/003 |
| INV-002 | Allowlisted inventory/registry and presence checks | T-002/003 | AC-002 |
| INV-003 | No-follow lookup, limits and read projection | T-002/003/005 | AC-003/004 |
| INV-004 | Socket boundary, rootless service and private owned route | T-003/004/006 | AC-004 |
| INV-005 | Snapshot freshness, partial errors and accessible rendering | T-003/005/006 | AC-005 |

The project owner reviews the proposed application location, stack and dedicated route.
Before implementation proceeds beyond packaging design, settle source repository/release
ownership, exact toolchain and socket/unit contracts; update this design with the reviewed
choices. Synthetic inventory drafting can proceed independently of deployment decisions.
