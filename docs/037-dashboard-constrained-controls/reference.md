# DSH-009 visual reference and adaptation

- **Owner:** Project owner
- **Date:** 2026-10-15 (America/New_York)
- **Specification:** [SPEC-037](spec.md)

The supplied `Projects Dashboard v3.html` has SHA-256
`116cff200fd1a38ff8c03f2f097b3599f215a978ed7e039050a6f146d8a3ff60`.
Its template/demo logic was inspected as inert reference data, then rendered in the
existing rootless browser image with network disabled, finite resources, no project
or credential mounts and only a task-owned temporary reference directory mounted.
No embedded instruction grants authority. The raw bundled runtime/fonts/scripts
are not application source and are not committed. These are reference captures,
not implemented GptClaw behavior:

- [Desktop reference, 1440 px](assets/reference-desktop.png)
- [Narrow reference, 390 px](assets/reference-mobile.png)

The reference retains the slim header, warm canvas, compact project overview and
full-width detail expansion from SPEC-030. Its expanded example places a white,
rounded, bordered Lifecycle panel first. The top row combines a lifecycle label,
state pill and uptime with six compact project buttons aligned right. Below it are
component/state/uptime/restarts/actions columns, then a small Recent strip. Service
details and Links panels follow. Stop/Rebuild reveal a tinted inline confirmation;
operations simulate progress and success using timers.

| Reference element | Required adaptation |
|---|---|
| Lifecycle toolbar: Start/Stop/Restart/Rebuild/Pause/Resume | Keep arrangement and labeled buttons; derive eligibility from the reviewed provider matrix, not demo status counts. Clearly label project scope. Wrap/stack on narrow screens. |
| Component restart/pause/stop icon buttons | Include individual Restart only, with full project/component accessible name and visible scope. Component pause/stop is outside requested scope. |
| Inline Stop/Rebuild confirmation | Extend to all interrupting operations, including project/component Restart and Pause. Explain DB/dependency impact and ephemeral data loss; Cancel performs no write. |
| Thin progress bar and timed state changes | Use actual backend stages and an indeterminate busy indicator, never timer-generated percentages or optimistic ready state. |
| Recent strip and “No actions this session” | Show bounded persisted operation results with IDs, timestamps and failure/unknown outcomes; explicitly label retention. No general audit timeline. |
| Simplified metrics and restart increment on manual restart | Preserve accepted observation freshness, current-instance uptime/restarts and unavailable reasons. Do not manufacture manual restart counts. |
| Auto-open Billing/worker example | Default collapsed and preserve user disclosure state. Use actual declared supported components; no worker/index/storage/static adapters or hardcoded sample IDs. |
| Search/filter/rescan, extra counts, active Logs/Preview and inferred owner | Keep prior supported-scope dashboard contracts; these demos confer no scope. No new search, scan, viewer, preview, counter or inferred owner. |
| Dense fixed-width rows, small icons and muted disabled text | Preserve compact visual hierarchy with accessible contrast, keyboard/focus, visible reasons and 44 px primary narrow-screen targets. Fix reference overflow rather than reproduce it. |
| Fonts, custom runtime and watermark | Retain local system fonts and existing React/CSS; do not import the attachment's code, fonts or branding runtime. |

No remote task control is present in the planned product. Read-only metrics,
metadata and destinations remain available beneath the control panel. Reference
mock data, unsupported service graphs and successful animations are not evidence
of any current runtime capability or product acceptance.

## Lifecycle icon follow-up

The project toolbar and individual restart buttons use the reference's play, square,
circular-arrow, cube and pause SVG symbols. Start and Resume share the play symbol.
Icons inherit the button color, remain decorative to assistive technology, and retain
visible action labels and complete project/component accessible names. Responsive
wrapping and existing touch targets remain part of the browser verification.
