# TDD-011: Architecture Decision Records

- **Status:** Approved for implementation
- **Owner:** Daniel
- **Specification:** [SPEC-011](./spec.md)
- **Tasks:** [TASKS-011](./tasks.md)
- **Last updated:** 2026-10-01

## Design and files

Use ordinary Markdown with a small machine-readable metadata block and prose
sections. Proposed metadata uses JSON in a labeled fenced block, parsed by the
Python standard library; no YAML dependency or document database is introduced.
The authoring guide defines its fields and distinguishes metadata validation
from review of the decision itself.

| Proposed path | Purpose |
|---|---|
| `templates/decisions/ADR.md.template` | Inert outline and metadata example |
| `templates/decisions/README.md` | When to write, numbering, status transitions, approval, correction/supersession and rollback |
| `docs/decisions/README.md` | Index of IDs, titles, states and successor relationships |
| `docs/decisions/0001-repository-skill-distribution.md` | Pilot proposal grounded in SPEC-006/007 and their actual PRs |
| `scripts/tests/test_decision_records.py` | Focused metadata/link/relationship checks and synthetic lifecycle cases |
| Existing documentation index/checker/quality filters | Discover records and include relevant checks without changing deployment gates |

## Record contract

Metadata fields: id, title, status, owner, decision_date (nullable until decided),
approval_reference (nullable while Proposed), supersedes IDs, superseded_by IDs,
and replacement scope where applicable. Implemented metadata also includes
`retirement` (date, approval reference and reason) for Superseded/Deprecated
records, retaining original acceptance in decision_date/approval_reference. Include a separate recorded date for
retrospective records; do not backdate authorship to an earlier implementation.
The filename ID and index ID must agree. Scope and partial replacement remain
explicit prose even when links are structurally valid.

Accepted/Rejected/Deprecated transitions need an approval reference and date;
validation checks presence and shape, not whether a human actually approved.
A supersession operation adds the new record, updates relationships/index, and
preserves the old choice/rationale. The accepted successor need not be already
implemented; status describes decision authority, not deployed behavior.
For partial replacement, document remaining scope in the index and both records
so Superseded cannot be mistaken for total irrelevance.

## Checks and verification

Read only the active decision directory and synthetic fixtures. Validate unique
IDs, required metadata, enumerated statuses, file/index consistency, nonempty
core sections and local file targets. Traverse the supersession graph to reject
cycles/self-reference and require reciprocal links to an accepted successor.
Use current record states carefully when a successor is later itself superseded:
its historical acceptance must remain evidenced, allowing valid longer chains.
Do not require retired successors to remain in Accepted state forever.

Positive/negative fixtures exercise every lifecycle transition, a multi-hop
chain, partial replacement, duplicate IDs, missing targets, missing approval
metadata, and hostile command text that must remain inert. A separate reviewer
checks the pilot against actual sources and flags ungrounded rationale.

Rollout adds index/template/checks and one pilot only; no historical bulk rewrite.
Rollback uses a targeted reviewed revert of convention changes, preserving later
records. Reversing a decision normally uses a new ADR rather than deleting its
history. No service, migration, global setting or production access is involved.

| Requirement | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| ADR-001 | Concise prose outline and grounded pilot | T-002, T-003, T-005 | AC-001, AC-004 |
| ADR-002 | Stable metadata, index and graph checks | T-003, T-004 | AC-002 |
| ADR-003 | Decision/execution distinction and owner review | T-003, T-005 | AC-001, AC-004 |
| ADR-004 | Index integration and narrow offline checks | T-004–T-006 | AC-003–005 |
