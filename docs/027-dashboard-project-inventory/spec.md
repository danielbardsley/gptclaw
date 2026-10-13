# SPEC-027: Dashboard project inventory

- **Status:** Implemented and accepted — review/merge pending
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Primary feature:** DSH-001
- **Supporting scope:** Bounded discovery prerequisite for PRJ-007; minimal private dashboard foundation
- **Design:** [TDD-027](technical-design.md) · **Tasks:** [TASKS-027](tasks.md)
- **Context:** [Architecture](../platform/architecture.md), [delivery sequence](../platform/sequence.md), [manifest contract](../project-manifest.md)

## Outcome and authorization

Give the project owner one private browser view of managed development projects,
including projects that are stopped or have incomplete metadata. Show project type,
repository, owner, runtime support and documentation state without opening each
repository or starting its services.

The project owner requested three separate specifications for DSH-001, DSH-002 and
DSH-003 on October 12. This authorizes planning and a reviewable planning PR.
The later implementation authorization is recorded below. Merge, private rollout and
acceptance remain separate gates, with actual evidence required.

## Scope and existing readiness

Include the first dashboard shell, private hosting, a read-only inventory contract,
bounded discovery, optional non-secret platform metadata and per-project diagnostics.
The planned application runs on the existing development EC2 host as forge, under
`/srv/forge/platform`, accessed through Tailscale Serve. It is a platform service,
separate from the repositories it lists. The exact service installation and route
must be reviewed before implementation and verified before deployment.

Existing code supplies strict `validate_project(root)` validation and manifests for
single web, single API, web/API groups and PostgreSQL-backed groups (schemas 1–4).
It does not supply a dashboard or general inventory API. Manifests do not declare
owner, repository URL or documentation status; those fields must not be invented or
silently added to existing schemas. Current runtime tooling manages targets below
`/srv/forge/projects`, not the proposed platform application directory.

The initial discovery slice covers immediate owned project directories below the
configured projects root. Exclude hidden platform/runtime directories and component
subdirectories; list one row per group. A directory with no manifest is outside the
managed inventory. Invalid or unreadable candidate manifests produce safe diagnostics,
not partially trusted project rows. Broader recursive discovery/export remains PRJ-007.

Exclude lifecycle controls, resource telemetry, Git branch/dirty state, log contents,
build/backup/cost views, search/filtering, public exposure, production projects,
accounts and databases. [SPEC-028](../028-dashboard-live-service-status/spec.md) owns
live status; [SPEC-029](../029-dashboard-project-links/spec.md) owns clickable targets.
Minimal accessibility and partial-failure behavior apply here without claiming full
TPL-008, QLT-005, DSH-012 or DSH-014 delivery.

## Requirements

### INV-001 — Deterministic inventory and identity

Discover bounded candidates without executing repository content. Validate each
manifest using the complete existing validator. Identify a row by its validated ID
and canonical root, sort deterministically, and detect duplicate IDs across roots.
Conflicting identities remain visibly conflicted and cannot select a runtime target.
Stopped valid projects remain listed; discovery never starts or adopts a project.

### INV-002 — Honest metadata and documentation state

Show validated name, ID, kind/components, project location relative to the configured
root, manifest version, runtime support, repository and owner. Optional repository
and owner come only from validated platform-owned metadata tied to that root/ID.
Missing values show “Not recorded”; invalid metadata never replaces valid identity.
Runtime support means compatibility with an observed provider capability, not service
health. Show unsupported/unavailable capability separately.

Check only the existence and safe file type of README.md and docs/README.md. Label
these states “Present”, “Missing” or “Unavailable”, with an explanation that presence
is not a documentation-quality review. Do not read repository prose for rendering.

### INV-003 — Safe and bounded observation

No repository commands, hooks, imports, package scripts, Git/network fetches, source
writes or credential acquisition occur during discovery. Enforce ownership, no-follow
path handling, file/scan/time/output limits and the validator's parser bounds. Do not
scan `.aws`, `.ssh`, environment files, runtime credential stores or arbitrary files.
Serialize an allowlist of display fields; omit manifest commands, raw errors, arbitrary
metadata fields and credential-bearing URLs. Treat names and metadata as plain text.

### INV-004 — Private platform hosting and read-only interface

Run under forge with rootless containers for the frontend and loopback/private local
transport for observation. Expose the dashboard only through Tailscale Serve to the
configured tailnet; do not enable Funnel or listen publicly. Browser requests accept
only typed inventory reads, with no arbitrary path, command, upstream or file parameter.
No mutation endpoint or lifecycle control is delivered. Validate the HTTP host/origin
boundary and prevent cross-origin reads; private networking does not replace input
validation. Document the existing shared-forge trust boundary.

### INV-005 — Useful empty, partial and unavailable states

Show a distinct empty inventory when a successful scan finds no valid projects. Show
scan failure, truncation, per-candidate validation issues and refresh timestamps without
hiding healthy rows or presenting stale rows as current. Last successful inventory may
remain in memory with a visible stale label; no persistent history is required. Supply
keyboard navigation, semantic headings/table structure and textual status labels.

## Acceptance criteria

| ID | Observable result and evidence needed | Requirement IDs |
|---|---|---|
| AC-001 | Synthetic schema-1/2/3/4 projects appear once in stable order; stopped projects remain; child components and non-project directories are excluded; duplicate IDs are visibly conflicted and cannot select a target. | INV-001 |
| AC-002 | Valid, missing and invalid metadata and documentation fixtures show the specified fields and honest labels; unavailable provider support is distinguished from health; no schema/source file is rewritten. | INV-002 |
| AC-003 | Fixtures for symlinks, replacement races, malformed/oversized manifests, unreadable files, scan/output bounds and synthetic secrets produce bounded sanitized results; execution/network spies show no repository execution, Git access or credential acquisition. | INV-001/003 |
| AC-004 | API tests reject arbitrary paths/commands, cross-origin and invalid-host requests and all mutation methods. Live evidence shows forge identity, rootless frontend, private/loopback listeners, owned Serve route and Funnel off; the owner opens inventory from a tailnet desktop browser. | INV-003/004 |
| AC-005 | Empty, partial, truncated, collector-down and stale-snapshot scenarios remain distinct; recovery refreshes timestamps; keyboard and text-label checks pass. Record local, CI, live and owner results separately. | INV-005 |

## Dependencies, assumptions and decisions

Reuse the accepted manifest/runtime/toolchain contracts and dependency policy. Existing
source is evidence of an interface, not proof of installed-provider parity. Verify
installed capabilities during implementation. A safe discovery adapter is delivered
as the bounded prerequisite here; no standalone PRJ-007 implementation is assumed.

Proposed defaults for review: Next.js/TypeScript frontend, trusted Python observation
adapter, no database, platform directory above, and a dedicated private `/dashboard/`
route that preserves `/projects/` and other Serve entries. The project owner approves
these defaults with the scope/design before implementation. Implementation must settle
exact pinned profiles, unit/socket paths, metadata schema, budgets and route ownership
in TDD-027 before rollout. If host configuration or Serve changes need an operator,
use the existing reviewed operator/IaC path; do not invent sudo or forge permissions.

## Implementation authorization

On October 12 the project owner instructed: “In order implement the specs for
DSH-001, DSH-002 and DSH-003. Finish once all acceptance criteria have been met.”
This approves the specified scope and defaults and authorizes implementation and
necessary reversible private runtime verification. Existing operator, review/merge,
public-exposure and production gates remain in force. Actual local/CI/private/owner evidence is recorded in [acceptance.md](acceptance.md); review/merge remains.
