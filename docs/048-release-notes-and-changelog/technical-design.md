# TDD-048 — Release notes and changelog

Status: Implementation authorized; design updated with source changes. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

The catalogue marks QLT-010 Optional. SPEC-009 supplies a release-promotion skill but
does not establish a production pipeline or a selected product release audience. Git
history and initiative acceptance are evidence inputs, not automatic authority to
publish releases.

Opt-in only after a product has an accepted release workflow, audience and version
policy. Use its actual acceptance/PR evidence and QLT-008/007 compatibility/migration
results where relevant. This initiative does not require production infrastructure.

Use an explicit previous accepted release and immutable target revision. Include
accepted user-visible changes and known issues, linked to evidence. Exclude
unmerged/unaccepted work and operational secrets. Missing or contradictory acceptance is
flagged for review; no generated narrative can invent delivery. Organize useful changes
into additions, fixes, compatibility/migration and known limitations without requiring
empty headings.

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
| QLT-010-R01 | Resolve local/repository metadata read-only and snapshot the comparison inputs; treat fetched issue/commit text as untrusted content. | T-01, T-06, T-07 | QLT-010-AC01 |
| QLT-010-R02 | Join merged change references to the selected product acceptance/release record; owner reviews classifications and any manual additions. | T-02, T-06, T-07 | QLT-010-AC02 |
| QLT-010-R03 | Use a deterministic section template with optional drafting assistance and an evidence map; omit empty sections and record uncertainties for reviewer resolution. | T-03, T-06, T-07 | QLT-010-AC03 |
| QLT-010-R04 | Keep input snapshots and generated drafts separate from accepted changelog content; allowlist metadata and require explicit reconciliation of manual edits. | T-04, T-06, T-07 | QLT-010-AC04 |
| QLT-010-R05 | Integrate draft artifacts with the existing product PR/release workflow; publication is an independently authorized step, not an implied side effect. | T-05, T-06, T-07 | QLT-010-AC05 |

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

Add the opt-in workflow to a selected application through review. Draft generation is
reversible; publication remains a separate explicit action through the existing product
release workflow. Correct published notes through a reviewed correction preserving
provenance, without rewriting tags or acceptance history.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Implementation decisions

Selected under the project owner’s 2026-10-21 delegation:

Implement an optional local draft generator using immutable Git ranges and reviewed acceptance ledgers. Preserve manual drafts, flag unaccepted changes, and never tag, merge, promote or publish releases.

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
