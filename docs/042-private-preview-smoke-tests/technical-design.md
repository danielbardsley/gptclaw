# TDD-042 — Preview smoke tests

Status: Draft proposal. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

SPEC-018 and stack-specific checker scripts already exercise private paths and synthetic
journeys. These are not a general smoke coordinator after every managed update. Source
quality for mobile does not prove a physical-device journey.

Reuse managed lifecycle/routing ownership, SPEC-025 groups and SPEC-033/034 Metro
limits. QLT-002 runs local preview checks; QLT-009 exercises the same contracts on owned
template fixtures.

A managed host check and an independent private client check are separate evidence
classes. Hosted CI has no implied tailnet access: use loopback/isolated routing in CI,
and a separately authorized private runner/operator for actual ingress. Capture source
digest and operation/activation identity at start and end; source reloads may reuse a
process, so PID alone cannot identify the tested revision.

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
| QLT-004-R01 | Read validated lifecycle receipts and reviewed route metadata; constrain redirects and never execute application instructions from response bodies. | T-01, T-06, T-07 | QLT-004-AC01 |
| QLT-004-R02 | Use stack-specific bounded HTTP/browser probes and explicit expected assertions; do not equate an HTTP 200 or process-alive result with journey success. | T-02, T-06, T-07 | QLT-004-AC02 |
| QLT-004-R03 | Serialize or generation-tag smoke requests under existing lifecycle ownership and compare source/activation identities before publishing results. | T-03, T-06, T-07 | QLT-004-AC03 |
| QLT-004-R04 | Separate probe policy from lifecycle authority; track exact fixture identities and never use reset/restore as smoke cleanup. | T-04, T-06, T-07 | QLT-004-AC04 |
| QLT-004-R05 | Keep bounded local reports and sanitized acceptance references; require a selected physical device for any claimed native journey. | T-05, T-06, T-07 | QLT-004-AC05 |

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

Introduce opt-in smoke profiles, then enable the selected release matrix. A smoke
failure reports unhealthy acceptance and can block promotion, but does not automatically
restart, migrate, roll back data or delete a project.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Open decision

Project owner confirms the initial application journey and private acceptance target
before execution. Proposed default checks are read-only; writing journeys require a
named disposable synthetic dataset.

Owner: project owner. Next action: review the proposed scope/defaults and resolve this
decision before dependent implementation. Continue independent documentation and source
review. Track implementation and acceptance independently of approval.