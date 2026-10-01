# SPEC-011 acceptance evidence

- Owner: Daniel. Evidence date: 2026-10-01.
- Status: merged and available; final acceptance pending.
- [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- [Implementation PR #20](https://github.com/danielbardsley/gptclaw/pull/20).

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | pending | Template/guide and source-grounded Proposed pilot written; Daniel must disposition the exact pilot text. |
| AC-002 | passed (local) | 19 tests cover metadata, approval presence, retirement, editorial correction, full/partial/multi-hop supersession, later-deprecated successor and invalid graphs/IDs. |
| AC-003 | passed (local) | Shipped index/record links and structure validated; checker reads only decision documents, checks other target existence and executes no content/network requests. |
| AC-004 | passed | Independent reader identified scope, evidence, present rationale and implementation limits; no actionable issues. [Review](reader-review.json). |
| AC-005 | pending | Local checks pass; full checks/CI passed below; owner disposition and merge remain. |

## Verification and limits

`python3 -B scripts/tests/test_decision_records.py` passed 19 tests.
`bash -n scripts/check-repository.sh` and `git diff --check` passed.
[Decision index](../decisions/README.md) links the
[Proposed pilot](../decisions/0001-repository-skill-distribution.md); the main
[documentation index](../README.md) discovers these records.

The record metadata adds retirement evidence separately from original acceptance
so successor chains do not erase their approval history. Checks validate current
metadata/index/graph shape, ordinary local file targets and nonempty sections.
They do not establish truth of approval, semantic scope, Git-history preservation,
heading anchors, remote URLs, or whether an editorial edit changes a decision.
Those remain review responsibilities. No dependency package, service, skill,
network request, global setting or downstream distribution change was introduced.

The pilot's facts cite SPEC-006/007, their actual recorded merges and bootstrap
source. Alternatives/rationale are labeled present analysis. Earlier approvals
remain valid, but do not accept the ADR's new framing. Daniel owns its disposition
and resulting-change review. A decision reversal normally creates a successor,
not deletion of historical records. No fresh-client skill test applies to AGT-009.

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

ADR-0001 remains Proposed; Daniel's explicit disposition of the decision remains pending (T-005).
Merge approval does not turn an unrun check into a pass or authorize the previously
rejected fixture edits. The four new skills are now advertised in the app's
repository skill inventory; that observation does not prove fresh-client behavior.
The catalogue records Deployed while remaining acceptance stays explicit.
