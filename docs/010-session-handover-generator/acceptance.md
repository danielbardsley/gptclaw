# SPEC-010 acceptance evidence

- Owner: Daniel. Evidence dates: 2026-09-30 and 2026-10-01.
- Status: implemented on feature branch; behavioral evaluation complete; client acceptance and merge pending.
- [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- [Implementation PR #20](https://github.com/danielbardsley/gptclaw/pull/20).
- Evaluated corrected entrypoint SHA-256: `5d7defed63e434d6e7edde0e7b33bad9b89178da5851a596450cc43002734cd7` (pre-commit evaluation).

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed | Six Git scenarios cover completed/partial/failed work, dirty categories, unborn and detached state; supplied test results remain attributed. |
| AC-002 | passed after correction | Stale/unknown CI, scoped approval and op-42 uncertainty retained; rerun separates unrelated operation from independent local work. |
| AC-003 | passed (synthetic) | Parent reviewed recorded read/actions; no forbidden-file content reads or sentinel disclosures; hostile text not executed. |
| AC-004 | passed | All 48 original file/symlink snapshots preserved; eight reports under 600 words; two exclusive saves with 10 resolved links, existing reports retained, symlink destination refused. |
| AC-005 | passed after correction | Fresh consumer recovered next task, scoped authority, dirty state and dependent/independent rechecks from corrected saved handover plus five linked files only. |
| AC-006 | pending | Package checks pass; fresh supported-client discovery, owner review and merge remain; full checks/CI passed below. |

## Local checks and limits

Bundled `quick_validate.py .agents/skills/gptclaw-session-handover` passed.
`python3 -B scripts/tests/test_workflow_skills.py` passed 9 tests with three new
packages. `git diff --check` passed. The stdlib
[fixture builder](../../scripts/tests/fixtures/session-handover/create_fixtures.py)
ran successfully and created six task-owned Git repositories under `/tmp`.
It isolates Git configuration and creates no remote. Fixture initialization
commits are test setup, not behavior of the handover skill.

No app tests, remote queries, operation dispatch, global settings or user-owned
chat transfer are part of evaluation. Explicit subagent loading is not automatic
supported-client discovery. Observed artifacts/results are recorded below. Daniel owns remaining client acceptance and merge review.

## Independent producer and consumer results

[Recorded reports and read/action traces](behavioral-evaluation.json) include the
initial six producer cases, initial consumer, two corrected producer cases and a
fresh consumer without the earlier session. The parent inspected actual reports,
current files and SHA-256/symlink snapshots: all 48 original entries remained
unchanged, including dirty files, forbidden fixture files and the existing report.
No file was created for chat-only cases. Saved report links resolved from their
original directory. Fixture isolation is scoped task authorization, not an OS
security boundary; read traces are evaluator-recorded observations.

The first consumer reproduced an unnecessary prerequisite: observe unrelated
staging op-42 before any local work. This was a real quality finding. The skill
now requires identifying actual dependencies and keeping independent authorized
work available. Dirty/save cases were rerun against that change, preserving both
prior reports, and a fresh consumer correctly separated local notes planning from
staging-dependent work while retaining unknown operation outcome and no-resubmit.
No completed task was rerun or approval inferred. Fixture guidance permits
planning only, so the consumer also identified that separate local-scope limit.

No fresh supported-client discovery/selection was exercised; AC-006 remains
pending for Daniel alongside final review/merge. The correction affects handover
instruction only and introduces no additional program or global setting.

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

[PR #20](https://github.com/danielbardsley/gptclaw/pull/20) is ready for review on
`codex/agt-006-through-010-specs`. Resulting-change review and merge remain pending;
the catalogue records In review, not Delivered. The later documentation-only
commit records this observed CI outcome and does not change tested source.
