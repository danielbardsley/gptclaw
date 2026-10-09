# SPEC-018: First private application workflow

- **Status:** Draft; planning authorized, implementation pending review
- **Owner:** Daniel
- **Date:** 2026-10-09 (America/New_York)
- **Features:** Initial slices of PRJ-002, TPL-001, RUN-001–005 and NET-101–103
- **Design:** [TDD-018](technical-design.md)
- **Tasks:** [TASKS-018](tasks.md)
- **Revision:** Desktop Hello World first; original APP-001–006 and AC-001–006 retained

## Outcome and scope

Create, run, open and edit one private web application, then run a second with
independent source, container, port and URL. Daniel selected this milestone in
September and confirmed returning to it on October 9. Daniel subsequently
requested a specification that starts with a desktop-accessible Hello World and
continues through the feature roadmap. This revision stages that work inside
SPEC-018. Planning is authorized; implementation and private route mutation await
execution authorization. Earlier smoke-test and deployment authorizations remain
valid for their recorded scope.

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

## Delivery stages and feature coverage

| Stage | User-visible result | Feature slices | Gate |
|---|---|---|---|
| 1 — Desktop Hello World | A real rootless Hello World web app opens on Daniel's desktop at its private Tailscale URL. | TPL-001 starter; RUN-001/002/004/005 single service; NET-101/102/103 first route | AC-007: actual desktop browser confirmation; no completed CLI prerequisite |
| 2 — Repeatable development | Create the same template with a CLI, start/stop it, inspect health/logs, run tests and see source edits in the browser. | PRJ-002; reusable TPL-001; RUN-001–005; NET-101–103 | Initial evidence toward AC-001/002/004/005; full two-project criteria close in stage 3 |
| 3 — Independent second app | Create a second app with its own source, service, port and URL; operate either without disrupting the other. | Same slices with port/ownership/concurrency proof | Complete AC-001–006 for both projects and owner acceptance |

The first stage builds the initial Next.js/TypeScript Hello World starter without
waiting for the full CLI. Use that starter in stage 2, preserving its source and
reconciling or removing only owned prototype runtime/route resources. A successful
localhost request or a static response supplied by Serve itself does not satisfy
the first-stage application result. Require Daniel's desktop browser observation.

Build in these stages rather than adding a separate application or acceptance
initiative. At each stage update the relevant catalogue slice and acceptance
record to actual Draft/In review/Implemented/Deployed/Delivered progress. Partial
stage completion does not deliver the broader feature. Keep PRJ-001's accepted
manifest and existing host acceptance requirements intact; add no dashboard,
production, public sharing or full toolchain-manager prerequisite.

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
  merely because their initial slices pass. Record measured creation, start,
  build and edit-to-browser times to assess speed and repeatability.
- APP-007: Deliver the first-stage Hello World as a real rootless web application
  before the full CLI. Wait for health, publish a selected owned private Serve
  route and return its actual current-node URL. Verify operator capability,
  HTTPS/certificate readiness and desktop access under the tailnet policy; retain
  unrelated configuration and keep Funnel disabled. Daniel confirms the page on
  his desktop; host-only success cannot substitute. Provide scoped stop/route
  removal instructions and retain source for later managed use.

## Acceptance

| ID | Observable result and evidence | Requirements |
|---|---|---|
| AC-001 | Create two new projects; both validate; existing paths and invalid manifests fail without execution or overwrites. | APP-001 |
| AC-002 | Container install/build/test and healthy start pass; status/logs are bounded; repeated and concurrent operations obey documented outcomes. | APP-002 |
| AC-003 | Two simultaneous projects have distinct ports/resources; stopping one leaves the other healthy; occupied-port/conflict failures preserve unrelated state. | APP-003 |
| AC-004 | Daniel opens both private base-path URLs; assets/health/updates work; loopback-only binding, route preservation and disabled Funnel verified. | APP-004 |
| AC-005 | Source edit becomes visible; restart/rebuild preserves source and guidance; ephemeral data limits are clear. | APP-005 |
| AC-006 | Focused tests, configured CI and live workflow results/timings recorded; owned cleanup verified and Daniel accepts this slice. | APP-006 |
| AC-007 | Stage 1 app is healthy on loopback and Daniel opens its actual private HTTPS URL from his desktop and sees Hello World. Selected route/host binding/Funnel state and prerequisite permissions are recorded; owned stop/removal works without losing source or unrelated routes. | APP-007, APP-002, APP-004, APP-006 |

## Decisions and readiness

The October 9 small container smoke test passed after repairing the test image's
missing HTTP server; [SPEC-014 evidence](../014-rootless-container-toolchain/acceptance.md)
records exact scope. That does not close logout/reboot or replacement acceptance.
Daniel confirmed independent CLI SSM access on October 9: the session reached
`forge-dev-01` as `ssm-user`. The earlier host-role registration query was denied;
that does not prevent operator access and no host permission expansion is needed.

Daniel reviews the proposed template/slice and authorizes implementation. Private
Serve changes need the existing operator capability and concrete authorized
scope; a missing capability blocks routing only. Read-only inspection found no
Serve routes configured and no active Funnel routes. Reading Serve status does
not prove permission to change it. Desktop-to-service access and HTTPS readiness
are still unverified. Select approved prerequisite changes before dependent work;
no new sudo/IAM grant or privileged service is assumed. Any necessary host
configuration change uses reviewed code and the existing protected pipeline;
any tailnet HTTPS/access change needs its concrete owner-reviewed scope.

Stage 1 may use synthetic Hello World content, followed by real product work once
the workflow succeeds. It does not change manifest v1 or imply durable app data.
Daniel supplies the desktop browser confirmation. The agent supplies scoped
host tests, exact URLs and operation evidence. Creating or merging this planning
revision does not start the application or alter routing.
