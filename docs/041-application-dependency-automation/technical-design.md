# TDD-041 — Dependency automation

Status: Draft proposal. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

The root .github/dependabot.yml covers GitHub Actions and Terraform weekly with five
open PRs per ecosystem. It does not configure package updates for generated
applications. Published template releases are immutable, including their dependency
pins.

Depend on QLT-001/002 for checks, SPEC-019/020 for dependency/toolchain policy and
SPEC-021 for release immutability. Expo compatibility remains governed by the reviewed
mobile profile.

Cover npm/pnpm, Python/uv and GitHub Actions where the selected updater supports the
actual lock format. Treat missing lockfile support as an explicit capability gap
requiring a reviewed adapter, not permission to switch package managers. Review majors,
runtime/profile changes and framework-coupled upgrades separately. Security updates use
the same merge gates; no auto-merge is proposed.

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
| QLT-003-R01 | Derive the update inventory from the supported template matrix; allocate per-ecosystem limits so their sum stays within five. | T-01, T-06, T-07 | QLT-003-AC01 |
| QLT-003-R02 | Use updater grouping/ignore rules plus profile-consistency checks and a dedicated manual upgrade path for toolchain/SDK changes. | T-02, T-06, T-07 | QLT-003-AC02 |
| QLT-003-R03 | Reuse dependency policy validation and standard PR CI; update source and lockfile together with no runtime dependency resolution. | T-03, T-06, T-07 | QLT-003-AC03 |
| QLT-003-R04 | Prefer service-native credentials and public approved registries; require a distinct reviewed proposal for private registry access. | T-04, T-06, T-07 | QLT-003-AC04 |
| QLT-003-R05 | Separate application updater config from the platform release-authoring process; track owner/reason/expiry for deferrals. | T-05, T-06, T-07 | QLT-003-AC05 |

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

Add config to new releases and adopt existing applications through reviewed PRs. Pause
an updater by reverting its config or using its reviewed settings path; preserve
existing PRs and lockfiles. Template dependency updates create a new release and
catalogue entry.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Open decision

Propose Dependabot first, weekly checks and at most five open update PRs per repository.
Project owner confirms ecosystem support, grouping and bot permissions; evaluate an
alternative only for a demonstrated gap.

Owner: project owner. Next action: review the proposed scope/defaults and resolve this
decision before dependent implementation. Continue independent documentation and source
review. Track implementation and acceptance independently of approval.