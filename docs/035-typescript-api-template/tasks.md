# TASKS-035 — TypeScript API template

Owner: Project owner. Status: Delivered — initial stateless slice accepted. Date: 2026-10-15.
[Specification](spec.md) · [Design](technical-design.md)

- [x] T1: Read guidance, existing API/catalogue designs and actual runtime sources;
  record implementation authorization and owner choice to defer migrations.
- [x] T2: Add versioned catalogue/manifest, generation, lifecycle and snapshot integration.
- [x] T3: Implement exact Fastify starter, schemas/docs, tests, quality and container.
- [x] T4: Run offline regressions, generated quality/fault checks and scoped runtime
  scenarios; record passed and pending criteria separately.
- [x] T5: Update documentation/status, open review PR, record CI; merge and project
  owner acceptance remain distinct gates.
- [x] T6: Complete managed Quadlet/private HTTPS and project-owner acceptance;
  review/merge and catalogue completion require their own observed evidence.

## Current handover

Provider 1.13.0 and exact Fastify 1.0.0 are merged in
[PR #82](https://github.com/danielbardsley/gptclaw/pull/82). All four workflows
passed on final PR revision `f6ea60a` before merge. Local focused, generated
container and compiled-image quality checks passed. Two actual managed private
APIs passed docs/schema/health, source reload/error recovery, managed test/logs,
restart and stop/source-retention/route-revocation checks while preserving the
independent service. Both instances remain ready. The project owner accepted the
presented private API checks October 15, 2026. All initial-slice acceptance
criteria pass; PostgreSQL/migrations remain deferred. See [evidence](acceptance.md).
