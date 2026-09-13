# TASKS-005: Nested Guidance Pattern

- **Status:** Implemented; review and remote acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-005](./spec.md)
- **Technical design:** [TDD-005](./technical-design.md)
- **Last updated:** 2026-09-13

## Phase 0: Planning and review

- [x] **0.1** Inspect AGT-003, architecture, root-template spec/design/tasks,
  current guidance, and Git status; preserve unrelated work.
- [x] **0.2** Draft spec, companion design, and tasks; link initiative 005 and
  mark AGT-003 Draft in the catalogue.
- [x] **0.3 Owner:** Review scope and authorize implementation, including the
  single infrastructure adoption, file budgets, examples, and remote scenarios.

**Gate:** Daniel approved the specification and authorized implementation on
2026-09-13. Review of resulting guidance, merge, and remote acceptance remain
separate gates; no repeat implementation approval is required.

## Phase 1: Baseline and reusable pattern

Depends on phase 0 approval.

- [x] **1.1** Recheck Git status, applicable instructions/overrides, current
  command sources, client discovery behavior, and effective chain budgets.
- [x] **1.2** Define the nested authoring contract and version metadata; write
  the inert template, placement/adaptation guide, and five inert examples.
- [x] **1.3** Review scope, parent relationships, local specialization, command
  applicability, conflict handling, and preservation of shared constraints.

**Gate:** NAG-001–005 are represented in a reviewable reusable pattern.

## Phase 2: Adoption and offline verification

Depends on phase 1.

- [x] **2.1** Adapt only `infra/dev-host/AGENTS.md`; add the root discovery
  pointer and guide link while retaining the existing root contract.
- [x] **2.2** Build inert fixture sources for siblings, deeper guidance,
  override shadowing, and conflicts; materialize only in task-owned scratch Git.
- [x] **2.3** Add narrow positive/negative authoring checks and a command
  sentinel; integrate with repository checks and review workflow path coverage.
- [x] **2.4** Run repository checks, changed-shell syntax checks, diff checks,
  and local-link review. Run Terraform checks only if actual Terraform changes
  become separately approved; report exact results and skipped checks.
- [x] **2.5** Rehearse adoption and update rollback, preserving unrelated
  committed and uncommitted work. Document version/update ownership.
- [x] **2.6a** Publish implementation and sanitized local evidence in PR #11.
- [ ] **2.6b Owner:** Review the resulting active guidance revision.

**Gate:** Local evidence for AC-001–003 and AC-007 is recorded; owner review of
the resulting guidance and actual loading remain pending.

## Phase 3: Fresh-task acceptance and delivery

Depends on phase 2 and review of the adopted revision.

- [ ] **3.1** Verify direct infrastructure starts and root-started discovery
  through the supported remote connection, without supplying policy answers.
- [ ] **3.2** Verify synthetic siblings, deeper specialization, cross-area
  work, override shadowing, and conflict handling with read-only scenarios.
- [ ] **3.3** Record instruction sources, effective budgets, reviewed revision,
  client/profile metadata, results, and unresolved limitations. Resolve failures
  through review and repeat affected scenarios in fresh tasks.
- [ ] **3.4** Map AC-001–008 to actual evidence in `acceptance.md`; record merged
  implementation PR and keep earlier initiatives' acceptance status separate.
- [ ] **3.5** Clean only task-owned fixtures after recording evidence. Mark
  AGT-003 Delivered only after merge and all criteria pass; otherwise state
  pending work. Hand over changed files, verification, limitations, and Git state.

**Gate:** Static checks or merge alone do not establish completion.

## Traceability

| Requirement | Tasks | Acceptance |
|---|---|---|
| NAG-001 | 1.2, 1.3, 2.1 | AC-001, AC-002 |
| NAG-002 | 1.1, 1.2, 2.1, 3.1–3.3 | AC-004–006 |
| NAG-003 | 1.3, 2.1, 3.2 | AC-002, AC-005, AC-006 |
| NAG-004 | 1.1, 2.1, 2.4, 3.3 | AC-001, AC-002, AC-006 |
| NAG-005 | 1.2, 2.5, 2.6 | AC-002, AC-007 |
| NAG-006 | 2.2–2.4, 3.1–3.5 | AC-003–006, AC-008 |

## Current handover

Implementation is in [PR #11](https://github.com/danielbardsley/gptclaw/pull/11).
The repository gate passes 41 tests: installer 17, bootstrap 5, root guidance 10,
nested guidance 9. Shell syntax, whitespace, and local-link checks are recorded
in [acceptance](./acceptance.md). Test-owned scratch fixtures were cleaned.
Phase 3 remote scenarios have a reproducible fixture helper and reviewer matrix
in the nested guide; no remote behavior is claimed from this continuing task.
Daniel owns resulting-policy review, supported-connection acceptance, and merge.
