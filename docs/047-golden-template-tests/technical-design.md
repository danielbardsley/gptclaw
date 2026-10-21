# TDD-047 — Golden-template tests

Status: Implementation authorized; design updated with source changes. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

scripts/check-template-releases.py already verifies catalogue integrity and historical
release immutability. Stack-specific checkers and private-app-workflow.yml cover
substantial generated-project behavior. Coverage is distributed; a complete support
matrix, common result contract and interruption-safe lifecycle coordinator remain to be
specified and implemented.

Build on SPEC-021 catalogue/provenance, QLT-001/002 checks and QLT-004 smoke profiles.
Persistent fixtures reuse SPEC-026 controls; mobile fixtures retain SPEC-033/034
source/Metro/device distinctions.

Enumerate catalogues v1–v7 and all exact releases, including both Expo revisions, rather
than treating the newest catalogue file as a replacement. Assign web/API/group releases
generate/restore/verify/start/route/journey/stop checks, database releases additional
persistence/migration/recovery checks, and mobile releases source/bundle checks plus
Metro only when supported. Native device acceptance and real private ingress remain
separate recorded trials. Retired releases retain integrity/generation checks and an
explicit retirement decision.

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
| QLT-009-R01 | Reuse catalogue validation and immutable provenance; keep supported/retired states explicit and never infer support from filesystem order. | T-01, T-06, T-07 | QLT-009-AC01 |
| QLT-009-R02 | Wrap existing stack checker scripts in a shared coordinator, reusing QLT-004 assertions and distinct source/runtime/client evidence classes. | T-02, T-06, T-07 | QLT-009-AC02 |
| QLT-009-R03 | Use a task-owned receipt/allowlist and safe finally/reconciliation paths; persistent test databases are disposable only by explicit fixture designation, never by name prefix alone. | T-03, T-06, T-07 | QLT-009-AC03 |
| QLT-009-R04 | Extend pinned workflow jobs and structured matrix outputs; hosted CI routing stays local and never assumes access to the managed tailnet. | T-04, T-06, T-07 | QLT-009-AC04 |
| QLT-009-R05 | Publish bounded QLT-002 artifacts and per-cell status, preserve historical release checks, and record unfinished private/native acceptance separately. | T-05, T-06, T-07 | QLT-009-AC05 |

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

First wrap existing stack checkers without weakening their assertions, then fill
documented gaps. Run offline metadata/unit suites on ordinary PRs, generated runtime
checks on relevant source changes and the full supported matrix on a reviewed weekly
schedule/manual release gate. CI uses isolated networking; private acceptance needs its
own authorized runner.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Implementation decisions

Selected under the project owner’s 2026-10-21 delegation:

Discover the complete exact-release inventory dynamically. Run full quality/lifecycle/fault checks for quality-enabled releases; retain historical integrity/generation checks for superseded pre-quality releases. Use unique labels and owned cleanup, with no shared prune.

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
