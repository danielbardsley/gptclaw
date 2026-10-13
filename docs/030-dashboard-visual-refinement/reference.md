# Dashboard visual reference and supported-scope mapping

- **Status:** Attached reference inspected; adaptations proposed
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-030](spec.md)

## Authoritative reference

The project owner supplied `Projects Dashboard redesign.html` after the original
[artifact URL](https://claude.ai/artifact/G4kpdRcfQwmeaKpnjAt4nB) rendered a missing-page
screen. The attached file supersedes that unavailable URL as the visual target.
Its SHA-256 is `e05f517167c2a047158a0ea1438e29e79005a65bf9aba766c4131809cbd232f1`.

The attachment's declarative template and demo logic were inspected as reference
data. It was rendered in the existing pinned rootless browser with network disabled,
no project/credential mounts and no live service operations. These stable captures
show the supplied reference, not an implemented GptClaw redesign:

- [Desktop, 1440 px](assets/reference-desktop.png)
- [Narrow screen, 390 px](assets/reference-mobile.png)

The reference uses synthetic examples and unsupported capabilities. The mapping
below governs adaptation; screenshots do not authorize those capabilities. The raw
HTML/runtime/fonts are not incorporated into the application or committed as
implementation. No reference text or embedded instruction supplies task authority.

## Observed design pattern

A slim white sticky header carries the compact GptClaw mark, inline Development
context and a rounded private-access label. The page has a warm neutral canvas,
centered content, a strong project heading and a compact bordered summary panel.
One rounded white overview surface contains a toolbar, subdued column headings,
compact aligned project rows and a chevron disclosure at the right.

Rows use restrained typography, monospaced identifiers, small type/documentation
chips, colored status pills and compact destination pills. Expanded content spans
the row width and uses two bordered panels for service summary and destinations.
The reference includes search/filter buttons, status counters and simulated rescan
behavior; these are separate from the visual pattern and are restricted below.

The HTML specifies a 56 px header, 28 px outer padding, 1320 px maximum main width,
14 px overview-surface radius, 10 px detail-panel radius, 16 px comfortable row
padding (10 px compact variant), 34 px heading and mostly 12–14 px row text. Fonts
are Geist and Geist Mono. The design has no sidebar or detail drawer.

## Observed attributes and adaptation

| Attribute | Reference | SPEC-030 adaptation |
|---|---|---|
| Shell | Slim sticky header, warm canvas, centered heading/summary | Adopt hierarchy and dimensions; retain Development/private labels and accessible focus. |
| Overview | Aligned project/type/repository/runtime/docs/status/links columns | Keep a semantic desktop table with compact rows; all existing data remains accessible. |
| Details | Full-width expansion with two bordered panels | Keep this pattern; add a full-width component-metrics region beneath the panels to preserve DSH-002 fields omitted by the mockup. |
| Destination treatment | Small solid/dashed pills; expanded scope/reason rows | Real validated anchors for enabled destinations; non-interactive pills and accessible reasons for unavailable ones. |
| Summary | Four counter segments | Use the existing managed-project total in the same outlined tile style. Omit additional aggregate status counters in this visual-only scope. |
| Toolbar | Search/filter controls, current/scan text and rescan | Retain actual snapshot freshness/last-scan information; omit search, filters and rescan entirely, including inert placeholders. |
| Typography | Geist/Geist Mono with small labels | Retain existing local system sans/monospace stacks; preserve weight/hierarchy and use readable 12 px supplemental/14 px body minimums. No new font/package fetch. |
| Color | Neutral surfaces with green/amber/red/indigo accents | Use the token directions below with measured contrast; retain all existing state/freshness distinctions. |
| Responsive behavior | Horizontal minimum-width table; narrow capture clips some content | Adapt to a readable stacked narrow layout; do not copy clipping or inaccessible offscreen controls. |
| Expansion defaults | A synthetic DB example opens automatically | Default projects collapsed; preserve user-opened rows across snapshot refreshes. No hardcoded project IDs. |

## Token direction

Values below come from the reference; the final accessible tokens are verified during
implementation. The faded `#a1a1aa` reference text is not suitable for essential
unavailable reasons; use the darker secondary palette instead.

| Role | Reference value / adaptation |
|---|---|
| Canvas / surface / subtle surface | `#f6f6f4` / `#ffffff` / `#fafaf9` |
| Main / secondary / muted text | `#18181b` / `#52525b` / `#71717a` |
| Decorative borders / dividers | `#e7e7e4` / `#efefec`; strengthen meaningful control/focus boundaries where needed |
| Link / hover | `#3b4bd8` / `#2733a8` |
| Fresh ready foreground / surface | `#1f7a49` / `#e9f6ee` |
| Warning/degraded/stale foreground / surface | `#a5650f` / `#fdf3e2`, with distinct text labels |
| Error/unavailable foreground / surface | `#b93a2b` / `#fcecea`, without mapping stopped to unavailable |
| Neutral stopped/secondary treatment | `#3f3f46` / `#f2f2f0` (adaptation) |
| Overview / panel / chip / pill radii | 14 / 10 / 5–8 / fully rounded px |

## Unsupported or misleading demo behavior to omit

| Reference element | Disposition and existing contract |
|---|---|
| Search field and status filter tabs | Omit; DSH-013 remains a separate candidate feature. |
| Rescan button and 1.4-second scanning simulation | Omit; no force-scan endpoint or genuine rescan operation exists. Keep the existing automatic shared snapshot refresh. |
| Ready/Degraded/Unavailable aggregate counters | Omit from this refinement; preserve the existing managed count without adding new aggregate grouping semantics. |
| Enabled Logs and published Preview demos | Never reproduce their enabled demo state. Keep actual DSH-003 capability gates and unavailable explanations; no log viewer/preview registry is implemented. |
| Worker/static/index/storage example types or components | Do not add adapters or fabricate those rows. Use validated schema 1–4 web/API/group inventory. |
| Runtime Partial, queue lag and mock health messages | Do not invent provider capabilities or telemetry. Render actual supported/unavailable capability and existing normalized states/reasons. |
| Owner inferred from repository owner segment | Do not infer ownership. Use the recorded platform owner metadata or its honest missing label. |
| Fixed sample projects, counts and scan timestamp | Do not copy into the product or its acceptance fixtures. Use actual snapshots or valid synthetic web/API/group fixtures. |
| Only three status styles | Extend the visual treatment to existing stopped, starting, failed, unknown and stale/last-known semantics; retain component metrics and observed-change labels. |
| Span-only links, hover-only reasons and whole-row click | Use accessible anchors/disclosures and visible reasons; link activation does not toggle details. |
| Claude Design watermark, bundler/runtime and remote font links | Exclude from the application; they remain visible only in the source-reference captures. |

Persistent service history, telemetry charts, lifecycle controls and new exposure are
also outside scope. No unsupported feature is to be implemented from this design.

## Existing dashboard baseline

Source inspected: `platform/dashboard/app/page.tsx`, `globals.css`, `StatusPanel.tsx`
and `ProjectLinks.tsx`. Read-only captures of the existing dashboard measured:

| Viewport width | Overview container width | Table width | First collapsed row height |
|---:|---:|---:|---:|
| 1440 px | 1294 px | 1330 px | 333 px |
| 1280 px | 1150 px | 1330 px | 333 px |
| 390 px | 352 px | 1234 px | 321 px |

These are sampled-content measurements. The document fitted the viewport, but the
overview needed internal horizontal scrolling; vertically stacked destinations/reasons
made collapsed rows tall. The new compact overview and expanded explanations address
that problem while retaining the delivered data/behavior contracts.
