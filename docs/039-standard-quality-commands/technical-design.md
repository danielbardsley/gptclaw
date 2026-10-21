# TDD-039 — Standard quality commands

Status: Draft proposal. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

Manifest v1 exposes build/start/test only. Later API and mobile contracts already
require broader command vectors; Fastify has package scripts, FastAPI has
scripts/quality.py, and Expo has checks/quality.cjs. Next.js and grouped projects still
need a reviewed common interface. Existing checks are a starting point, not evidence
that every template meets this standard.

Build on SPEC-019/020 dependency/toolchain selection and SPEC-021 immutable generation;
coordinate CI invocation with QLT-002 and regression coverage with QLT-009.

The proposed common verbs are format (explicit source-writing action), lint (including
formatting checks), typecheck, test, build and verify. Verify runs all applicable
read-only quality gates, including existing security/contract gates, without calling
format. Build may write ignored output. Mobile build means deterministic source/bundle
validation, not native signing. A check with no applicable meaning must be documented
and reported as not applicable; it must not silently become a successful empty script.

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
| QLT-001-R01 | Use stack-owned runners and a shared documented capability matrix, preserving existing security gates and avoiding recursive verify invocation. | T-01, T-06, T-07 | QLT-001-AC01 |
| QLT-001-R02 | Extend bundled schemas, validator dispatch, generation and provider capability checks together, with no in-place v1 widening. | T-02, T-06, T-07 | QLT-001-AC02 |
| QLT-001-R03 | Keep pinned stack-native configurations alongside template guidance; choose exact tool versions from reviewed source profiles rather than installing host tools. | T-03, T-06, T-07 | QLT-001-AC03 |
| QLT-001-R04 | Reuse dependency and toolchain adapters; publish structured gate/status summaries and separate restore from check execution. | T-04, T-06, T-07 | QLT-001-AC04 |
| QLT-001-R05 | Use SPEC-021 release/provenance validation and a per-component aggregation report. | T-05, T-06, T-07 | QLT-001-AC05 |

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

Publish new exact releases and explicit opt-in adoption guidance. Preserve all
historical manifest meanings and release bytes. Revert generated application changes
through reviewed Git changes; selecting an older release affects new generation only.

Any provider update follows its reviewed installer/operator path. Infrastructure, public
exposure, production operations and destructive retained-data changes need their own
concrete authorization and existing gates; a quality gate grants none. No prior scoped
acceptance is broadened by this proposal.

## Open decision

Project owner reviews the initial supported-template matrix and command/schema proposal
before implementation. Use existing API/mobile conventions where compatible; allocate
any new schema versions at implementation time.

Owner: project owner. Next action: review the proposed scope/defaults and resolve this
decision before dependent implementation. Continue independent documentation and source
review. Track implementation and acceptance independently of approval.