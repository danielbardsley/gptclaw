# TASKS-002: Automated EBS Snapshots

- **Status:** Implementation in progress
- **Owner:** Daniel
- **Specification:** [SPEC-002](./spec.md)
- **Technical design:** [TDD-002](./technical-design.md)
- **Last updated:** 2026-09-06

## Working rules

The owner authorized implementation and accepts silent DLM failures. Implement
snapshots and retention only. All AWS mutations use committed Terraform ->
GitHub Actions -> HCP Terraform. Preserve live data, attachment, host access,
and deployment-role self-management restrictions.

## Phase 0: Inputs and authorization

- [x] **0.1 Owner:** Approve implementation and the simplified scope.
- [ ] **0.2 Operator:** Read-only verification of current account/Region, volume,
  encryption key, attachment, and existing deletion protection.
- [ ] **0.3 Operator:** Supply an already-authorized, short-lived HCP maintenance
  session for the deployment-role update. Never send credentials to the task.
- [x] **0.4 Repository:** Check pinned provider schema and official DLM/IAM docs.

**Gate:** Deployment waits for an authorized maintenance session; local work can
continue.

## Phase 1: Deployment-permission prerequisite

- [x] **1.1 Repository:** Add narrowly scoped DLM plan reads, tagged policy
  management, one service role, and passing only that role to DLM.
- [x] **1.2 Repository:** Test IAM boundaries, tag/Region conditions, and absence
  of host privilege expansion or notification/monitor permissions.
- [x] **1.3 Repository:** Document temporary HCP authentication, protected
  plan/apply, cleanup on failure, and restoration of OIDC.
- [x] **1.4 Repository:** Prepare separate prerequisite PR with passing local
  checks: [PR #3](https://github.com/danielbardsley/gptclaw/pull/3).
- [ ] **1.5 Operator:** Review/merge prerequisite after CI; configure temporary
  HCP session only, inspect the protected plan, and apply only the two expected
  inline-policy updates.
- [ ] **1.6 Operator:** Remove every temporary credential variable, restore
  phase-specific OIDC, and verify a new protected remote plan.

**Gate:** Permissions installed, credentials removed, OIDC verified.

## Phase 2: Snapshot implementation

- [x] **2.1 Repository:** Add validated schedule/retention inputs, examples, and
  non-secret outputs.
- [x] **2.2 Repository:** Add a dedicated selection tag to the existing project
  volume without altering its storage, key, attachment, or lifecycle.
- [x] **2.3 Repository:** Implement one custom DLM VOLUME policy, the declared
  schedule/count, and explicit non-secret snapshot tags.
- [x] **2.4 Repository:** Implement scoped DLM trust, source-volume creation,
  new/owned snapshot tagging, and policy-attributed deletion.
- [x] **2.5 Repository:** Test defaults, overrides, invalid inputs, selection,
  privacy/encryption, lifecycle IAM, and preserved host/deployment controls.

**Gate:** Policy code passes local checks without any new runtime or alerting
resources.

## Phase 3: Operations and review

- [x] **3.1 Repository:** Write manual backup inspection, diagnosis, retention,
  safe rollback, and cost guidance.
- [x] **3.2 Repository:** Update recovery guidance for completed-snapshot
  selection and RES-002 pipeline-only restore handoff. Preserve historical
  SPEC-001 acceptance facts.
- [x] **3.3 Repository:** Run repository checks, Terraform formatting,
  backend-free validation and mocked tests; review the complete diff.
- [x] **3.4 Repository:** Push feature PR with the prerequisite dependency and
  precise validation evidence: [PR #4](https://github.com/danielbardsley/gptclaw/pull/4).

**Gate:** Reviewable code and operational documentation with passing CI.

## Phase 4: Deployment and acceptance

- [ ] **4.1 Operator:** Merge reviewed feature after prerequisite completion;
  inspect the protected remote plan and apply with exact confirmation.
- [ ] **4.2 Operator:** Verify unchanged compute/attachment/key/protection/access,
  enabled policy, matching volume set, and completed permission attachments.
- [ ] **4.3 Operator:** Observe a naturally scheduled completed snapshot. Record
  source, policy, timestamp, encryption/key, and private permissions.
- [ ] **4.4 Operator:** Record retention expiry or assign Daniel a dated
  follow-up after at least eight daily runs, as allowed by AC-005.
- [ ] **4.5 Operator:** Verify a same-revision/variable pipeline plan reports no
  unexpected changes or drift from service-created snapshots.
- [ ] **4.6 Repository:** Record each active acceptance criterion with sanitized
  evidence and outstanding limitations.
- [ ] **4.7 Owner/repository:** Mark the feature complete only after all active
  acceptance criteria pass. Restore remains unproven until RES-002.

**Gate:** Automated snapshots accepted; no notification or freshness checks are
required.

## Traceability

| Requirement | Tasks | Acceptance |
|---|---|---|
| BAK-001 | 1.1-1.6, 2.3, 3.3-3.4, 4.1, 4.5 | AC-001, AC-002, AC-009 |
| BAK-002 | 0.2, 2.2-2.5, 4.2 | AC-001, AC-003 |
| BAK-003 | 2.1, 2.3, 2.5, 4.3-4.4 | AC-004, AC-005 |
| BAK-004 | 0.2, 2.3-2.5, 4.3 | AC-001, AC-004 |
| BAK-005 | 1.1-1.6, 2.4-2.5 | AC-001, AC-002 |
| BAK-007 | 2.1, 3.1-3.2, 4.6-4.7 | AC-004, AC-010 |
| Safety/rollback | 1.3, 1.6, 3.1-3.3, 4.1-4.2, 4.5 | AC-002, AC-009, AC-010 |
