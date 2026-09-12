# TASKS-002: Automated EBS Snapshots

- **Status:** Implementation in progress
- **Owner:** Daniel
- **Specification:** [SPEC-002](./spec.md)
- **Technical design:** [TDD-002](./technical-design.md)
- **Last updated:** 2026-09-12

## Working rules

The owner authorized implementation and accepts silent DLM failures. Implement
snapshots and retention only. All AWS mutations use committed Terraform ->
GitHub Actions -> HCP Terraform. Preserve live data, attachment, host access,
and deployment-role self-management restrictions.

## Phase 0: Inputs and authorization

- [x] **0.1 Owner:** Approve implementation and the simplified scope.
- [x] **0.2 Operator:** Read-only verification of current account/Region, volume,
  encryption key, attachment, and existing deletion protection.
- [x] **0.3 Operator:** Supply authorized HCP maintenance credentials for the
  deployment-role update. The owner explicitly approved a one-time existing-key
  exception on 2026-09-12; sensitive HCP variables were removed after the attempt
  and successful apply. No values were sent in chat.
- [x] **0.4 Repository:** Check pinned provider schema and official DLM/IAM docs.

**Gate:** Passed; see the [deployment record](./deployment-attempt-2026-09-12.md).

## Phase 1: Deployment-permission prerequisite

- [x] **1.1 Repository:** Add narrowly scoped DLM plan reads, tagged policy
  management, one service role, and passing only that role to DLM.
- [x] **1.2 Repository:** Test IAM boundaries, tag/Region conditions, and absence
  of host privilege expansion or notification/monitor permissions.
- [x] **1.3 Repository:** Document temporary HCP authentication, protected
  plan/apply, cleanup on failure, and restoration of OIDC.
- [x] **1.4 Repository:** Prepare separate prerequisite PR with passing local
  checks: [PR #3](https://github.com/danielbardsley/gptclaw/pull/3).
- [x] **1.5 Operator:** Review/merge prerequisite after CI; configure temporary
  HCP credentials, inspect the protected plan, and apply the two expected
  inline-policy updates plus twelve revision-tag-only resource updates explicitly
  approved by the owner. GitHub #42 / HCP run-JpBLUBdNJJhCFFJE succeeded.
- [x] **1.6 Operator:** Remove every temporary credential variable, restore
  phase-specific OIDC, and verify a new protected remote plan.
  GitHub #43 / HCP run-NSkiDND3mwXgV7d9 reported no changes.

**Gate:** Passed: permissions installed, credentials removed, OIDC verified.

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

- [x] **4.1 Operator:** Merge reviewed feature after prerequisite completion;
  inspect the protected remote plan and apply with exact confirmation.
- [x] **4.2 Operator:** Verify unchanged compute/attachment/key/protection/access,
  enabled policy, matching volume set, and completed permission attachments.
- [ ] **4.3 Operator:** Observe a naturally scheduled completed snapshot. Record
  source, policy, timestamp, encryption/key, and private permissions.
- [x] **4.4 Operator:** Record retention expiry or assign Daniel a dated
  follow-up after at least eight daily runs, as allowed by AC-005.
  Daniel: 2026-09-21. Expiry is not yet observed.
- [ ] **4.5 Operator:** Verify a same-revision/variable pipeline plan reports no
  unexpected changes or drift from service-created snapshots.
  Post-deployment plan #47 has no changes; repeat after the first scheduled
  snapshot completes before marking this criterion passed.
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
