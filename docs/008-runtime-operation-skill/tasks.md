# TASKS-008: Runtime-operation Skill

- **Status:** Implementation authorized; work in progress
- **Owner:** Daniel
- **Specification:** [SPEC-008](./spec.md)
- **Design:** [TDD-008](./technical-design.md)
- **Last updated:** 2026-10-01

- [x] **T-001** Inspect catalogue/architecture and actual repository capability;
  draft independent plans and link initiative 008.
- [ ] **T-002 Owner:** Approve scope/implementation. Record provider dependencies
  separately; choose concrete contract/version before live integration (ROP-001).
- [x] **T-003** After T-002 approval, write skill, operation reference and report
  outline; retain missing-provider blocking behavior (ROP-001–004).
- [x] **T-004** After T-003, run synthetic target/auth/state/log scenarios and
  relevant package/repository checks; record AC-001–004 results.
- [ ] **T-005** After T-004 and actual provider readiness, select a disposable
  managed development service and exercise fresh-client live operations for
  AC-005. Keep this gate pending if the runtime dependencies remain unavailable.
- [ ] **T-006** Record AC-001–006 evidence, actual CI, limitations and owners;
  publish implementation PR and obtain review/merge authorization. Update
  catalogue after actual merge and acceptance; clean owned fixtures only.

Current handover: scope approved and implementation authorized on 2026-09-30.
T-002's scope approval is complete; concrete live-provider selection remains
pending. Skill/resources and 17 synthetic evaluations are complete. T-005 waits
for the real runtime; T-006 awaits owner review and merge; full checks and PR CI run #70 passed. See
[acceptance evidence](acceptance.md). The other four initiatives are not dependencies.
