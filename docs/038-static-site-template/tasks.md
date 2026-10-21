# TASKS-038 — Static site template

Status: Complete; T1–T8 verified.
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

- [x] T6: Run repository checks, release-immutability checks and historical/default
  template regressions; prove source/snapshot generation parity and refusal paths.
  Run generated frozen restore/build/quality/security/container checks and
  interrupted/failed export tests. Confirm source edits invalidate build readiness.
  Record exact revisions/results and review implementation PR with actual CI.
  Depends on T3–T5. Covers STATIC-001,004,006; AC-001, AC-004, AC-006.
- [x] T7: Under scoped live-fixture authorization, create two named private static
  sites using the reviewed provider. Exercise HTTPS pages/assets/navigation/404,
  edit/rebuild, failure/repair, restart and scoped stop/source retention while the
  independent site remains available. Record budgets, build/start timings,
  resources and actual owner keyboard/focus/200%-zoom checks. Preserve source;
  remove only specifically owned disposable fixtures under the documented cleanup
  scope. Add acceptance.md with passed/failed/pending criteria and evidence.
  Depends on T6 and reviewed runtime prerequisites. Covers STATIC-003–007;
  AC-003–006. Do not convert CI success into live or owner acceptance.
- [x] T8: Verify runbook/example/adaptation instructions, finalize acceptance and
  handover, complete PR review and merge through existing gates. Mark TPL-005
  Delivered only after merged implementation and every required criterion passes;
  record retained fixtures and follow-ups. Covers STATIC-007; AC-006.

## Completed handover

Implementation merged in [PR #92](https://github.com/danielbardsley/gptclaw/pull/92)
at `0288de9fcc224892acc6756e1496331faac07657`, after all five workflows passed
on final head `959355ccb04717b10e2d607e78de042ec4b7a180`. AC-001–AC-006 pass;
the project owner accepted the UI and explicitly requested merge and completion.
TPL-005 is Delivered. The combined provider is 1.17.0; all 22 exact releases pass
local generation, and all nine current releases pass metadata checks. Focused
static, smoke, quality and template tests pass. See [acceptance](acceptance.md)
for local/CI/live evidence, the unchanged Metro timing rerun and limitations.

Both private previews and their source/receipts are retained. A managed ready-state
start under provider 1.17.0 returned `changed: false`; both projects remain ready
with configured private routes. No further implementation or acceptance tasks
remain for TPL-005. Public/production hosting and downstream product adaptation
retain their separate scopes. The unrelated original checkout is unchanged.
