# TDD-031: Branch and worktree policy

- **Status:** Draft proposal; implementation not authorized
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-031](spec.md) · **Tasks:** [TASKS-031](tasks.md)

## Approach and existing interfaces

Add a trusted `scripts/project_worktrees.py` module behind the existing
`scripts/gptclawctl.py` provider. Proposed `worktrees plan/create/status/handoff/
resume/cleanup` subcommands accept a canonical `--project-root` and stable task
identity. Create consumes the validated plan; cleanup defaults to preview and
requires an explicit apply selection. Mutation results and JSON errors contain
fixed codes and sanitized metadata, never raw config, credentials or Git output.
These are proposed interfaces, not available commands.

Git 2.43.0 is the observed baseline; verify used options against that version and
fail with a setup result if unavailable. Use explicit argv, validated refs and
machine-readable NUL-delimited Git output. Linked worktrees share refs/config and
have separate HEAD/index. Git's worktree lock protects administrative retention,
not agent mutual exclusion; use platform file locks for managed operations. See
[Git worktree documentation](https://git-scm.com/docs/git-worktree/2.42.0) and
[Git config documentation](https://git-scm.com/docs/git-config/2.43.0).

## Identity, layout and records

Propose source checkouts under `/srv/forge/projects/.gptclaw-worktrees/<project-id>/
<allocation-id>/`; exclude the entire managed parent from runtime and inventory
scans before exposing creation. State belongs under the existing runtime-owned
store in a separate `worktrees/v1/` namespace, never committed source manifests.
A project-level record binds canonical root, canonical Git common-directory
identity and PRJ-005 immutable repository ID; project ID alone is insufficient.
Reject non-owned paths, symlinks, traversal, unexpected mount/path changes and
unsupported submodule/nested/bare repositories. Preserve unmanaged entries.

Version-1 allocation receipts contain allocation/task IDs, bounded owner identity,
branch, base ref/SHA and observation time, worktree path, canonical binding,
operation intent/stage, observed head, handoff/check summaries and retention
state. Exclude prompts, source contents, ignored-file names, config values and
secret material. Bound all metadata and validate optional GitHub PR URLs against
this exact repository; user-supplied check results are attributed reports.
Owner-only atomic receipt writes retain a tombstone after removal. No automatic
migration of manifests, credential bindings or existing worktrees is required.

Creation revalidates the plan's canonical identity/base under the project lock,
records intent, creates one explicit branch/worktree with Git (no force options),
then records observed identity. A duplicate task request reconciles its allocation;
a second task cannot reuse its branch. Existing partial state is retained and
reported as interrupted/conflicted. Do not automatically remove a branch or
checkout if Git succeeds but receipt persistence fails.

## Ownership and concurrency

Use a hash of canonical repository identity for the short `worktree-project` lock,
reusing the provider's owned no-follow nonblocking flock pattern. Durable ownership
uses receipt state plus a generation counter; mutations validate the expected
owner/generation to reject stale producer requests after a transfer. Editing an
allocated checkout needs no long-lived process lock. Same-user manual Git can
bypass this coordination; observe drift and explain that limitation.

Managed allocation/handoff/removal need only the worktree-project lock. Prefer
credential issuance outside that lock; when nesting is unavoidable, use
worktree-project then credential-profile then credential-repository, and audit
existing paths so none acquire these in reverse. Runtime guards read managed-root
identity without taking worktree locks; task lifecycle never acquires runtime,
group, registry or database locks. No lock is held while awaiting user input.

Status observes without receipt writes. Handoff records actual head and dirty
presence plus sanitized evidence, then releases the current owner. Resume takes
explicit target owner and expected generation, compares receipt/Git identity,
and preserves uncommitted files. A crashed owner needs explicit recovery transfer,
not a PID/timeout heuristic. Run bounded Git subprocesses; terminate their process
groups before releasing operation locks so children cannot continue mutating.

## Credential, hooks and canonical runtime

Keep the canonical PRJ-005 helper and repository binding in shared Git config.
Creation verifies the effective origin/helper configuration, common directory,
binding enablement and exact singleton repository grant. Task registration gives
no additional remote authority. Validate unexpected worktree config, includes,
URL rewrites, helper overrides and push URLs as conflicts. The existing helper
remains canonical-root-bound; do not enroll each linked checkout separately or
copy a binding/key into it. Test actual Git helper resolution from a linked
checkout, including disabled binding and response loss.

Canonical hooks currently embed the canonical root, and linked `.git` is a file.
Before enabling task creation, make recognized platform-owned hooks resolve and
validate the invoking checkout. In a managed source-only task they must return
an actionable unsupported result when checks require the canonical runtime,
never run canonical verification as if it verified task edits. Unknown hooks or
`core.hooksPath` are conflicts: report for reviewed adaptation, do not overwrite
or bypass them. Do not enable shared worktree configuration extensions or alter
global Git settings implicitly. Git hooks, checkout filters and other executable
configuration require explicit trusted-project review; local creation does not
execute project-provided initialization, dependency or quality commands.

Guard all provider execution/activation entry points against managed task roots,
including group component delegation, database and dependency adapters and hook
installation. Pure manifest validation may remain read-only. Dashboard discovery
must exclude the managed parent even if task source contains a valid manifest.
Do not allocate duplicate IDs, ports, volumes or routes. Integration is the
existing explicit PR/canonical-update workflow; no worktree command merges or
updates the running source. Document that hot reload observes canonical edits,
so integration must follow that project's runtime/data procedures.

## Cleanup, recovery and rollout

Cleanup preview binds exact allocation, owner generation, worktree identity and
head. Apply reacquires the lock and rechecks every prerequisite, including all
ignored/untracked presence, active provider jobs, release and verified retention.
Read only status metadata, not ignored-file contents. For a pushed head, verify
an exact permitted remote ref still retains it through scoped read-only Git;
local cached remote-tracking refs alone are insufficient. Canonical ancestry can
prove normal integration; squash integration needs verified PR/head/merge evidence
bound to the repository and actual canonical revision. Offline uncertainty retains
work. Use non-force `git worktree remove`; leave the branch and tombstone.

Fault recovery compares receipt, worktree listing, directory identity and refs
before completing a known interrupted stage. If removal succeeded but the response
was lost, record removal only when the exact prior registration is gone and no
replacement path/identity exists. Never run global prune, reset, clean, forced
checkout or remote deletion. Unexpected missing/moved paths require explicit
reconciliation; retention expiry never triggers deletion.

Ship guards, credential/hook compatibility and lifecycle together through a
reviewed PR/provider snapshot update. Adoption is opt-in; changing repository
guidance does not update installed host policy. Rollback disables new allocations
and reverts reviewed code while retaining receipts/worktrees/branches. Existing
managed roots must remain excluded from older discovery/runtime paths; establish
that guard or retain the new guarded provider until allocations are resolved.
Do not automatically uninstall guards or delete allocations during rollback.

## Components and verification

| Component | Proposed change | Requirements |
|---|---|---|
| `scripts/project_worktrees.py`, provider CLI/snapshot | Plans, binding, lifecycle, records, scoped locks and safe errors | WT-001/002/003/005/006 |
| `scripts/repository_credentials.py`, Git helper | Validate shared canonical enrollment and linked-checkout configuration without broadening grants | WT-004 |
| Runtime/group/database/dependency entry points, dashboard discovery | Reject managed task execution/activation; exclude task source from inventory | WT-004/007 |
| Platform-owned hooks | Resolve invoking checkout; preserve unknown hooks and canonical behavior | WT-004 |
| Focused Git tests, repository checker, runbook and reviewed guidance | Concurrency/failure/retention checks and adoption/handoff procedure | WT-001–007 |

Use task-owned temporary Git repositories, synthetic configuration/tokens and two
real child processes for concurrency tests. Disable network and executable Git
hooks/filters in fixtures except explicit controlled spies. Cover interruption at
every receipt/Git boundary, paths/config tampering, stale ownership, squash merge
retention and ignored files. Do not place actual App credentials in fixtures.
Run focused tests then the prepared-environment repository checker, diff checks
and relevant shell syntax checks. CI is separate from local results.

A later authorized live exercise uses two task allocations in an exact enrolled
private fixture and an independent running app. Record scoped fetch/branch push,
optional requested PR, producer/consumer handoff, denied task runtime operations,
continued app health and cleanup/retention disposition. No real remote writes or
checkout removal are authorized by this draft. Owner acceptance and implementation
merge are separate gates; no existing app/database is a disposable test fixture.

## Traceability and decisions

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| WT-001 | Validated plan, explicit base, names, durable intent/reconciliation | T-002/003/007 | AC-001/007 |
| WT-002/003 | Independent checkout ownership, generations, short locks | T-002/003/005/007 | AC-001/002/007 |
| WT-004 | Canonical helper validation, hooks, execution/discovery guards | T-004/007 | AC-003/004/007 |
| WT-005 | Observed source-only handoff and explicit resume | T-005/007/008 | AC-005/007 |
| WT-006 | Retention proof, cleanup preview/recheck and tombstones | T-006/007/008 | AC-006/007 |
| WT-007 | Opt-in guidance, regressions and separate live acceptance | T-008/009 | AC-004/007 |

Project-owner decision: approve the bounded source-only defaults in SPEC-031
before implementation. Implementation must settle exact CLI flags, error/receipt
schemas and hook recognition with tests, within those defaults. Parallel task
runtime/build/database adapters and broader repository enrollment require separate
scope decisions; they are not prerequisites for this initial Git policy.
