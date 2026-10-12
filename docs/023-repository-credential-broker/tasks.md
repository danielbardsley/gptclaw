# TASKS-023: Repository credential broker

- **Status:** Complete — implementation merged, live acceptance and main CI passed
- **Owner:** Project owner
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-023](spec.md) · **Design:** [TDD-023](technical-design.md)

## Planning and authorization

- [x] T-001: Read catalogue/sequence/architecture, delivered SPEC-022 and actual
  PAT/Git interfaces; verify current official App creation/installation/token
  documentation. Draft requirements/design/traceability. The project owner selected private
  repos with PR review without enforced branch protection for this proposal.
- [x] T-002a: The instruction “Ok, now implement the spec” approved the bounded
  design/scope and authorized implementation. The selected standing policy and
  owner-neutral naming remain in force.
- [x] T-002b: Approve exact private App settings/bootstrap/key handling
  and retained live targets, then provide App/installation IDs and the external
  private key path. Prove actual personal-account creation/inclusion/main behavior
  through the canary before activation; no broader grant/PAT fallback. CRD-001/002;
  AC-001/002. The concrete proposal is in the runbook/settings checklist.
  Owner setup, supplied IDs/key path and both retained targets/activation are now
  approved. The original selected/explicit enrollment candidates failed; after
  explicit All repositories approval the retained canary recovered, actual
  scope/grants passed readback and activation succeeded. See [live evidence](acceptance.md).

T-002 is split to distinguish completed implementation authorization from the
pending external setup/feasibility gate; it does not reopen existing approval.

## Dependency-ordered implementation

- [x] T-003: Version private setup/profile/binding/receipt contracts and build
  doctor/status, strict safe key/path readers, account/App/installation identity
  checks and selected-repository readiness. CRD-001; AC-001.
- [x] T-004: Implement maintained signing/installation-token acquisition with
  explicit one-repository/permission scope, actual response validation, fresh
  bounded lifetime, sanitized transport and no persisted bearer cache. Select
  pinned isolated tooling if needed. CRD-003/004/005; AC-003/004/005.
- [x] T-005: Integrate verified creation capability/automatic inclusion with the
  existing journaled provisioning flow and configured normal new. Explicitly
  record the activated standing policy; keep local-only/unconfigured/manual PAT
  paths and existing apps unchanged. CRD-002/006; AC-002/006.
- [x] T-006: Add exact project-local Git helper/enrollment and scoped later-PR
  path; extend reviewed Git config validation rather than permit arbitrary
  helpers. Preserve source/worktrees/remotes and reject cross-project binding
  or credential-bearing URLs. CRD-004/007; AC-004/007.
- [x] T-007: Add concurrency, renewal, response-loss reconciliation, per-project
  disable/revocation and owner-controlled App key rotation/rollback. Document
  residual lifetimes and actual versus unknown outcomes. CRD-005/007; AC-005/007.
- [x] T-008: Add meaningful offline/helper/Git transport negative tests and
  compatibility/bundle checks; update existing CI and run focused suites,
  repository/whitespace/link checks. Deliver implementation through reviewed PRs.
  CRD-001–008; AC-001–008.

## Live acceptance and delivery

- [x] T-010: Evaluate the October 11 owner-approved explicit installation
  enrollment candidate, verify the updated grant and attempt retained recovery.
  Require exact creation-journal/binding identity; keep installation
  management out of project credentials and stop on unsupported access. CRD-001/002/003;
  AC-001/002/003/005.
  Provider 1.5.1 and 43 focused tests pass; actual updated installation approval
  was verified. The same-operation live enrollment attempt failed; this candidate
  was retired in favor of the explicitly approved T-011 All repositories policy.

- [x] T-009: With explicitly approved App/installation/key/targets, prove one-time
  setup and two successive private projects without per-project credential or
  installation clicks. Verify scoped Git/PR operations, renewal, cross-repository
  denial, rotation/revocation and retained recovery. Run existing starter quality
  and private app/independent-service checks; obtain the project owner's desktop/owner
  observations. Record sanitized acceptance.md, actual final-head CI/merge and
  credential/fixture disposition. Mark the accepted slice Delivered only after
  merged implementation and all criteria pass. AC-001–008.

- [x] T-011: Implement/test the explicitly approved All repositories policy,
  schema-2 inactive-profile migration and exact singleton project tokens; remove
  the unused installation-management grant. Resume the retained first operation,
  then activate and create the approved second project through normal new. Record
  actual broad App authority separately from project-token scope. CRD-001–008;
  AC-001–008. The owner instruction “Lets do all repos” and completed GitHub
  installation switch authorize this amendment; no repeat approval is required.

## Current handover

Provider 1.5.2 implements private App profile/doctor, OpenSSL-backed JWT signing,
exact one-repository/permission token leases, native Git helper, new preview and
combined configured creation, guarded resume, rotation and disable/enable.
Existing manual PAT, local-only and unrelated runtime interfaces are retained.
Offline synthetic App tests include real RSA signatures and authenticated native
Git TLS fetch/push; evidence and counts are in [acceptance.md](acceptance.md).

T-008 is complete for code revision `30bf742`: all three configured workflows
passed, alongside 39 focused tests, existing regressions and full repository
checks. The owner approved All repositories after the narrower candidates failed.
The actual App/installation now has exactly four grants; inactive schema-2 migration,
retained first recovery, activation and normal second new completed. 47 focused
tests and full repository checks pass. Both private apps pass build/test/typecheck,
page/health and owner desktop checks. Scoped native worktree fetch/push/later PRs,
credential reacquisition, private cross-repo denial and disable/enable pass.
Live signing-key rotation/new-key Git access passed; owner confirmed retirement,
and the old local key is absent, so independent post-retirement HTTP verification
is not claimed. All code/final-head CI workflows passed. PR #54 merged as
`f48519007a0b5df94e95dbd5814a73d3c371eab6`; all three push-to-main workflows
passed. T-009 is complete and the accepted All repositories slice is Delivered.
No real App/root
credential or remote project was used during
the earlier offline tests. Existing
revoked PATs were not read or reused. No deployment/public callback/new host
package/service mutation occurred. PR #54 contains reviewable implementation;
merge is not implied by the coding request. The later separately authorized live
checks are recorded as passed with their actual limits in acceptance.md.

## October 12 approved workflow extension

- [x] T-012a: Diagnose the workflow-entry denial without broader credentials or
  recreation; prepare the concrete policy and obtain project-owner approval.
  CRD-009/010; AC-009/010. Approval is recorded in the current chat.
- [ ] T-012b: Implement/test explicit schema-3 policy, preflight, immutable binding
  checks, singleton provisioning grants, role exclusions, compatible helper
  migration and interruption/unknown-edit recovery. Deliver a reviewed PR with
  actual local and final-head CI evidence. CRD-009/010; AC-009/010.
- [ ] T-012c: After owner App/installation grant update, verify exact readback,
  migrate the inactive profile, resume the retained first operation, activate only
  after actual workflow publication, create the second target and prove private
  repository CI plus existing scoped helper behavior. Record actual limitations
  and rollback disposition. CRD-009/010; AC-009/010.
