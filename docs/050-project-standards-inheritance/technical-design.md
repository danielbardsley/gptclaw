# TDD-050: Shared creation guidance bundle

Owner: project owner. Status: Implementation authorized.
[Specification](spec.md) · [Tasks](tasks.md).

## Approach

Add a fixed shared resource mapping and a versioned engineering reference package
under templates/projects. Seed standards from the existing reviewed Python,
mobile and application-quality sources, preserving their contracts. An applicability
index distinguishes universal rules, stack-specific rules and template examples.
No executable app configuration is fabricated for a stack-neutral project.

Planning bootstrap reads the package and skill from the selected immutable Git
revision and includes them in its existing hash inventory. Catalogue creation
adds a separately identified creation-time guidance layer after validating the
exact immutable app release, before publication. Its source inventory/hashes are
recorded separately from template-release provenance. Provider packaging includes
the same helper/resources. Existing lifecycle validation does not rewrite projects.
Application creation also renders the planning index/catalogue, extending an
existing documentation index while preserving its content and links.
Root guidance points to local standards and requires a design/task mapping to
commands, tests and explicit deviations before implementation. Specification
outlines reinforce that handoff when a planning project gains a stack.

## Verification and traceability

| Requirement | Mechanism / task | Acceptance |
|---|---|---|
| PSI-001 | Shared fixed inventory and both generators / PSI-T01 | PSI-AC01–02 |
| PSI-002 | Applicability index, root links and planning workflow / PSI-T02 | PSI-AC01–02 |
| PSI-003 | Immutable reads, separate provenance, fail-closed publication and provider bundle / PSI-T01, PSI-T03 | PSI-AC01–03 |
| PSI-004 | Synthetic creation/failure/packaging tests and repository gates / PSI-T03 | PSI-AC03 |

Run focused Python suites and the prepared offline repository checker. Verify
relative links and whitespace; no Terraform or live application checks are needed.
Record actual results in acceptance.md. A future installed provider must use the
reviewed new bundle; this task does not replace an installed provider or prove
client loading. Existing projects require separately authorized adoption.
