# TASKS-002: Automated EBS Snapshots

- **Status:** Planned; implementation not started
- **Owner:** Daniel
- **Specification:** [SPEC-002](./spec.md)
- **Technical design:** [TDD-002](./technical-design.md)
- **Last updated:** 2026-09-06

## Working rules

These tasks implement RES-001 only. All implementation boxes remain unchecked.
The approved specification authorizes planning; the current request is to create
these documents and keep them on the feature branch. Do not merge, deploy, or
change HCP/AWS configuration as part of this documentation task.

Repository tasks produce reviewable code, tests, or documentation. Operator
tasks require the named external configuration or live evidence. AWS mutations
use committed Terraform -> GitHub Actions -> HCP Terraform. Remote plan/apply
jobs remain restricted to current `main`; branch review must not weaken that
gate. Preserve the live volume and user changes.

## Phase 0: Review and implementation inputs

**Entry:** SPEC-002 approved; TDD-002 available for review.

- [ ] **0.1 Repository/owner:** Review D-001 through D-007, the proposed input
  contract, email behavior, timing bounds, and the explicit one-time identity
  maintenance exception. Record design approval and implementation authorization.
- [ ] **0.2 Operator:** Confirm deployed account, Region, project-volume ID,
  encryption key, attachment, protection, and matching tags using read-only
  inspection. Compare with Terraform outputs, not historical inventory.
- [ ] **0.3 Operator:** Identify an already-authorized short-lived session for
  the narrow identity-maintenance apply. Confirm it can refresh the root and
  update only the two intended inline policies. Do not create credentials or
  roles out of band.
- [ ] **0.4 Repository:** Verify pinned Terraform/AWS provider schemas, Lambda
  runtime support, DLM tagging permissions, and alarm dimensions against official
  documentation. Record any design corrections before implementation.
- [ ] **0.5 Operator:** Supply the notification email through sensitive HCP
  configuration when rollout is scheduled; arrange subscription confirmation.
  Set the fixed initial enablement timestamp immediately before feature rollout,
  not during this planning phase.

**Exit:** Design and implementation authorized; target and credential path known.
Absence of the authorized session blocks deployment, not local coding.

## Phase 1: Prepare deployment-permission maintenance

**Entry:** Phase 0 decisions accepted.

- [ ] **1.1 Repository:** Add narrowly scoped plan reads and apply resource
  management permissions in `hcp_identity.tf` for DLM, monitoring, SNS, and
  the two runtime roles. Include optional test resources with separate scope.
  Preserve denial-by-absence of deployment-role/OIDC self-management.
- [ ] **1.2 Repository:** Add tests for role passing, permitted role/resource
  names, Region/namespace conditions, wildcard justification, and absence of
  host privilege expansion. Update the repository invariant checks if needed
  so they cover all new permission statements.
- [ ] **1.3 Repository:** Clarify the maintenance runbook: session variable
  names, temporary dynamic-auth disablement, protected plan/apply, no `-target`,
  failure cleanup, and restoration of phase-specific OIDC.
- [ ] **1.4 Repository:** Run existing repository and Terraform checks. Prepare
  a dedicated prerequisite PR containing only identity policies, tests, and
  maintenance documentation; retain its revision for review.

**Exit:** Reviewable prerequisite with no feature resources or compute changes.

## Phase 2: Apply and close the identity prerequisite

**Entry:** Implementation authorized and prerequisite PR reviewed.

- [ ] **2.1 Operator:** Merge the prerequisite; place the expiring AWS session
  only in sensitive HCP environment variables, including session token. Record
  settings to restore without recording values; remove authentication conflicts.
- [ ] **2.2 Operator:** Dispatch protected plan from current `main`. Verify only
  the expected two inline policies change and account/Region are correct.
- [ ] **2.3 Operator:** Dispatch the exact-confirmation apply through the existing
  workflow. Record matching GitHub/HCP revision and run links.
- [ ] **2.4 Operator:** Remove all temporary session variables and restore OIDC
  settings on success or failure. Verify with a fresh protected remote plan.
  Do not leave temporary credentials configured while coding the feature.

**Exit:** Narrow permissions installed, temporary credentials removed, OIDC
plan verified. If the stage fails, restore authentication and repair via review.

## Phase 3: Implement snapshot policy

**Entry:** Design approved; coding can proceed while Phase 2 awaits an operator.

- [ ] **3.1 Repository:** Add validated policy inputs and fixed enablement-time
  contract. Add examples containing placeholders only, and non-secret outputs.
- [ ] **3.2 Repository:** Add the dedicated tag to the existing volume without
  changing size, key, attachment, lifecycle, bootstrap, or networking.
- [ ] **3.3 Repository:** Implement one custom DLM VOLUME policy, the declared
  schedule/count, explicit snapshot tag allowlist, and no sharing/copy/archive
  options. Generated snapshots must remain outside Terraform state.
- [ ] **3.4 Repository:** Implement dedicated DLM trust and scoped create/read,
  tagging, and policy-attributed deletion permissions. Separate post-policy
  permissions to avoid dependency cycles. Verify the initial scheduling window
  permits all attachments to complete.
- [ ] **3.5 Repository:** Add Terraform tests for valid/invalid inputs, exact
  selection, stable tags, retention, encryption/privacy, IAM positive/negative
  cases, and preservation of existing host controls.

**Exit:** Snapshot configuration and tests satisfy BAK-001 through BAK-005.

## Phase 4: Implement monitoring and notification

**Entry:** Resource/input names from Phase 3 established.

- [ ] **4.1 Repository:** Implement pure state evaluation and paginated read
  adapters for policy, matching volumes, and own-policy/source snapshots.
  Compare UTC start timestamps; preserve no-recovery-point state during grace.
- [ ] **4.2 Repository:** Implement explicit unhealthy/unknown outcomes,
  bounded retries, allowlisted logs, all expected metric gauges, and heartbeat
  publication only with a complete observation result. Metric-write failures
  must fail the invocation.
- [ ] **4.3 Repository:** Package runtime-only Python source deterministically
  inside the HCP upload. Pin archive tooling, update the lockfile, and verify
  repeat archives do not create spurious Lambda updates.
- [ ] **4.4 Repository:** Add the five-minute rule, function, scoped invocation
  permission, execution role, 14-day logs, timeout, and concurrency limit.
- [ ] **4.5 Repository:** Add status, zero-filled heartbeat, DLM failure, Lambda,
  and EventBridge alarms with correct dimensions and missing-data treatment.
  Configure ALARM/OK actions and useful sanitized descriptions.
- [ ] **4.6 Repository:** Add the restricted SNS topic and sensitive email
  subscription. Expose confirmation status through documented reads without
  outputting the address.
- [ ] **4.7 Repository:** Test stale/fresh boundaries, grace expiry/no reset,
  missing/pending/failed/unrelated snapshots, pagination, extra/missing targets,
  disabled/error/missing policy, malformed timestamps, read failures, and
  failed telemetry. Verify no case can falsely publish healthy state.
- [ ] **4.8 Repository:** Extend credential-free CI with Python tests and
  Terraform assertions for monitoring roles, namespace restrictions, alarm
  actions, packaging, and live/test isolation.

**Exit:** BAK-006 is implemented with independently detectable monitor failures.

## Phase 5: Build acceptance harness and operational docs

**Entry:** Live evaluator and alarm definitions available.

- [ ] **5.1 Repository:** Add the default-disabled fixture function, independent
  role/namespace/dimensions, and TEST-labeled alarms using the real SNS topic.
  Use the same evaluator/publisher and alarm construction as live monitoring.
- [ ] **5.2 Repository:** Implement the bounded timeline: healthy, stale,
  recovered, inspection failure, recovered, withheld heartbeat, recovered.
  Keep each phase at least twenty minutes and the timeline at most three hours.
  Publish healthy test telemetry after expiry until removal.
- [ ] **5.3 Repository:** Add tests proving event input cannot enable fixtures
  in the live function, the test role cannot read data/write live metrics, and
  native failure alarm tests use only the custom test namespace.
- [ ] **5.4 Repository:** Write `runbooks/inspect-backups.md` covering outputs,
  current observation time, policy/volume/snapshot reads, subscription status,
  alarm semantics, diagnosis, notification limitations, and cost drivers.
- [ ] **5.5 Repository:** Update recovery guidance for snapshot selection,
  retained snapshots, policy replacement, safe disablement, and the RES-002
  pipeline-only restore handoff. Preserve historical SPEC-001 acceptance facts.

**Exit:** Safe test path and operator instructions exist before deployment.

## Phase 6: Review and deploy the feature

**Entry:** Phase 2 complete; Phases 3-5 pass all local/CI checks.

- [ ] **6.1 Repository:** Run repository security checks, Terraform formatting,
  backend-free initialization/validation/mock tests, and Python tests. Inspect
  final diff for unrelated changes and credential/generated-file leakage.
- [ ] **6.2 Operator:** Review and merge the feature PR only when authorized.
  Configure email and initial timestamp; dispatch the protected remote plan.
- [ ] **6.3 Operator:** Verify no compute replacement, attachment change,
  protection removal, key change, or inbound rule. Resolve unrelated drift
  separately rather than accepting it with the feature.
- [ ] **6.4 Operator:** Apply with the existing confirmation and environment
  gate using the ordinary OIDC apply role. Record identity, revision, and runs.
- [ ] **6.5 Operator:** Confirm SNS subscription, exact target matching, enabled
  policy, completed role attachment, monitor telemetry, alarm configuration,
  and unchanged live host/volume controls.

**Exit:** Feature deployed with ordinary identities and initial monitoring active.

## Phase 7: Capture acceptance and hand over

**Entry:** Deployment complete and email confirmed.

- [ ] **7.1 Operator:** Observe at least one naturally scheduled snapshot reach
  `completed`. Record source, policy/system tags, UTC start time, state,
  encryption/key, private permissions, and monitor-reported age. A pending
  snapshot or successful policy apply is insufficient.
- [ ] **7.2 Operator:** Enable the isolated harness through the pipeline.
  Measure ALARM/OK email arrivals, unhealthy detection, missing-monitor
  detection, and recovery against TDD-002 timing bounds. Label synthetic and
  observed AWS evidence separately.
- [ ] **7.3 Operator:** Remove test resources through a reviewed pipeline apply.
  Confirm live monitoring remained active throughout and no test alarms remain.
- [ ] **7.4 Operator:** Inspect approved retention and policy-attributed snapshot
  inventory. Record observed expiry, or assign Daniel a dated follow-up after
  at least eight daily runs, as permitted by AC-005.
- [ ] **7.5 Operator:** Run a same-revision, same-variable pipeline plan and
  verify no unexpected changes or drift from DLM-created snapshots.
- [ ] **7.6 Repository:** Create `acceptance.md` mapping AC-001 through AC-010
  to exact evidence, including credential cleanup, notifications, live snapshot,
  timing, no-change plan, and any retention follow-up.
- [ ] **7.7 Repository/owner:** Mark spec/design/tasks and catalogue complete
  only when all acceptance conditions pass. State that restore remains unproven
  until RES-002, and retain the follow-up date/owner for any unobserved expiry.

**Exit:** Automated backups accepted, evidence retained, restore work clearly
handed to RES-002, and temporary resources/credentials removed.

## Requirement and acceptance traceability

| Requirement | Tasks | Acceptance |
|---|---|---|
| BAK-001 | 1.1-2.4, 3.3, 6.1-6.4, 7.5 | AC-001, AC-002, AC-009 |
| BAK-002 | 0.2, 3.2-3.5, 4.1, 6.5 | AC-001, AC-003 |
| BAK-003 | 3.1, 3.3, 3.5, 7.1, 7.4 | AC-004, AC-005 |
| BAK-004 | 0.2, 3.3-3.5, 4.2, 4.6, 7.1 | AC-001, AC-004 |
| BAK-005 | 1.1-2.4, 3.4, 4.4, 4.8, 5.3 | AC-001, AC-002 |
| BAK-006 | 4.1-4.8, 5.1-5.3, 7.2-7.3 | AC-006, AC-007, AC-008 |
| BAK-007 | 3.1, 5.4-5.5, 7.6-7.7 | AC-004, AC-010 |
| Safety and rollback | 1.3, 2.4, 5.1-5.5, 6.3, 7.3, 7.5 | AC-002, AC-009, AC-010 |
