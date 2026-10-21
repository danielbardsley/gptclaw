# QLT-010 acceptance evidence

Status: in review; automated implementation evidence recorded; full acceptance pending.
Owner: Project owner. Evidence date: 2026-10-21 UTC.
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
[Implementation PR](https://github.com/danielbardsley/gptclaw/pull/95) · [Shared verification record](../039-standard-quality-commands/verification-2026-10-21.json)

Tested application code: `4f7d934788f757fbd241012a9ff9b0a3037ca396`.
Credential fixture correction: `0627380d52cef1f99e9f27805e5d2c8c354dea37`.
Generated cache keys and expanded negative tests were corrected at
`3c29d3905536743483fae19ff6ee6d346fd3bdbc`; final CI is linked in the PR.
A pending criterion can contain passing automated checks; its full original result
has not been demonstrated. Neither this file nor the PR declares owner acceptance.

## Criterion mapping

| Criterion | State | Evidence or limitation | Remaining action and owner |
|---|---|---|---|
| QLT-010-AC01 | passed | Real synthetic Git range tests validate immutable commits and reject malformed/missing commits, reversed/empty ranges, out-of-range/duplicate claims and absent evidence without changing HEAD or tags. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-010-AC02 | passed | Accepted target-revision Markdown evidence is required; pending changes are excluded and leave a pending draft. The marker does not imply owner acceptance of generated prose. | Project owner reviews evidence. |
| QLT-010-AC03 | pending | Category formatting covers added/fixed/compatibility-migration/limitations with evidence links. Project-owner review of a selected product sample remains pending. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-010-AC04 | passed | Real Git/CLI tests reject credential/private-origin and executable-Markdown canaries; repeated generation is identical and a manually edited draft is preserved with a failed rerun. Source content is handled as data. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-010-AC05 | pending | Tool creates drafts only and performs no release/tag/push/merge operations; synthetic Git test leaves HEAD/tags unchanged. Human reviewed draft and correction scenario remain pending. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |

## Verification and delivery

The full local repository gate passed 927 Python tests across 48 suites, plus
repository invariants and isolated shell fixtures (exit status 0).
The shared record contains each executed local cell's digest, source/toolchain,
quality outcomes, injected-fault outcomes and performance measurements, plus the
five-start calibration. CI matrix run 39561024843 passed metadata and all eight
exact committed releases using Docker. Local cells used rootless Podman and
synthetic, task-owned fixtures. See the shared snapshot for exact commands and matrix evidence; the linked PR
review notes record the final full repository/CI outcome. Source bundles are not physical native acceptance.

No managed provider installation, retained-data migration, production operation,
public exposure, merge, tag or deployment was performed. Existing products and
SPEC-036 owner evidence retain their own acceptance boundaries. Templates are
reusable intentional fixtures; adopting products must review/remove demo content
and recheck their actual API/UI/journeys under their own specification.

Remaining acceptance layers above are explicit. No expired exception/quarantine
can authorize a pass: this implementation provides no exception bypass. Historical
release bytes are retained. Rollback/adoption procedure is in the
[quality runbook](../../runbooks/manage-project-quality.md). The project owner
reviews the draft PR in the morning; catalogue state stays In review.
