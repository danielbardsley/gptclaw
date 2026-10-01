# TASKS-011: Architecture Decision Records

- **Status:** Implementation merged; remaining acceptance tracked below
- **Owner:** Daniel
- **Specification:** [SPEC-011](./spec.md)
- **Design:** [TDD-011](./technical-design.md)
- **Last updated:** 2026-10-01

- [x] **T-001** Review architecture decision intent and existing skill-distribution
  evidence; draft independent plans and catalogue/index links.
- [x] **T-002 Owner:** Approve convention, proposed pilot and metadata format;
  authorize implementation. This does not accept the unwritten pilot's rationale.
- [x] **T-003** After T-002, write template/guide, index and pilot proposal with
  actual source links; preserve distinctions between facts and new decisions
  (ADR-001–003, AC-001).
- [x] **T-004** Add narrow metadata/link/lifecycle checks and synthetic positive/
  negative cases, including multi-hop/partial supersession; integrate relevant
  repository/CI checks (ADR-002/004, AC-002/003).
- [ ] **T-005** Conduct source-grounded pilot review and reader evaluation;
  record Daniel's actual disposition and any changes without fabricated approval
  (ADR-001–004, AC-004).
- [ ] **T-006** Record AC-001–005 evidence and CI, publish PR and obtain merge
  authorization. Record actual merge, update catalogue, and clean owned fixtures.

Current handover: Daniel approved the resulting implementation and authorized
merge on 2026-10-01. [PR #20](https://github.com/danielbardsley/gptclaw/pull/20)
merged as `033c30b96ae355b0de54ddb24cf1c2f405328920`; all 107 repository tests and final PR CI run #71 passed.
ADR-0001 remains Proposed; Daniel's explicit disposition of the decision remains pending (T-005).
The delivery-record task retains any outstanding acceptance/fixture closeout;
review and merge themselves are complete. See [acceptance](acceptance.md).
