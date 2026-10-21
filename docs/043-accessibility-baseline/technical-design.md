# TDD-043 — Accessibility baseline

Status: Draft proposal. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

Dashboard and mobile initiatives contain scoped keyboard/native interaction evidence.
SPEC-036 still records pending native/final acceptance. These records neither establish
a platform-wide baseline nor certify a generated product after its UI changes.

Coordinate UI conventions with TPL-008, use QLT-001/002 for automated gates and
QLT-004/009 for journey/template coverage. Applying the baseline to the dashboard is a
separate selected adoption task.

The proposed minimum includes semantic controls, meaningful names/roles/state,
programmatic labels and errors, visible focus, logical focus order and recovery,
keyboard operation without traps, and non-color-only status. Text contrast targets are
4.5:1 for ordinary text and 3:1 for large text; applicable control/focus contrast
targets are 3:1. Include 200% zoom, narrow layout, reduced motion and enlarged native
text. Automated success cannot replace manual assistive-technology evidence.

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
| QLT-005-R01 | Use platform-native semantics first, shared guidance/components where available, and interaction tests for focus transitions. | T-01, T-06, T-07 | QLT-005-AC01 |
| QLT-005-R02 | Encode reviewed colors and focus tokens in stack styling, with layout/state fixtures and an explicit contrast measurement checklist. | T-02, T-06, T-07 | QLT-005-AC02 |
| QLT-005-R03 | Add stack-appropriate static/rendered analyzers and deterministic interaction tests to QLT-001/002; choose exact versions during implementation review. | T-03, T-06, T-07 | QLT-005-AC03 |
| QLT-005-R04 | Maintain a per-template manual matrix with repeatable steps and owner acceptance; do not infer native behavior from web rendering. | T-04, T-06, T-07 | QLT-005-AC04 |
| QLT-005-R05 | Use new releases and QLT-009 starter checks, plus explicit adoption PRs for existing products/dashboard. | T-05, T-06, T-07 | QLT-005-AC05 |

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

Publish new accessible template releases and guidance; migrate selected existing
applications through their own reviewed UI changes. Revert faulty UI code through Git
while preserving user data and reporting any accessibility regression left by rollback.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Open decision

Propose WCAG 2.2 AA as the web engineering target, with a documented applicable-criteria
checklist rather than a certification claim. Project owner confirms
browser/assistive-technology coverage; initial native acceptance is Android-first, with
iOS explicitly pending until tested.

Owner: project owner. Next action: review the proposed scope/defaults and resolve this
decision before dependent implementation. Continue independent documentation and source
review. Track implementation and acceptance independently of approval.