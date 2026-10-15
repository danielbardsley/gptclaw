# SPEC-035 — TypeScript API template (TPL-002)

Status: Delivered — initial stateless slice accepted. Owner: Project owner.
Date: 2026-10-15 (America/New_York).
[Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

The project owner requested implementation of TPL-002 and selected an initial
stateless API, deferring PostgreSQL and migrations. Deliver an exact Fastify
starter through the existing local generation, dependency and private lifecycle
interfaces. No new host software, infrastructure, public exposure, production,
application repository creation or persistent data is included. Keep the default
Next.js template and all published releases unchanged. Implementation authorization
is recorded here; review, merge and runtime/owner acceptance remain separate.

## Requirements

- TSAPI-001: Exact `fastify@1.0.0` catalogue selection, hashed assets, provenance,
  safe atomic generation, supported Node/pnpm selection and frozen dependency
  restore. Discovery performs no application execution or network access.
- TSAPI-002: Strict TypeScript application factory and typed non-secret settings,
  versioned synthetic echo/list API with bounded pagination, input and response
  schemas, useful validation and missing-route errors, OpenAPI and bundled docs.
  Invalid settings fail clearly; request bodies and secrets are not logged.
- TSAPI-003: Separate liveness/readiness, private prefix-preserving paths and docs,
  managed start/test/status/logs/restart/stop and source reload with error recovery.
  Reuse resource limits, locks, loopback ports and owned route removal; preserve
  unrelated services and source. No trust of arbitrary forwarded headers.
- TSAPI-004: Exact dependencies, meaningful build, format/lint/type/test/security
  gates, generated CI and container recipe. Tests cover failure paths and API
  contracts. Container execution uses the existing reviewed Node profile.
- TSAPI-005: Explicit versioned contracts and provider snapshot support; document
  generation, adaptation, operation and deferred migrations. Older contracts remain
  valid and unknown versions fail before application execution.

## Acceptance criteria

| ID | Observable evidence | Requirements |
|---|---|---|
| AC-001 | Offline selection/generation, tamper/unknown-version refusal, snapshot parity and old-release regression checks pass | TSAPI-001,005 |
| AC-002 | Generated API tests and strict quality/build gates pass; injected defects fail | TSAPI-002,004 |
| AC-003 | Real managed lifecycle, private docs/OpenAPI, update/error recovery, stop retention and independent-service checks pass | TSAPI-003 |
| AC-004 | Runbook, CI and acceptance evidence reviewed; implementation merged and project owner accepts initial slice | TSAPI-004,005 |

Implementation merged in [PR #82](https://github.com/danielbardsley/gptclaw/pull/82).
The project owner accepted the private API checks on October 15, 2026. See
[acceptance evidence](acceptance.md). Delivered covers this initial stateless
slice; PostgreSQL/migrations remain separately scoped.
