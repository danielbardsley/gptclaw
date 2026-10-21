# TDD-040 — Pull-request workflow template

Status: Draft proposal. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

GptClaw has its own pinned workflows. Some generated releases, including Expo and
fastapi-postgres, already ship read-only quality workflows; others do not share a
complete workflow baseline. Repository creation under SPEC-022 did not itself deliver
QLT-002.

Use QLT-001 command semantics, SPEC-019/020 toolchain/dependency policy and SPEC-021
release publishing. Coordinate scan policy with SEC-004/005 rather than claiming those
broader features delivered.

Use pull_request and main push checks with a stable final aggregate status. Cancel
superseded PR runs, cap job duration, and ensure skipped/path-filtered dependencies
cannot produce a misleading required success. Source from an untrusted PR must never
receive host, tailnet, production or repository-broker credentials. Branch protection
changes and repository-wide scanner enablement are separate target-specific actions.

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
| QLT-002-R01 | Generate stack-aware jobs and an always-evaluated final aggregate with explicit dependency result checks. | T-01, T-06, T-07 | QLT-002-AC01 |
| QLT-002-R02 | Reuse reviewed workflow conventions with container resource bounds, exact toolchain inputs and job-level permission exceptions only where separately justified. | T-02, T-06, T-07 | QLT-002-AC02 |
| QLT-002-R03 | Cache package downloads rather than mutable environments or secrets; isolate trust domains and record deterministic cache keys. | T-03, T-06, T-07 | QLT-002-AC03 |
| QLT-002-R04 | Use reviewed pinned scanners and synthetic canaries, with scoped owner/reason/expiry exceptions and redacted summaries. | T-04, T-06, T-07 | QLT-002-AC04 |
| QLT-002-R05 | Allowlist report paths, scrub logs and upload diagnostic artifacts even when ordinary checks fail without changing failure status. | T-05, T-06, T-07 | QLT-002-AC05 |

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

Publish a new template release; existing projects adopt by reviewed PR. Test in an
explicitly selected synthetic repository. Reverting workflow source does not undo
repository settings, which need their own recorded recovery plan.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Open decision

Project owner selects required status names and an initial scan policy during
implementation planning. Proposed default is one stable required aggregate check;
repository settings need explicit target authorization.

Owner: project owner. Next action: review the proposed scope/defaults and resolve this
decision before dependent implementation. Continue independent documentation and source
review. Track implementation and acceptance independently of approval.