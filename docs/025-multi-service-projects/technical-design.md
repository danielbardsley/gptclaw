# TDD-025: Two-service project orchestration

- **Status:** Approved — implementation in progress
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-025](spec.md) · **Tasks:** [TASKS-025](tasks.md)

## Approach and existing seams

Extend the existing trusted stack adapters and `private_apps.py` orchestration;
do not introduce a second manager or delegate ownership to arbitrary Compose files.
Keep web and API in one source repository, with `web/` and `api/` component roots,
independent dependency locks/toolchain selections and one project identity/lock.
The starter is a useful ephemeral notes application, reusable through exact-release
catalogue selection. A generated local project is the behavioral acceptance fixture;
GptClaw remains platform code, not the application runtime repository.

Reuse the Node/pnpm profile in [registry v1](../../config/toolchains/v1.json),
Python/uv in [registry v2](../../config/toolchains/v2.json), existing dependency
policies and the [versioned Python standards](../024-python-fastapi-template/python-standards.md).
Do not copy old template releases and edit their published bytes. Register a new
release with its own digest and component provenance, keeping current defaults.
The existing project contract has separate single-web v1 and single-API v2 schemas;
introduce proposed v3 for a group. Template metadata and provider receipts need
explicit compatible versioning where their shapes change. Older readers must fail
before execution, and existing projects must keep their existing interpretation.

## Source and declaration contract

Proposed layout:

```text
.gptclaw/project.yaml          # v3 group identity, components and private ingress
web/                          # Next.js, package.json, pnpm lock, selected Node profile
api/                          # FastAPI src/tests, pyproject.toml, uv lock, Python profile
docs/                         # generated standards, API/use/recovery guidance
```

The implementation schema defines component IDs `web` and `api`, disjoint safe
relative roots, supported adapter identities, argument-vector build/start/test and
supported quality commands, internal port/readiness/liveness, exact profile selection
and `depends_on: [api]` for web. Project exposure stays private and data ephemeral.
Only this two-component topology is supported initially, even if a later schema can
expand. No arbitrary plugin paths, shell expansion, container definitions, host binds,
environment maps, runtime secrets or user-selected upstream URLs are permitted.
Component IDs and root paths are validated before ownership names or mounts are made.
Retain parser/resource/symlink protections and sanitized validator errors.

Preparation/commands resolve paths relative to the selected component root. Mount
only the selected source and owned caches for jobs; service connectivity is handled
separately. A Node fingerprint and a Python fingerprint prevent one lock change
from silently invalidating or rewriting the other's source. Group prepared state
requires both successful component receipts. Dependency operations and formatting
require explicit component selection, stopped group and group lock; ordinary
build/test/verify does not mutate dependency declarations. Existing single-service
CLI behavior and result shapes remain compatible.

## Networking and routing

Propose one rootless, project-owned isolated container network with stable owned
component aliases. Allocate distinct loopback upstream ports through existing
reservation/availability logic; source declares only internal ports. No home,
credentials, Podman socket or host-network mode is mounted. Container network
access is not a hostile-project security boundary: both services share forge's identity.

Use the existing private gateway for deterministic longest-prefix routing:

| Private path | Component | Behavior |
|---|---|---|
| `/projects/<id>/` and web assets | web | Next.js configured for the project base path |
| `/projects/<id>/api/v1/` | API | Prefix-preserving typed notes API |
| `/projects/<id>/api/docs`, `/api/openapi.json`, `/api/docs-assets/` under the project prefix | API | Bundled private docs and schema |
| `/projects/<id>/api/health`, `/api/ready` under the project prefix | API | Liveness/readiness, independent of web's own health path |

Reserve the API namespace in web; route segment boundaries prevent `/api-other`
from matching `/api/`. Probe components directly at declared upstream health paths;
web readiness also verifies its declared API dependency with a short timeout via
the owned network. Forward paths, query strings and redirects consistently with
existing mounted FastAPI routing. Do not trust arbitrary forwarded hosts or allow
open-proxy requests. Keep existing router body/time/worker limits; notes payloads
fit within them. Browser calls use base-path-aware relative same-origin API URLs,
so no wildcard CORS or public API origin configuration is needed. Only the platform
supplies the derived non-secret internal API readiness address to web; it is not
an arbitrary environment forwarding mechanism.

Publish UI/API routes as one owned group only after both are ready. Recheck
aggregate readiness for routed requests/status so runtime API failure withdraws
useful group access and produces an explicit unavailable response; recover when
both are ready without declaring a failed process healthy from stale receipts.
API health diagnostics can remain available to direct owned probes, even while
public project routes are unavailable. Do not cache successful readiness beyond a
short documented bound; tests must prove the bound. Existing Serve prefix is reused
with no new operator command or public exposure.

## Lifecycle, state and limits

Use one project lock and persistent operation ID with per-component stages and
owned network/unit/container/port/job identities. Reserve/reconcile ownership
before external actions; persist completed stages after each transition. Brief
registry locks protect allocation only. Never retain them across build/health waits.

Start: validate all metadata, acquire group lock, prepare/build serially, create
owned network, start API and wait ready, start web and wait ready, publish route
set, record ready. An already healthy start reconciles rather than duplicating
resources. A failed start removes resources created by that attempt in reverse
order, never steals unknown resources or stops a pre-existing healthy component
without recording the necessary repair transition. No partial route set is success.

Stop: withdraw route set, attempt web then API shutdown, remove owned activation
and network when unused, retain source/locks/dependency caches/reservations. Report
partial cleanup if an owned job/resource remains unresolved. Restart uses explicit
stop/start and loses API memory. Status observes actual component health/ownership,
not just the last mutation. Degraded covers a running group with unavailable
components; failed covers a terminal unsuccessful lifecycle operation. Interrupted
operations preserve stages for same-operation reconciliation; unresolved jobs remain
busy rather than being cancelled or replaced blindly.

Retain current per-component ceilings of 1 CPU, 1536 MiB and 256 PIDs; the proposed
group ceiling is the sum, 2 CPU/3072 MiB/512 PIDs, with serial build/quality jobs
and no unbounded worker spawning. Verify actual host headroom before live trials;
capacity shortfall is a reported limitation, not permission to resize/install.
Retain existing 300-second job and 120-second service-readiness bounds, so two
sequential stages have an explicitly reported bounded total. Gateway resources
remain shared platform resources. Record actual peak/timing observations rather
than promise performance from limits alone.

Group lifecycle commands stay at project scope. `logs`, dependency and component
quality operations require an explicit component; group `test`/`verify` run both
component gates and a bounded cross-service suite. A reserved `--component` selector
is a proposed CLI extension, not an available command today. Component-only
start/stop/restart is deferred; source reload already exercises independent updates.
Include new schemas/catalogue assets/network and routing logic in immutable provider
bundles and advertise group capabilities. Unsupported providers must refuse group
metadata/state without mutating source or deleting owned resources.

## Notes implementation

FastAPI uses an injected `NotesService` with typed models and a concrete in-memory
store protected against concurrent mutations. One Uvicorn application worker with
development reload owns the store; reload creates a fresh store. No persistence
interface/classes are added without a real need. Apply src boundaries, Google
docstrings, JSON metadata logging/redaction, default-deny CORS, security headers,
admission and quality/security/coverage rules from SPEC-024.

| Relative API route | Contract |
|---|---|
| `GET /api/v1/notes?limit=20&offset=0` | 200 typed ID/title/90-character-preview items/total; limit 1–100, offset >=0; creation order with ID tie-break |
| `POST /api/v1/notes` | 201 note and prefixed Location; server-generated UUID; capacity full returns 409 |
| `GET /api/v1/notes/<id>` | 200 note, 404 missing |
| `PUT /api/v1/notes/<id>` | 200 complete replacement of title/body, 404 missing |
| `DELETE /api/v1/notes/<id>` | 204, 404 missing |

Use title/body limits from MS-005; malformed payloads return safe 422, admission
429, and unavailable dependency 503 at ingress. Logs exclude note titles/bodies,
query values and raw error internals. No automatic create retries or multi-user
consistency guarantees beyond synchronized individual operations.

Next.js supplies one notes list and editor, create/save/delete controls, clear
loading/errors/empty state, bounded pagination and semantic keyboard-accessible
forms. Render text as text. A visible message states that notes are shared and
lost when the API reloads or the project restarts. Keep failed edits locally in
component state without browser persistence; refresh can lose an unsaved draft.
Use the API's typed OpenAPI contract to validate frontend calls in tests rather
than maintain an untested duplicated shape.

## Planned changes and traceability

| Component | Change | Requirements | Tasks | Acceptance |
|---|---|---|---|---|
| Project schema/validator/docs | Explicit v3 component/path/dependency contract | MS-001 | T-002 | AC-001, AC-007 |
| Catalogue/generator/repository selection | Exact grouped release/provenance, no default changes | MS-002 | T-003 | AC-002 |
| Toolchain/dependency/job adapters | Component roots/fingerprints, group locks and transactions | MS-002, MS-007 | T-004 | AC-002, AC-007 |
| Lifecycle/receipts/provider bundles | Group stages/network/resources/order/recovery | MS-003, MS-007 | T-005 | AC-003, AC-007 |
| Gateway/health | Atomic grouped routing and aggregate availability | MS-004 | T-006 | AC-004 |
| Notes source/CI/standards | In-memory CRUD/UI/contracts/quality/update tests | MS-005, MS-006 | T-007, T-008 | AC-005, AC-006 |
| Runbooks/acceptance/index/catalogue | Compatibility, rollback, live/client evidence and scope | MS-008 | T-009, T-010 | AC-007, AC-008 |

## Verification, rollout and rollback

Use synthetic isolated tests for parsing/unsafe paths, exact generation, component
preparation and transactions, graph/order, busy locks, port collisions, failed
second startup, missing units, route-publication failure and interrupted-stage
reconciliation. Assert unrelated resources/source hashes stay unchanged. Golden
checks generate the release, run both locked container check stacks, seed meaningful
quality defects and execute browser/API CRUD and outage tests. Pinned generated CI
must exercise two-service connectivity, not just independent unit suites.

After authorization, install the reviewed provider snapshot and generate a named
local-only synthetic notes fixture on EC2. Verify resources/network/loopback,
cold/warm preparation, group lifecycle, source reload/syntax recovery, expected data
loss and private prefixed UI/API/docs. Keep independent synthetic web and API
fixtures healthy throughout. Record host capacity and durations. Obtain project
owner browser confirmation of CRUD and an observable source update separately;
loopback/CI cannot substitute. Do not publish private host identity in evidence.

Rollback: first stop the selected group with the capable provider; preserve source,
locks and unknown resources, then restore a reviewed older snapshot or revert the
platform change. Older snapshots must explicitly reject the group. Do not attempt
rollback while group jobs/cleanup are unresolved, reuse single-service receipts for
a group, prune shared caches/images or rewrite application source to v1/v2. Trial
refusal/source preservation using isolated fixtures. API memory is intentionally
unrecoverable; rollback never promises note restoration. No database migration,
Terraform apply, Serve reset or credential change is required.

The approved implementation uses provider 1.7.0, project/catalogue schema v3,
explicit group receipt v2 and `notes@1.0.0`. Component stack receipts retain v1;
trusted in-memory component contracts reuse the existing adapters while generated
component metadata blocks independent CLI operations. Installed Quadlet 4.9 uses
`PodmanArgs=--network-alias=...` rather than the newer NetworkAlias key. Existing
SPEC-024 final acceptance wording is retained in its own record. Local/CI/live
and independent browser outcomes are recorded separately in acceptance.md when observed.
