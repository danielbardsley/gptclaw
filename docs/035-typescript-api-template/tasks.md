# TASKS-035 — TypeScript API template

Owner: Project owner. Status: In progress. Date: 2026-10-15.
[Specification](spec.md) · [Design](technical-design.md)

- [x] T1: Read guidance, existing API/catalogue designs and actual runtime sources;
  record implementation authorization and owner choice to defer migrations.
- [x] T2: Add versioned catalogue/manifest, generation, lifecycle and snapshot integration.
- [x] T3: Implement exact Fastify starter, schemas/docs, tests, quality and container.
- [ ] T4: Run offline regressions, generated quality/fault checks and scoped runtime
  scenarios; record passed and pending criteria separately.
- [ ] T5: Update documentation/status, open review PR, record CI; merge and project
  owner acceptance remain distinct gates.

## Current handover

Provider source 1.13.0 adds exact Fastify 1.0.0 catalogue v6, manifest v7,
generation/provenance and immutable bundle integration. Local generated quality,
fault rejection and two-container update/recovery checks passed. Final broad
regressions and compiled image are in progress; managed/private HTTPS, remote CI,
merge and project-owner acceptance remain pending. See [evidence](acceptance.md).
