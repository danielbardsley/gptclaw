# SPEC-042 — Preview smoke tests (QLT-004)

- **Status:** Implemented — PR #95 merged; task records closed by project-owner request; remaining acceptance is tracked separately.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-004
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

After an authorized private service update, the owner gets revision-bound evidence that
its routed URL, health, assets and one meaningful journey work, with failures
distinguished from process readiness.

A managed host check and an independent private client check are separate evidence
classes. Hosted CI has no implied tailnet access: use loopback/isolated routing in CI,
and a separately authorized private runner/operator for actual ingress. Capture source
digest and operation/activation identity at start and end; source reloads may reuse a
process, so PID alone cannot identify the tested revision.

The project owner authorized implementation of QLT-001–QLT-010 and necessary
dependencies on 2026-10-21, with reasonable decisions delegated to the agent.
The initial overnight authorization covered pushing branches and opening PRs.
The project owner subsequently authorized PR #95 merge and closure of all tasks
on 2026-10-21; PR #95 is now merged. Deployment remains excluded. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

SPEC-018 and stack-specific checker scripts already exercise private paths and synthetic
journeys. These are not a general smoke coordinator after every managed update. Source
quality for mobile does not prove a physical-device journey.

Reuse managed lifecycle/routing ownership, SPEC-025 groups and SPEC-033/034 Metro
limits. QLT-002 runs local preview checks; QLT-009 exercises the same contracts on owned
template fixtures.

Source/previous-record evidence, not a new runtime verification:

- [scripts/tests/check_app_template.py](../../scripts/tests/check_app_template.py)
- [scripts/tests/check_group_template.py](../../scripts/tests/check_group_template.py)
- [scripts/tests/check_database_template.py](../../scripts/tests/check_database_template.py)
- [scripts/tests/check_mobile_backend_template.py](../../scripts/tests/check_mobile_backend_template.py)
- [runbooks/manage-private-apps.md](../../runbooks/manage-private-apps.md)
- [runbooks/manage-metro.md](../../runbooks/manage-metro.md)

## Requirements

### QLT-004-R01 — Trusted target

Resolve a named canonical project and owned private route/activation, checking source
revision and target identity before any request. Reject arbitrary public URLs,
credential-bearing URLs and cross-project redirects.

### QLT-004-R02 — Meaningful checks

Verify readiness, liveness, routed base path, an expected asset and a project-specific
critical journey after each successful managed update; API-only profiles validate schema
and a useful request.

### QLT-004-R03 — Update races

Trigger after readiness on start/restart/source-update completion; bound retries and
deadlines, supersede stale runs, and never label evidence for an older revision as
current.

### QLT-004-R04 — Data and isolation

Use synthetic fixtures only; default live checks to read-only and permit writes/cleanup
only for explicitly owned disposable journey records. Preserve persistent and unrelated
data.

### QLT-004-R05 — Evidence and clients

Report revision, activation, check results, timestamps, vantage point and safe
diagnostics. Record native device checks separately from browser/API/Metro checks.

## Acceptance criteria

Criterion-by-criterion results and remaining trials are recorded in [acceptance evidence](acceptance.md). Automated implementation does not establish full owner acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-004-AC01 | Owned private and isolated CI fixtures work; mismatched project/activation, public target and cross-origin redirect cases fail before journey execution. | QLT-004-R01 |
| QLT-004-AC02 | Healthy web/API/group fixtures pass; broken asset, wrong prefix, failed readiness and wrong-content responses each fail with distinct diagnostics. | QLT-004-R02 |
| QLT-004-AC03 | Two racing updates leave only the latest source/activation accepted; source changes during a test mark its result stale; timeout/unreachable results remain failures. | QLT-004-R03 |
| QLT-004-AC04 | A fixture writes and removes only its own records when enabled; denied-write and failed-cleanup trials preserve unrelated records and report remaining owned data. | QLT-004-R04 |
| QLT-004-AC05 | A sample report distinguishes CI, managed ingress and independent client results, excludes credentials/private origins from public evidence and does not claim native acceptance from mocks. | QLT-004-R05 |

## Decisions and completion

Use owned isolated probes in generated checks, an explicit read-only private-ingress CLI, opt-in post-start evidence and a bounded source observer. Never start/stop/restart a service or recover data in response to a smoke failure.

The project owner delegated reasonable implementation choices on 2026-10-21.
The initial scope authorized source changes, synthetic tests and PR publication.
The project owner subsequently authorized merge and closure of all tasks; PR #95
is merged. Deployment remains separately authorized.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.