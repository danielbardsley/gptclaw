# TDD-044 — Performance budgets

Status: Implementation authorized; design updated with source changes. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

Managed containers already have resource limits and readiness deadlines, and existing
checkers exercise builds and requests. Those controls are not a calibrated,
revision-comparable performance budget suite. No universal runtime baseline is claimed.

Use QLT-001/002 build/test reporting, QLT-004 readiness and journeys, QLT-009 disposable
fixtures and existing resource/toolchain profiles. No load testing of active user
projects is implied.

Record compressed production JS per route (or native source bundle, without equating it
to an installed binary), warm API p95, cold-start-to-readiness and peak container
memory. Initial proposed sampling is five isolated cold starts and a 30-second warmup
followed by 200 bounded sequential requests, repeated three times; compare the median
run p95. Record cache state, dataset and hardware. Use absolute caps alongside relative
limits once calibrated; a missing baseline is inconclusive and cannot silently pass.

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
| QLT-006-R01 | Add a versioned proposed budget/report contract and source-controlled profile-specific baseline records, with no arbitrary benchmark command execution during discovery. | T-01, T-06, T-07 | QLT-006-AC01 |
| QLT-006-R02 | Use owned container fixtures, exact source/toolchain/build inputs and the sampling protocol above; cap CPU/memory/concurrency and total duration. | T-02, T-06, T-07 | QLT-006-AC02 |
| QLT-006-R03 | Compare structured reports with reviewed baselines; distinguish measurement errors from measured regressions and apply explicit variance policy. | T-03, T-06, T-07 | QLT-006-AC03 |
| QLT-006-R04 | Reuse QLT-009 fixture ownership and existing runtime limits; refuse unmanaged targets and avoid credentials in reports. | T-04, T-06, T-07 | QLT-006-AC04 |
| QLT-006-R05 | Integrate with QLT-002 artifacts and an explicit baseline-update process outside untrusted PR execution. | T-05, T-06, T-07 | QLT-006-AC05 |

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

Collect informational baselines first, review variance and absolute caps, then enable
required checks. Budget changes require measured justification and review. Revert
checker/config changes independently of application rollback; keep previous baselines
for comparison.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Implementation decisions

Selected under the project owner’s 2026-10-21 delegation:

Enforce conservative per-template absolute development ceilings and provide profile-bound 10% bundle / 20% latency/startup/memory regression comparisons. Collect real samples; dedicated HTTP calibration repeats five independent starts with 30-second warmups. Native runtime performance remains a physical-device criterion.

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
