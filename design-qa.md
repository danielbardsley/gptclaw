# Dashboard dark mode design QA

final result: passed

Source visual truth: supplied `Projects Dashboard redesign.zip`, latest
`Projects Dashboard v3.dc.html`, rendered offline as
`.dashboard-qa/dark-mode/reference-dark.png` (1440 × 2077 pixels).
Implementation: `.dashboard-qa/dark-mode/dashboard-dark-1440.png` (1440 × 1991)
and `dashboard-confirm-dark.png` (1440 × 1818); mobile:
`dashboard-dark-390.png` (390 × 4478) and `dashboard-confirm-dark-mobile.png`
(390 × 3451) in the same directory.

## Comparison and findings

Opened both reference and implementation and inspected the combined
`comparison-desktop.png` (2880 × 1000) plus focused `comparison-header.png`
(800 × 250). Browser CSS viewports are 1440 × 1000 for source, 1440 × 900
for implementation overview and 1440 × 1000 for confirmation; device density
is 1. Composite crops retain 1:1 pixels; viewer downscaling is not a CSS change.
State: dark theme, expanded service details; synthetic content differs.
This comparison assesses the requested theme adaptation, not a redesign or a
claim that the existing dashboard reproduces every mock feature.

No actionable P0/P1/P2 theme discrepancies remain.

- Fonts/typography: existing local system sans/mono stacks, sizes and hierarchy
  retained as required by SPEC-030. No reference font/CDN dependency added.
- Spacing/layout: existing table, expanded lifecycle/details and responsive
  stacking preserved. Header places the supplied theme control beside private
  access. Desktop target 32 px; narrow target 44 px. Existing mock toolbar and
  extra counters remain excluded. Mobile source's fixed-width table is deliberately
  adapted to the dashboard's existing stacked summaries.
- Colors/tokens: charcoal canvas `#0d0e11`, paper `#15171c`, subtle surface
  `#1a1c22`, foreground `#ecedee`, indigo links `#8f9bff`, and green/amber/red
  status families match the latest source. Muted text is intentionally brighter
  for contrast. Status/link/metadata/toggle/logo text and both confirmation hover
  states passed measured 4.5:1 contrast checks. Confirmation foreground uses a
  dark ink on bright red; logo uses paper ink on its inverted background.
- Images/assets: supplied sun/moon vectors reused; existing logo and component
  assets retained. No generated imagery or external runtime added. Existing QR
  rendering remains untouched and independent decoding passes.
- Copy/content: existing honest freshness, capability, disabled-state and
  confirmation explanations preserved. Accessible toggle name is stable; its
  title describes the next action and pressed state exposes dark mode.

## Interaction evidence

The isolated browser assertions passed toggle/pressed state, reload persistence,
explicit light over dark OS, system changes without a saved choice, cross-tab
updates, denied-storage session choice, retained row disclosure/focus through
snapshot polling, and all existing status/link/control regressions. Dark bounds
checks passed 1440/1280/768/390/720 CSS px, including narrow 44 px target checks.
Existing keyboard skip/disclosure, reduced-motion and 200% equivalent reflow
checks passed. A separate successful production-build smoke verified Space/Enter
theme activation, retained focus and correct theme at DOM ready, including a
saved light preference overriding a dark system; its runner exited 0 and removed
its task-owned loopback container. Main-page uncaught error list was empty; expected synthetic HTTP
failure scenarios remain part of the regression suite. This is local browser
acceptance, not installed-dashboard or project-owner acceptance.

Comparison history: first visual comparison found no new P0/P1/P2 issue. Logo
inversion and confirmation foreground were adapted during implementation before
capture. The multi-tab test setup needed an explicit browser context; after that
correction all browser assertions passed. The surrounding Python runner was
terminated with signal 15 after those PASS lines, before cleanup completed; its
owned container was independently verified and removed. No passing end-to-end
runner exit is claimed.

## Implementation checklist

- [x] Apply complete dark surface, text, border, semantic and control tokens.
- [x] Add pre-paint theme selection and persistent accessible header toggle.
- [x] Compare source and rendered implementation together and inspect header detail.
- [x] Verify desktop/narrow bounds, storage/system behavior and contrast.

Follow-up polish: none required for this scoped theme change.
