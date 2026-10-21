# QLT-004 acceptance evidence

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
| QLT-004-AC01 | pending | Ten focused source smoke tests pass for identity/port/origin/source guards. Isolated application browser probes pass. Installed managed ingress/private-client acceptance remains pending; provider not installed. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-004-AC02 | passed | Owned web/API/group isolated probes pass assets, declared readiness, documentation prefix and useful journeys; wrong asset/source/content and redirect fault tests fail. | Project owner reviews evidence. |
| QLT-004-AC03 | pending | Source/activation stability, bounded observer, transient retry, quiet unchanged state and failed exit status are tested. A real two-update managed runtime race remains pending. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |
| QLT-004-AC04 | not applicable | Selected smoke profile is strictly read-only. Write probes and cleanup of application records are not enabled; DB mutation tests use separate disposable integration fixtures. | No action unless a write profile is separately selected. |
| QLT-004-AC05 | pending | Reports identify generated-container versus local/CI vantage; native devices remain pending. An independent private-client report is intentionally absent. | Project owner selects the remaining adoption/manual trial after review; automated follow-up stays tracked here. |

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
