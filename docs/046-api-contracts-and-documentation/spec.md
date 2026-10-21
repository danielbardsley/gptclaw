# SPEC-046 — Contract and API documentation (QLT-008)

- **Status:** Implementation authorized; review, merge and acceptance pending.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-008
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

Services and clients share a deterministic versioned API contract, runnable
documentation and compatibility checks that reveal drift before a cross-service change
is accepted.

Treat application route schemas as the authoritative HTTP source, normalize
deterministic output and retain the last accepted contract for compatibility comparison.
Document auth assumptions, validation/error envelopes, pagination and base-path
behavior. Never bake private origins, credentials or live data into schemas/examples. A
version increment alone does not prove compatibility or authorize retirement of existing
consumers.

The project owner authorized implementation of QLT-001–QLT-010 and necessary
dependencies on 2026-10-21, with reasonable decisions delegated to the agent.
Pushing branches and opening PRs are authorized; merging and deployment are excluded. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

FastAPI and Fastify starters already expose OpenAPI and bundled docs; SPEC-036 includes
a checked-in notes contract and typed mobile client with drift checks. These are
stack-specific slices, not a uniform contract lifecycle across all supported service
boundaries.

Reuse SPEC-024/025/035/036 contracts and QLT-001/002 checks; coordinate
database-compatible changes with QLT-007 and real routed checks with QLT-004. No new API
framework is needed.

Source/previous-record evidence, not a new runtime verification:

- [templates/apps/releases/fastapi/1.0.0/scripts/quality.py](../../templates/apps/releases/fastapi/1.0.0/scripts/quality.py)
- [templates/apps/releases/fastify/1.0.0/src/app.ts](../../templates/apps/releases/fastify/1.0.0/src/app.ts)
- [templates/apps/releases/expo-notes/1.0.0/contract/openapi.json](../../templates/apps/releases/expo-notes/1.0.0/contract/openapi.json)
- [templates/apps/releases/expo-notes/1.0.0/checks/contract.cjs](../../templates/apps/releases/expo-notes/1.0.0/checks/contract.cjs)
- [docs/036-mobile-python-backend/technical-design.md](../../docs/036-mobile-python-backend/technical-design.md)

## Requirements

### QLT-008-R01 — Deterministic contract

Export a validated OpenAPI contract for every supported HTTP service boundary from
authoritative route schemas; fail on missing paths, invalid references and
nondeterministic or stale checked-in output.

### QLT-008-R02 — Compatibility policy

Compare against the last accepted version and detect removed operations, required-input
additions, narrowed types and incompatible response/error changes; require explicit
version/consumer migration disposition.

### QLT-008-R03 — Typed clients

Generate or validate deterministic typed clients using reviewed pinned tooling, checking
request serialization, responses and safe errors without manual drift.

### QLT-008-R04 — Usable private docs

Serve bundled API documentation and contract paths under the owned private prefix, with
synthetic examples and clear development/auth/error/health boundaries.

### QLT-008-R05 — Reviewable lifecycle

Include contract/client checks in standard CI, publish safe revision-bound artifacts and
document adoption, versioning and retirement without silently upgrading existing
consumers.

## Acceptance criteria

All criteria are pending; drafting does not establish implementation acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-008-AC01 | Two clean exports match byte-for-byte after normalization; changed route/schema with stale output fails; malformed references and an omitted exposed endpoint fail. | QLT-008-R01 |
| QLT-008-AC02 | Breaking fixtures fail without disposition; additive examples pass policy; previous accepted client still works against an accepted compatible API. | QLT-008-R02 |
| QLT-008-AC03 | Regeneration is clean; stale client output fails; representative valid/invalid/error responses and cancellation paths pass client/server tests. | QLT-008-R03 |
| QLT-008-AC04 | Routed docs and local assets load without external CDN requests; try-out calls retain the prefix; examples and scan fixtures contain no credentials or private host defaults. | QLT-008-R04 |
| QLT-008-AC05 | A generated multi-service/mobile fixture passes CI with matching artifacts; unsupported boundaries report explicit status; historical releases stay byte-identical. | QLT-008-R05 |

## Decisions and completion

Export and compare deterministic API shapes, check local references and conservative compatibility changes, retain existing generated clients, and separately assert actual private prefixes/docs/assets. Reuse FastAPI/Fastify rather than introduce frameworks.

The project owner delegated reasonable implementation choices on 2026-10-21.
This scope is authorized for source changes, synthetic tests and PR publication;
merge and deployment are explicitly excluded.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.