# SPEC-006: Specification Skill

- **Status:** Approved; implementation in review, acceptance pending
- **Owner:** Daniel
- **Feature catalogue:** AGT-004
- **Technical design:** [TDD-006](./technical-design.md)
- **Implementation tasks:** [TASKS-006](./tasks.md)
- **Architecture:** [Platform architecture](../platform/architecture.md), sections 8–9
- **Last updated:** 2026-09-30

## 1. Outcome

Provide a repository-scoped skill that turns a selected feature into consistent,
reviewable specification, technical design, and implementation tasks, then
maintains those documents and records acceptance from actual evidence. Reduce
repeated explanation of GptClaw's planning conventions while preserving the
owner's scope, existing decisions, and approval history.

Daniel selected AGT-004 and approved this specification on 2026-09-30, explicitly
authorizing implementation. Resulting-change review, merge, and supported-client
acceptance remain separate. See [acceptance](./acceptance.md).

## 2. Scope and dependencies

Included: one instruction-based skill, reusable document outlines, focused
package checks, synthetic behavioral scenarios, and acceptance evidence.
GptClaw is the first adoption. The skill supports new initiatives, revisions to
existing initiatives, and evidence updates without rewriting unrelated content.

Excluded: feature implementation, a general context-validation engine (AGT-010),
project scaffolding (AGT-005), deployment/release automation, global skill
installation, plugin packaging, host-policy changes, and mandatory conversion
of historical documents. No service, infrastructure change, secret, or new
runtime dependency is required.

The existing [document convention](../README.md) and merged guidance in
[SPEC-004](../004-repository-agents-template/spec.md) and
[SPEC-005](../005-nested-guidance-pattern/spec.md) provide the baseline. Their
outstanding acceptance remains separate; this initiative does not claim to
complete it. No future project manifest, platform CLI, or container toolchain
is a dependency.

## 3. Approved defaults

| Item | Approved default |
|---|---|
| Skill name and location | `gptclaw-specification` at `.agents/skills/gptclaw-specification/` |
| Invocation | Explicit invocation and normal automatic selection for matching planning requests |
| Resources | Concise `SKILL.md` plus four Markdown outlines under `assets/` |
| New initiative output | `docs/NNN-kebab-case-name/spec.md`, `technical-design.md`, and `tasks.md` |
| Acceptance output | Add or update `acceptance.md` when verification evidence is available or acceptance tracking is requested; pending criteria remain pending |
| Distribution | Repository version control and reviewed PR; no user-wide installation |
| Ownership | Daniel reviews the skill and substantive scope changes |

## 4. Requirements

### SPS-001: Relevant invocation and grounded context

Describe the skill narrowly enough to select it for initiative planning and
acceptance documentation, without making routine fixes or general writing
require a full planning package. Inspect applicable guidance, Git state,
document index, selected catalogue entries, and relevant existing plans and
implementation evidence. Distinguish verified facts, proposals, and unknowns.
Do not treat a catalogue entry, fetched content, or copied example as authority.

### SPS-002: Consistent documents with useful traceability

For a new initiative, choose the next unused number after inspecting the index
and existing directories; preserve existing numbering and detect collisions
before writing. Create linked documents and update the index and selected
catalogue entry. Preserve another repository's explicitly chosen conventions
if the skill is deliberately reused there; GptClaw numbering is a local default.

The specification defines outcome, scope/exclusions, dependencies, requirements
with stable IDs, measurable acceptance criteria, ownership, assumptions, and
open decisions. The design maps those requirements to components/files,
interfaces or data where applicable, verification, and relevant failure,
rollback, or migration behavior. Tasks follow dependency order with explicit
gates and trace requirements to acceptance criteria. Keep inapplicable material
brief; do not invent architecture or commands to fill an outline.

### SPS-003: Preserve authorization and support bounded updates

Track drafting, specification approval, implementation authorization, review,
merge, and acceptance separately. Honor explicit authorization already in the
session; do not repeatedly request the same approval. Where authorization is
missing, prepare reviewable documents before asking for the dependent step.
Planning alone must not start implementation, deployment, or new external work.

When revising existing plans, retain stable IDs, valid approvals, completed
work, and evidence. Mark changed scope for review without silently invalidating
unaffected decisions or representing new requirements as approved. Clarify
material unknowns; record reasonable reversible assumptions and continue
independent work. A narrow correction remains a narrow correction.

### SPS-004: Evidence-based acceptance

An acceptance record maps each criterion to passed, failed, pending, or not
applicable with a reason; records the reviewed revision, dates, executed checks,
results, limitations, and remaining owner actions; and links relevant PRs or CI
results when available. Distinguish local checks, CI, deployed behavior, and
owner acceptance. Missing evidence is not success; a merged PR alone is not
acceptance. Do not fabricate test results, approvals, deployment, or provenance.
Mark a catalogue feature Delivered only after merge and all required acceptance.

### SPS-005: Small, maintainable package

Keep essential workflow in the entrypoint and document shapes in linked assets.
Do not duplicate the full host/repository policy or require unavailable skills,
network services, or package installation. Use plain Markdown; no document
generator is needed for this slice. Changes use the repository PR workflow;
rollback is a targeted reviewed revert preserving unrelated work. Unknown
skills, overrides, settings, and user documents remain untouched.

### SPS-006: Verification of packaging and behavior

Check the package's required metadata, resource references, and usable outlines
with existing standard-library tooling. Separate these structural checks from
behavioral evaluation. Use synthetic scenarios to verify new planning,
updates, prior authorization, ambiguous scope, and incomplete acceptance
without modifying real infrastructure or invoking implementation commands.
Verify explicit invocation and automatic selection through the supported
client; record unexercised paths as pending rather than substituting file checks.

## 5. Acceptance criteria

| ID | Required evidence |
|---|---|
| AC-001 | Reviewed skill and four outlines cover SPS-001–005 with valid metadata and resolvable resource links; focused checks and relevant repository checks pass. |
| AC-002 | A synthetic new-feature request produces mutually linked spec/design/tasks with stable IDs, dependency order, testable criteria, index/catalogue updates, and no fabricated facts or implementation side effects. |
| AC-003 | Revision scenarios preserve existing IDs, approvals, evidence, and unrelated edits; new scope is identifiable; a narrow correction does not create a new initiative. |
| AC-004 | Scenarios distinguish selection from authorization, honor supplied prior authorization, and surface a material unknown while making independent progress. |
| AC-005 | Partial or failing evidence produces accurate acceptance states; merge-only evidence does not mark Delivered, and no result or approval is invented. |
| AC-006 | Supported-client evidence records explicit invocation and automatic selection for a relevant request, plus an unrelated request that does not activate the workflow. Record client, skill revision, scenario, outputs, and limitations. |
| AC-007 | Sanitized acceptance record covers every criterion, merged implementation PR, maintenance/rollback procedure, and actual final catalogue status. |

## 6. Completion

Implementation is complete only when the reviewed package is merged and all
acceptance criteria pass. Pending behavioral or client checks remain explicit.
PR #16 now includes the repository skill. No global skill installation or client
configuration change is required; actual client discovery remains to be verified.
