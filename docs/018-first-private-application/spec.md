# SPEC-018: First private application workflow

- **Status:** Draft; planning authorized, implementation pending review
- **Owner:** Daniel
- **Date:** 2026-10-09 (America/New_York)
- **Features:** Initial slices of PRJ-002, TPL-001, RUN-001–005 and NET-101–103
- **Design:** [TDD-018](technical-design.md)
- **Tasks:** [TASKS-018](tasks.md)

## Outcome and scope

Create, run, open and edit one private web application, then run a second with
independent source, container, port and URL. Daniel selected this milestone in
September and confirmed returning to it on October 9. This request authorizes
planning plus a small container smoke test, not implementation of this workflow.

Use the existing [manifest v1](../project-manifest.md), rootless Podman and forge
user manager. Proposed first template follows the architecture's Next.js,
TypeScript and pnpm default. Language tools run inside a reviewed container;
no host Node/npm or Terraform installation is required. Implementation selects
supported exact tool/dependency versions and a base-image digest before execution.

Include a small local lifecycle CLI, one web template, bounded per-project
services, health/logs and private routes under `/projects/<slug>/`. Projects live
on the retained project volume; container images and runtime metadata remain
rebuildable. Manifest `data.mode: ephemeral` stays unchanged: source persistence
is supported, managed application data is not.

Exclude automatic GitHub repository/credential creation, databases, dashboard,
public sharing, production, full template catalogue, full language toolchain
manager and new infrastructure. Existing formal host logout/reboot/replacement
acceptance remains pending; it is not a separate new prerequisite initiative.
Actual defects that block this workflow must be fixed and verified within their
reviewed scope before dependent operations proceed.

## Requirements

- APP-001: A narrow CLI creates one template into a new project directory without
  overwriting existing files, emits valid manifest v1 and adapted guidance, and
  exposes help/version plus `new`, `validate`, `start`, `stop`, `status`, `logs`
  and `test`. Existing validation stays observation-only; commands use argument
  vectors in the container, never shell interpolation on the host.
- APP-002: Build, dependency install, test and development service run as forge
  through rootless containers with project-specific names/network and locked
  dependencies. Start waits for declared HTTP health, exposes bounded status/logs,
  and fails clearly on invalid input, occupied resources or timeout. Repeated
  start/stop is idempotent; serialize operations on the same project.
- APP-003: Allocate distinct stable loopback ports from a reviewed bounded range;
  enforce CPU/memory/PID limits and preserve unrelated services. One project
  starting, stopping or failing must not alter the other project's state.
- APP-004: Publish only healthy services via private Tailscale Serve paths.
  Preserve existing routes; verify required operator capability before changes.
  Keep Funnel disabled, EC2 ingress unchanged and host ports on loopback. Assets,
  links, health and development updates work beneath each project's base path.
- APP-005: Changing project source produces an observable browser update without
  hand-editing platform service configuration. Restart/rebuild retains source;
  ephemeral app data and disposable images are explicitly documented.
- APP-006: Verify the complete workflow from a tailnet client for two projects,
  remove only task-owned services/routes on cleanup, and record commands, revision,
  URLs, results and limitations. Do not mark broad catalogue features Delivered
  merely because their initial slices pass.

## Acceptance

| ID | Observable result and evidence | Requirements |
|---|---|---|
| AC-001 | Create two new projects; both validate; existing paths and invalid manifests fail without execution or overwrites. | APP-001 |
| AC-002 | Container install/build/test and healthy start pass; status/logs are bounded; repeated and concurrent operations obey documented outcomes. | APP-002 |
| AC-003 | Two simultaneous projects have distinct ports/resources; stopping one leaves the other healthy; occupied-port/conflict failures preserve unrelated state. | APP-003 |
| AC-004 | Daniel opens both private base-path URLs; assets/health/updates work; loopback-only binding, route preservation and disabled Funnel verified. | APP-004 |
| AC-005 | Source edit becomes visible; restart/rebuild preserves source and guidance; ephemeral data limits are clear. | APP-005 |
| AC-006 | Focused tests, configured CI and live workflow results recorded; owned cleanup verified and Daniel accepts this slice. | APP-006 |

## Decisions and readiness

The October 9 small container smoke test passed after repairing the test image's
missing HTTP server; [SPEC-014 evidence](../014-rootless-container-toolchain/acceptance.md)
records exact scope. That does not close logout/reboot or replacement acceptance.
Daniel confirmed independent CLI SSM access on October 9: the session reached
`forge-dev-01` as `ssm-user`. The earlier host-role registration query was denied;
that does not prevent operator access and no host permission expansion is needed.

Daniel reviews the proposed template/slice and authorizes implementation. Private
Serve changes need the existing operator capability and concrete authorized
scope; a missing capability blocks routing only. No sudo, IAM expansion or new
privileged service is assumed. The first app may be synthetic for acceptance;
real product content can follow once the workflow works.
