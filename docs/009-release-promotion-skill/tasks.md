# TASKS-009: Release and Production-promotion Skill

- **Status:** Draft; implementation not authorized
- **Owner:** Daniel
- **Specification:** [SPEC-009](./spec.md)
- **Design:** [TDD-009](./technical-design.md)
- **Last updated:** 2026-09-30

- [x] **T-001** Review feature/architecture and existing host-pipeline boundary;
  draft standalone plans and index/catalogue links.
- [ ] **T-002 Owner:** Approve skill scope and authorize implementation. Separately
  select a product release contract before live integration; this does not
  authorize any production release (REL-001/002).
- [ ] **T-003** After scope approval, write workflow, contract reference and
  release-record outline covering REL-001–004.
- [ ] **T-004** Run synthetic readiness, authorization, async dispatch, health,
  and recovery scenarios; validate package and relevant repository checks;
  record AC-001–004 without real tags, publications, or deployments.
- [ ] **T-005** After T-004 and product-pipeline readiness, obtain concrete
  rehearsal scope and run AC-005 on the existing isolated non-production target.
  Missing prerequisites leave this task pending, not silently waived.
- [ ] **T-006** Record criterion evidence, CI, run identities and limitations;
  publish PR, obtain review/merge authorization, record merge and update catalogue
  with actual acceptance. Preserve release records; clean owned test artifacts.

Current handover: planning only. Implementing this skill requires none of the
other AGT-006/008/009/010 packages. Its live acceptance requires a separately
approved product pipeline. No release operation is authorized by these plans.
