# TASKS-006: Specification Skill

- **Status:** Implemented; review, merge, and supported-client acceptance pending
- **Owner:** Daniel
- **Specification:** [SPEC-006](./spec.md)
- **Technical design:** [TDD-006](./technical-design.md)
- **Last updated:** 2026-09-30

## Phase 0: Planning and review

- [x] **0.1** Review AGT-004, architecture, existing document conventions,
  applicable guidance, skill-authoring guidance, and Git state.
- [x] **0.2** Draft specification, design, and tasks; link initiative 006 and
  mark AGT-004 Draft in the catalogue.
- [ ] **0.3 Owner:** Approve concrete scope and authorize implementation.

**Gate:** Daniel approved SPEC-006 and explicitly authorized implementation on
2026-09-30. No repeat implementation approval is required.

## Phase 1: Skill package

Depends on phase 0 approval.

- [x] **1.1** Recheck applicable guidance, repository skill discovery support,
  existing skill names, and Git state; preserve unknown files and settings.
- [x] **1.2** Write the concise skill entrypoint and four outlines.
- [x] **1.3** Review new/update/acceptance flows against SPS-001–005, including
  stable IDs, prior authorization, proportionality, and evidence boundaries.

**Gate:** Reviewable package satisfies the document contract without a global
installation or feature-implementation side effect.

## Phase 2: Verification

Depends on phase 1.

- [x] **2.1** Add narrow structural tests and inert synthetic scenario inputs;
  integrate checks and relevant CI path filters without changing deploy gates.
- [x] **2.2** Run focused tests, repository checks, changed-shell syntax,
  whitespace checks, and local-link review. Report unavailable checks exactly.
- [x] **2.3** Run behavioral scenarios for new planning, bounded updates,
  ambiguity, prior authorization, and mixed acceptance evidence in isolated
  task-owned fixtures; review outputs against AC-002–005.
- [ ] **2.4** Verify explicit invocation, automatic relevant selection, and
  unrelated-request behavior through the supported client; record client,
  revision, scenario, results, and limitations for AC-006.
- [x] **2.5** Record sanitized evidence against AC-001–007 in acceptance.md;
  document update/rollback and remove only owned temporary fixtures.

**Gate:** File checks do not substitute for behavioral or client evidence.
Failures require a scoped fix and repeat of affected scenarios; unavailable
execution paths stay pending with an owner and next action.

## Phase 3: Review and delivery

Depends on phase 2; a PR may be opened earlier for review.

- [x] **3.1** Publish implementation PR and record actual CI results.
- [ ] **3.2 Owner:** Review and authorize merge of the resulting skill revision.
- [ ] **3.3** Record merged revision and remaining acceptance; mark AGT-004
  Delivered only after all criteria pass. Keep prior initiatives' status intact.
- [x] **3.4** Hand over changed files, verification, limitations, remaining
  actions, and Git state.

## Current handover

The repository skill, four outlines, package tests, synthetic scenarios, and CI
path coverage are implemented in PR #16. All 51 repository tests and the bundled
skill validator pass. CI run #61 passed for package revision 1d85796; five
synthetic behavioral scenarios passed after review. Supported-client limitations are
tracked in [acceptance](./acceptance.md). No global skill installation, deployment,
or merge has been performed.
