# TASKS-009: Release and Production-promotion Skill

- **Status:** Implementation merged; remaining acceptance tracked below
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

Current handover: Daniel approved the resulting implementation and authorized
merge on 2026-10-01. [PR #20](https://github.com/danielbardsley/gptclaw/pull/20)
merged as `033c30b96ae355b0de54ddb24cf1c2f405328920`; all 107 repository tests and final PR CI run #71 passed.
Live non-production rehearsal waits for the product contract and separately scoped operations (T-002/T-005).
The delivery-record task retains any outstanding acceptance/fixture closeout;
review and merge themselves are complete. See [acceptance](acceptance.md).
