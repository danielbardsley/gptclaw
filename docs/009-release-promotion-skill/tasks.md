# TASKS-009: Release and Production-promotion Skill

- **Status:** Implementation authorized; work in progress
- **Owner:** Daniel
- **Specification:** [SPEC-009](./spec.md)
- **Design:** [TDD-009](./technical-design.md)
- **Last updated:** 2026-10-01

- [x] **T-001** Review feature/architecture and existing host-pipeline boundary;
  draft standalone plans and index/catalogue links.
- [ ] **T-002 Owner:** Approve skill scope and authorize implementation. Separately
  select a product release contract before live integration; this does not
  authorize any production release (REL-001/002).
- [x] **T-003** After scope approval, write workflow, contract reference and
  release-record outline covering REL-001–004.
- [x] **T-004** Run synthetic readiness, authorization, async dispatch, health,
  and recovery scenarios; validate package and relevant repository checks;
  record AC-001–004 without real tags, publications, or deployments.
- [ ] **T-005** After T-004 and product-pipeline readiness, obtain concrete
  rehearsal scope and run AC-005 on the existing isolated non-production target.
  Missing prerequisites leave this task pending, not silently waived.
- [ ] **T-006** Record criterion evidence, CI, run identities and limitations;
  publish PR, obtain review/merge authorization, record merge and update catalogue
  with actual acceptance. Preserve release records; clean owned test artifacts.

Current handover: skill/resources and 18 synthetic evaluations complete. Scope
approval in T-002 was supplied on 2026-09-30; product-contract selection remains
pending. T-005 waits for that dependency and scoped rehearsal authorization;
T-006 awaits owner review and merge; full checks and PR CI run #70 passed. See [acceptance](acceptance.md).
No release operation is authorized by implementation approval.
