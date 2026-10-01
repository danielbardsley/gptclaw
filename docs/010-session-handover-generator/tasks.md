# TASKS-010: Session Handover Generator

- **Status:** Implementation authorized; work in progress
- **Owner:** Daniel
- **Specification:** [SPEC-010](./spec.md)
- **Design:** [TDD-010](./technical-design.md)
- **Last updated:** 2026-10-01

- [x] **T-001** Review existing project/session evidence conventions and draft
  independent spec/design/tasks with index/catalogue links.
- [x] **T-002 Owner/implementation:** After Daniel approves scope and authorizes
  implementation, write the skill and handover outline (HND-001–004).
- [x] **T-003** Create synthetic producer fixtures; evaluate factual state,
  freshness, authorization, read minimization and save collision behavior for
  AC-001–004. Run appropriate package/repository checks.
- [x] **T-004** Give an independent consumer only the generated handover and
  permitted project files; inspect next-step understanding and actions (AC-005).
- [ ] **T-005** Exercise supported-client selection/invocation, record revision
  and actual results. Missing access leaves that acceptance explicit (AC-006).
- [ ] **T-006** Publish evidence and PR; obtain resulting-change review/merge,
  update catalogue after actual merge and acceptance, preserve user work and
  remove only owned fixtures. No message or handoff to another real chat is
  implied by testing this feature.

Current handover: skill/outline and independent producer/consumer evaluations
complete, including a verified correction separating unrelated pending operations
from independent work. T-005 fresh supported-client selection and T-006 review/merge remain pending;
the full repository suite and PR CI run #70 passed. See [acceptance](acceptance.md).
