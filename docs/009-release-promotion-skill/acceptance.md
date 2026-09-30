# SPEC-009 acceptance evidence

- Owner: Daniel. Evidence date: 2026-09-30.
- Status: implemented on feature branch; real-product rehearsal and merge pending.
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
| AC-006 | pending | Local package and synthetic review passed; final repository checks, CI, owner review and merge tracked below. |

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
