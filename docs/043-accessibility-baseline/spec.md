# SPEC-043 — Accessibility baseline (QLT-005)

- **Status:** Implementation authorized; review, merge and acceptance pending.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Feature:** QLT-005
- [Design](technical-design.md) · [Tasks](tasks.md)

## Outcome and scope

Supported generated web and mobile interfaces can be used with a keyboard and assistive
technology, communicate errors and state clearly, and include repeatable checks for
common accessibility regressions.

The proposed minimum includes semantic controls, meaningful names/roles/state,
programmatic labels and errors, visible focus, logical focus order and recovery,
keyboard operation without traps, and non-color-only status. Text contrast targets are
4.5:1 for ordinary text and 3:1 for large text; applicable control/focus contrast
targets are 3:1. Include 200% zoom, narrow layout, reduced motion and enlarged native
text. Automated success cannot replace manual assistive-technology evidence.

The project owner authorized implementation of QLT-001–QLT-010 and necessary
dependencies on 2026-10-21, with reasonable decisions delegated to the agent.
Pushing branches and opening PRs are authorized; merging and deployment are excluded. No infrastructure change, host installation, public exposure, production
operation, real-user dataset or automatic adoption is included.

## Observed baseline and dependencies

Dashboard and mobile initiatives contain scoped keyboard/native interaction evidence.
SPEC-036 is Android-owner-accepted with scoped manual-evidence waivers; those
waivers do not establish a platform-wide accessibility baseline. These records neither establish
a platform-wide baseline nor certify a generated product after its UI changes.

Coordinate UI conventions with TPL-008, use QLT-001/002 for automated gates and
QLT-004/009 for journey/template coverage. Applying the baseline to the dashboard is a
separate selected adoption task.

Source/previous-record evidence, not a new runtime verification:

- [docs/030-dashboard-visual-refinement/spec.md](../../docs/030-dashboard-visual-refinement/spec.md)
- [docs/031-expo-project-creation/spec.md](../../docs/031-expo-project-creation/spec.md)
- [docs/036-mobile-python-backend/spec.md](../../docs/036-mobile-python-backend/spec.md)
- [templates/apps/releases/expo-notes/1.0.0/src/components/Notebook.tsx](../../templates/apps/releases/expo-notes/1.0.0/src/components/Notebook.tsx)
- [templates/apps/releases/nextjs/1.0.0/app/counter.tsx](../../templates/apps/releases/nextjs/1.0.0/app/counter.tsx)

## Requirements

### QLT-005-R01 — Semantic interaction

Use semantic controls, accessible names/roles/states, labels and associated errors;
support keyboard-only completion and predictable focus through key journeys.

### QLT-005-R02 — Perceivable layouts

Meet the proposed contrast targets, preserve content/actions at 200% zoom and narrow
viewports, avoid color-only messages, and respect reduced motion and enlarged mobile
text.

### QLT-005-R03 — Automated gates

Ship pinned web/native accessibility checks in standard verification with no unexplained
suppressions; distinguish automated coverage from manual criteria.

### QLT-005-R04 — Assistive-technology evidence

Manually verify a selected web screen-reader/browser pair and Android TalkBack journeys;
claim iOS/VoiceOver coverage only when actually tested.

### QLT-005-R05 — Template and product boundaries

Publish accessible exact releases, explanatory guidance and a product adaptation
checklist; demo removal and retained routes remain governed by the adopting product
spec.

## Acceptance criteria

All criteria are pending; drafting does not establish implementation acceptance.

| ID | Observable result and required evidence | Requirements |
|---|---|---|
| QLT-005-AC01 | Manual keyboard and automated semantic checks complete each selected journey, including invalid input and modal/error recovery; injected unlabeled controls and focus traps fail. | QLT-005-R01 |
| QLT-005-AC02 | Measured normal/error/disabled/focus states meet applicable contrast targets; zoom, narrow-layout and large-text trials retain all actions; reduced-motion behavior is recorded. | QLT-005-R02 |
| QLT-005-AC03 | A clean starter passes; deliberately invalid labels/roles and a web contrast fixture fail the gate; exclusions require criterion, reason, owner and review date. | QLT-005-R03 |
| QLT-005-AC04 | Evidence names versions/device, steps and outcomes for navigation, readout, editing, errors and status; untested platforms remain pending and automated results are separate. | QLT-005-R04 |
| QLT-005-AC05 | Generated starters pass their applicable matrix; a changed product UI is rechecked against its own journeys; historical release hashes and unrelated product scope remain intact. | QLT-005-R05 |

## Decisions and completion

Use bundled pinned axe for web journeys, existing native semantic interaction tests, visible focus and reduced-motion conventions. Keep manual keyboard/assistive-technology/device acceptance distinct and pending until actually performed.

The project owner delegated reasonable implementation choices on 2026-10-21.
This scope is authorized for source changes, synthetic tests and PR publication;
merge and deployment are explicitly excluded.

Completion requires the mapped tests, applicable CI/runtime/client evidence, reviewed
implementation merge and project-owner acceptance. Record actual results in an
acceptance record at that time; do not mark the catalogue Delivered from a plan or a
passing subset. Preserve existing initiative approvals and evidence.