# TASKS-014: Rootless Container Toolchain

- **Status:** Implementation merged; deployment authorized, acceptance pending
- **Owner:** Daniel
- **Last updated:** 2026-10-01 (America/New_York)
- **Specification:** [SPEC-014](spec.md)
- **Design:** [TDD-014](technical-design.md)

## Planning and authorization

- [x] T-000: Inspect the catalogue, architecture, PRJ-001 boundary, committed
  bootstrap, replacement behavior and recovery guidance; draft this initiative.
  Evidence: source links and baseline observations in the specification/design.
- [x] T-001: Daniel reviews the specification and proposed storage policy, resolves
  requested changes, and explicitly authorizes implementation. Recorded October 1,
  2026: “Lets go ahead and implement SYS-001 now then.” Deployment remains separate.

## Implementation, after T-001

- [x] T-002: Inspect non-secret current identity and existing container/configuration
  metadata. Select supported package baseline, dependencies, network/storage
  backends, stable subordinate allocation and fixture image digest. Check Noble
  capabilities against version-matched upstream documentation. Record conflicts
  and resolve migration decisions before writing configuration. (RCT-001–RCT-004)
- [x] T-003: Add the declared toolchain bootstrap phase, safe managed configuration,
  stable identity checks, user-manager persistence, capability checks and completion
  gating. Preserve unknown settings and all existing security/data protections.
  Do not deploy. (RCT-001–RCT-003, RCT-005, RCT-006)
- [x] T-004: Add a digest-pinned synthetic build/run and Quadlet fixture with scoped
  verification/cleanup, restart/resource bounds and no secrets; write the operator
  runbook including graph-store loss, capacity checks and recovery instructions.
  Cover port collisions and bind-mount ownership. (RCT-002–RCT-005, RCT-007)

## Verification and delivery

- [x] T-005: Add meaningful isolated tests for allocation collisions, existing
  storage/configuration, repeated execution, missing prerequisites and completion
  gating. Test rendered bootstrap ordering and unchanged infrastructure safeguards.
  Run `./scripts/check-repository.sh` in the prepared manifest environment,
  `bash -n` for changed shell scripts, both Git diff checks, and pinned Terraform
  format/validate/test with backend-free initialization if needed. Record exact
  outcomes and limitations; local checks do not pass host criteria. Open the
  implementation PR and obtain review/CI before merge. (AC-001–AC-003, AC-006)
- [ ] T-006: Obtain Daniel's specific replacement/deployment authorization and
  maintenance window after reviewing the plan and recovery point. Use only the
  protected pipeline. Verify access, protected data/identity and deployed toolchain.
  Run all host acceptance scenarios, including last-session logout, reboot before
  login, replacement/rebuild behavior and fixture cleanup. Record rollback review
  separately from any executed rollback. (AC-001–AC-007)
- [ ] T-007: Create `acceptance.md` with revision, sanitized command results,
  PR/CI/deployment references and every criterion's actual disposition. Obtain
  Daniel's acceptance; mark SYS-001 Delivered only after merged implementation
  and all required acceptance passes. Preserve unresolved limitations and remove
  only task-owned fixtures. (RCT-007, AC-007)

## Current handover

Implementation and operator/fixture instructions are complete locally. Discovery
selected the existing UID/GID and subordinate allocation, Noble Podman 4.9.x and
a digest-pinned fixture; no existing store needs migration. T-005 local checks and
CI and the completed merge are recorded in [acceptance.md](acceptance.md). Daniel
authorized deployment and necessary repairs; corrected plan, recovery/enrollment
readiness and T-006/T-007 host acceptance remain pending. No live package installation, mappings, user-manager
settings, containers or infrastructure have been changed. Next step is review of
the implementation PR, followed by separately authorized pipeline deployment.

- [ ] T-008: Review and deploy the October 8 storage-parent ownership repair
  through the protected pipeline. The bootstrap explicitly assigns `.local` and
  `.local/bin` to forge; its regression reproduced the live failure and passes
  locally. Confirm CI, review the new protected plan and recovery readiness, then
  obtain authorization for replacement. Verify actual rootless receipts,
  Tailscale enrollment and protected data after deployment; the disposable
  capability probe is not final acceptance. See [the evidence](acceptance.md).
