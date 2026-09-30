# TDD-008: Runtime-operation Skill

- **Status:** Draft
- **Owner:** Daniel
- **Specification:** [SPEC-008](./spec.md)
- **Tasks:** [TASKS-008](./tasks.md)
- **Last updated:** 2026-09-30

## Design

An instruction-based adapter consumes an already-approved lifecycle interface.
It owns orchestration and reporting, not lifecycle implementation. No privileged
helper, service, runtime schema, or production credential is introduced.

| Proposed component | Purpose |
|---|---|
| `.agents/skills/gptclaw-runtime-operation/SKILL.md` | Target resolution, authorization, observation/mutation separation, bounded state reconciliation |
| Skill `references/operations.md` | Contract discovery and operation-specific verification, populated from the selected runtime's reviewed docs |
| Skill `assets/operation-report.md` | Concise target/version, before/after state, evidence and unresolved outcome outline |
| `scripts/tests/fixtures/runtime-operation/` | Synthetic project identities, operation transcripts, sentinel data, and separate reviewer expectations |
| Existing repository checker/quality workflow | Narrow package checks and path coverage if needed; no changes to deploy gates |

## Interface contract and flow

Before live integration, map project identity, supported operation names and
argument types, version/capability discovery, idempotency behavior, operation
receipt/status, health states, log limits, timeout and busy/error semantics to
the actual provider. Do not invent flags now or turn the mapping into PRJ-001.
A missing mapping blocks only the dependent operation.

Resolve target -> inspect state -> establish authorization -> invoke once ->
follow receipt/status -> verify final state -> report. Observation can finish
without mutation. Treat timeout as unknown, then reconcile with the same
operation ID; if no ID exists, use documented target-state reconciliation and
stop if it cannot establish a safe next action. No automatic crash-loop repair,
permission change, process killing, or blind restart loop.

For a multi-service project, use the provider's explicit group operation only
when the request covers that group. Report partial completion accurately. Do
not compensate by stopping healthy services unless the reviewed contract and
existing authorization cover that exact recovery action.

## Verification and rollout

Use synthetic transcripts/typed tool stubs to record operation calls and return
predefined states without starting processes. Exercise every spec scenario,
including shell-text arguments, mismatched target identity, concurrent busy
responses, and secret sentinels in logs. Inspect actions and reports, not just
headings. Fresh-client selection and actual service health require separate
live evidence when a provider exists.

Daniel selects the disposable service and authorized operations once dependencies
are ready; save data/recovery prerequisites before the live test. A target with
non-disposable data is outside acceptance scope. Preserve existing gates.
Revert the skill through review for rollback; reverting it does not stop services
or undo operations already performed. Report any outstanding operation before
handover. No migration of existing runtime configuration is included.

| Requirement | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| ROP-001 | Reviewed provider mapping and exact target binding | T-002, T-003, T-005 | AC-001, AC-005 |
| ROP-002 | Explicit operation scope and typed calls | T-003, T-004 | AC-001, AC-002 |
| ROP-003 | Bounded receipt/state/health reconciliation | T-003–T-005 | AC-003, AC-005 |
| ROP-004 | Bounded sanitized observation/report | T-003–T-006 | AC-004, AC-006 |
