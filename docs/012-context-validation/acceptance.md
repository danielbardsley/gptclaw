# SPEC-012 acceptance evidence

- Owner: Daniel. Evidence date: 2026-10-01.
- Status: implemented on feature branch; read-only behavioral review complete; two repair tests blocked by automatic approval review.
- [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- [Implementation PR #20](https://github.com/danielbardsley/gptclaw/pull/20).
- Evaluated entrypoint SHA-256: `0fae0e3dd1eff106c890a48f9dc14985f3252f5fc8b315bacece2ce9e541d4ca` (pre-commit evaluation).

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed (synthetic review) | Six evidence-specific findings cover broken plan link, CSV/JSON scope, missing quoting coverage, unsupported completion/runtime and changed-source test evidence. |
| AC-002 | passed | Valid fixture has no invented findings: older approval, nested specialization, superseded JSON plan, absent optional conventions and unrelated documentation change were distinguished. |
| AC-003 | passed | Only unapproved deletion blocked; original CSV work remains authorized and unknown override is preserved with loading uncertainty. |
| AC-004 | pending (repair portion) | Read-only cases and all original files preserved; no forbidden reads or hostile command execution. Two exact synthetic repairs were rejected before execution by automatic approval review; explicit user authorization requested. |
| AC-005 | pending | Relevant/trivial requests evaluated through explicit loading; supported-client automatic selection remains unverified. |
| AC-006 | pending | Package checks pass; full checks/CI passed below; owner review and merge remain. |

## Verification and limits

Bundled `quick_validate.py .agents/skills/gptclaw-context-validation` passed.
`python3 -B scripts/tests/test_workflow_skills.py` passed 9 tests covering all four
new skills. The standard-library
[fixture builder](../../scripts/tests/fixtures/context-validation/create_fixtures.py)
created five isolated Git projects successfully. Its commits are synthetic setup,
not behavior of the context validator. No global hook, policy parser, network
query, runtime operation, credential or production access is introduced.

Evaluation is scoped semantic review of allowed project files and Git metadata.
Explicit subagent loading cannot prove automatic selection or actual instruction
loading in a fresh supported client. Report-only cases must preserve all bytes;
requested repairs must leave all independent work unchanged. Observed results are recorded below. Daniel owns remaining client and merge review.

## Independent semantic evaluation

The parent inspected [five recorded case traces/reports](behavioral-evaluation.json)
and compared all 59 original file SHA-256 values against setup snapshots;
all were unchanged. Six concrete contradictions were identified in the problems
case, no false blockers in the valid case, and the retention conflict affected
only deletion. The evaluator verified the changed-source hash and meaningful
source diff, and separately confirmed the valid case's source was unchanged.
Sentinel-bearing excluded content was absent from recorded reads and reports.
These are task-scoped observations, not an OS-enforced isolation claim.

For the narrow link repair and trivial typo request, the evaluator inspected only
relevant guidance/files and Git metadata and prepared exact substitutions.
Automatic approval review rejected a combined write before execution, stating
that user authorization for repository implementation did not cover fixture edits.
A retry citing the user's explicit batch approval and SPEC-012 AC-004/T-003 was
also rejected. Both files remain unchanged; no bypass was attempted. The parent
requested explicit authorization for those two concrete disposable-file edits.
AC-004's repair portion remains pending until approved and actually verified.
No broader audit was introduced for the typo case. Fresh supported-client routing
still remains AC-005; explicit subagent loading cannot establish it.

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
