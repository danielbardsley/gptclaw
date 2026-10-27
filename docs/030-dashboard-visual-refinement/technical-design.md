# TDD-030: Reference-derived dashboard presentation

- **Status:** Approved for implementation — work in progress
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-030](spec.md) · **Tasks:** [TASKS-030](tasks.md)
- **Reference:** [Observed design, captures and feature mapping](reference.md)

## Approach and boundaries

Refine the current Next.js/React frontend in `platform/dashboard/`. Reuse its typed
snapshot, refresh/elapsed-time handling, `lib/status.ts`, `lib/links.ts` and private
request boundary. No provider/collector, manifest, persistence, exposure or access
change is needed. Reuse the pinned package/toolchain/lockfile from package.json and
[dashboard operations](../../runbooks/manage-dashboard.md); add no UI/font/icon package.

The attached HTML provides a verified visual target. Its custom component runtime,
inline event machinery, mock DATA/ST maps, bundled fonts and watermark remain inert
reference material. Implement the documented supported adaptation in existing React;
do not install the bundle or translate its unsupported demo behavior into product code.

## Shell and overview

Use local CSS tokens corresponding to reference.md: warm canvas, white surfaces,
neutral dividers, indigo anchors and accessible green/amber/red/neutral state styles.
Use the existing system sans/monospace stacks. A roughly 56 px desktop header and
centered main content with a 1320 px outer maximum/28 px desktop padding reflect the
reference; adapt padding/header wrap at narrow widths. Use scroll margin for focused
anchors so sticky chrome does not obscure the skip-link target.

Arrange heading/intro and the existing managed count in a compact outlined tile.
Remove search/filter/rescan and extra status counter segments from the reference's
toolbar; fill the useful area with actual freshness and last-scan information.
Render clear loading, empty/partial/truncation, stale/outage and diagnostics regions
without fake current indicators or new interactions.

Use a semantic table with project/type/repository/runtime/status/destinations
and a disclosure column. Flexible column sizing must fit at 1280 px rather than
copy the reference's combined fixed minima. All normal rows start collapsed and
target 72–88 px height with approximately 16 px vertical padding, restrained text
and small chips. Let long-value rows grow. Shorten a validated repository for display
only; keep its full value in details and never infer an owner or URL from project ID.
Keep README/Index presence in the expanded details with explicit Present/Missing/Unavailable labels.

## Expanded presentation and interaction

A focusable project-specific disclosure button uses aria-expanded/aria-controls
and stable IDs derived from the opaque row key. An adjacent table detail row spans
the overview columns and contains the reference's two bordered panels:

1. Project/service summary: overall state/freshness, declared components, manifest,
   recorded owner, relative location, runtime support, documentation and full metadata.
2. Destinations: actual semantic anchors or unavailable text, with scope and fixed
   availability explanation. No dummy placeholders or enabled missing capabilities.

A full-width component region below the panels renders the existing web/API/DB
health, uptime/counter and observation/change fields. Use a semantic comparison
layout at desktop widths and stacked labeled component blocks on narrow screens.
This extension intentionally preserves metrics that the reference's simplified
summary omits. No drawer/modal, selection route or persisted disclosure settings.

Track open rows locally by opaque key; preserve them and keyboard focus on shared
snapshot refresh. Remove state only for rows absent from a complete inventory;
partial/stale retained rows keep their disclosure. Link clicks do not trigger the
row's expand handler. Prefer an explicit disclosure hit area rather than making
an unfocusable div a clickable row. No auto-expansion for a sample ID or failing state.

Keep all availability/freshness decisions in existing helpers. Solid indigo pills
are actual enabled links; unavailable pills are non-interactive and retain complete
accessible labels/explanations. Apply noopener/noreferrer to external tabs as today.
Decorative chevrons/dots can use small local inline SVG/CSS; icons do not replace text.

At 768 px and narrower, adapt the overview into labeled stacked summaries/details
while keeping one set of interactive controls and data. Primary status/destinations
must not become offscreen table columns. Keep semantic relationships appropriate
for the chosen responsive structure. Do not render duplicate invisible anchors or
read the API separately for desktop/mobile/details.

## Planned changes

| Current file / possible extraction | Responsibility | Requirements |
|---|---|---|
| `app/page.tsx`, local project-row/detail components as useful | Shell, count, snapshot notices, semantic compact overview and stable disclosure state | VIS-001/VIS-002/VIS-003/VIS-006 |
| `app/globals.css` | Reference tokens, flexible columns, pill/panel styling, responsive stack and focus/contrast | VIS-001/VIS-002/VIS-005 |
| `app/StatusPanel.tsx` | Full-width component comparison/stack preserving current status/metric semantics | VIS-003/VIS-004/VIS-005 |
| `app/ProjectLinks.tsx` | Real compact anchors and expanded scoped explanations, preserving render validation | VIS-003/VIS-004/VIS-006 |
| `scripts/tests/dashboard-browser.cjs` | Reference comparison, density/bounds and keyboard/refresh/semantic fixture checks | VIS-001–006 |
| Existing `tests/status.test.ts`, `tests/links.test.ts`, `tests/boundary.test.ts` | Retain accepted freshness/expiry/security checks; extend only for meaningful changed behavior | VIS-004/VIS-006 |

Component extraction names are implementation choices. Keep the patch small; this
is not a framework migration, backend feature or cross-project UI-library project.

## Verification and operation

Use deterministic valid schema 1–4 fixtures: six normal projects, a larger inventory,
long values, missing metadata/docs, conflicts, stopped/unsupported, partial/truncated,
collector outage/recovery and groups with zero/null counters and one stale component.
Do not use reference Worker/Static/queue examples as valid product data. Preview
expiry remains a synthetic capability fixture; no real viewer/registry is created.

Preserve meaningful semantic/security/freshness assertions while updating brittle
selectors when layout changes. Add bounds checks for document/primary content and
normal-row density, link-versus-disclosure behavior, preserved focus/open state,
contrast and reduced motion. Capture matching deterministic desktop viewports against
the committed reference; record deliberate missing-controls/font/metrics/mobile
adaptations. Screenshots supplement behavioral assertions and owner comparison.

Run container frontend `pnpm test`, `pnpm typecheck`, `pnpm build` and the existing
portable `scripts/tests/check_dashboard.py` HTTP/browser workflow, frozen install
only when needed. Run applicable repository/diff/link gates for the implementation
patch. This planning change needs documentation/image/link review only; no application
build, Terraform check or service action is needed to write these documents.

After explicit implementation/private-rollout authorization, use the reviewed
`scripts/manage_dashboard.py` release path and retain enabled status/link flags,
exact private origin, owned socket contract and resource limits. Verify the owner
browser comparison and existing group/destination behavior. Rollback selects the
previous owned immutable dashboard release; it never resets Serve, stops projects
or removes data. A frontend-only release anticipates no new privileged operator step;
existing integrity/ownership/refusal gates still apply.

## Traceability

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| VIS-001/VIS-002 | Verified reference tokens, shell, count and compact table | T-001/T-002/T-003/T-005 | AC-001/AC-002 |
| VIS-003 | Full-width two-panel expansion plus complete component region | T-003/T-004/T-005 | AC-001/AC-003 |
| VIS-004 | Reused state/link helpers and honest chip/pill labels | T-004/T-005 | AC-003/AC-005 |
| VIS-005 | Responsive semantic structure, bounds/focus/contrast checks | T-003/T-004/T-005 | AC-002/AC-004 |
| VIS-006 | Existing shared snapshot and private read boundary | T-003/T-004/T-005/T-006 | AC-005/AC-006 |

Implementation is authorized; verification, owner acceptance and review/merge remain. The visual
reference is resolved; unsupported design features are explicitly excluded.

## Implementation authorization

The project owner instructed “implement the spec” on October 12. This approves
SPEC-030 and its documented supported-only adaptation and authorizes implementation
and necessary reversible private rollout/verification through the owned dashboard
release path. Review/merge and actual owner acceptance remain separate delivery gates.
