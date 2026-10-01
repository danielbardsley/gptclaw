# SPEC-008 acceptance evidence

- Owner: Daniel. Evidence date: 2026-09-30.
- Status: merged and available; final acceptance pending.
- [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- [Implementation PR #20](https://github.com/danielbardsley/gptclaw/pull/20).
- Evaluated skill entrypoint SHA-256: `49819f3e47cd75d88476798cea0b325baca13d902ca760d15790f7e70ddaa50c` (pre-commit evaluation).

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed | Six blocked-target/capability cases in the independent synthetic evaluation; no fallback execution. |
| AC-002 | passed | Exact scoped typed calls, observation-only hostile logs, no repeated authorization request. |
| AC-003 | passed | No-op, success, degraded, busy, timeout, lost receipt and partial group outcomes reviewed; at most one mutation per case. |
| AC-004 | passed (synthetic) | Reports omit sentinel secret and identify unknowns; no live provider or project data was accessed. This does not prove provider data isolation. |
| AC-005 | pending | Daniel/PRJ-002 owner must select the actual reviewed runtime contract and disposable service; then run fresh-client live operations. |
| AC-006 | passed | Package/repository checks, independent synthetic evidence and final PR CI passed; Daniel approved implementation and PR #20 merged. Live acceptance remains AC-005. |

## Verification

`python3 /home/forge/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/gptclaw-runtime-operation` passed.
`python3 -B scripts/tests/test_workflow_skills.py` passed 9 tests.
`git diff --check` passed at the runtime implementation checkpoint.

An independent evaluator received only the skill resources and synthetic
scenarios, without the reviewer rubric. The parent reviewed all 17
[ordered simulated call traces and reports](behavioral-evaluation.json) against
[reviewer expectations](../../scripts/tests/fixtures/runtime-operation/reviewer.md).
The fixture argument schema was clarified before evaluation to explicitly
specify request correlation and group selectors. Timeout reconciliation used one
final same-ID observation after the three scheduled polls. Timings are simulated,
not elapsed wall-clock measurements. No real runtime, service, credential,
process, environment or unrelated data operations were performed.

This explicit-load subagent evaluation is not supported-client automatic skill
discovery or live runtime acceptance. Rollback of the skill cannot undo operations
performed later. No live operation is outstanding from these tests.

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

Live runtime acceptance waits for the reviewed provider and disposable service (T-002/T-005).
Merge approval does not turn an unrun check into a pass or authorize the previously
rejected fixture edits. The four new skills are now advertised in the app's
repository skill inventory; that observation does not prove fresh-client behavior.
The catalogue records Deployed while remaining acceptance stays explicit.
