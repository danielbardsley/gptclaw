# TASKS-031: Branch and worktree policy

- **Status:** Implemented — verification and review pending
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-031](spec.md) · **Design:** [TDD-031](technical-design.md)

## Planning and authorization

- [x] T-001: Inspect catalogue/index, repository guidance, current Git version,
  credential binding/configuration, runtime lock/source identity and hook behavior.
  Draft the bounded specification/design/tasks and update the index/catalogue.
  Evidence: cited source interfaces in TDD-031; this planning revision.
- [x] T-002: Project owner reviews source-only scope and proposed defaults, then
  explicitly approves the specification and authorizes implementation. Resolve
  receipt/CLI schemas and lock-order audit before dependent coding. The project owner approved the scope and authorized implementation on
  October 13: “Ok, lets implement the spec.” CLI/receipt schemas and lock order
  are now specified in TDD-031; named live fixture writes remain separately gated. (WT-001–007)

## Implementation, in dependency order

- [x] T-003: Implement canonical repository identity, safe managed paths, validated
  allocation plans/base freshness, atomic versioned receipts, owner generations,
  short locks, creation/status and interrupted-state reconciliation. Preserve
  unmanaged entries and dirty canonical source. (WT-001/002/003; AC-001/002)
- [x] T-004: Before enabling creation, implement discovery/execution guards and
  linked-checkout credential/config validation; adapt only recognized owned hooks.
  Keep canonical scopes, runtime/data bindings and existing operations unchanged.
  Audit group component/database/dependency entry points and provider snapshot
  packaging. (WT-004/007; AC-003/004)
- [x] T-005: Implement sanitized observed handoff, explicit owner release/transfer
  and drift-aware resume. Separate local/publication/PR/integration state and
  attribute supplied test reports. No automatic publish or merge. (WT-002/003/005;
  AC-002/005)
- [x] T-006: Implement cleanup preview and guarded apply with remote/canonical
  retention proof, squash evidence, ignored/untracked and active-job refusal,
  non-force removal, retained branches/tombstones and interruption recovery.
  (WT-006; AC-006)

## Verification and delivery

- [x] T-007: Add meaningful synthetic Git tests for all criteria, actual multi-process
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

Lifecycle, ownership/generations, receipt recovery, short project locks, scoped
helper refresh/membership checks, owned hook adaptation, runtime/discovery guards,
handoff and conservative cleanup are implemented. The runbook and inert agent
adoption reference are written. The local repository gate and canonical regressions passed. The expanded lifecycle and targeted timeout/UID tests passed, and all four
implementation CI workflows passed at `4db542d`. The final follow-up is evidence
only; its PR checks remain governed by the ordinary final-head merge gate. See [acceptance](acceptance.md)
for actual observations and unresolved private/owner gates. The branch remains
`codex/prj-006-spec`; PR #74 contains the implementation and evidence. Named private Git acceptance,
fresh-task guidance, owner acceptance and merge remain pending.
No installed host-policy, AWS/HCP or production changes are made.
