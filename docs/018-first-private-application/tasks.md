# TASKS-018: First private application workflow

- **Status:** Implementation on feature branch; remaining live acceptance pending
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
- [ ] T-007: After T-006, configure only the approved owned private route; verify
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
- [ ] T-004: After T-003, within authorized private routing scope, implement owned
  Serve paths,
  prefix-aware template and browser updates; preserve unrelated configuration and
  prove source edit/restart behavior. Verify APP-004/APP-005 / AC-004/AC-005.

## Stage 3: Second app and feature closeout

- [ ] T-005: After T-004, run relevant repository checks and the live two-project
  workflow from a
  tailnet client, verify scoped cleanup/source preservation, deliver implementation
  PR and record acceptance by criterion. Obtain Daniel's acceptance of this slice
  and update only the supported catalogue scope. Verify APP-006 / AC-006.

Original T-000 discovery/smoke evidence and APP/AC/T IDs are preserved. This
revision adds T-006/T-007 and AC-007 for the first desktop Hello World, placed
before the full CLI. No app or route has been created by this planning revision.
Next: review/authorize the staged implementation, then T-006/T-007. Formal host
logout/reboot and replacement evidence remain in their existing records. After
each stage record only the completed feature slice; broad catalogue entries do
not become Delivered from a prototype.

## Implementation handover

Template/CLI and bounded rootless lifecycle are implemented; local source edit,
health, build/test/typecheck, stop/start/restart and two-port isolation checks
passed. A stable provider snapshot and unprivileged loopback ingress are running.
Daniel confirmed the first private Hello World page and counter on his desktop.

T-007/T-004/T-005 remain open for the shared-prefix operator transition, both
private desktop URLs and browser updates, CI/review/merge and final acceptance.
The implementation uses one operator-owned private Serve prefix and unprivileged
per-app mappings, avoiding a general Unix operator grant. No privileged broker
or infrastructure change was introduced. [Acceptance evidence](acceptance.md)
records failures/fixes and exact remaining obligations.

Implementation CI passed at `0c9d75b` (all three workflows). Review/merge and
remaining shared-prefix/two-app desktop acceptance are still pending.
