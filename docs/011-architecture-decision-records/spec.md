# SPEC-011: Architecture Decision Records

- **Status:** Implementation reviewed and merged; final acceptance pending
- **Owner:** Daniel
- **Feature:** AGT-009
- **Design:** [TDD-011](./technical-design.md)
- **Tasks:** [TASKS-011](./tasks.md)
- **Architecture:** [Platform architecture](../platform/architecture.md), section 8.3
- **Last updated:** 2026-10-01

Daniel approved these specifications and authorized sequential implementation in
one feature branch on 2026-09-30. This does not authorize runtime operations,
product releases, or acceptance of the unwritten pilot ADR.

## Outcome

Preserve the context, alternatives, rationale, consequences and supersession of
important cross-cutting decisions beyond an individual feature or conversation.
A future contributor can find which decision applies, why it was chosen, and
what replaced it without inferring approval from implementation alone.

## Scope and independence

Include an ADR template, a concise authoring/lifecycle guide, a GptClaw decision
index and one reviewed pilot record, plus focused link/lifecycle checks. This
is a document convention; no skill, database or ADR-generation service is needed
for the first release. Keep numbering independent of initiative numbers.

Use ADRs for durable cross-feature choices or materially changed constraints;
do not require one for every library, local implementation detail, routine fix,
or feature specification. Specs define outcomes and acceptance; ADRs explain
choices. Never use an ADR to bypass feature scope or operational approval.

Exclude bulk conversion of historical conversations, automatic decision mining,
rewriting accepted history, retroactive invented approvals, and implementing the
pilot decision's downstream consequences. No dependency on AGT-006/007/008/010;
existing Markdown, Git, PRs and architecture references suffice.

## Proposed defaults and pilot decision

Inert template/guide: `templates/decisions/ADR.md.template` and README.md.
Active records: `docs/decisions/NNNN-kebab-case-name.md`, with README.md index.
Allocate one greater than the highest used number in index or directory; never
reuse an ID. Each record has owner, date, status, scope, source/approval evidence,
context, alternatives, decision, consequences, and applicable related links.

Statuses: Proposed, Accepted, Rejected, Superseded, Deprecated. Acceptance
requires identified owner approval, not simply a merged document. Rejected
proposals remain discoverable. Deprecated means no longer governing without a
replacement; Superseded names an accepted successor with a reciprocal link.

Pilot proposal: document the repository-scoped, pinned-copy skill-distribution
choice used by SPEC-006/007, with alternatives such as a globally installed
shared skill. Existing specs/merged PRs are evidence of the concrete past scope;
Daniel reviews the ADR's exact framing before it becomes Accepted. Do not infer
that every future skill must be copied or global installation is permanently
forbidden. This feature does not change AGT-005's distribution behavior.

## Requirements

### ADR-001: Useful and proportionate records

State the decision question, scope, constraints, credible alternatives and
tradeoffs, selected/proposed choice, consequences and conditions for revisit.
Reference underlying specs/evidence without duplicating their requirements.
Distinguish historical facts from new rationale or proposals; unknown historical
reasoning remains unknown. A short decision should remain a short record.

### ADR-002: Stable identity and lifecycle

Use unique stable IDs and an index showing current status and relationships.
Refuse numbering collisions and preserve existing records. Transition Proposed
to Accepted or Rejected only with attributable owner evidence. Accepted records
may receive editorial corrections with review; materially different decisions
require a new record rather than silently rewriting the old rationale.

Superseding requires a successor with recorded acceptance (even if later
superseded itself), reciprocal links, and explicit scope: partial replacement must state which parts remain applicable. Reject
self-links, cycles, missing successors, and duplicate IDs. Deprecation records
why/when and who approved it; it does not imply a replacement was implemented.

### ADR-003: Separate decisions from execution

A recorded decision does not change infrastructure, permissions, application
behavior, or approval history. Link follow-up implementation initiatives where
known, otherwise identify the owner/next action. Do not claim implementation or
acceptance from ADR status. Preserve prior approved scope and resolve conflicts
through review, without automatically removing contradictory guidance.

### ADR-004: Discovery and reviewable maintenance

Link the decision index from the documentation index. Make current and retired
records easy to trace from relevant specs. Check structure, local references,
identity and lifecycle relationships with offline standard-library tooling;
semantic validity and approval provenance remain human review responsibilities.
Keep records non-secret and self-contained within the repository. Changes use
normal review, preserve unrelated work, and record actual verification.

## Acceptance

| ID | Observable evidence | Requirements |
|---|---|---|
| AC-001 | Reviewed template/guide and pilot clearly separate facts, alternatives, proposal/decision, consequences, implementation follow-up and actual approval evidence. | ADR-001, ADR-003 |
| AC-002 | Synthetic lifecycle cases cover acceptance/rejection, editorial correction, complete/partial supersession and deprecation while preserving IDs/history; invalid duplicate/cyclic/missing relationships are detected. | ADR-002 |
| AC-003 | Index and pilot local links resolve, current/retired records are discoverable, and narrow checks run without network or executing document content. | ADR-004 |
| AC-004 | A reviewer given the pilot and linked project sources can identify the decision's scope, source evidence, alternatives, applicability, and remaining implementation limits without original chat history. | ADR-001–004 |
| AC-005 | Actual tests/CI, resulting review, pilot approval status, merged PR and maintenance limitations are recorded before catalogue completion. | ADR-001–004 |

## Completion

Daniel owns the GptClaw convention and pilot review. The pilot can remain
Proposed while its exact framing is reviewed, but AC-001/005 require the final
owner disposition to be explicit before Delivered. No fresh-client skill loading
is required: this feature ships documents and checks, not active instructions.
