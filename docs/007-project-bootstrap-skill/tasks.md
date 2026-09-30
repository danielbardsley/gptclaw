# TASKS-007: Project Bootstrap Skill

- **Status:** Draft; implementation not authorized
- **Owner:** Daniel
- **Specification:** [SPEC-007](./spec.md)
- **Design:** [TDD-007](./technical-design.md)
- **Last updated:** 2026-09-30

## 0. Planning and approval

- [x] **0.1** Inspect existing conventions, source skill/template, feature
  dependencies, and Git state; draft initiative 007 and catalogue/index links.
- [ ] **0.2 Owner:** Approve planning-starter scope and authorize implementation.

Gate: a request to write this specification is not implementation authorization.

## 1. Starter and workflow

Depends on 0.2.

- [ ] **1.1** Recheck applicable subtree guidance, actual source revisions,
  destination permissions, and existing skill names.
- [ ] **1.2** Adapt the approved root-guidance pattern and create a minimal
  planning starter with no fabricated commands or runtime capabilities.
- [ ] **1.3** Write the bootstrap skill's input, creation, verification, and
  handoff procedure. Preserve existing authorization and distribution boundaries.

Gate: reviewable starter and workflow cover PBS-001/PBS-003 and AC-001.

## 2. Safe local creation

Depends on phase 1.

- [ ] **2.1** Implement immutable-source allowlisting, metadata/path validation,
  provenance, and complete skill copying (PBS-002/PBS-004).
- [ ] **2.2** Implement and test exclusive publication, local Git initialization,
  idempotent unchanged retry, modified-output refusal, and failure cleanup.
- [ ] **2.3** Add positive/negative tests and preservation sentinels for AC-002
  and AC-003; cover documented failure and concurrency windows.

Gate: no source secrets/settings copied, no user-owned paths overwritten, and
source-checkout-independent output demonstrated structurally.

## 3. Verification and evidence

Depends on phase 2.

- [ ] **3.1** Evaluate synthetic creation and first-feature planning using only
  the generated project; inspect artifacts against AC-001/003/004.
- [ ] **3.2** Run supported-client explicit and implicit invocation in the new
  project; record client/revision/output evidence for AC-005 or a precise gap.
- [ ] **3.3** Integrate tests and CI path coverage; run repository checks,
  changed-script checks, diff and link review. Preserve protected deploy gates.
- [ ] **3.4** Record AC-001–006 evidence, actual results, limitations, update/
  rollback steps, and clean only owned fixtures after recording evidence.

Gate: structural checks, behavioral evaluation, client discovery, and owner
acceptance are distinct. No unexecuted operation is recorded as passing.

## 4. Delivery

- [ ] **4.1** Publish implementation PR, record CI, and obtain resulting-change
  review/merge authorization. Record the actual merge revision.
- [ ] **4.2** Update catalogue and handover after merge: Deployed when available,
  Delivered only after required acceptance. State remaining owners/actions and
  Git status; do not close earlier initiatives without their own evidence.

## Current handover

Planning only. Proposed first release creates local planning-ready repositories
and copies AGT-004; application stacks and remote repository automation remain
separate. Daniel reviews SPEC-007 before implementation. No starter, helper,
bootstrap skill, or new project has been created by this planning task.
