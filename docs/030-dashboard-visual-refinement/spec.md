# SPEC-030: Dashboard visual refinement

- **Status:** Approved for implementation — work in progress
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Primary feature:** DSH-015
- **Design:** [TDD-030](technical-design.md) · **Tasks:** [TASKS-030](tasks.md)
- **Visual target:** [Reference brief and captures](reference.md)
- **Dependencies:** Delivered [inventory](../027-dashboard-project-inventory/spec.md), [live status](../028-dashboard-live-service-status/spec.md) and [links](../029-dashboard-project-links/spec.md)

## Outcome and authorization

Refine the private projects dashboard to follow the supplied design's compact,
aligned project table, restrained visual hierarchy and full-width expandable
panels. Replace oversized rows and crowded formatting with a readable overview
and clear project/service details.

The project owner requested this planning work October 12 and supplied
`Projects Dashboard redesign.html`, explicitly excluding unsupported features.
This authorizes the specification, design/tasks and a reviewable planning PR.
Implementation and necessary private rollout were subsequently authorized below. Prior delivered
DSH-001/002/003 approvals and acceptance remain intact.

The attached reference supersedes the unavailable artifact URL. It was inspected
and rendered offline. [reference.md](reference.md) records its provenance, observed
styles, stable captures and the exact supported/omitted mapping. The visual pattern
is the target; its mock services, controls and data are not product requirements.

## Scope

Include a slim header, neutral canvas, heading and managed-count tile, compact
semantic project table, restrained column headings, type/documentation/status/link
pills, full-width detail expansion, local typography/color/spacing tokens, overflow
handling and responsive/accessibility refinements for these elements.

Use the existing validated inventory, shared snapshot refresh, status/freshness and
destination contracts. All current fields remain accessible; secondary metadata
and unavailable-destination explanations may move into one labeled detail area.
Project identity, ordering, discovery, health semantics and URL policy stay intact.

Omit reference search/filter controls, rescan, extra aggregate status counters,
density settings, unsupported project adapters, simulated metrics, active demo
logs/previews and external design branding/runtime. Also exclude persistent history,
new navigation, lifecycle controls, telemetry, accounts, production and API/provider
changes. Keep DSH-012/013, TPL-008 and QLT-005 broader scope separate; this is a small
frontend refinement of the accepted dashboard.

## Requirements

### VIS-001 — Reference-derived shell and tokens

Adopt the reference's slim white header, compact GptClaw mark, inline Development
context and private-access label. Use the warm neutral canvas, centered content,
strong project heading and bordered managed-count tile described in reference.md.
A sticky header must not hide focused targets or the skip-link destination.

Use the recorded color/spacing/radius directions with verified contrast, existing
local system sans/monospace fonts, at least 14 px ordinary content and 12 px
supplemental text. Keep the reference's visual hierarchy without importing fonts,
packages, scripts, sample data or Claude branding. Omit unsupported controls
entirely rather than draw inert search/filter/rescan placeholders.

The managed tile uses the existing displayed inventory count. Loading is not zero,
a partial scan is not exhaustive, and a cached count is visibly last-known when
stale. No additional status-aggregation semantics are introduced.

### VIS-002 — Compact, complete project overview

Use desktop columns for project name/ID, type/components/manifest version,
recorded repository, runtime support, documentation presence, overall service
status/freshness, applicable destination pills and a disclosure control.
Move owner, relative location, full values and detailed explanations into the
project detail area where useful; retain every accepted inventory field.

At 1440 × 900, the heading, snapshot-state notice and at least six collapsed normal
synthetic projects fit without vertical scrolling. Target 72–88 px collapsed rows
for that fixture; long-value fixtures may grow instead of clipping. At 1280 px,
summary identity, status and primary links fit without horizontal scrolling.
Do not preserve the reference's fixed minimum widths if they cause overflow.

Use subdued headers/dividers, aligned cells, monospaced IDs and compact chips.
README/Index pills have accessible and visible Present/Missing/Unavailable meaning;
color alone and a hover tooltip are insufficient. Keep the explanation that
file presence does not assess documentation quality.

### VIS-003 — Full-width details with complete component information

An explicit chevron/button disclosure opens a detail row spanning the overview
width. Start with the reference's two bordered panels: project/service summary
and destinations. Add a full-width component-metrics region beneath them so the
existing web/API/DB detail contract is preserved rather than squeezed or removed.
Stack these regions on narrow screens. Do not introduce a drawer, modal or new route.

Preserve component-specific health/freshness, observed/last-success times,
operation-busy information, reasons, current-run uptime, container-instance restart
counts and first-observed/change-detected semantics. Zero remains measured zero;
missing counters/times remain unavailable with their reason. Status history is
limited to the existing in-memory observation semantics; no timeline is added.

Default rows collapsed. A user may open multiple projects. Preserve disclosure
state and focus across snapshot refreshes using the stable opaque row key; never
hardcode the reference's sample DB project or automatically open failed rows.
Enabled link clicks do not toggle the row. Keyboard users can open/close details
and reach all information and links in logical order.

### VIS-004 — Honest status and destination pills

Use the reference's compact pill treatment, adapting it to all existing states:
ready, stopped, starting, failed, degraded and unknown, plus independent
current/stale/unavailable freshness. Stale ready is visibly last-known rather
than a fresh green healthy claim. Missing/unsupported/conflicted/busy states and
per-component failures retain their text and fixed diagnostic reasons.
Runtime support remains a capability statement, separate from health.

Enabled destination pills are semantic links using the same validated URLs and
safe external-tab attributes. Short visual labels have complete accessible names.
Private/repository/public scope and full availability reasons remain available
in expanded destination rows within one labeled disclosure; they are not hover-only.
Unavailable destinations have no active anchor and no launch behavior.

Repository and owner come only from recorded platform metadata; do not infer them
from IDs or repository segments. Keep repository navigation independent of runtime
health and retain real link expiry/clock-skew protections. Logs and previews keep
existing capability gates/unavailable explanations, regardless of their enabled
state in the reference's synthetic examples.

### VIS-005 — Responsive, legible and accessible layout

Verify 1440, 1280, 768 and 390 px viewports and desktop 200% zoom. The document has
no horizontal overflow and text/reasons do not overlap or leave their surfaces.
On narrow screens use labeled stacked project summaries/details so primary
identity, state and destinations are reachable without dragging across the desktop
table. A component-comparison region may scroll internally if labeled and keyboard
accessible. Do not copy the reference's clipped mobile counters or minimum-width table.

Retain skip-link, headings, table/list semantics, visible focus and labeled
project/disclosure relationships. A row's visual click target is not a substitute
for a focusable disclosure button. Link activation and disclosure focus work
independently. Essential meaning cannot depend on color/icons/animation/hover.
Respect reduced-motion preferences and avoid motion on routine status updates.

Verify normal-text contrast at least 4.5:1, large text 3:1 and meaningful
control/focus boundaries 3:1; decorative light separators need not convey state.
Use at least 24 × 24 CSS px disclosure/link targets and 44 × 44 primary touch
targets on narrow screens, with adequate spacing. Long names/paths/URLs wrap or
truncate with their full value accessible in details. These are scoped dashboard
acceptance targets, not a platform-wide accessibility certification.

### VIS-006 — Preserve read-only behavior and failure presentation

Reuse the current snapshot, five-second browser refresh, elapsed-time aging and
rendering validation. Expanding a project does not start a polling loop, force a
scan or trigger observation/lifecycle work. No new write, history, telemetry,
logs, preview, search/filter or rescan endpoint is added.

Keep loading, empty, partial/truncated, stale, collector-loss/recovery, conflicting
and unsupported states useful in the new layout. Last-known rows stay labeled
when reads fail. Keep the private /dashboard/ route and existing host/origin/method
boundary, plain-text rendering and safe URL semantics. Frontend release/rollback
uses the reviewed owned dashboard lifecycle after implementation authorization;
this refinement changes no provider, socket protocol, Serve or infrastructure.

## Acceptance criteria

| ID | Observable result and evidence needed | Requirements |
|---|---|---|
| AC-001 | Side-by-side synthetic desktop captures show the reference-derived slim header, neutral surfaces, aligned compact table, small pills and two-panel full-width expansion. The documented font/mobile/component-detail adaptations are present; unsupported reference controls/data are absent. Owner visual comparison passes. | VIS-001/VIS-002/VIS-003 |
| AC-002 | A six-project valid-schema fixture meets the 1440 × 900 density target and 1280 px fit target. Long/missing/conflicting metadata remains readable; all inventory fields and full values are reachable. Count/docs labels remain honest for loading/partial/stale cases. | VIS-001/VIS-002/VIS-005 |
| AC-003 | Single web/API and web/API/DB fixtures expose all component fields, zero/unavailable counters and independent stale/busy/failure reasons. Details/focus survive refresh; enabled pills navigate safely without toggling disclosure; unavailable explanations and repository independence pass. | VIS-003/VIS-004 |
| AC-004 | Viewport/200%-zoom captures and bounds checks show no document overflow/clipped content; narrow layouts expose primary identity/status/links. Keyboard/skip/disclosure/focus, contrast measurements, touch-target spacing and reduced-motion checks pass. | VIS-005 |
| AC-005 | Loading, empty, partial/truncated, collector loss/recovery, unsupported/conflicted and malicious-name/URL fixtures preserve existing labels/security. All status/freshness/expiry/boundary/shared-read regressions pass. No search/filter/rescan, unsupported adapter, synthetic product datum, active fake logs/preview or history persistence is introduced. | VIS-004/VIS-006 |
| AC-006 | Relevant frontend tests, typecheck/build and applicable CI pass. After authorized private rollout, the owner confirms design, group details and destinations. Owned release rollback restores the prior dashboard without affecting projects/data/routes. Local, CI, deployed and owner evidence are recorded separately. | VIS-001–006 |

## Completion and ownership

The reference mapping and concrete adaptation are prepared for project-owner scope
review. Implementation/private rollout are authorized; the supplied HTML is a
visual reference, not an application to install. Completion requires authorized
implementation, all criteria, actual private browser acceptance and merged evidence.
Mark only DSH-015 Delivered then; preserve prior dashboard acceptance and create
acceptance.md when this redesign's verification evidence exists.

## Implementation authorization

The project owner instructed “implement the spec” on October 12. This approves
SPEC-030 and its documented supported-only adaptation and authorizes implementation
and necessary reversible private rollout/verification through the owned dashboard
release path. Review/merge and actual owner acceptance remain separate delivery gates.
