# TASKS-031: Branch and worktree policy

- **Status:** Draft planning complete; approval and implementation pending
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-031](spec.md) · **Design:** [TDD-031](technical-design.md)

## Planning and authorization

- [x] T-001: Inspect catalogue/index, repository guidance, current Git version,
  credential binding/configuration, runtime lock/source identity and hook behavior.
  Draft the bounded specification/design/tasks and update the index/catalogue.
  Evidence: cited source interfaces in TDD-031; this planning revision.
- [ ] T-002: Project owner reviews source-only scope and proposed defaults, then
  explicitly approves the specification and authorizes implementation. Resolve
  receipt/CLI schemas and lock-order audit before dependent coding. The planning
  request alone does not authorize implementation or live Git writes. (WT-001–007)

## Implementation, in dependency order

- [ ] T-003: Implement canonical repository identity, safe managed paths, validated
  allocation plans/base freshness, atomic versioned receipts, owner generations,
  short locks, creation/status and interrupted-state reconciliation. Preserve
  unmanaged entries and dirty canonical source. (WT-001/002/003; AC-001/002)
- [ ] T-004: Before enabling creation, implement discovery/execution guards and
  linked-checkout credential/config validation; adapt only recognized owned hooks.
  Keep canonical scopes, runtime/data bindings and existing operations unchanged.
  Audit group component/database/dependency entry points and provider snapshot
  packaging. (WT-004/007; AC-003/004)
- [ ] T-005: Implement sanitized observed handoff, explicit owner release/transfer
  and drift-aware resume. Separate local/publication/PR/integration state and
  attribute supplied test reports. No automatic publish or merge. (WT-002/003/005;
  AC-002/005)
- [ ] T-006: Implement cleanup preview and guarded apply with remote/canonical
  retention proof, squash evidence, ignored/untracked and active-job refusal,
  non-force removal, retained branches/tombstones and interruption recovery.
  (WT-006; AC-006)

## Verification and delivery

- [ ] T-007: Add meaningful synthetic Git tests for all criteria, actual multi-process
  concurrency and process termination at each write boundary. Verify independent
  files/indexes, config/token denials, stale owners, hook targeting, runtime and
  dashboard exclusion, canonical regression, all retention blockers and recovery.
  Run focused tests and prepared-environment repository checks, relevant changed
  shell syntax, diff/relative-link checks. Record exact commands/results and
  limitations; clean only task-owned synthetic fixtures. (WT-001–007; AC-001–007)
- [ ] T-008: Write operator/agent allocation, guidance-loading, source-only checks,
  publication, handoff/resume, canonical integration, cleanup and rollback
  instructions. Preserve unknown guidance and installed host policy. Obtain a
  specifically authorized enrolled private fixture, remote-operation scope and
  retention/removal disposition before the live exercise. Run two task checkouts,
  scoped Git access, producer/consumer resume and independent app health checks;
  verify guidance in a fresh task. Record actual per-criterion evidence in
  acceptance.md, separating local/CI/private/owner observations. (WT-005/006/007;
  AC-003–007)
- [ ] T-009: Deliver implementation through a reviewed PR; verify final-revision
  CI, merge under existing authorization and obtain project-owner acceptance.
  Update index/catalogue to Delivered only after merge and all criteria pass.
  Preserve pending broader task-runtime scope and retained-resource follow-through.
  (WT-007; AC-007)

## Current handover

Only planning documents and index/catalogue references are changed. No provider,
credential, hook, runtime, database or installed-policy changes are made. The
planning branch is `codex/prj-006-spec`; implementation and acceptance are pending.
Documentation whitespace and relative-link checks are appropriate for this PR;
Terraform/runtime tests are not required for planning-only changes. Next action:
project-owner review of SPEC-031's proposed defaults and implementation scope.
