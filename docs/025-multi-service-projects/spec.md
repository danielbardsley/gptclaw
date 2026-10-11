# SPEC-025: Multi-service projects with a notes application

- **Status:** Delivered — initial two-service slice merged and accepted
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Primary feature:** RUN-006, initial two-service HTTP slice
- **Supporting slices:** PRJ-001/002/003/009, RUN-001–005, NET-103, QLT-004/008/009
- **Design:** [TDD-025](technical-design.md) · **Tasks:** [TASKS-025](tasks.md)
- **Dependencies:** [SPEC-018](../018-first-private-application/spec.md), [SPEC-024](../024-python-fastapi-template/spec.md), [Python standards](../024-python-fastapi-template/python-standards.md), [delivery sequence](../platform/sequence.md)

## Outcome and scope

Run a Next.js frontend and Python/FastAPI API as one declared private project,
then prove the platform workflow with a simple note-taking application. The
project owner selected RUN-006 and this example on October 11 and requested the
specification. The project owner approved this scope and authorized implementation, local application
creation and scoped synthetic live verification on October 11 with “Great, implement
the spec.” Review/merge and independent browser acceptance remain separate gates.

This is a suitable first slice: notes exercise real browser-to-API operations,
service ordering, readiness, networking and failure recovery without a database.
A single repository and release lifecycle keep orchestration central. Deliver a
reusable exact-release two-service starter and a concrete generated notes example;
do not merely run two unrelated single-service projects beside each other.

Included: exactly one web and one API component per group; explicit versioned
manifest/catalogue/provider contracts; component-specific dependency/toolchain and
quality operations; group start/status/logs/restart/stop; private prefixed routing;
automatic source updates; an in-memory notes API and accessible basic UI.

Excluded: databases, caches, workers, arbitrary service graphs, Compose adoption,
managed data volumes, migrations/backups for notes, authentication/accounts,
collaborative editing, secrets, AI calls, rich text, public exposure, production,
new host infrastructure and live GitHub application repository creation. Existing
repository generation must support the new selection under its separate authorization.
The broader RUN-006 catalogue scope stays open.

Observed dependencies: SPEC-024 code is merged in PR #56 at `f8b83e8`, with
standalone API local/CI/live/client evidence recorded. Its initial standalone slice is now Delivered, with acceptance in
[the SPEC-024 record](../024-python-fastapi-template/acceptance.md).
Existing source provides Next.js/pnpm and FastAPI/uv adapters, exact profiles,
rootless lifecycle, ingress, transactional dependencies and provider snapshots.
These are reusable foundations, not proof that group orchestration exists.

## Requirements

### MS-001 — Explicit group declaration and compatibility

Introduce a new manifest version for a project with exactly two uniquely named
components: web and API. Declare each relative source root, supported stack,
commands, exact toolchain selection, port and health contract; declare web's API
dependency and one private project prefix. Reject duplicate identities, escaping
or overlapping roots, symlinks, unknown versions/stacks/fields and invalid dependency
references/cycles before execution. Validation/discovery remain observation-only.
Preserve existing v1 web/v2 API projects, published template bytes and runtime state;
no implicit migration or reinterpretation. Generated state/ports stay outside Git.

### MS-002 — Reproducible grouped generation and preparation

Generate an exact versioned two-service starter, complete independent pnpm/uv
locks, toolchain metadata, Python standards, guidance, checks, CI and provenance.
Keep existing defaults unchanged and refuse occupied destinations. Use existing
reviewed container profiles/policies without host installs or interpreter downloads.
Prepare/build each component with its own fingerprints; a failure never marks the
group prepared. No silent lock updates or source rewrites. Typed dependency and
format operations require an explicit component and a stopped, non-busy group;
transactions/recovery remain scoped to that component and preserve concurrent edits.

### MS-003 — One owned lifecycle with bounded recovery

Start API first, require readiness, then start web and publish only a fully ready
group. Stop withdraws routing first and stops dependants before dependencies.
Restart is an explicit group stop/start. One project lock serializes mutations;
component jobs cannot bypass it. Failed starts remove only newly created owned
resources, preserve useful failure receipts and never report success for a partial
group. Interrupted operations reconcile from persisted component ownership and
operation IDs; status enables safe recovery without blind retries. Stop must attempt
both components even if one is absent/failed and report unresolved cleanup honestly.
Unknown resources and unrelated projects are preserved.

### MS-004 — Private networking and health

Provide one browser URL at `/projects/<id>/`; frontend calls the API through the
same HTTPS origin. Only declared UI, API and bundled docs paths are routed; no
arbitrary proxy destinations or client-selected upstreams. API remains private to
the managed path/container or loopback transport. Keep host publications loopback-only,
Funnel off, credential/home/socket mounts absent and approved resource bounds.
Report component health and aggregate ready/degraded/stopped/failed state. API
outage makes group readiness fail and blocks note operations; liveness is distinct.
Unknown/stopped/unhealthy paths fail without a misleading successful page or URL.

### MS-005 — Useful ephemeral notes behavior

Provide list, create, edit and delete from a responsive Next.js UI backed by typed
versioned FastAPI routes. Notes have generated ID, title and plain-text body.
Trimmed titles are 1–120 characters; bodies at most 10,000 characters. Paginate
with bounded limit/offset and deterministic ordering; cap the store at 100 notes
and reject excess creates explicitly. Invalid inputs, missing IDs and capacity
failure have documented statuses and safe error responses. The UI includes empty,
loading, saving and failure states, labels, keyboard access and deletion confirmation.
It renders note text safely and retains an unsaved draft on a failed request.

Store notes only in one API process's memory, with synchronized mutations. No
file, browser storage, database or cache persistence. Page refresh and web-only
reload preserve notes while the API process lives; API reload/restart, group
restart/stop-start and host replacement can lose all notes. Show this clearly in
the UI and README. No auto-retry of non-idempotent creates. There is no per-user
isolation: authorized tailnet viewers share this synthetic demo store. Use only
synthetic notes in verification; no real personal notes or payload logging.

### MS-006 — Quality, contracts and iteration

Apply SPEC-024 Python standards and its exact locked quality/security commands,
including strict typing and at least 80% statement and branch coverage for critical
notes/API/config/readiness modules. Retain documented frontend checks and add
meaningful UI/API contract and end-to-end CRUD/error tests. Group test/verify runs
both components and cross-service checks, with explicit failures and bounded jobs.
Source edits reload their component without silently changing dependencies; prove
updates and syntax-error recovery in both components. API reload data loss is expected
and documented. Versioned OpenAPI, bundled docs and prefix/query/redirect handling
must work at the private URL. Security/advisory failures cannot become clean scans.

### MS-007 — Component diagnosis and resource ownership

Status exposes each component's state, selected profile, bounded readiness result,
owned resource identity and last operation, plus group/route outcome. Logs require
an explicit component and use existing bounded/redacted behavior; no payloads,
query values or environment dumps. Allocate owned units, network/ports and caches
without collisions with another group or single-service project. Apply per-component
limits and a documented aggregate group budget; keep build/quality concurrency
bounded to fit the host. Stop retains source/locks and only removes owned runtime
resources; ephemeral note loss is intentional.

### MS-008 — Evidence and honest completion

Record isolated validation/lifecycle failures, generated checks/CI, actual managed
EC2 behavior and an independent authorized browser's CRUD/update observation
separately. Prove unaffected single-service Next.js and FastAPI operation, cold/warm
preparation, partial-start failure, API outage/recovery, interrupted reconciliation,
stop/source retention and rollback/refusal. Record versions, budgets, timings,
limitations and fixture disposition without private runtime identity or secrets.
Mark only this slice Delivered after implementation merge, all criteria and project
owner acceptance. Planning merge alone does not authorize implementation.

## Acceptance criteria

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| AC-001 | Offline tests accept the two-service contract and refuse duplicate/unsafe roots, unknown versions, invalid dependencies and stacks without execution or file mutation. V1/v2 fixtures remain valid. | MS-001 |
| AC-002 | Exact starter generates locally with complete locks/provenance; occupied destination and tampered releases fail. Both profiles/policies prepare cold/warm without source/lock changes; component dependency transactions, failure/recovery and active/busy refusal pass. Existing defaults/releases remain unchanged. | MS-002 |
| AC-003 | Lifecycle tests and scoped EC2 start/status/restart/stop prove ordering, readiness-gated publication, group locks and cleanup of both components. Partial starts/interruption/unknown ownership preserve honest receipts and recover safely; source is retained. | MS-003, MS-007 |
| AC-004 | Actual private HTTPS UI/API/docs/assets/query/redirects work beneath one prefix. API failure yields degraded group and unavailable note calls, then recovery; stopped/unknown paths fail. Loopback/network/resource inspection confirms declared bounds and no exposure change. | MS-004, MS-007 |
| AC-005 | Browser and API tests prove CRUD, pagination/order, validation/missing IDs/capacity, safe text rendering and draft preservation. Refresh/web reload retains notes; API and group restart clear them. UI explains shared ephemeral data and keyboard/label checks pass. | MS-005 |
| AC-006 | Locked container checks and generated CI pass for both services and cross-service tests, Python critical statement/branch coverage each >=80%, security/audit and build. Meaningful defects fail. Source updates/syntax failures recover in both services with documented API data loss. | MS-006 |
| AC-007 | During group operations independent web/API fixtures retain health/routes/source. Distinct owned identities, ports, bounded component logs and aggregate resource evidence pass. Rollback refuses unsupported groups without touching them or preserves source on a stopped-group provider restore. | MS-001, MS-007, MS-008 |
| AC-008 | Sanitized evidence records actual revisions/CI/live/client results, cold/warm timings, recovery/rollback and cleanup. Independent browser CRUD/update confirmation, implementation merge and project owner acceptance close the initial slice only. | MS-008 |

## Decisions and completion

The project owner approved SPEC-025 and authorized implementation on October 11.
The project owner confirmed independent CRUD/source-update behavior, then accepted
this initial slice with “ok, merge the PR.” Implementation merged in
[PR #58](https://github.com/danielbardsley/gptclaw/pull/58) as `c1afac9` on October 11;
[acceptance](acceptance.md) records AC-001–008 passed and the non-blocking hydration follow-up.
The proposed design uses exactly two services, shared same-origin routing and
single-process ephemeral notes. No database prerequisite or infrastructure change
is necessary. Deliver platform contracts/orchestration, a versioned starter,
a generated notes example, runbooks, tests/CI and later acceptance evidence.
Exact new release/provider identities and measured budgets are finalized in code
review from existing registries; no invented new pins are approved by this draft.
