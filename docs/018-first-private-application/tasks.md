# TASKS-018: First private application workflow

- **Status:** Delivered — accepted initial single-web workflow
- **Owner:** Daniel
- **Specification:** [SPEC-018](spec.md)
- **Design:** [TDD-018](technical-design.md)

- [x] T-000: Refocus on the selected private-app milestone; inspect manifest,
  runtime contract and architecture defaults; run/clean up a small container smoke
  test and draft this plan. SPEC-017 remains reserved by closed unmerged PR #37.
- [x] T-001: Daniel reviews the narrow template/workflow and authorizes
  implementation. Resolve each stage's pins, limits and routing capability before
  dependent work; the full CLI state contract can follow the desktop prototype.
  Independent SSM access is confirmed by Daniel. Implementation and specified
  private routes authorized by “implement the spec” on October 9; resolve each
  stage's choices below before dependent work. Existing host-role bounds remain.

## Stage 1: Desktop Hello World first

- [x] T-006: After T-001 execution authorization, inspect actual Serve/HTTPS,
  desktop access and operator prerequisites; resolve scoped permissions before
  dependent changes. Pin the initial container toolchain and implement the small
  Next.js/TypeScript Hello World starter with valid manifest and base-path health.
  Start a bounded rootless loopback service and verify direct readiness. A full
  CLI is not required. (APP-007; initial APP-002/APP-004; AC-007)
- [x] T-007: After T-006, configure only the approved owned private route; verify
  forwarding/asset/health paths and disabled Funnel, then give Daniel the actual
  current-node URL. Record his desktop confirmation and measured first-app setup
  time. Demonstrate scoped stop/route removal retaining source; reuse/reconcile
  this starter in stage 2. (APP-007/APP-006; AC-007)

## Stage 2: Repeatable application workflow

- [x] T-002: After T-007, implement the initial CLI/template and reuse manifest
  validation;
  preserve existing files, define version/help/result contracts and container-only
  command execution. Verify APP-001 / AC-001.
- [x] T-003: After T-002, implement locked lifecycle transitions, rootless
  service/limits,
  port reservation, bounded health/status/logs and reconciliation; test repeated,
  concurrent, occupied-port and failed-health cases. Verify APP-002/APP-003 /
  AC-002/AC-003 before dependent routing.
- [x] T-004: After T-003, within authorized private routing scope, implement owned
  Serve paths,
  prefix-aware template and browser updates; preserve unrelated configuration and
  prove source edit/restart behavior. Verify APP-004/APP-005 / AC-004/AC-005.

## Stage 3: Second app and feature closeout

- [x] T-005: After T-004, run relevant repository checks and the live two-project
  workflow from a
  tailnet client, verify scoped cleanup/source preservation, deliver implementation
  PR and record acceptance by criterion. Obtain Daniel's acceptance of this slice
  and update only the supported catalogue scope. Verify APP-006 / AC-006.

Original T-000 discovery/smoke evidence and APP/AC/T IDs are preserved. This
revision adds T-006/T-007 and AC-007 for the first desktop Hello World, placed
before the full CLI. The original revision was planning only; implementation is
now authorized and recorded below. Formal host logout/reboot and replacement
evidence remain in their existing records. After
each stage record only the completed feature slice; broad catalogue entries do
not become Delivered from a prototype.

## Implementation handover

Template/CLI and bounded rootless lifecycle are implemented; local source edit,
health, build/test/typecheck, stop/start/restart and two-port isolation checks
passed. A stable provider snapshot and unprivileged loopback ingress are running.
Daniel confirmed both private pages and their counters on his desktop. The shared
Serve prefix is configured and the prototype override removed, as verified by
read-only status; additional apps need no per-app Serve command.

T-007/T-004/T-005 are complete. Daniel confirmed automatic desktop source
updates; the temporary edit was restored. Managed first-app stop/start retained
all 16 existing source/guidance/manifest files and kept the second app available.
The stop test exposed a TCP TIME_WAIT probe defect; provider 1.0.1 fixes it while
continuing to refuse active listeners. The patch/evidence merged in PR #43 as
`fdfaf3d0f911caed9f6efa59cf0d490053597ac9`, after all three CI workflows passed.
The focused suite passed 32 cases and the full offline repository checker passed.

Daniel requested these two checks so the initial workflow could close. Their
passing evidence completes this slice; wider roadmap, fresh-client skill and
formal host acceptance remain separate. Both demo apps remain running with
original source and private URLs. [Acceptance evidence](acceptance.md) preserves
actual receipts/timings, failure/recovery, owner attribution and unmeasured timing
limits. No additional per-app operator route is required.
