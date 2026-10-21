# SPEC-040 — Pull-request workflow template (QLT-002)

- **Status:** Implementation authorized; review, merge and acceptance pending.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-002
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

Generated application pull requests receive reproducible quality, security and artifact
checks with minimal permissions, bounded execution and clear failures before review.

Use pull_request and main push checks with a stable final aggregate status. Cancel
superseded PR runs, cap job duration, and ensure skipped/path-filtered dependencies
cannot produce a misleading required success. Source from an untrusted PR must never
receive host, tailnet, production or repository-broker credentials. Branch protection
changes and repository-wide scanner enablement are separate target-specific actions.

The project owner authorized implementation of QLT-001–QLT-010 and necessary
dependencies on 2026-10-21, with reasonable decisions delegated to the agent.
Pushing branches and opening PRs are authorized; merging and deployment are excluded. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

GptClaw has its own pinned workflows. Some generated releases, including Expo and
fastapi-postgres, already ship read-only quality workflows; others do not share a
complete workflow baseline. Repository creation under SPEC-022 did not itself deliver
QLT-002.

Use QLT-001 command semantics, SPEC-019/020 toolchain/dependency policy and SPEC-021
release publishing. Coordinate scan policy with SEC-004/005 rather than claiming those
broader features delivered.

Source/previous-record evidence, not a new runtime verification:

- [.github/workflows/private-app-workflow.yml](../../.github/workflows/private-app-workflow.yml)
- [templates/apps/releases/expo-notes/1.0.0/.github/workflows/quality.yml](../../templates/apps/releases/expo-notes/1.0.0/.github/workflows/quality.yml)
- [templates/apps/releases/fastapi-postgres/1.0.0/.github/workflows/quality.yml](../../templates/apps/releases/fastapi-postgres/1.0.0/.github/workflows/quality.yml)
- [docs/022-github-repository-automation/spec.md](../../docs/022-github-repository-automation/spec.md)

## Requirements

### QLT-002-R01 — Required checks

Run frozen restore and the applicable QLT-001 gates for every supported project shape,
with stable job names and aggregate failure propagation on pull requests and main
updates.

### QLT-002-R02 — Execution trust

Pin third-party actions to reviewed full commits, use contents: read by default, disable
persisted checkout credentials and avoid privileged PR execution or secrets in untrusted
jobs.

### QLT-002-R03 — Caches and limits

Key dependency caches by OS/architecture, exact toolchain and lockfile; prevent
untrusted cache/artifact content from entering privileged jobs; bound jobs and
concurrent runs.

### QLT-002-R04 — Security gates

Run dependency and source/secret checks applicable to the approved stack policy, with
actionable findings and explicit outage/exception states; do not silently drop existing
security gates.

### QLT-002-R05 — Review artifacts

Publish bounded test, coverage, build and scan summaries tied to revision/toolchain with
a proposed seven-day retention; exclude credentials, private origins and environment
dumps.

## Acceptance criteria

All criteria are pending; drafting does not establish implementation acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-002-AC01 | A passing synthetic PR succeeds; a test failure, missing required job and malformed lockfile each block the aggregate; component errors are attributed. | QLT-002-R01 |
| QLT-002-AC02 | Static workflow checks reject mutable action refs, write-default tokens, privileged PR triggers and secret-bearing untrusted jobs; a fork-style run passes ordinary checks without secrets. | QLT-002-R02 |
| QLT-002-AC03 | Cold and warm runs both pass; changed lock/profile misses the cache; cancellation and timeout trials terminate owned work and preserve the failure result. | QLT-002-R03 |
| QLT-002-AC04 | A synthetic secret and a controlled vulnerable-dependency fixture fail the relevant gate; unavailable scanners cannot yield an all-passed result; exception expiry is tested. | QLT-002-R04 |
| QLT-002-AC05 | A generated-project trial exposes useful revision-bound reports; failed jobs retain safe diagnostics; artifact canary and size/retention checks pass. | QLT-002-R05 |

## Decisions and completion

Use read-only pull_request/main checks, a stable required aggregate, full action commit pins, per-ref/OS/architecture/lock/toolchain caches and report-only artifacts retained seven days. Keep repository settings and broad SEC features outside this change.

The project owner delegated reasonable implementation choices on 2026-10-21.
This scope is authorized for source changes, synthetic tests and PR publication;
merge and deployment are explicitly excluded.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.