# SPEC-006 acceptance evidence

- **Status:** Merged and available; supported-client acceptance pending
- **Owner:** Daniel
- **Evidence date:** 2026-09-30
- **Specification:** [SPEC-006](./spec.md)
- **Design:** [TDD-006](./technical-design.md)
- **Tasks:** [TASKS-006](./tasks.md)
- **Implementation PR:** [PR #16](https://github.com/danielbardsley/gptclaw/pull/16)
- **Tested package revision:** `1d857964f8c6a4834b3418e3e34a71eba57d0c25`

Daniel approved the specification and explicitly authorized implementation in
this chat on 2026-09-30. Daniel subsequently accepted the implementation and
explicitly authorized merging PR #16. The package
is repository-scoped; no global installation, settings change, or deployment
was made.

## Acceptance mapping

| Criterion | State and evidence | Remaining action/owner |
|---|---|---|
| AC-001 | Local pass: skill and four outlines reviewed against SPS-001–005; bundled validator and 51 repository tests pass. | Daniel approved the resulting implementation; CI tracked below. |
| AC-002 | Passed in explicit-loading synthetic evaluation: unused initiative 005, linked plans and index/catalogue updates, original source preserved. | Supported-client discovery remains AC-006. |
| AC-003 | Passed after evaluator review: spelling-only diff retained IDs, approvals, completed tasks and dirty README; extension remained proposed. | Supported-client discovery remains AC-006. |
| AC-004 | Passed in synthetic evaluation: format/destination question recorded alongside independent drafting; prior authorization recorded without implementation or repeat approval. | Supported-client discovery remains AC-006. |
| AC-005 | Passed after review correction: supplied pass/fail/pending results attributed, merge unverified, catalogue Planned and final acceptance pending. | No live acceptance inferred from synthetic reports. |
| AC-006 | Partial: the app supplied the repository skill in its updated skill inventory; fresh-session explicit/implicit/unrelated-request scenarios remain unrun. | Daniel runs explicit, implicit, and unrelated-request scenarios through the supported connection. |
| AC-007 | Partial: criterion mapping, provenance, and maintenance procedure recorded; PR #16 merged. | Merge recorded below. Complete remaining client checks before Delivered. |

## Local checks

Executed against the package committed as `1d85796`:

- `python3 -B scripts/tests/test_specification_skill.py`: 10 tests passed.
- `python3 /home/forge/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/gptclaw-specification`: passed, `Skill is valid!`.
- `./scripts/check-repository.sh`: repository invariants and all 51 tests passed
  (installer 17, bootstrap 5, repository guidance 10, nested guidance 9, skill 10).
- `bash -n scripts/check-repository.sh`: passed.
- `git diff --check` and `git diff --cached --check`: passed for implementation.
- Relative file-link review: 54 links across 11 changed skill/planning documents
  resolved; external URLs and section-anchor semantics were not validated.

The repository tests use Python's standard library and isolated fixtures. The
bundled authoring validator was already available; it is not a new repository
runtime or CI dependency. Static package checks cannot establish agent behavior.
No Terraform source changed, so local Terraform checks were not run. Existing
PR CI runs broader Terraform quality checks; protected plan/apply remain manual.

## Behavioral and client evaluation

Scenario inputs and reviewer expectations live separately under
`scripts/tests/fixtures/specification-skill/`. Evaluation uses task-owned
synthetic repositories only and must preserve actual outputs/diffs. Explicit
skill-loading evaluation does not establish client discovery or selection.
Automatic selection is left enabled by default; no explicit-only policy or
client setting was added. The current chat's initial skill inventory predates
this package, so continuing-chat behavior cannot pass AC-006.

### Independent synthetic results

An independent evaluation agent explicitly read the skill and its outlines,
then created and edited five task-owned temporary Git fixtures. The parent
reviewed its generated documents, bounded-update diffs, and check results. This
is a small manual behavioral evaluation, not a statistical eval or client
discovery test. Synthetic variants exercised the shipped scenario themes:

| Scenario | Observed outcome |
|---|---|
| New CLI formatting plan | Index highest 003 and occupied unindexed 004 resulted in 005. Three linked plans, catalogue/index changes, measurable criteria, and requirement/task mapping; no source change. |
| Narrow correction | Only `lable` became `label`; existing IDs, approvals, completed work, and unrelated dirty README remained byte-identical. |
| Export extension | Proposed REQ-002/AC-002 and dependent design/tasks added; format/destination decision assigned to Daniel; original authorization retained. |
| Mixed acceptance | Supplied pass/fail/pending evidence explicitly attributed; reported merge not independently verified; no Delivered claim. |
| Prior authorization | Only the pending authorization sentence changed; original scope remained approved, no implementation or repeat approval occurred. |

All five fixture whitespace and relative-link checks passed. Snapshot comparison
confirmed source and README preservation. During evaluator review, an initial
acceptance edit repurposed the existing final-acceptance task. It was corrected
to retain pending T-002 and add completed evidence-recording T-006 before the
reported final results. This illustrates why artifact review remains necessary;
no claim of error-free first-pass behavior is made. The existing skill already
requires preserving task progress; no speculative additional rule was added.

No fixture application tests were executed: reported behavior-test results were
synthetic inputs. Temporary repositories and generator were removed only after
parent inspection and recording this sanitized evidence. Supported-client
explicit/implicit/unrelated-request checks remain pending for Daniel.

## Maintenance and rollback

Daniel owns skill changes through reviewed PRs. Revert the specific skill update
through a reviewed Git revert, retaining unrelated later edits, then validate
and verify the restored package in a fresh context. Existing project documents
are not migrated when outlines change. There is no global copy to uninstall.
Earlier AGT-001–003 acceptance remains unchanged.

## CI and delivery

[Run #61](https://github.com/danielbardsley/gptclaw/actions/runs/36785233735)
passed for `1d85796`. Repository invariants/tests, Terraform formatting,
backend-free initialization, validation, and tests all passed. Protected plan
and apply were skipped. No deployment was dispatched.
AGT-004 is Deployed: available in the repository and observed in the app skill
inventory. Required fresh-session acceptance remains pending before Delivered.

[Run #62](https://github.com/danielbardsley/gptclaw/actions/runs/36785467783)
also passed the full quality job at documentation revision `6ed52fc`; protected
plan/apply were skipped. The subsequent documentation-only correction checks
the already-approved phase-0 task and records this CI result.

[Run #63](https://github.com/danielbardsley/gptclaw/actions/runs/36785563365)
passed at `810302a`. Daniel accepted the implementation and authorized merge
after this revision. The app subsequently advertised `gptclaw-specification`
from the repository in its skill inventory. This is observed discovery, not
proof of the complete fresh-session behavior matrix. No unrun check is marked
passed based on owner acceptance.

## Merge closeout

Daniel authorized merge; PR #16 merged on 2026-09-30 as
`aed4fe4bb5e4202a1df2e372057699d68fc933c6`.
[Run #64](https://github.com/danielbardsley/gptclaw/actions/runs/36786055998)
passed for final PR head `cbe32513d3da267ed438376e2f6953a5e39d183b`.
The local main checkout was fast-forwarded to the merge with clean Git status.
This records PR CI, not post-merge CI or completion of unrun client scenarios.
