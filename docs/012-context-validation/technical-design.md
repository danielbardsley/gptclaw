# TDD-012: Context Validation

- **Status:** Draft
- **Owner:** Daniel
- **Specification:** [SPEC-012](./spec.md)
- **Tasks:** [TASKS-012](./tasks.md)
- **Last updated:** 2026-09-30

## Approach and artifacts

Use an instruction-based review skill with explicit scope and an evidence matrix.
Avoid a global scanner: semantic conflicts depend on project intent, instruction
scope, and actual authorization that string matching cannot establish. Existing
file/Git tools can inspect exact paths and metadata without executing project code.

| Proposed path | Purpose |
|---|---|
| `.agents/skills/gptclaw-context-validation/SKILL.md` | Bounded discovery, evidence comparison, proportional findings and requested repairs |
| Skill `references/review-checklist.md` | Missing/inconsistent/current-versus-historical evidence prompts, including legitimate specializations |
| Skill `assets/context-report.md` | Reviewed scope/revision, confirmed findings, uncertainties, unchecked areas and next actions |
| `scripts/tests/fixtures/context-validation/` | Synthetic positive/negative context sets, secret/command sentinels, and reviewer rubric |
| Existing quality tooling | Minimal package/link checks as needed; no new mandatory implementation hook |

## Review flow

Resolve the requested work and applicable guidance. Inventory relevant files and
revision metadata, then read the selected plan and only evidence needed for its
claims. Track source, asserted state, observed support, and consequence. A useful
finding connects a concrete discrepancy to the requested action; unsupported
speculation is a question, not a confirmed failure.

Use stable local finding IDs within a report, location references, impact,
confidence, recommendation and owner. Do not claim a complete instruction chain
when session/client settings are unknown. A narrower area convention may refine
root guidance; a real contradiction needs a resolution within actual instruction
priority, not automatic overwrite or precedence inferred from file age.

Status observations are timestamped and revision-bound. Do not fetch remote CI
to make a report look complete unless the user/task already authorizes that
inspection. Treat supplied remote outcomes as attributed reports if unverified.
When a source changed since a test, determine whether the changed behavior
invalidates the evidence rather than assuming any commit makes every test stale.

An explicit repair request permits only its scope. Prepare a diff, preserve
stable IDs/history and dirty user files, run affected checks, and update finding
states from actual outcomes. Owner decisions remain open when not supplied.
The report never becomes a replacement policy or new source of authorization.

## Verification and lifecycle

Create small paired fixtures: real contradiction versus legitimate specialization;
missing required task versus optional absent ADR; ungrounded completion versus
proper pending acceptance; obsolete evidence versus unchanged relevant behavior.
Include a dirty file, unreadable excluded file, unknown override and malicious
command text. Inspect evaluator read/action traces and before/after bytes.
Tests must judge the meaning and action impact of reports, not exact phrases.

Supported-client evaluation uses synthetic scopes and both a relevant review
request and a trivial correction that should not trigger a broad audit. Record
all unexercised paths explicitly. No runtime or production operation is needed.
Roll back the skill with a reviewed targeted revert; preserve prior reports and
unrelated repairs. No data migration, daemon, scheduled run or global hook exists.

| Requirement | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| CTX-001 | Bounded inventory and read exclusions | T-002, T-003 | AC-001, AC-004 |
| CTX-002 | Semantic evidence matrix and paired counterexamples | T-002, T-003 | AC-001, AC-002 |
| CTX-003 | Finding consequence/confidence and action-specific gating | T-003, T-004 | AC-002, AC-003 |
| CTX-004 | Report-only default, bounded repair and recheck | T-003–T-005 | AC-004–006 |
