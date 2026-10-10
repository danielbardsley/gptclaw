# TASKS-022: New GitHub repository automation

- **Status:** Delivered — initial slice merged and accepted
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-022](spec.md) · **Design:** [TDD-022](technical-design.md) · **Evidence:** [Acceptance](acceptance.md)

## Completed implementation and acceptance

- [x] T-001: Establish context, confirm personal-account target and draft spec/design/tasks.
- [x] T-002a: Daniel approved implementation, the seven-day token limit and an explicit protection waiver for the retained verification operation.
- [x] T-002b: Verify creation/configuration credentials, actor, real expiries and scoped endpoint results; record the actual protection denial/waiver and pending ongoing Git handoff. Token revocation is tracked below as owner follow-through.
- [x] T-003: Implement strict preview/plan/receipt contracts, safe staging and locks. REP-001/006; AC-001/006.
- [x] T-004: Implement private creation, isolated authentication, immutable identity, bootstrap/initial PR and reconciliation. REP-002/003/005/006; AC-002/003/005/006.
- [x] T-005: Implement protection readback and explicit waiver, optional development environments and metadata-only references. REP-003/004; AC-003/004.
- [x] T-006: Verify response loss, locks, drift, credential redaction and retained recovery using isolated Git/API fixtures. REP-001–006; AC-001–006.
- [x] T-007: Package provider 1.4.0 and document commands, scope, recovery and rollback. REP-007; AC-007.
- [x] T-008: 41 focused tests, full repository checks, whitespace/syntax/links and all three final-head PR workflows passed.
- [x] T-009: Retained private fixture setup/initial PR, build/start/tests/typecheck, page/health and independent-app checks passed. Daniel confirmed desktop access and requested platform merge/completion. PR #52 merged as `869b1b7f275c4555ce8ce82acab2de0565d84069`. All criteria pass for the approved slice; actual evidence is linked above.

## Operational follow-through and separate scope

Daniel owns manual revocation/removal of both temporary provisioning tokens;
that action is still pending and is not claimed complete. Their actual expiries
and removal procedure are recorded in acceptance.md. Ongoing per-repository Git
access and automatic credential handling belong to PRJ-005 or separately approved
manual provisioning. The initial verification PR remains open; this feature
opens initial PRs and does not automatically merge them.

The retained fixture stays private/running with the explicit protection waiver.
Next.js generated two uncommitted local configuration edits; retain them. No
public exposure, production, infrastructure deployment or deletion occurred.
Broader organization/templates/CI/production capabilities remain separate scope.

T-002 was split into T-002a and T-002b to distinguish authorization from live
readiness. Historical denials, corrections and approvals remain in acceptance.md.
