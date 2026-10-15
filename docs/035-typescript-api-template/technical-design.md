# TDD-035 — Fastify initial stateless API

Status: Implementation design. Owner: Project owner. Date: 2026-10-15.
[Specification](spec.md) · [Tasks](tasks.md)

## Approach

Reuse the exact Node 24.21.0 / pnpm 12.10.1 profile and existing pnpm dependency
policy. Add catalogue v6 and manifest v7 for provider `fastify-v1`; v2 remains
the Python API contract. Manifest v7 has the same single API shape as v2 but
Node command vectors. Keep dispatch explicit in generation and runtime target
validation. Add all new contracts to immutable provider bundles and capability
reporting. Existing dependency transactions and rootless service orchestration
are reused without new install hooks or credentials.

Fastify factory registers route JSON schemas before OpenAPI generation. Bundled
Swagger UI assets are served under the project prefix. Settings accept only a
validated project identity; paths derive from that identity. Use Node native
TypeScript stripping and watch mode for development; tsc compiles production
output with strict checking. Tests inject requests without host ports, and build
constructs the application to catch invalid registration. Use explicit formatting,
check-only lint, typecheck, tests and pnpm advisory auditing; advisory-service
failure remains failure. Container recipe uses the existing pinned base/toolchain.

## Traceability

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| TSAPI-001,005 | Catalogue v6, manifest v7, provenance, snapshot inventory and offline tests | T1,T2 | AC-001 |
| TSAPI-002,004 | Factory/settings/routes, generated quality and fault tests | T3,T4 | AC-002 |
| TSAPI-003 | Existing rootless lifecycle plus Node watch and prefix-aware docs | T2,T4 | AC-003 |
| TSAPI-004,005 | CI, runbook, acceptance record and review PR | T4,T5 | AC-004 |

## Verification and operation

Use only synthetic data in task-owned temporary projects. Run repository checks,
release immutability and generated app checks in the pinned container. Record
actual outcomes separately from remote CI and managed runtime acceptance. No
Terraform change or deployment is needed. Rollback uses a reviewed revert; existing
generated source and published identities must be preserved. PostgreSQL/migrations
and service-group integration are explicitly deferred by owner scope selection.
