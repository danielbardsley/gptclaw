# SPEC-011 acceptance evidence

- Owner: Daniel. Evidence date: 2026-10-01.
- Status: implemented on feature branch; pilot remains Proposed.
- [Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- [Implementation PR #20](https://github.com/danielbardsley/gptclaw/pull/20).

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | pending | Template/guide and source-grounded Proposed pilot written; Daniel must disposition the exact pilot text. |
| AC-002 | passed (local) | 19 tests cover metadata, approval presence, retirement, editorial correction, full/partial/multi-hop supersession, later-deprecated successor and invalid graphs/IDs. |
| AC-003 | passed (local) | Shipped index/record links and structure validated; checker reads only decision documents, checks other target existence and executes no content/network requests. |
| AC-004 | passed | Independent reader identified scope, evidence, present rationale and implementation limits; no actionable issues. [Review](reader-review.json). |
| AC-005 | pending | Local checks pass; final repository/CI results, owner disposition and merge remain. |

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
