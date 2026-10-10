# TASKS-022: New GitHub repository automation

- **Status:** Implementation in review; live verification pending
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-022](spec.md) · **Design:** [TDD-022](technical-design.md)

## Planning and authorization

- [x] T-001: Read catalogue, architecture, sequence, existing CLI/catalogue and
  specification workflow; confirm personal account `danielbardsley`; draft
  scope, design, traceability and acceptance criteria. This task records planning
  only; no GitHub fixture creation or implementation acceptance occurred.
- [x] T-002a: Daniel approved the bounded spec/defaults and authorized implementation
  with “Ok, implement the spec” on October 10. The adapter uses an explicit private
  fine-grained token file and creation-only/scoped-configuration phases. Daniel
  separately authorized retaining `danielbardsley/gptclaw-prj004-verification`.
- [ ] T-002b: Creation token path/expiry/grants and actor are verified. Daniel supplies the
  repository-specific configuration token path/expiry/grants; verify private
  protection through actual scoped endpoints (subscription metadata was omitted);
  record provisioning-token revocation and ongoing Git handoff separately.
  REP-005; AC-005. Do not substitute broader credentials after a denial.

T-002 is split into T-002a (completed authorization/interface decision) and
T-002b (pending live credential readiness) so the latter cannot reopen approval.

## Implementation order

- [x] T-003: Define plan/receipt versions, input allowlists, exact template
  integration, safe staging, target locks and no-write preview/status. Include
  unchanged-plan verification and conflicting-operation rejection.
  REP-001/006; AC-001/006.
- [x] T-004: Implement reviewed credential/API/Git adapter, private creation,
  journaled immutable identity, bootstrap main, protected publication branch,
  initial PR and non-destructive reconciliation. Never auto-merge or retry an
  ambiguous create blindly. REP-002/003/005/006; AC-002/003/005/006.
- [x] T-005: Add strict protection readback, optional development environments
  and metadata-only secret-reference reporting; test empty selections, unsupported
  settings, production rejection and pending provisioning. REP-003/004; AC-003/004.
- [x] T-006: Add failure injection at each boundary, response-loss, races, drift,
  wrong-ID/credential rejection, token-redaction and isolated Git safety tests.
  Prove source/resource retention and one repository/branch/PR per completed
  operation. REP-001–006; AC-001–006.
- [x] T-007: Package the operation in source/installed providers; document
  readiness, permissions, commands, single-owner protections, ongoing Git access,
  recovery, rollback and separately authorized retained-resource cleanup. Preserve
  existing local/runtime interfaces. REP-007; AC-007.

## Verification and delivery

- [x] T-008: Run focused tests, repository checker and whitespace/link checks;
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

Provider 1.4.0 implements plan/apply/resume/status, exact starter publication,
verified protection/environments, metadata-only references and retained recovery
journals. Focused offline tests use real isolated Git history/objects and a fake
GitHub transport; evidence and remaining criterion gates are recorded in
[acceptance.md](acceptance.md). Source and installed bundles include the adapter
and executable anonymous-fd askpass helper. Immutable template assets are unchanged.

Scope/defaults and implementation are authorized. The retained live target is
authorized; creation-only authentication/expiry and remote identity are verified. GitHub
omitted plan metadata; protection API enforcement, scoped configuration, live
private app validation and owner acceptance are pending. Daniel's next
input is the repository-specific configuration token path, actual expiry and
permission metadata; no token values. Offline verification created no remote application repository. The later live
creation-only phase created the authorized retained private repository with
operation `c33aa2188ed84326a0f6bc2dc0fe2ad1`, ID `1413668232`; its scoped configuration
credential is pending. Daniel approved the seven-day limit and owns revocation.
PR #52 carries implementation for review; merge is not authorized by the coding
request. T-008 is complete for updated implementation revision `ebfe69c`: all three configured
CI workflows passed. T-009 retains live/merge/owner acceptance gates.
