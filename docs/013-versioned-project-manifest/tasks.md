# TASKS-013: Versioned Project Manifest

- **Status:** Draft planning complete; specification approval and implementation authorization pending
- **Owner:** Daniel
- **Last updated:** 2026-09-30 (America/New_York)
- **Specification:** [SPEC-013](./spec.md)
- **Design:** [TDD-013](./technical-design.md)

## Planning and authorization

- [x] T-000: Read repository guidance, catalogue, architecture, planning starter,
  and runtime-operation contract/acceptance. Reserve initiative 013, draft the
  specification/design/tasks, and index PRJ-001 as Draft. User selected PRJ-001
  as the first feature toward a working private app and deferred further RES work.
- [ ] T-001: Daniel reviews the single-service manifest scope and proposed field
  contract; record specification approval separately from implementation
  authorization. A planning PR merge alone is not implementation authorization.

## Implementation, after T-001 authorization

- [ ] T-002: Verify available Python/tool versions; select maintained YAML and
  JSON Schema libraries, pin dependencies reproducibly, and document isolated
  local/CI setup without host installs. Verify required parser restrictions and
  offline schema resolution; update the design with exact paths and commands.
  Covers PMF-001/004; prerequisite for T-003 and T-005.
- [ ] T-003: Implement bundled schema, strict bounded parser, semantic checks,
  reusable validator, and thin CLI with documented exit/result/error contracts.
  Preserve observation-only behavior and safe file opening. Covers PMF-001–005;
  verify against AC-001–004.
- [ ] T-004: Add the synthetic web example and field/author reference. Explain
  commands, health/base paths, private/ephemeral limits, versioning, validation
  versus authorization, and explicit future adoption. Do not modify AGT-005's
  planning starter. Covers PMF-002/003/006; verify against AC-001/002/005.

## Verification and delivery

- [ ] T-005: Add and run isolated positive/negative tests for AC-001–004; execute
  the copy/validate/break/fix workflow for AC-005. Include command/environment
  sentinels, unchanged project bytes, network-unavailable validation, permission
  failures, symlinks/non-regular files, and input limits. Run existing bootstrap
  tests, the repository checker, shell syntax checks for any changed shell
  files, diff checks, and documentation link review. Add CI coverage for actual
  implementation paths and report exact outcomes. Covers PMF-001–006.
- [ ] T-006: Create sanitized acceptance evidence mapped to AC-001–006, obtain
  Daniel's implementation review, deliver through the PR workflow, and record
  CI/merge separately from local checks and owner acceptance. Mark Delivered
  only after merged implementation and all criteria pass. Hand off to the
  runtime/CLI/template/private-route work with live-app acceptance still open.

## Current handover

Only planning documents and catalogue/index references have changed. No schema,
validator, example file, dependency, runtime, host setting, or project manifest
has been installed. No implementation acceptance criterion has been executed.
Next decision: Daniel's specification review and implementation authorization
(T-001). PRJ-002 and the runtime foundation follow this contract; further RES
work waits for the working-product milestone.
