# SPEC-012 acceptance evidence

- Owner: Daniel. Evidence date: 2026-10-01.
- Status: implemented on feature branch; independent behavioral evaluation in progress.
- [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- [Implementation PR #20](https://github.com/danielbardsley/gptclaw/pull/20).
- Evaluated entrypoint SHA-256: `0fae0e3dd1eff106c890a48f9dc14985f3252f5fc8b315bacece2ce9e541d4ca` (pre-commit evaluation).

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | pending | Independent review of synthetic missing-link, scope, evidence, source and completion contradictions. |
| AC-002 | pending | Paired valid older/specialized/superseded/optional-absence case under review. |
| AC-003 | pending | Scoped approval/retention conflict and unknown override scenario under review. |
| AC-004 | pending | Read-only preservation, forbidden reads and two narrow repair diffs await parent verification. |
| AC-005 | pending | Relevant/trivial requests evaluated through explicit loading; supported-client automatic selection remains unverified. |
| AC-006 | pending | Package checks pass; final repository/CI results, owner review and merge remain. |

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
requested repairs must leave all independent work unchanged. Final observed
results will be recorded below. Daniel owns remaining client and merge review.
