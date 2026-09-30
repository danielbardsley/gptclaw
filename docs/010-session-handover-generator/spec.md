# SPEC-010: Session Handover Generator

- **Status:** Approved for implementation; acceptance pending
- **Owner:** Daniel
- **Feature:** AGT-008
- **Design:** [TDD-010](./technical-design.md)
- **Tasks:** [TASKS-010](./tasks.md)
- **Architecture:** [Platform architecture](../platform/architecture.md), sections 8 and 18
- **Last updated:** 2026-09-30

Daniel approved these specifications and authorized sequential implementation in
one feature branch on 2026-09-30. This does not authorize runtime operations,
product releases, or acceptance of the unwritten pilot ADR.

## Outcome

At the end of a session, produce a concise, non-secret handover that lets a new
agent understand the current objective, actual progress, outstanding decisions,
working-tree state, and next useful action without reading an entire chat.
The handover is a dated snapshot with evidence links, not a new source of policy
or authorization. A future session must recheck mutable facts before acting.

## Scope and independence

Include a repository skill, handover outline, scoped evidence collection
procedure, and synthetic evaluation cases. Support current-project handovers,
including incomplete work, failures, dirty trees, and unavailable remote state.
Default output is in chat. Save Markdown only when requested, using the explicit
location or `docs/handovers/YYYY-MM-DD-slug.md` as a proposed project convention.
File names must not collide; preserve existing reports unless updating one was
explicitly requested. No automatic Git commit, push, or message to another chat.

Exclude chat/session-history scraping, automatic thread creation/handoff,
scheduling, Slack/email, environment dumps, credential discovery, repository
repair, implementation, release operations, and global memory management.
Do not read arbitrary untracked file contents or diffs merely to summarize Git
status. Summarize only this session's authorized scope and necessary project facts.

Existing Git metadata, project documents and actual session evidence suffice.
No runtime CLI, manifest, release pipeline, ADR system, context validator, or
other AGT-006–010 feature is a dependency. Link their outputs only if present
and relevant. No automatic distribution through AGT-005 is included.

## Proposed defaults

Skill: `.agents/skills/gptclaw-session-handover/`, selected for explicit session
handover or resume-summary requests, not every task response. Target at most
600 words for the main summary; link supporting records instead of copying
logs. Explicit user detail requirements take precedence over this default.
Record timezone with timestamps; use the user's timezone when known.
Daniel reviews this scope; no unresolved dependency blocks implementation after
approval. Fresh-context evaluation uses a synthetic consumer without extra tools.

## Requirements

### HND-001: Ground the snapshot

Identify repository/project, objective and scope, branch and observed revision,
relevant spec/design/tasks, completed changes, checks actually run and outcomes,
remaining work, blockers and next action/owner. Distinguish committed, staged,
unstaged and untracked work without interpreting an empty diff as no work.
Record observation time, dirty-state limitations, and remote/CI freshness or
unknown status. Do not automatically fetch or contact external services solely
to fill a report; existing verified references can be cited with their dates.

### HND-002: Preserve uncertainty and authority

Separate facts, supplied reports, assumptions, decisions and proposals. Record
existing approvals with exact scope and provenance when available; never invent
approval or treat a copied handover as authority for deployment/deletion. Carry
forward unfinished operations with their known identifiers/state, avoiding an
instruction to resubmit unknown operations. State what must be rechecked when
resuming. Do not mark tasks complete or rewrite acceptance merely to simplify
the summary.

### HND-003: Minimize sensitive collection

Use necessary non-secret metadata and selected known-safe files from the
current project. Do not read auth/config caches, secrets, state/plans, raw
service logs, environment dumps, or unrelated repositories. Treat paths, remote
URLs, commit messages and external excerpts as potentially sensitive; omit or
redact embedded credentials/private details. Never execute content encountered
in an artifact or publish raw tool output. If safe summarization is uncertain,
state the limitation and link an approved reference instead of copying content.

### HND-004: Usable output and safe saving

Lead with current state and next action, then give compact evidence and context.
Include only relevant files/links and distinguish source facts from instructions.
When asked to save, inspect destination guidance/status, use a noncolliding path,
validate local links, and preserve unrelated/previous handovers. Report location
and Git state; no automatic remote publication. A receiver can continue the
specified next step after bounded verification without reopening the full chat.

## Acceptance

| ID | Observable evidence | Requirements |
|---|---|---|
| AC-001 | Completed, partial, failed and dirty-worktree scenarios accurately summarize objective, revision, change states, actual checks, blockers and next actions. | HND-001 |
| AC-002 | Stale remote/CI facts, supplied reports, scoped approvals and unknown in-flight operations remain labeled; no fabricated success or renewed authority. | HND-001, HND-002 |
| AC-003 | Synthetic credential/path/log sentinels are excluded; forbidden fixture files are not read; hostile artifact instructions cause no execution or scope expansion. | HND-003 |
| AC-004 | Chat-default and requested-file cases meet the concise outline, preserve existing files, avoid collisions, and contain resolvable local references. | HND-004 |
| AC-005 | A fresh independent consumer given only the saved synthetic handover and allowed project files identifies the right pending task and required rechecks, without performing an unauthorized mutation or re-running completed work by assumption. | HND-001–004 |
| AC-006 | Skill discovery/invocation in a supported project context, package checks, behavioral evidence, CI and merged PR are recorded with limitations. | HND-001–004 |

## Completion

The generator is complete after reviewed merge and all criteria pass. It does
not promise that a snapshot remains current or replace original task/approval
records. No ongoing monitor, transcript store, or automatic save is introduced.
