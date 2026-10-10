# TASKS-022: New GitHub repository automation

- **Status:** Draft planning complete; implementation not authorized
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-022](spec.md) · **Design:** [TDD-022](technical-design.md)

## Planning and authorization

- [x] T-001: Read catalogue, architecture, sequence, existing CLI/catalogue and
  specification workflow; confirm personal account `danielbardsley`; draft
  scope, design, traceability and acceptance criteria. This task records planning
  only; no GitHub fixture creation or implementation acceptance occurred.
- [ ] T-002: Daniel reviews requirements/defaults and authorizes implementation.
  Confirm account capabilities, endpoint permissions and a bounded provisioning
  credential/transport; document PRJ-005 handoff and live fixture approval as
  separate gates. REP-005; AC-005. Resolve unsupported required capabilities
  before dependent work rather than substituting public visibility.

## Implementation order

- [ ] T-003: Define plan/receipt versions, input allowlists, exact template
  integration, safe staging, target locks and no-write preview/status. Include
  unchanged-plan verification and conflicting-operation rejection.
  REP-001/006; AC-001/006.
- [ ] T-004: Implement reviewed credential/API/Git adapter, private creation,
  journaled immutable identity, bootstrap main, protected publication branch,
  initial PR and non-destructive reconciliation. Never auto-merge or retry an
  ambiguous create blindly. REP-002/003/005/006; AC-002/003/005/006.
- [ ] T-005: Add strict protection readback, optional development environments
  and metadata-only secret-reference reporting; test empty selections, unsupported
  settings, production rejection and pending provisioning. REP-003/004; AC-003/004.
- [ ] T-006: Add failure injection at each boundary, response-loss, races, drift,
  wrong-ID/credential rejection, token-redaction and isolated Git safety tests.
  Prove source/resource retention and one repository/branch/PR per completed
  operation. REP-001–006; AC-001–006.
- [ ] T-007: Package the operation in source/installed providers; document
  readiness, permissions, commands, single-owner protections, ongoing Git access,
  recovery, rollback and separately authorized retained-resource cleanup. Preserve
  existing local/runtime interfaces. REP-007; AC-007.

## Verification and delivery

- [ ] T-008: Run focused tests, repository checker and whitespace/link checks;
  exercise existing local new/test/start/stop regression scenarios. Open an
  implementation PR and record configured CI outcomes. AC-001–007.
- [ ] T-009: After explicit live-target/credential authorization, exercise a
  retained private fixture: settings readback, protected-main denial, initial
  PR, selected environment metadata, exact starter checks and private runtime
  smoke test with another app available. Record sanitized revision/results,
  credential handoff limitations and fixture disposition in acceptance.md.
  Daniel reviews acceptance; merge and update catalogue only when the actual
  gates pass. No automatic deletion, merge or production action. AC-001–007.

## Current handover

The initial spec/design/tasks are reviewable. Personal-account ownership is
confirmed; policy defaults, account-plan readiness and provisioning credentials
remain proposed/unverified. Next action is Daniel's scope review, followed by
T-002. Wider organization/public/production, credential brokering and generated
CI workflows remain separate scope. Documentation checks do not establish
implementation, CI, GitHub or runtime acceptance.
