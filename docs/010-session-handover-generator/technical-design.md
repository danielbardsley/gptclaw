# TDD-010: Session Handover Generator

- **Status:** Draft
- **Owner:** Daniel
- **Specification:** [SPEC-010](./spec.md)
- **Tasks:** [TASKS-010](./tasks.md)
- **Last updated:** 2026-09-30

## Approach and artifacts

Use a skill that synthesizes current authorized context and bounded project
reads. No generic scanner or chat API is needed. Existing Git tools provide
branch/revision and change categories; the model decides which known-safe
project references explain the work. Do not recursively ingest the checkout.

| Proposed path | Purpose |
|---|---|
| `.agents/skills/gptclaw-session-handover/SKILL.md` | Evidence selection, privacy, snapshot freshness, concise output and requested-save behavior |
| Skill `assets/handover.md` | Objective/current state; revision/worktree; decisions/authorization; evidence; remaining work; next action and rechecks |
| `scripts/tests/fixtures/session-handover/` | Synthetic project states, provided session facts, forbidden read sentinels and separate consumer/reviewer prompts |
| Existing quality checks | Narrow package/resource validation if needed; no network or mandatory runtime commands |

## Collection and output

Read the active initiative and necessary task-owned change records, using exact
paths. Git status categories and revision identity are enough for inventory;
read content only when already relevant and safe. No automatic full diff,
commit-message history, remote configuration dump, or untracked-file ingestion.
For unborn repositories report no commit; for detached/worktree contexts report
actual identity; for stale remote metadata identify observation age. Preserve
user work; the generator performs no fetch, checkout, cleanup, or refresh mutation.

The report carries an observation timestamp, factual provenance links, unknowns,
and separate approval scope. It is not a runnable script. A consumer rechecks
Git/target state and consults authoritative authorization before mutation.
Candidate next steps are proposals where authority is missing. Keep the main
summary under the proposed 600-word default, excluding links-only references;
prefer a shorter useful report over filling every outline section.

For requested local saving, validate the parent and candidate name, reject
unexpected symlinks/collisions, and use exclusive creation. Update an existing
report only when requested and preserve reviewable differences. Do not append
sensitive raw output to an evidence file. No repository-wide handover database.

## Verification and lifecycle

Producer fixtures include mixed staged/unstaged/untracked work, a failed test,
unknown CI, an already-authorized narrow action, and a pending operation ID.
Place secret sentinels in excluded fixture files and misleading text in allowed
artifacts; review the actual read/action trace and generated report. A separate
consumer gets the handover and allowed project only, with no original session
history. Assess correct understanding and bounded rechecks, not prose matching.

After supported-client discovery/invocation, record its version and tested skill
revision. Revert skill updates through reviewed Git changes; existing handovers
remain dated artifacts and are not retroactively rewritten. Remove only owned
fixtures after sanitized evidence. No data migration or running service exists.

| Requirement | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| HND-001 | Bounded state/evidence collection | T-002, T-003 | AC-001, AC-002 |
| HND-002 | Fact/approval/proposal and freshness distinction | T-002–T-004 | AC-002, AC-005 |
| HND-003 | Minimal reads, safe references, no raw output | T-002, T-003 | AC-003 |
| HND-004 | Concise outline and exclusive requested save | T-002–T-005 | AC-004–006 |
