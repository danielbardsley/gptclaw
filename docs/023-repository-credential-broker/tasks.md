# TASKS-023: Repository credential broker

- **Status:** Draft planning complete; implementation not authorized
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-023](spec.md) · **Design:** [TDD-023](technical-design.md)

## Planning and authorization

- [x] T-001: Read catalogue/sequence/architecture, delivered SPEC-022 and actual
  PAT/Git interfaces; verify current official App creation/installation/token
  documentation. Draft requirements/design/traceability. Daniel selected private
  repos with PR review without enforced branch protection for this proposal.
- [ ] T-002: Daniel approves full scope/design and authorizes implementation.
  Review exact App grant/selected bootstrap repo and key handling; authorize
  owner setup and specific retained live targets separately. Prove or resolve
  personal-account installation-authenticated creation/automatic inclusion and
  main default-branch behavior before finalizing the consumer adapter. No broader
  grant or deploy-key/PAT fallback is automatically authorized. CRD-001/002; AC-001/002.

## Dependency-ordered implementation

- [ ] T-003: Version private setup/profile/binding/receipt contracts and build
  doctor/status, strict safe key/path readers, account/App/installation identity
  checks and selected-repository readiness. CRD-001; AC-001.
- [ ] T-004: Implement maintained signing/installation-token acquisition with
  explicit one-repository/permission scope, actual response validation, fresh
  bounded lifetime, sanitized transport and no persisted bearer cache. Select
  pinned isolated tooling if needed. CRD-003/004/005; AC-003/004/005.
- [ ] T-005: Integrate verified creation capability/automatic inclusion with the
  existing journaled provisioning flow and configured normal new. Explicitly
  record the activated standing policy; keep local-only/unconfigured/manual PAT
  paths and existing apps unchanged. CRD-002/006; AC-002/006.
- [ ] T-006: Add exact project-local Git helper/enrollment and scoped later-PR
  path; extend reviewed Git config validation rather than permit arbitrary
  helpers. Preserve source/worktrees/remotes and reject cross-project binding
  or credential-bearing URLs. CRD-004/007; AC-004/007.
- [ ] T-007: Add concurrency, renewal, response-loss reconciliation, per-project
  disable/revocation and owner-controlled App key rotation/rollback. Document
  residual lifetimes and actual versus unknown outcomes. CRD-005/007; AC-005/007.
- [ ] T-008: Add meaningful offline/helper/Git transport negative tests and
  compatibility/bundle checks; update existing CI and run focused suites,
  repository/whitespace/link checks. Deliver implementation through reviewed PRs.
  CRD-001–008; AC-001–008.

## Live acceptance and delivery

- [ ] T-009: With explicitly approved App/installation/key/targets, prove one-time
  setup and two successive private projects without per-project credential or
  installation clicks. Verify scoped Git/PR operations, renewal, cross-repository
  denial, rotation/revocation and retained recovery. Run existing starter quality
  and private app/independent-service checks; obtain Daniel's desktop/owner
  observations. Record sanitized acceptance.md, actual final-head CI/merge and
  credential/fixture disposition. Mark the accepted slice Delivered only after
  merged implementation and all criteria pass. AC-001–008.

## Current handover

Planning package is reviewable; only planning documents were authored. No
broker/runtime/App settings or live project resources changed.
The desired automatic workflow and current-plan branch policy are explicit. A
selected-repository GitHub App is proposed using documented automatic access to
App-created repositories, with actual endpoint/account feasibility as a gate.
One-time owner registration/installation/key setup is necessary; future ordinary
projects should need no manual token generation. Revocation or key maintenance
can require later owner action and is not hidden behind a permanent-token claim.

Daniel reported both SPEC-022 temporary tokens revoked. This report is attributed
in the spec; no token files were read, deletion performed or API revocation probed
for this planning task. App settings/grant/bootstrap/live fixtures remain unapproved.
Next step is Daniel's review, then T-002; no implementation or setup is authorized
by the request to create this specification. PRJ-004 remains Delivered and its
existing verification app/source/PR are retained.
