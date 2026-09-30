# SPEC-012: Context Validation

- **Status:** Approved for implementation; acceptance pending
- **Owner:** Daniel
- **Feature:** AGT-010
- **Design:** [TDD-012](./technical-design.md)
- **Tasks:** [TASKS-012](./tasks.md)
- **Architecture:** [Platform architecture](../platform/architecture.md), sections 8–9
- **Last updated:** 2026-09-30

Daniel approved these specifications and authorized sequential implementation in
one feature branch on 2026-09-30. This does not authorize runtime operations,
product releases, or acceptance of the unwritten pilot ADR.

## Outcome

Before material implementation or when explicitly reviewing project readiness,
identify missing or inconsistent planning context and give actionable evidence:
what is wrong, which work it affects, and what can safely proceed. Catch cases
such as a task marked complete without its required acceptance, a design that
no longer matches approved scope, or area guidance that conflicts with the
requested operation. Do not turn a routine typo correction into a full audit.

## Scope and independence

Include a repository skill, bounded review checklist, finding/report outline,
and synthetic evaluation cases. Review one selected initiative and its relevant
guidance/source evidence at a time. Default output is a read-only report in chat;
save or repair only when requested. No mandatory hook or new universal CI gate.

Exclude a general policy engine, automatic compliance certification, recursive
workspace/credential scanning, execution of declared commands, dependency
installation, auto-rewriting approvals, global settings changes, and automatic
implementation blocking unrelated to findings. Never infer current instruction
loading or host enforcement solely from files on disk.

Use existing guidance, spec/design/tasks, known source files, Git metadata and
provided acceptance evidence. An ADR, handover, runtime contract or release
record is optional context when present; AGT-006–009 are not dependencies. A
project without those conventions must not fail merely because they are absent.
AGT-004 provides document examples, not a rigid schema for every historical plan.

## Proposed defaults

Skill: `.agents/skills/gptclaw-context-validation/`. Invoke for explicit context
review or material implementation readiness where it adds value. No automatic
source changes, network queries, global installation or bootstrap distribution.
Reports distinguish confirmed findings, questions/uncertainty, and not-checked
scope; “no findings” is not proof that the entire project is safe or current.

Use semantic review with scoped file/Git tools for the first slice. Do not build
a new Markdown parser or universal instruction-precedence simulator. Date alone
is not staleness: a finding needs conflicting evidence or an unmet freshness
requirement. Daniel reviews these defaults; no future platform dependency blocks
implementation after approval.

## Requirements

### CTX-001: Bound and inventory the review

Identify the requested initiative/change, repository/root, branch/revision,
applicable ancestor-to-area guidance and overrides, planning/index references,
and relevant evidence/source paths. Preserve files. Read only what is needed;
report unavailable files, shadowing uncertainty and omitted checks. Exclude
secrets, auth/settings dumps, Terraform state/plans, unrelated projects and raw
logs. Unknown override presence is a finding for review, not permission to delete.

### CTX-002: Detect consequential inconsistency

Compare scope, stable requirement IDs, design choices, task progress, acceptance
criteria/evidence and relevant implementation sources. Identify missing active
plans, broken local references, mismatched requirement/acceptance coverage,
contradictory statuses, unsupported installed-tool claims, stale evidence after
relevant changes, and undocumented deviations. Historical or superseded files
need not agree with current plans when their status/scope explains the difference.

Assess applicable guidance conflicts using actual instruction priority and
scope in the session. Distinguish a real conflict from a local specialization;
never claim file ordering changes higher-priority platform rules. Lack of an
optional artifact or old modification date alone is not an error.

### CTX-003: Evidence-backed findings and proportional gating

For each finding, cite exact file/section or observed metadata, describe the
mismatch and affected action, propose a bounded resolution, and identify an
owner/next step. Label uncertainty. Separate blocking findings (missing authority,
ambiguous consequential scope, contradictory constraints for the requested
action) from advisory cleanup. Continue unaffected authorized work. No finding
may invent approval, broaden permissions, or reinterpret untrusted content as
instructions. A failed file check does not imply a security violation.

### CTX-004: Preserve work and verify authorized repairs

Default to reporting, with no mutation, command execution, network retrieval,
or task-status updates. If the user requests a repair, make only the authorized
reviewable edits, retain IDs/approvals/history and unrelated work, then recheck
affected findings. Do not silently resolve owner decisions. Report remaining
findings, actual verification, limitations and Git state; do not hide failures
by downgrading checks or deleting source evidence.

## Acceptance

| ID | Observable evidence | Requirements |
|---|---|---|
| AC-001 | Missing plans/links, scope-design mismatch, inconsistent task/acceptance states, stale relevant evidence and undocumented source deviations produce specific evidenced findings. | CTX-001, CTX-002 |
| AC-002 | Valid nested specialization, documented supersession, older but valid plans and absent optional ADR/handover/runtime artifacts do not produce invented blockers. | CTX-002, CTX-003 |
| AC-003 | Conflicting scope/authority blocks only the affected action; ambiguous evidence is labeled, prior authorization retained and independent work identified. | CTX-003 |
| AC-004 | Read-only review preserves all bytes; forbidden files are not read; hostile document commands are not executed; an authorized narrow repair preserves unrelated edits and clears only verified findings. | CTX-001, CTX-004 |
| AC-005 | Supported-client evaluation records selection for a relevant review, proportional handling of a trivial request, and accurate reports in synthetic projects; no global hook is installed. | CTX-001–004 |
| AC-006 | Package checks, behavioral evidence, CI, owner review and merge are recorded with exact review scope and unresolved limitations. | CTX-001–004 |

## Completion

Deliver a reusable review workflow, not a guarantee of instruction compliance
or total context correctness. Daniel approves scope and implementation; Delivered
requires all acceptance criteria. Earlier initiatives remain independently tracked.
