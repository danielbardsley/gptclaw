# TASKS-035 — TypeScript API template

Owner: Project owner. Status: Implemented in review. Date: 2026-10-15.
[Specification](spec.md) · [Design](technical-design.md)

- [x] T1: Read guidance, existing API/catalogue designs and actual runtime sources;
  record implementation authorization and owner choice to defer migrations.
- [x] T2: Add versioned catalogue/manifest, generation, lifecycle and snapshot integration.
- [x] T3: Implement exact Fastify starter, schemas/docs, tests, quality and container.
- [x] T4: Run offline regressions, generated quality/fault checks and scoped runtime
  scenarios; record passed and pending criteria separately.
- [x] T5: Update documentation/status, open review PR, record CI; merge and project
  owner acceptance remain distinct gates.
- [ ] T6: Complete managed Quadlet/private HTTPS and project-owner acceptance;
  review/merge and catalogue completion require their own observed evidence.

## Current handover

Provider source 1.13.0 adds exact Fastify 1.0.0 catalogue v6, manifest v7,
generation/provenance and immutable bundle integration. Local generated quality,
fault rejection and two-container update/recovery checks passed. Compiled image
build, unprivileged verify and default-command smoke checks passed.
[PR #82](https://github.com/danielbardsley/gptclaw/pull/82) is open; all six private
application CI jobs and all four workflows, including the complete repository
gate, passed at implementation commit `202b7e8`. Duplicate local full runs were
stopped after equivalent CI passed; focused local and container checks completed.
Managed/private HTTPS, merge and project-owner acceptance remain pending. See [evidence](acceptance.md).
