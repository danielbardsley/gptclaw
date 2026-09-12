# TASKS-005: Nested Guidance Pattern

- **Status:** Draft; implementation awaits approval
- **Owner:** Daniel
- **Specification:** [SPEC-005](./spec.md)
- **Technical design:** [TDD-005](./technical-design.md)
- **Last updated:** 2026-09-12

## Phase 0: Planning and review

- [x] **0.1** Inspect AGT-003, architecture, root-template spec/design/tasks,
  current guidance, and Git status; preserve unrelated work.
- [x] **0.2** Draft spec, companion design, and tasks; link initiative 005 and
  mark AGT-003 Draft in the catalogue.
- [ ] **0.3 Owner:** Review scope and authorize implementation, including the
  single infrastructure adoption, file budgets, examples, and remote scenarios.

**Gate:** This request authorizes drafting. Implementation approval is not yet
recorded; no active guidance or runtime changes are part of phase 0.

## Phase 1: Baseline and reusable pattern

Depends on phase 0 approval.

- [ ] **1.1** Recheck Git status, applicable instructions/overrides, current
  command sources, client discovery behavior, and effective chain budgets.
- [ ] **1.2** Define the nested authoring contract and version metadata; write
  the inert template, placement/adaptation guide, and five inert examples.
- [ ] **1.3** Review scope, parent relationships, local specialization, command
  applicability, conflict handling, and preservation of shared constraints.

**Gate:** NAG-001–005 are represented in a reviewable reusable pattern.

## Phase 2: Adoption and offline verification

Depends on phase 1.

- [ ] **2.1** Adapt only `infra/dev-host/AGENTS.md`; add the root discovery
  pointer and guide link while retaining the existing root contract.
- [ ] **2.2** Build inert fixture sources for siblings, deeper guidance,
  override shadowing, and conflicts; materialize only in task-owned scratch Git.
- [ ] **2.3** Add narrow positive/negative authoring checks and a command
  sentinel; integrate with repository checks and review workflow path coverage.
- [ ] **2.4** Run repository checks, changed-shell syntax checks, diff checks,
  and local-link review. Run Terraform checks only if actual Terraform changes
  become separately approved; report exact results and skipped checks.
- [ ] **2.5** Rehearse adoption and update rollback, preserving unrelated
  committed and uncommitted work. Document version/update ownership.
- [ ] **2.6** Obtain review of resulting active guidance and publish a
  reviewable implementation PR with sanitized local evidence.

**Gate:** AC-001–003 and AC-007 have concrete evidence; actual loading remains
unproven until phase 3.

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
