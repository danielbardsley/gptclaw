# TASKS-013: Versioned Project Manifest

- **Status:** Complete; implementation merged and accepted
- **Owner:** Daniel
- **Last updated:** 2026-09-30 (America/New_York)
- **Specification:** [SPEC-013](./spec.md)
- **Design:** [TDD-013](./technical-design.md)

## Planning and authorization

- [x] T-000: Read repository guidance, catalogue, architecture, planning starter,
  and runtime-operation contract/acceptance. Reserve initiative 013, draft the
  specification/design/tasks, and index PRJ-001 as Draft. User selected PRJ-001
  as the first feature toward a working private app and deferred further RES work.
- [x] T-001: Daniel approved the specification and explicitly authorized
  implementation with “Implement the spec” on 2026-09-30 (America/New_York).
  Daniel subsequently accepted the implementation and authorized merge; PR #22
  merged as `aa55583`.

## Implementation, after T-001 authorization

- [x] T-002: Verify available Python/tool versions; select maintained YAML and
  JSON Schema libraries, pin dependencies reproducibly, and document isolated
  local/CI setup without host installs. Verify required parser restrictions and
  offline schema resolution; update the design with exact paths and commands.
  Covers PMF-001/004; prerequisite for T-003 and T-005.
- [x] T-003: Implement bundled schema, strict bounded parser, semantic checks,
  reusable validator, and thin CLI with documented exit/result/error contracts.
  Preserve observation-only behavior and safe file opening. Covers PMF-001–005;
  verify against AC-001–004.
- [x] T-004: Add the synthetic web example and field/author reference. Explain
  commands, health/base paths, private/ephemeral limits, versioning, validation
  versus authorization, and explicit future adoption. Do not modify AGT-005's
  planning starter. Covers PMF-002/003/006; verify against AC-001/002/005.

## Verification and delivery

- [x] T-005: Add and run isolated positive/negative tests for AC-001–004; execute
  the copy/validate/break/fix workflow for AC-005. Include command/environment
  sentinels, unchanged project bytes, network-unavailable validation, permission
  failures, symlinks/non-regular files, and input limits. Run existing bootstrap
  tests, the repository checker, shell syntax checks for any changed shell
  files, diff checks, and documentation link review. Add CI coverage for actual
  implementation paths and report exact outcomes. Covers PMF-001–006.
- [x] T-006: Create sanitized acceptance evidence mapped to AC-001–006, obtain
  Daniel's implementation review, deliver through the PR workflow, and record
  CI/merge separately from local checks and owner acceptance. Mark Delivered
  only after merged implementation and all criteria pass. Hand off to the
  runtime/CLI/template/private-route work with live-app acceptance still open.

## Current handover

The schema, bounded offline validator, CLI, hash-pinned setup, synthetic example,
reference, behavioral tests, and CI integration are implemented. All 134 repository tests pass, including 27 manifest tests. Local evidence is
recorded; implementation CI #73 and final PR CI #74 passed. Daniel accepted the
implementation and PR #22 merged as `aa55583`. PRJ-001 is Delivered.
No application, runtime, route, or infrastructure has been deployed. See
[acceptance](acceptance.md) for exact verification and merge evidence.
PRJ-002 and the runtime foundation follow this contract; further RES work waits
for the working-product milestone.
