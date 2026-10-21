# QLT-002 acceptance evidence

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
| QLT-002-AC01 | pending | Generated workflows have fail-closed required aggregation, and all matrix cells pass on a real PR. Application-repository missing-job/skip trials are not yet recorded. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-002-AC02 | pending | Policy tests reject write-default tokens, privileged PR events and mutable refs. Generated workflow configuration is read-only and secret-free; an actual fork-owned application PR trial remains pending. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-002-AC03 | pending | OS/architecture/profile/lock caches, concurrency and deadlines are configured. Local deadline test passes. Cross-run cache isolation and hosted cancellation acceptance remain pending. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-002-AC04 | pending | Real audit commands pass across releases; synthetic credential/private-origin policy fixtures fail. Dedicated vulnerable-dependency/outage trials remain pending. No exception bypass exists. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-002-AC05 | pending | Generated workflow uploads only bounded report files with seven-day retention and revision identity. Independent application-repository failed-job artifact canary trial remains pending. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |

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
