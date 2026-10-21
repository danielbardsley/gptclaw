# SPEC-044 — Performance budgets (QLT-006)

- **Status:** Implemented — PR #95 merged; task records closed by project-owner request; remaining acceptance is tracked separately.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-006
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

Supported templates expose reproducible measurements and reviewed limits for bundle
size, response latency, memory and startup, so meaningful regressions fail review with
useful evidence.

Record compressed production JS per route (or native source bundle, without equating it
to an installed binary), warm API p95, cold-start-to-readiness and peak container
memory. Initial proposed sampling is five isolated cold starts and a 30-second warmup
followed by 200 bounded sequential requests, repeated three times; compare the median
run p95. Record cache state, dataset and hardware. Use absolute caps alongside relative
limits once calibrated; a missing baseline is inconclusive and cannot silently pass.

The project owner authorized implementation of QLT-001–QLT-010 and necessary
dependencies on 2026-10-21, with reasonable decisions delegated to the agent.
The initial overnight authorization covered pushing branches and opening PRs.
The project owner subsequently authorized PR #95 merge and closure of all tasks
on 2026-10-21; PR #95 is now merged. Deployment remains excluded. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

Managed containers already have resource limits and readiness deadlines, and existing
checkers exercise builds and requests. Those controls are not a calibrated,
revision-comparable performance budget suite. No universal runtime baseline is claimed.

Use QLT-001/002 build/test reporting, QLT-004 readiness and journeys, QLT-009 disposable
fixtures and existing resource/toolchain profiles. No load testing of active user
projects is implied.

Source/previous-record evidence, not a new runtime verification:

- [scripts/tests/check_app_template.py](../../scripts/tests/check_app_template.py)
- [scripts/tests/check_python_template.py](../../scripts/tests/check_python_template.py)
- [scripts/tests/check_database_template.py](../../scripts/tests/check_database_template.py)
- [config/toolchains/v1.json](../../config/toolchains/v1.json)
- [scripts/project_toolchains.py](../../scripts/project_toolchains.py)

## Requirements

### QLT-006-R01 — Budget contract

Define per-template metrics, units, workload, runner/profile, baseline revision,
relative limits and numeric absolute caps before enabling enforcement; mark inapplicable
metrics explicitly.

### QLT-006-R02 — Repeatable measurement

Measure production bundle size, bounded warm response latency, peak memory and cold
readiness using synthetic workloads on comparable pinned environments.

### QLT-006-R03 — Regression detection

Fail when any enforced absolute cap or allowed relative regression is exceeded; do not
accept missing baselines or automatically increase them on PRs.

### QLT-006-R04 — Safe execution

Run benchmarks only on named owned ephemeral targets, with bounded requests/resources,
no real datasets and no implicit production or public load.

### QLT-006-R05 — Review and evidence

Publish revision-bound metric/baseline deltas, raw safe sample summaries and reviewable
budget changes; exceptions have owner, reason and expiry.

## Acceptance criteria

Criterion-by-criterion results and remaining trials are recorded in [acceptance evidence](acceptance.md). Automated implementation does not establish full owner acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-006-AC01 | Schema fixtures reject absent units/limits and unknown metrics; every supported enforced profile has numeric caps and an identified baseline, while unsupported metrics report not applicable. | QLT-006-R01 |
| QLT-006-AC02 | Repeated clean runs report all applicable metrics, workload/cache/hardware identity and variance; incomparable hardware/profile or missing samples produce inconclusive results. | QLT-006-R02 |
| QLT-006-AC03 | Controlled bundle, delayed-response, memory and startup regressions each fail; values at/below limits pass; missing/stale/mismatched baselines cannot yield success. | QLT-006-R03 |
| QLT-006-AC04 | Target ownership and request caps are tested; cancellation removes owned benchmark processes; an unrelated service/data fixture remains unchanged. | QLT-006-R04 |
| QLT-006-AC05 | A synthetic PR shows per-metric deltas; changed baselines require explicit review; expired exceptions fail and reports distinguish informational from enforced measurements. | QLT-006-R05 |

## Decisions and completion

Enforce conservative per-template absolute development ceilings and provide profile-bound 10% bundle / 20% latency/startup/memory regression comparisons. Collect real samples; dedicated HTTP calibration repeats five independent starts with 30-second warmups. Native runtime performance remains a physical-device criterion.

The project owner delegated reasonable implementation choices on 2026-10-21.
The initial scope authorized source changes, synthetic tests and PR publication.
The project owner subsequently authorized merge and closure of all tasks; PR #95
is merged. Deployment remains separately authorized.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.