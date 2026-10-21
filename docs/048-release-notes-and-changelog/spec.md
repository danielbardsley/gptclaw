# SPEC-048 — Release notes and changelog (QLT-010)

- **Status:** Draft for review; optional capability, not selected for delivery.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-010
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

An application with a selected accepted release workflow can prepare accurate, reviewed
human-facing release notes from accepted changes, preserving provenance and clearly
describing compatibility and migration impacts.

Use an explicit previous accepted release and immutable target revision. Include
accepted user-visible changes and known issues, linked to evidence. Exclude
unmerged/unaccepted work and operational secrets. Missing or contradictory acceptance is
flagged for review; no generated narrative can invent delivery. Organize useful changes
into additions, fixes, compatibility/migration and known limitations without requiring
empty headings.

This request authorizes drafting the specification, design and tasks. Specification
approval, implementation authorization, PR review/merge, rollout and acceptance remain
separate. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

The catalogue marks QLT-010 Optional. SPEC-009 supplies a release-promotion skill but
does not establish a production pipeline or a selected product release audience. Git
history and initiative acceptance are evidence inputs, not automatic authority to
publish releases.

Opt-in only after a product has an accepted release workflow, audience and version
policy. Use its actual acceptance/PR evidence and QLT-008/007 compatibility/migration
results where relevant. This initiative does not require production infrastructure.

Source/previous-record evidence, not a new runtime verification:

- [docs/009-release-promotion-skill/spec.md](../../docs/009-release-promotion-skill/spec.md)
- [.agents/skills/gptclaw-release-promotion/SKILL.md](../../.agents/skills/gptclaw-release-promotion/SKILL.md)
- [docs/platform/sequence.md](../../docs/platform/sequence.md)
- [docs/platform/features.md](../../docs/platform/features.md)

## Requirements

### QLT-010-R01 — Explicit release range

Require selected product/version/audience and immutable previous accepted release plus
target revision; reject ambiguous or reversed ranges and retain exact source references.

### QLT-010-R02 — Accepted changes only

Include user-facing changes supported by accepted release evidence; identify
missing/contradictory evidence and exclude drafts, unrelated internal noise and
unaccepted claims.

### QLT-010-R03 — Useful reader content

Summarize additions/fixes, breaking behavior, migration/recovery instructions and known
limitations relevant to the audience with evidence links and no invented impact.

### QLT-010-R04 — Safe drafts

Produce editable Markdown and a changelog proposal without secrets, private origins, raw
logs or uncontrolled embedded instructions; repeated generation is idempotent for
unchanged reviewed inputs.

### QLT-010-R05 — Human review and publication boundary

Require owner review before notes become accepted release documentation; generation
cannot tag, merge, promote or publish. Record corrections and retain previous release
history.

## Acceptance criteria

All criteria are pending; drafting does not establish implementation acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-010-AC01 | A valid fixture resolves a stable change set; missing baseline, wrong repository, changed target and reversed range fail clearly without publishing anything. | QLT-010-R01 |
| QLT-010-AC02 | Synthetic accepted/unaccepted/mixed PR fixtures yield only justified claims; missing evidence is visibly flagged and cannot produce a ready-for-publication status. | QLT-010-R02 |
| QLT-010-AC03 | An owner-reviewed sample correctly describes a breaking contract, migration prerequisite and known limitation; each factual change maps to an accepted reference. | QLT-010-R03 |
| QLT-010-AC04 | Canary credentials/private origins and prompt-like source text are excluded or safely quoted; reruns create no duplicate entries and preserve manual edits by proposing a diff. | QLT-010-R04 |
| QLT-010-AC05 | A dry run has no repository/release mutation; a reviewed draft records version/revision/evidence; a correction scenario preserves the original release identity and history. | QLT-010-R05 |

## Decisions and completion

Project owner selects a product, audience, accepted baseline/target and publication
destination before enabling this optional capability. Proposed initial output is a local
Markdown/PR draft; automatic publishing, tagging and promotion are excluded.

This is a proposed default, not a recorded owner decision. The project owner reviews the
open decision before dependent implementation; source discovery and planning review can
proceed meanwhile. Implementation should recheck current source versions, supported
templates and applicable guidance rather than assume this snapshot establishes installed
capability.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.