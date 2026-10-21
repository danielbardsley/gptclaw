# QLT-005 acceptance evidence

Status: implemented and merged; task records closed by project-owner direction; remaining acceptance criteria retain their recorded states.
Owner: Project owner. Evidence date: 2026-10-21 UTC.
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
[Implementation PR](https://github.com/danielbardsley/gptclaw/pull/95) · [Shared verification record](../039-standard-quality-commands/verification-2026-10-21.json)

Tested application code: `4f7d934788f757fbd241012a9ff9b0a3037ca396`.
Credential fixture correction: `0627380d52cef1f99e9f27805e5d2c8c354dea37`.
Generated cache keys and expanded negative tests were corrected at
`3c29d3905536743483fae19ff6ee6d346fd3bdbc`; final CI is linked in the PR.
PR #95 merged on 2026-10-21 as `d0d69cc1077bddb6db10501922b5b539efd1bbf1`. All five
CI workflows passed at the reviewed implementation head. The project owner then
requested all tasks be marked complete; this is recorded as task closure.
A pending criterion can contain passing automated checks; its full original result
has not been demonstrated. Existing pending states below are preserved.

## Criterion mapping

| Criterion | State | Evidence or limitation | Remaining action and owner |
|---|---|---|---|
| QLT-005-AC01 | pending | Automated real-browser keyboard/focus and semantic checks pass selected web journeys. Manual keyboard, modal/error focus-trap and physical native interaction trials remain pending. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-005-AC02 | pending | Axe, narrow layout, enlarged text and reduced-motion checks pass web releases; focus/motion CSS is improved. Full manual contrast-state, zoom and native dynamic-text acceptance remains pending. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-005-AC03 | pending | Pinned axe-core and existing native semantic tests run in verify. Dedicated web label/contrast fault and exemption record trial remain pending; no exemption bypass is implemented. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-005-AC04 | pending | No physical TalkBack/VoiceOver or human assistive-technology session was performed. Existing SPEC-036 Android owner acceptance has scoped waivers and is not transferred to this generic baseline. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-005-AC05 | passed | All selected starter source/browser gates pass in eight new releases; historical hashes are preserved and adoption requires product-specific journey review. | Project owner reviews evidence. |

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
public exposure, tag or deployment was performed. The implementation PR has merged. Existing products and
SPEC-036 owner evidence retain their own acceptance boundaries. Templates are
reusable intentional fixtures; adopting products must review/remove demo content
and recheck their actual API/UI/journeys under their own specification.

Remaining acceptance layers above are explicit. No expired exception/quarantine
can authorize a pass: this implementation provides no exception bypass. Historical
release bytes are retained. Rollback/adoption procedure is in the
[quality runbook](../../runbooks/manage-project-quality.md). The project owner authorized merge and all task closure on 2026-10-21.
Catalogue state is Implemented; full acceptance remains governed by the table above.
