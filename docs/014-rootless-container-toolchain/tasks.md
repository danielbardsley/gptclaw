# TASKS-014: Rootless Container Toolchain

- **Status:** Draft; implementation not authorized
- **Owner:** Daniel
- **Last updated:** 2026-10-01 (America/New_York)
- **Specification:** [SPEC-014](spec.md)
- **Design:** [TDD-014](technical-design.md)

## Planning and authorization

- [x] T-000: Inspect the catalogue, architecture, PRJ-001 boundary, committed
  bootstrap, replacement behavior and recovery guidance; draft this initiative.
  Evidence: source links and baseline observations in the specification/design.
- [ ] T-001: Daniel reviews the specification and proposed storage policy, resolves
  requested changes, and explicitly authorizes implementation. Record the decision.

## Implementation, after T-001

- [ ] T-002: Inspect non-secret current identity and existing container/configuration
  metadata. Select supported package baseline, dependencies, network/storage
  backends, stable subordinate allocation and fixture image digest. Check Noble
  capabilities against version-matched upstream documentation. Record conflicts
  and resolve migration decisions before writing configuration. (RCT-001–RCT-004)
- [ ] T-003: Add the declared toolchain bootstrap phase, safe managed configuration,
  stable identity checks, user-manager persistence, capability checks and completion
  gating. Preserve unknown settings and all existing security/data protections.
  Do not deploy. (RCT-001–RCT-003, RCT-005, RCT-006)
- [ ] T-004: Add a digest-pinned synthetic build/run and Quadlet fixture with scoped
  verification/cleanup, restart/resource bounds and no secrets; write the operator
  runbook including graph-store loss, capacity checks and recovery instructions.
  Cover port collisions and bind-mount ownership. (RCT-002–RCT-005, RCT-007)

## Verification and delivery

- [ ] T-005: Add meaningful isolated tests for allocation collisions, existing
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

Planning documents are drafted; no toolchain code, installation, deployment or
runtime tests have been performed. The documentation index and SYS-001 catalogue
entry link this draft. Next action is Daniel's specification review (T-001), then
version/identity/storage discovery (T-002) once implementation is authorized.
