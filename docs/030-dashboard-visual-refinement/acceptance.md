# ACCEPTANCE-030: Dashboard visual refinement

- **Status:** Local/CI/private acceptance passed — owner/review gates pending
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-030](spec.md) · **Design:** [TDD-030](technical-design.md) · **Tasks:** [TASKS-030](tasks.md)
- **Delivery:** [PR #71](https://github.com/danielbardsley/gptclaw/pull/71), `codex/dashboard-visual-specs`; implementation revision `4ca26592c7034ef6c8b072177ff0ef1095b78b58`

## Criterion mapping

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | Passed locally; owner pending | Reference-derived slim header, neutral surface, compact table/pills and full-width two-panel expansion captured with deterministic valid-schema fixtures. Actual component metrics retained below the panels. No unsupported reference controls/runtime/fonts/data copied. Owner visual comparison remains. |
| AC-002 | Passed locally | Six normal projects fit at 1440 × 900; collapsed rows satisfy 72–88 px bounds. 1280 px overview fits. Long/missing/conflicting metadata, partial count and accessible full values pass. |
| AC-003 | Passed locally | Real browser group/component checks preserve measured zero/null, per-component stale health, scoped links and expiry. Disclosure state/focus survive shared refresh; links do not toggle details. All six normalized state treatments covered. |
| AC-004 | Passed locally; owner zoom pending | Bounds, semantic headers/row headers and primary target sizes pass at 1440/1280/768/390 px. 720 × 450 CSS reflow models 1440 × 900 at 200%; actual owner-browser zoom remains. Text contrast is measured at least 4.5:1 for status/secondary/link/reason/count treatments; reduced motion removes chevron transition. |
| AC-005 | Passed locally | Existing empty/partial/stale/outage/recovery, malicious text, safe tabs, preview clock-skew expiry and HTTP boundary checks pass. Disclosure does not start collection loops. No search/filter/rescan, extra status aggregate, adapter, history, demo logs/preview capability or storage is introduced. |
| AC-006 | Passed local/CI/private; owner/merge pending | Frozen install, seven frontend tests, typecheck/build, full offline repository gate, all four implementation CI workflows and real private rollout/rollback/browser checks passed. Owner acceptance and review/merge remain. |

## Executed local verification

On the isolated project-volume worktree, using the prepared manifest interpreter
and existing verified rootless Node/browser images:

- `scripts/tests/check_dashboard.py --engine podman --reuse-node-image localhost/gptclaw-node:24.21.0-pnpm12.10.1 --reuse-browser-image localhost/gptclaw-dashboard-check:6ad13efadb324b6d9644b5bfe9c952ed-browser --output .dashboard-qa/visual-release`: passed frozen dependency install, all seven frontend tests, route type generation/TypeScript, production build, actual Unix socket/HTTP restrictions and full browser acceptance.
- Extended browser suite also passed all-state contrast, responsive semantics, 24 px desktop/44 px narrow primary targets, keyboard/disclosure/focus preservation, long metadata and absence of unsupported controls. Temporary fixture collector/containers were stopped/removed only after confirming the ownership label.
- `git diff --check`: passed; staged diff and relative-link checks passed.
- Reference screenshots are committed planning inputs; redesigned screenshots are ignored task-owned QA evidence. No real project dataset or credential material is committed.

The first browser run used an obsolete total-table-row assertion and counted the
new hidden detail rows (8 rather than 4). It failed; the project-row identity count
was corrected without weakening the inventory assertion. A test fixture originally
aliased a source row; it now deep-clones the row so layout fixtures retain valid
schema/type/component combinations. Final release checks passed after that correction.
Unavailable short pills use real screen-reader text, rather than relying on naming
a generic span. The final source was rebuilt and the full browser gate passed.

The first full repository command printed passing suites but the execution tool
returned termination status 143. It is not recorded as a successful overall gate.
A repeat with isolated process-group execution and an explicit return-code receipt
passed: exit 0 in 594 seconds. All repository suites completed successfully. Terraform checks and project lifecycle/database operations are not local
requirements for this frontend-only patch; applicable CI keeps existing path gates.

## Scope and rollout preparation

The change is confined to frontend presentation/types and meaningful browser checks.
Existing status/link helpers, provider, collector, API/socket protocol, package pins,
private boundary and polling cadence are unchanged. Search/filter/rescan, additional
aggregate counters, external fonts, unsupported reference project types and fake
logs/previews are absent. Persistent status history is not added.

Current owned release, captured read-only before rollout:
`7ea8b649f931d93480c413f07edc40580ec76015a9a509e55f2071917d25b5a7`.
Provider snapshot remains `dad82ad62342c9fd0afea4249d3324ef7e709adec222ed8a7debb83000575e83`,
frontend image `sha256:56cb97c5d887e341f46dd848e859e357957c92951c8c0879e08b97c4b971052c`,
with both status and links enabled at
`https://forge-dev-01-4.tail8c3304.ts.net/dashboard/`.

Implementation and necessary reversible private rollout are explicitly authorized.
Prepare the new owned release with existing status/link flags, preserve the origin,
listener/mounts/Serve and project data, then verify actual HTTPS UI and rollback.
The reviewed manager restarts its owned collector as part of activation; its in-memory
observed-change tracking restarts, while project containers/uptimes/data stay intact.
Record new release/source/CI provenance and actual owner comparison/zoom/navigation.
No redesigned production/deployed or merged acceptance is implied by local tests.

## Implementation CI

All four workflows passed for implementation revision
`4ca26592c7034ef6c8b072177ff0ef1095b78b58`:
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38335307263),
[development-host quality](https://github.com/danielbardsley/gptclaw/actions/runs/38335307255),
[Tailscale federation quality](https://github.com/danielbardsley/gptclaw/actions/runs/38335307333),
and [private applications](https://github.com/danielbardsley/gptclaw/actions/runs/38335307262).
No protected Terraform deployment/apply was invoked.

## Actual private rollout and rollback

The new owned release is
`d0485098d81d573b41943793b91a39b03f8a509bbfb22c3aa261ef3e64d803d1`.
Read-only descriptor comparisons prove provider snapshot, image, origin and enabled
status/link flags match the previous release recorded above. Both owned services
are active. HTTPS health, page and snapshot pass, with 16 discovered projects.
Existing /dashboard/ and /projects/ Serve handlers and Funnel-off were verified.
No project service, source/data, handler, socket protocol or infrastructure was changed.

A pinned real browser opened the actual private URL, verified the refined semantic
table and real Group component metrics, retained keyboard focus/open state through
refresh, checked 1280/768/390 px bounds and opened a published Group API-doc link.
The destination returned HTTP 200 and rendered Swagger at its exact owned prefix.
Screenshots are ignored task-owned QA evidence; only reference images are committed.

The reviewed manager's rollback selected the prior release. Actual HTTPS served
its old summary/layout and health. Re-activating the new release restored the
refined UI and health. The original release remains available; project runtimes
and private handlers were preserved. Collector in-memory observation history restarts
as documented; application container-instance timing remains independent.

## Remaining owner and merge evidence

Owner confirmation is requested for the visual comparison, Group details, keyboard,
destinations and actual 200% browser zoom. It is not inferred from the rootless-browser
or CSS-reflow checks. Final review/merge and criterion bookkeeping remain.
