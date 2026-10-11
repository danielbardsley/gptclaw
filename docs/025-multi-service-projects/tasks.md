# TASKS-025: Multi-service projects

- **Status:** Implemented — local/CI/live/client verified; review/merge pending
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-025](spec.md) · **Design:** [TDD-025](technical-design.md)

## Planning and authorization

- [x] T-001: Review RUN-006, existing manifest/lifecycle/catalogue/profile sources
  and merged SPEC-024 Python implementation/standards. Draft the two-service notes
  slice, design, measurable acceptance and tasks; update index/catalogue/sequence.
  Evidence: planning files on this branch and documentation checks recorded below.
- [x] T-002: Project owner approves SPEC-025 and authorizes implementation/live
  synthetic verification. Finalize proposed schema/provider/catalogue versions,
  component command syntax and compatibility fixtures in review; implement the
  versioned contract and observation-only validator with unsafe path/topology and
  legacy tests. MS-001; AC-001, AC-007. Gate: no implementation before authorization.

## Implementation

- [x] T-003: Add exact-release grouped generation, complete independent locks,
  component toolchains/provenance/standards/guidance and local repository-generation
  selection. Keep defaults/published releases unchanged; prove occupied/tampered
  destination refusal. Depends on T-002. MS-002; AC-002.
- [x] T-004: Make preparation, jobs, quality/format and typed dependencies explicitly
  component-aware under a single group lock; separate fingerprints and owned caches.
  Test frozen restore, active/busy refusal, transaction conflict and interrupted
  recovery without cross-component source edits. Depends on T-002/T-003. MS-002,
  MS-007; AC-002, AC-007.
- [x] T-005: Implement owned group network/units/ports, staged receipts, bounded
  readiness ordering, status/logs, stop/restart, reverse cleanup and same-operation
  recovery. Test partial startup, absent resources, unknown ownership, collision,
  busy/interruption and failed cleanup. Include capabilities/assets in snapshots.
  Depends on T-004. MS-003, MS-007; AC-003, AC-007.
- [x] T-006: Extend private ingress with group route sets, segment-safe API namespace,
  aggregate readiness and dependency outage/recovery. Test mounted UI/assets/API/docs,
  query/redirects, spoofed headers, stopped/unknown targets and atomic publication.
  Verify network/loopback/limits; reuse existing private Serve prefix. Depends on
  T-005. MS-004; AC-004.
- [x] T-007: Implement notes service/models/store and Next.js editor/list with full
  CRUD, bounds/pagination/capacity, safe text/error/draft states, deletion confirmation,
  keyboard labels and visible shared/ephemeral data explanation. Apply inherited
  Python standards and locked checks; test synchronized mutation and data reset.
  Depends on T-003. MS-005, MS-006; AC-005, AC-006.
- [x] T-008: Add grouped golden-template and pinned generated CI checks, browser/API
  contract/CRUD/error tests, Python critical statement and branch coverage >=80%,
  meaningful seeded quality/security defects and source reload/syntax recovery for
  both components. Verify group test/verify failures and no implicit lock changes.
  Depends on T-004/T-006/T-007. MS-006; AC-005, AC-006.

## Verification and delivery

- [x] T-009: Run relevant focused suites, prepared repository checks, generated
  container/browser checks, changed shell syntax and diff/link checks. Submit
  implementation PR, record final-head configured CI and versioned provider rollout.
  Trial rollback/refusal and preserve v1/v2/template/repository-credential behavior.
  Depends on T-008. MS-001, MS-008; AC-001–003, AC-006–008.
- [ ] T-010: After authorized rollout, use named local-only synthetic fixtures on EC2;
  inspect capacity/network/resource bounds, measure cold/warm preparation, exercise
  private UI/API/docs, group lifecycle, outage/recovery, reload/data loss and stop/
  source retention while independent web/API projects remain healthy. Obtain an
  independent authorized browser's CRUD/source-update confirmation. Write sanitized
  acceptance.md mapping AC-001–008, local/CI/live/client results, actual revisions,
  timings, limitations, rollback and owned fixture disposition. Update runbooks.
  Complete merge and project owner acceptance, then mark only the initial RUN-006
  slice Delivered and record deferred database/cache/worker graphs. Depends on
  T-009 and actual CI/runtime evidence. MS-004–008; AC-004–008.

## Current handover

The project owner approved scope and authorized implementation October 11.
Provider 1.7.0 now supports manifest/catalogue v3, explicit group receipt v2,
component-scoped preparation/dependency/quality/hooks, owned separate containers
and internal networks, ordered group lifecycle and health-gated private routing.
The exact notes starter includes API/UI CRUD, bounded previews/full-detail reads,
inherited Python standards and generated container/contract/browser CI.

Local evidence: the prepared repository gate passed 430 tests; the 14 focused
group tests pass. Both exact-container quality stacks and isolated OpenAPI/CRUD
checks pass. Browser CRUD, refresh retention, safe text, failed drafts, keyboard
and responsive checks pass after correcting the isolated dev-origin setup and
waiting for asynchronous detail loading. API/web dependency add/remove through
the stopped group lock passed with independent sources preserved. Cold local
Node acquisition hit the existing build nproc limit; exact verified images were
reused without changing host limits. The final golden seeded-defect checks and managed live/client observations now
pass. The project owner confirmed independent CRUD and source-update behavior.
Final source CI passed all three configured workflows at `ca0080b`; review/merge
remain in T-010; see [acceptance](acceptance.md).

Published existing release integrity and whitespace checks pass. Terraform was
not changed and no local Terraform or infrastructure apply was run. Acceptance
will distinguish local, generated CI, live and client observations. Earlier
SPEC-024 acceptance wording remains independently tracked.


Final verification closeout: 436 repository tests, 36 focused lifecycle/proxy tests,
16 focused group tests and the full exact-container/golden/browser/seeded-defect
workflow pass. Critical API coverage is 275/277 statements and 18/18 branches.
Actual managed group tests, separate containers/loopback/limits, private REST/docs,
real HTTPS browser, both source failure/recovery paths, busy/active refusals,
restart/data reset, stop/source retention and old-provider refusal pass. Project
owner independently confirmed the requested private CRUD and visible source update.
All 211 reviewed local links resolve; whitespace, Python compilation, changed Bash
syntax and published release immutability pass. Final source CI at `ca0080b` is green
in all three workflows; acceptance.md links exact runs. The notes fixture remains
ready with source retained. T-010 stays unchecked for review/merge and final delivery;
no infrastructure apply/public exposure or unrelated data cleanup occurred.
