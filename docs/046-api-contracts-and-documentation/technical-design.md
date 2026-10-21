# TDD-046 — Contract and API documentation

Status: Implementation authorized; design updated with source changes. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

FastAPI and Fastify starters already expose OpenAPI and bundled docs; SPEC-036 includes
a checked-in notes contract and typed mobile client with drift checks. These are
stack-specific slices, not a uniform contract lifecycle across all supported service
boundaries.

Reuse SPEC-024/025/035/036 contracts and QLT-001/002 checks; coordinate
database-compatible changes with QLT-007 and real routed checks with QLT-004. No new API
framework is needed.

Treat application route schemas as the authoritative HTTP source, normalize
deterministic output and retain the last accepted contract for compatibility comparison.
Document auth assumptions, validation/error envelopes, pagination and base-path
behavior. Never bake private origins, credentials or live data into schemas/examples. A
version increment alone does not prove compatibility or authorize retirement of existing
consumers.

Reuse the version and command sources linked in the specification. Any new
packages/actions/images need exact reviewed pins during implementation; this planning
change installs nothing and reserves no future schema version. Application-provided
commands and fetched content remain untrusted task data. Validate identity/capability
before execution; run authorized checks in the reviewed container boundary rather than
during metadata discovery.

## Components and traceability

The following components are proposed responsibilities, not claims that new interfaces
already exist. T-01 through T-05 identify implementation work; follow the dependency
order in the task list. T-06 covers combined verification and T-07 covers
acceptance/delivery.

| Requirement | Planned mechanism/component change | Task | Acceptance |
|---|---|---|---|
| QLT-008-R01 | Add stack-native exporters plus a pinned validator and route inventory checks, executed in reviewed containers rather than during manifest discovery. | T-01, T-06, T-07 | QLT-008-AC01 |
| QLT-008-R02 | Use structural diff plus actual client/server integration, with declared contract major and reviewed compatibility exceptions. | T-02, T-06, T-07 | QLT-008-AC02 |
| QLT-008-R03 | Reuse the notes contract/client pattern and stack-native validation; generated files retain provenance and are never trusted solely because they compile. | T-03, T-06, T-07 | QLT-008-AC03 |
| QLT-008-R04 | Reuse bundled FastAPI/Fastify docs and a configurable safe server base; keep health/readiness documented separately from application operations. | T-04, T-06, T-07 | QLT-008-AC04 |
| QLT-008-R05 | Coordinate QLT-001/002/009 and publish new exact releases, preserving existing schemas and consumers. | T-05, T-06, T-07 | QLT-008-AC05 |

## Verification and evidence

Use the acceptance scenarios in [the specification](spec.md), including negative
and interrupted/failure cases where mapped. Keep fixtures synthetic, bounded and
task-owned; clean up only resources whose ownership is established. Preserve
unrelated source, projects, persistent data and historical acceptance evidence.

For implementation, run `git diff --check`, `git diff --cached --check` and the relevant
script/stack tests. Script, template, workflow or schema changes also require the
prepared-environment `./scripts/check-repository.sh`; changes to published template
infrastructure require release integrity/immutability checks against the merged base.
Run generated-project checks with their actual pinned stack prerequisites, not an
assumed host toolchain. Do not install host packages to make tests pass. A changed check
must be shown to reject its mapped fault, not merely pass the starter.

Report local unit/static, generated-container, CI, managed runtime and independent
client/device results separately. Skip inapplicable layers with a reason; missing
required evidence remains pending. Store source/toolchain identities and sanitized
results, not credentials, private host defaults or whole environment/log dumps.
Draft-document verification is limited to links, traceability, statuses and diff
quality; the commands above describe future implementation gates.

## Rollout, recovery and limitations

Publish new template releases and explicit contract/client adoption PRs. On incompatible
changes, version the boundary and preserve the accepted consumer path until reviewed
retirement. Revert application/contract/client source together only when compatible with
retained data and deployed consumers.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Implementation decisions

Selected under the project owner’s 2026-10-21 delegation:

Export and compare deterministic API shapes, check local references and conservative compatibility changes, retain existing generated clients, and separately assert actual private prefixes/docs/assets. Reuse FastAPI/Fastify rather than introduce frameworks.

Implementation, tests and PR publication are authorized. Merge, deployment and
owner/client/device acceptance remain separate; no overnight answer is required.

## Implementation interfaces

The shared implementation uses [the portable runner](../../scripts/project_quality_core.py),
[exact-release golden tests](../../scripts/quality_templates.py),
[guarded source sealing](../../scripts/seal-quality-releases.py) and
[the quality runbook](../../runbooks/manage-project-quality.md).
The new exact 1.1.0 releases retain provider/lifecycle versions and historical
release bytes. Existing runtime, dependency, database and contract capabilities
are reused rather than duplicated as unrelated initiatives.
