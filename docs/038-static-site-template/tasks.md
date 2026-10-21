# TASKS-038 — Static site template

Status: Implementation authorized and in progress.
Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Technical design](technical-design.md)

## Planning and authorization

- [x] T1: Read applicable guidance, catalogue, related plans and actual template,
  generation/runtime/toolchain sources; inspect main and preserve existing work.
  Record the project owner's Next.js static-export selection and draft linked
  requirements/design/tasks. No implementation authorization was supplied.
- [x] T2: The project owner approved the specification and authorized implementation
  with “Ok, lets implement the spec.” Confirmed budgets, exact release and rebuild
  downtime; allocated manifest v10 and catalogue v8 against the current contracts. Map adapter/generation/snapshot/control dispatch before editing.
  Covers STATIC-001; AC-001. Gate: authorized scope before T3–T7 implementation.

## Implementation order

- [x] T3: Implement exact immutable release, strict generation/contracts/provenance,
  complete static starter, prefix-aware file server, quality command interface,
  Containerfile and generated guidance/CI. Do not alter old releases/defaults.
  Include adaptation guidance identifying which demonstration pages/assets to
  replace and how to remove dependent navigation/tests. The template's example
  pages are intentional; downstream product acceptance must review their removal
  or retention against that product's spec.
  Covers STATIC-001,002,003,005,006,007; AC-001, AC-002, AC-003, AC-005, AC-006.
- [x] T4: Integrate managed build/start/status/test/logs/restart/rebuild/stop,
  completion/readiness and source-input invalidation; stop/build/start failures
  and interruption remain recoverable. Package adapter/contracts/assets in
  immutable snapshots and preserve locks/resources/private routing and unrelated
  adapters. Depends on T3. Covers STATIC-004; AC-004.
- [x] T5: Add meaningful output/protocol/reference/accessibility/budget checks in
  pinned containers. Test direct loads and client navigation, no-JS content,
  malformed/traversing paths, symlinks, HEAD/MIME/404 behavior, static-only build
  limitations and injected quality failures. Verify checker tools and exact
  versions/advisories, documenting setup separately from offline execution.
  Depends on T3. Covers STATIC-002,003,005,006; AC-002, AC-003, AC-005, AC-006.

## Verification and delivery

- [ ] T6: Run repository checks, release-immutability checks and historical/default
  template regressions; prove source/snapshot generation parity and refusal paths.
  Run generated frozen restore/build/quality/security/container checks and
  interrupted/failed export tests. Confirm source edits invalidate build readiness.
  Record exact revisions/results and review implementation PR with actual CI.
  Depends on T3–T5. Covers STATIC-001,004,006; AC-001, AC-004, AC-006.
- [ ] T7: Under scoped live-fixture authorization, create two named private static
  sites using the reviewed provider. Exercise HTTPS pages/assets/navigation/404,
  edit/rebuild, failure/repair, restart and scoped stop/source retention while the
  independent site remains available. Record budgets, build/start timings,
  resources and actual owner keyboard/focus/200%-zoom checks. Preserve source;
  remove only specifically owned disposable fixtures under the documented cleanup
  scope. Add acceptance.md with passed/failed/pending criteria and evidence.
  Depends on T6 and reviewed runtime prerequisites. Covers STATIC-003–007;
  AC-003–006. Do not convert CI success into live or owner acceptance.
- [ ] T8: Verify runbook/example/adaptation instructions, finalize acceptance and
  handover, complete PR review and merge through existing gates. Mark TPL-005
  Delivered only after merged implementation and every required criterion passes;
  record retained fixtures and follow-ups. Covers STATIC-007; AC-006.

## Current handover

The static release, adapter/contracts, private lifecycle integration, generated
quality/browser/CI gates and runbook are implemented. Focused static (7 tests) and
manifest (28 tests) suites pass. The actual export passes authoring tests, links,
budgets, browser/accessibility/no-JS/navigation and the advisory check. Broader
repository, generated defect/container and two-project managed acceptance checks
are running. See [acceptance](acceptance.md). PR review/merge, final CI and manual
project-owner acceptance remain separate pending gates.
