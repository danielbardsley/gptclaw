# TASKS-023: Repository credential broker

- **Status:** Implementation in review; one-time App setup/live acceptance pending
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
- [ ] T-002b: Approve exact private App settings/selected bootstrap/key handling
  and retained live targets, then provide App/installation IDs and the external
  private key path. Prove actual personal-account creation/inclusion/main behavior
  through the canary before activation; no broader grant/PAT fallback. CRD-001/002;
  AC-001/002. The concrete proposal is in the runbook/settings checklist.

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

- [ ] T-009: With explicitly approved App/installation/key/targets, prove one-time
  setup and two successive private projects without per-project credential or
  installation clicks. Verify scoped Git/PR operations, renewal, cross-repository
  denial, rotation/revocation and retained recovery. Run existing starter quality
  and private app/independent-service checks; obtain the project owner's desktop/owner
  observations. Record sanitized acceptance.md, actual final-head CI/merge and
  credential/fixture disposition. Mark the accepted slice Delivered only after
  merged implementation and all criteria pass. AC-001–008.

## Current handover

Provider 1.5.0 implements private App profile/doctor, OpenSSL-backed JWT signing,
exact one-repository/permission token leases, native Git helper, new preview and
combined configured creation, guarded resume, rotation and disable/enable.
Existing manual PAT, local-only and unrelated runtime interfaces are retained.
Offline synthetic App tests include real RSA signatures and authenticated native
Git TLS fetch/push; evidence and counts are in [acceptance.md](acceptance.md).

T-008 is complete for code revision `30bf742`: all three configured workflows
passed, alongside 39 focused tests, existing regressions and full repository
checks. T-002b/T-009 require the separate
owner App setup/target approval and actual App ID, installation ID and private
key path. No real App/root credential or remote project was used during tests,
and actual personal-account creation/inclusion is not claimed proved. Existing
revoked PATs were not read or reused. No deployment/public callback/new host
package/service mutation occurred. PR #54 contains reviewable implementation;
merge/full live acceptance are not implied by the coding request.
