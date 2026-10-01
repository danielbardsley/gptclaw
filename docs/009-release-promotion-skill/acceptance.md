# SPEC-009 acceptance evidence

- Owner: Daniel. Evidence date: 2026-09-30.
- Status: merged and available; final acceptance pending.
- [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- [Implementation PR #20](https://github.com/danielbardsley/gptclaw/pull/20).
- Evaluated entrypoint SHA-256: `6f2959af17c9b3fdc804c46f07796a24620cf44e7d388e73e8cd60ee5585b3d3` (pre-commit evaluation).

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed | Notes-only and hostile metadata cases draft notes without publication; missing artifact/tests explicit. |
| AC-002 | passed | Mutable/mismatched artifact, changed approval scope, missing prior/recovery, incompatible data, denied access and waiting protected gate scenarios reviewed. |
| AC-003 | passed | Exact authorization honored; timeout/lost receipt observed without duplicate dispatch or unrelated cancellation. |
| AC-004 | passed | Failed health/wrong deployed identity stay unaccepted; only explicitly authorized recovery dispatched and still-running recovery remains unverified. |
| AC-005 | pending | Daniel selects an existing product contract and isolated non-production pipeline, artifact and specific rehearsal/recovery scope. |
| AC-006 | passed | Package/repository checks, independent synthetic evidence and final PR CI passed; Daniel approved implementation and PR #20 merged. Live acceptance remains AC-005. |

## Verification and limitations

Bundled `quick_validate.py .agents/skills/gptclaw-release-promotion` passed.
`python3 -B scripts/tests/test_workflow_skills.py` passed 9 tests with both packages.
`python3 -B scripts/tests/test_project_bootstrap.py` passed 28 tests, confirming
existing bootstrap distribution remains unchanged. `bash -n scripts/check-repository.sh`
and `git diff --check` passed.

The parent inspected all 18 independent
[simulated call traces and reports](behavioral-evaluation.json) against the
[separate reviewer rubric](../../scripts/tests/fixtures/release-promotion/reviewer.md).
The evaluator saw only skill/resources and synthetic input. Two stale-approval
requests were clarified during evaluation so that they referred to prior approval,
rather than themselves authorizing a new target/artifact; the evaluator reread them.
Candidate arguments use artifact identity in the synthetic inspect call. The
contract supplies its version and acceptance predicate; no real product version
or freshness convention is inferred. Recovery inherits the fixture's no-migration
compatibility facts; the missing reconciliation response remains unknown.

This is tabletop instruction evaluation: no tag, publication, pipeline, data,
production credential or AWS operation occurred. No real elapsed timing or
fresh-client automatic selection is claimed. Reverting the package cannot undo
a future release. Real product acceptance remains a separate prerequisite.

## Batch verification and delivery state

Implementation sources at `4e649bffcc62aaf4e0c79e93f2c9fe730735f0fe` passed
`./scripts/check-repository.sh`: all 107 tests and repository invariants passed
(installer 17, host bootstrap 5, repository guidance 10, nested guidance 9,
specification package 10, project bootstrap 28, workflow packages 9, ADR 19).
`bash -n scripts/check-repository.sh`, `git diff --check` and
`git diff --cached --check` passed. Local relative-link review resolved 157
file targets in 40 changed Markdown documents before this evidence addition;
external URLs and heading anchors were not checked.

[PR CI run #70](https://github.com/danielbardsley/gptclaw/actions/runs/36794756237)
passed for that implementation revision on 2026-10-01: repository quality checks,
Terraform format, backend-free initialization, validation and tests. Protected
plan/apply were skipped. No Terraform source changed, so separate local Terraform
runs were unnecessary; no infrastructure deployment was performed.

## Merge closeout

Daniel approved the resulting implementation and authorized merge on 2026-10-01.
[PR #20](https://github.com/danielbardsley/gptclaw/pull/20) merged as
`033c30b96ae355b0de54ddb24cf1c2f405328920`. Final PR head `d20997c365bab1fd0504524bf4b69ebf7cc2c3c9`
passed [CI run #71](https://github.com/danielbardsley/gptclaw/actions/runs/36794914080),
including repository checks and Terraform quality checks; protected plan/apply
were skipped. This records PR CI, not a new infrastructure deployment.

Live non-production rehearsal waits for the product contract and separately scoped operations (T-002/T-005).
Merge approval does not turn an unrun check into a pass or authorize the previously
rejected fixture edits. The four new skills are now advertised in the app's
repository skill inventory; that observation does not prove fresh-client behavior.
The catalogue records Deployed while remaining acceptance stays explicit.
