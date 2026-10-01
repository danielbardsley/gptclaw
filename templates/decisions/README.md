# Architecture decision records

Write an ADR for a durable cross-feature choice or a material change in its
constraints. Routine fixes and local details usually belong in the feature
plans. Specs define outcomes; ADRs preserve why a choice was made. An accepted
ADR never authorizes implementation, infrastructure or release operations.

Copy [the inert outline](ADR.md.template) into `docs/decisions/` after checking
applicable guidance and Git status. Allocate one above the highest ID in both
the index and directory. Use `NNNN-kebab-case-name.md`; never reuse a retired
number or overwrite an occupied filename. Adapt the prose to the decision's
size; link supporting plans instead of duplicating them.

## Metadata and index

The single `adr-metadata` fence contains JSON, parsed with Python's standard
library. Required keys are `id` (four-digit string), `title`, `status`, `owner`,
`recorded_date`, `decision_date`, `approval_reference`, `supersedes`,
`superseded_by`, `replacement_scope`, and `retirement`.

Dates use YYYY-MM-DD. Record authorship separately from historical decision date;
do not backdate authorship. Proposed records have null decision date and approval
reference. Accepted/Rejected records require attributable owner evidence and a
decision date. For Superseded/Deprecated records those two fields retain the
original acceptance evidence; `retirement` adds its own date, approval reference
and reason. The checker verifies shape and links, not truth of owner approval.

Relationship lists contain IDs, not filenames. `replacement_scope` maps each
related ID to an object with `kind` (`full` or `partial`), `replaced` (scope text),
and `remaining` (nonempty for partial, null for full). Put the same scope object
in both related records. Describe its meaning in both records' Scope sections.
A proposed successor can discuss replacement in prose, but add active metadata
relationships only when its acceptance is recorded.

The index table uses columns ID, Title, Status, Supersedes, Superseded by, Scope.
ID is a relative Markdown link to the record. Lists use comma-space separated
IDs, or `—` when empty. Scope entries are sorted by related ID, separated by
` / `: `0002 (full: replaced text)` or
`0002 (partial: replaced text; remains: remaining text)`. With no relationship
use `—`. Keep metadata/index single-line values free of `|` table separators.

## Lifecycle and review

- Proposed → Accepted or Rejected: record the owner's actual decision evidence.
  A merged proposal alone is not acceptance. Retain rejected records in the index.
- Accepted editorial correction: make a reviewed, limited diff preserving its
  identity, acceptance and rationale. A materially different choice needs a new ADR.
- Accepted → Superseded: accept the successor, add reciprocal relationships and
  scope to both records/index, and record retirement evidence. Partial replacement
  must identify what remains applicable; Superseded does not mean wholly irrelevant.
- Accepted → Deprecated: record retirement date, owner approval and why it no
  longer governs without a replacement. Keep original acceptance evidence.
- A successor can later itself be Superseded or Deprecated; preserve its acceptance
  history so multi-hop chains remain valid. Never create self-links, cycles or
  relationships to missing/unaccepted records.

Review historical statements against sources. Label newly reconstructed rationale
as a present proposal; unknown historical reasoning remains unknown. A change in
status proves neither deployed behavior nor implementation of a successor.
Reference follow-up initiatives or name the owner/next action without granting
new authority. Preserve conflicting guidance for review rather than deleting it.

Run `python3 -B scripts/tests/test_decision_records.py` from the repository root,
plus relevant repository checks. These narrow offline checks read decision records
and validate local link targets without executing document content or fetching
URLs. Human review must verify semantic scope, actual approval provenance and
whether editorial changes have silently altered a decision. CI includes decision
and template paths; protected deployment gates remain unchanged.

Use normal PR review. Reverting the convention must preserve later records;
reversing a decision normally requires a new ADR rather than deleting history.
