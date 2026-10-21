# SPEC-047 — Golden-template tests (QLT-009)

- **Status:** Implementation authorized; review, merge and acceptance pending.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-009
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

Every supported exact template release is continuously checked through its applicable
generation, quality and lifecycle path using owned disposable projects, so template
regressions are caught without risking retained projects or data.

Enumerate catalogues v1–v7 and all exact releases, including both Expo revisions, rather
than treating the newest catalogue file as a replacement. Assign web/API/group releases
generate/restore/verify/start/route/journey/stop checks, database releases additional
persistence/migration/recovery checks, and mobile releases source/bundle checks plus
Metro only when supported. Native device acceptance and real private ingress remain
separate recorded trials. Retired releases retain integrity/generation checks and an
explicit retirement decision.

The project owner authorized implementation of QLT-001–QLT-010 and necessary
dependencies on 2026-10-21, with reasonable decisions delegated to the agent.
Pushing branches and opening PRs are authorized; merging and deployment are excluded. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

scripts/check-template-releases.py already verifies catalogue integrity and historical
release immutability. Stack-specific checkers and private-app-workflow.yml cover
substantial generated-project behavior. Coverage is distributed; a complete support
matrix, common result contract and interruption-safe lifecycle coordinator remain to be
specified and implemented.

Build on SPEC-021 catalogue/provenance, QLT-001/002 checks and QLT-004 smoke profiles.
Persistent fixtures reuse SPEC-026 controls; mobile fixtures retain SPEC-033/034
source/Metro/device distinctions.

Source/previous-record evidence, not a new runtime verification:

- [config/templates/v1.json](../../config/templates/v1.json)
- [config/templates/v7.json](../../config/templates/v7.json)
- [scripts/check-template-releases.py](../../scripts/check-template-releases.py)
- [scripts/tests/test_project_templates.py](../../scripts/tests/test_project_templates.py)
- [scripts/tests/check_app_template.py](../../scripts/tests/check_app_template.py)
- [scripts/tests/check_mobile_template.py](../../scripts/tests/check_mobile_template.py)
- [scripts/tests/check_mobile_backend_template.py](../../scripts/tests/check_mobile_backend_template.py)
- [.github/workflows/private-app-workflow.yml](../../.github/workflows/private-app-workflow.yml)

## Requirements

### QLT-009-R01 — Complete inventory

Derive a deterministic exact-release test matrix from all supported catalogues, with
stack capabilities, lifecycle applicability and explicit retirement dispositions.

### QLT-009-R02 — End-to-end paths

Generate each supported release, restore frozen dependencies, run quality/build and
applicable owned lifecycle/routing/journey checks; test database persistence/recovery
and mobile-specific limits.

### QLT-009-R03 — Owned teardown

Allocate unique fixture roots, IDs, networks, ports, containers and data; prove
ownership before cleanup and survive interruption without touching retained or unrelated
projects.

### QLT-009-R04 — Continuous execution

Run a bounded relevant PR matrix, the complete supported matrix on schedule and a
release gate, using exact toolchains and isolated runners without host/runtime
credentials.

### QLT-009-R05 — Actionable evidence

Report exact release/digest, source/toolchain, executed and skipped stages, cleanup
state and safe diagnostics. Quarantines require owner, reason and expiry and do not
count as acceptance.

## Acceptance criteria

Criterion-by-criterion results and remaining trials are recorded in [acceptance evidence](acceptance.md). Automated implementation does not establish full owner acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-009-AC01 | Every catalogue release appears once with required checks or a reviewed retirement reason; a newly added unclassified release fails matrix validation. | QLT-009-R01 |
| QLT-009-AC02 | The full selected matrix passes; injected bad hash, build fault, route-prefix failure, lost DB record and mobile bundle fault each fail the relevant cell. | QLT-009-R02 |
| QLT-009-AC03 | Success/failure/cancellation trials remove owned ephemeral resources; forged/ambiguous ownership refuses deletion; sentinel unrelated data/source survives every trial. | QLT-009-R03 |
| QLT-009-AC04 | A synthetic changed-template PR selects the correct cells; catalogue/shared-runner changes select all affected cells; weekly/manual configuration includes every supported release and deadlines. | QLT-009-R04 |
| QLT-009-AC05 | Reports distinguish local, CI, managed ingress and physical-device results; an expired quarantine fails; leaked-secret/private-origin canaries are absent from public artifacts. | QLT-009-R05 |

## Decisions and completion

Discover the complete exact-release inventory dynamically. Run full quality/lifecycle/fault checks for quality-enabled releases; retain historical integrity/generation checks for superseded pre-quality releases. Use unique labels and owned cleanup, with no shared prune.

The project owner delegated reasonable implementation choices on 2026-10-21.
This scope is authorized for source changes, synthetic tests and PR publication;
merge and deployment are explicitly excluded.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.