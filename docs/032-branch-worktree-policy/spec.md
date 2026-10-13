# SPEC-032: Branch and worktree policy

- **Status:** Implemented — verification and review pending
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Feature:** PRJ-006, initial single-host Git coordination slice
- **Design:** [TDD-032](technical-design.md) · **Tasks:** [TASKS-032](tasks.md)
- **Context:** [Catalogue](../platform/features.md) · [Architecture](../platform/architecture.md)

## Outcome and authorization

Two agents can work on the same enrolled project without changing each other's
branch, index or source files. Each task has a named branch, an isolated checkout,
an accountable owner and a recoverable handoff. Shared Git changes are serialized;
unfinished work survives interruption and cleanup cannot silently discard it.

The October 13 request authorizes this planning set and a reviewable planning PR.
The project owner subsequently instructed “Ok, lets implement the spec.” This
approves the bounded defaults and authorizes implementation and necessary
reversible verification. Merge, fixture remote writes and removal of retained
resources remain governed by the explicit delivery/fixture gates below.

This initiative was drafted as SPEC-031. It is renumbered SPEC-032 after the
concurrently reviewed Expo initiative occupied 031 on main; approved scope and
WT/AC/task identifiers remain unchanged. The project owner explicitly authorized
the named Trailboard Git-only exercise, clean test-checkout removal with retained
branches/receipts, and PR #74 merge on October 13.

## Scope and baseline

Include a typed local worktree lifecycle in the existing provider, predictable
branch/path allocation, operation locks, durable task ownership, credential
compatibility, source-only handoff and conservative cleanup. Initially support
non-bare repositories already enrolled by [PRJ-005](../023-repository-credential-broker/spec.md)
on this forge host, with one canonical source root and an existing `origin/main`.
This supports web, API and group repositories at the Git layer; it adds no runtime
adapter. Local synthetic Git repositories exercise the same policy without tokens.

Git 2.43.0 is observed on this host. The current provider has nonblocking file
locks, PR-based repository creation and repository-scoped credentials, but no
managed task worktree registry. Native worktree fetch/push already passed
[PRJ-005 acceptance](../023-repository-credential-broker/acceptance.md); its helper
validates the canonical project even when invoked from a linked checkout.
Credential validation reads `.git/config` beneath
the canonical root. Hook installation assumes a `.git` directory and embeds that
root. Hook targeting and managed registration need explicit compatibility work; linked worktrees cannot
be treated as independent enrolled projects.

Keep one existing runtime source root, project ID, private route and database
identity. Task worktrees are source checkouts, excluded from dashboard project
inventory and runtime activation. Existing app jobs, dependency mutations and
hooks must not quietly execute against the canonical checkout when invoked from
a task checkout. Source-only checks may use documented task-local commands and
isolated output; container/runtime checks use the canonical project after an
explicit integration handoff. Parallel runtime previews, isolated task databases
and general worktree build/test execution are follow-up scopes.

Exclude automatic agent spawning/scheduling, multi-host or distributed locks,
repository adoption, submodules, nested repositories, bare repositories, automatic
merge/rebase/cherry-pick, branch-protection changes, remote branch deletion,
public exposure, production, AWS/HCP changes and installation of host tools.
Worktrees share forge's identity and Git object/config storage; this is cooperation
between authorized agents, not isolation from hostile code or users.

## Requirements

- **WT-001 — Explicit allocation.** Provide read-only planning and local create,
  status, handoff, resume and cleanup operations for an enrolled project/task.
  Use `codex/<task-slug>-<allocation-id>` branches and a managed task-checkout
  area outside canonical source roots. A new task starts from an explicitly
  recorded `origin/main` commit, never another agent's uncommitted checkout.
  Report whether the base is locally observed or freshly fetched; creation is
  local-only by default. Reject unsafe identities/paths, collisions, unsupported
  repositories and active merge/rebase operations before changes. Repeated
  requests reconcile one allocation, preserving existing branches and directories.
- **WT-002 — Independent ownership.** Assign one current agent/session owner to
  each allocation; one branch belongs to one task checkout. Never switch, reset,
  stash or clean another checkout, force checkout an occupied branch, or overwrite
  unrelated work. Agents read applicable guidance in their allocated checkout.
  Status distinguishes active, handed-off, interrupted/conflicted and removed
  allocations. Ownership transfer requires an explicit target owner and task
  identity; age or a missing process alone never authorizes takeover or deletion.
- **WT-003 — Shared-operation coordination.** Use short nonblocking per-project
  locks for managed worktree/ref/receipt changes and one consistent order when
  credential or runtime locks are also needed. Competing operations return a
  bounded busy result without partial competing writes. Do not hold a project
  lock while an agent edits or waits for review. Task ownership is durable state,
  distinct from a process lock. Interruption releases the process lock but retains
  source and recovery intent. Other projects remain independently operable.
- **WT-004 — Credential, hook and runtime boundaries.** Prove each managed
  checkout's membership in its canonical repository before allowing scoped Git
  credentials; preserve the existing exact remote/repository binding, enabled
  state, token bounds and no-fallback policy. No new credential scope, copied
  keys, token-bearing remotes or global config changes. Unknown config/hooks
  stop with a conflict; existing canonical hooks cannot silently verify the wrong
  checkout. Runtime/database/dependency/hook operations targeting a managed task
  checkout fail with a fixed explanation; canonical operations remain available.
  Do not copy ignored credentials, caches, environments or application data into
  a task checkout or container.
- **WT-005 — Reviewable handoff.** Produce a sanitized handoff tied to allocation,
  owner, canonical repository, base/head commits and branch: summarize dirty and
  untracked/ignored presence without file contents, executed checks/results,
  outstanding work, local versus published state and optional verified PR URL.
  Publication is a separate explicitly requested scoped Git/PR action; never
  claim a local branch is pushed or merged. Resume revalidates actual Git and
  ownership state; drift stops for reconciliation. Integration into the canonical
  source root remains the repository's explicit PR/update workflow and must
  preserve dirty canonical work and existing runtime/data bindings.
- **WT-006 — Recoverable retention and cleanup.** Preview cleanup for one exact
  owned allocation. Removal requires a released owner, no running managed job,
  a clean checkout including ignored/untracked files, and evidence the head is
  retained outside that checkout by a verified remote ref or current canonical
  integration. Squash merges require recorded PR/head/merge evidence rather
  than an ancestry assumption. Unpublished, ambiguous, dirty, externally moved
  or unknown worktrees are retained. Remove only the selected checkout using
  non-force Git removal; retain its local branch and receipt. No automatic age
  expiry, global prune, forced branch deletion or rollback of source edits.
- **WT-007 — Adoption and evidence.** Existing unmanaged worktrees and naming
  schemes continue unchanged and are reported as unmanaged, not auto-adopted.
  Provide operator recovery and agent guidance through reviewed repository
  sources, preserving unknown guidance and installed host policy. Completion
  requires concurrent local/failure tests, CI and an authorized private-project
  exercise with producer/consumer handoff and scoped Git access. Record local,
  CI, private-host and project-owner acceptance separately.

## Acceptance criteria

| ID | Observable result and evidence needed | Requirements |
|---|---|---|
| AC-001 | A dirty canonical checkout remains byte-for-byte unchanged while two tasks allocate different branches/checkouts from the recorded base. Invalid paths/IDs, collisions, occupied branches and unsupported repo states fail safely; retry creates no duplicate allocation. Planning writes nothing and reports base freshness honestly. | WT-001/002 |
| AC-002 | Two processes editing separate tasks retain independent HEAD/index/files. Same-project concurrent allocation/handoff/cleanup returns busy or a reconciled result; a different project progresses. Killing a mutator releases its process lock and retains recoverable intent/work. Explicit transfer/resume succeeds; silent takeover fails. | WT-002/003 |
| AC-003 | Managed worktree fetch/push to its exact enrolled private repository succeeds with singleton scoped credentials. Wrong remote/common directory, forged metadata, disabled binding and hostile config fail without issuance/fallback. Synthetic leak checks pass. Canonical Git access and hooks remain valid; task hooks cannot run checks against canonical files. | WT-004 |
| AC-004 | Task checkouts cannot acquire runtime routes, containers, database identities, dependency operations or hook installation. Canonical web/API/group/database regression checks pass; discovery does not add task projects. An independent private app remains available throughout the live Git exercise. | WT-004/007 |
| AC-005 | A consumer resumes a producer's exact head and outstanding work from a sanitized handoff. Local-only, pushed and PR-linked states are distinguished. Dirty/conflicting canonical integration and unrecorded branch/ref drift stop without overwrites; no merge or source update occurs as a handoff side effect. | WT-005 |
| AC-006 | Cleanup retains dirty, ignored/untracked, unpublished, active, moved, unknown and ambiguously merged worktrees. After explicit release and verified retention, one clean owned checkout is removed without force; branch/receipt and other worktrees remain. Lost responses and interruptions reconcile safely. | WT-006 |
| AC-007 | Run focused tests and repository checks in the prepared environment, record CI for the final implementation revision, then complete an authorized two-task private Git exercise and owner handoff acceptance. Record retained branches/checkouts and cleanup disposition; fresh-task guidance is verified without changing installed host policy. | WT-001–007 |

## Approved defaults and completion

The project owner approved: source-only initial scope, enrolled repositories only,
`origin/main` as the recorded default base, no implicit fetch, one owner per task,
short locks, retained branches and explicit cleanup. These defaults were approved with implementation authorization on October 13. Existing repository
and area guidance still govern every task, including task-specific delegation
permission and review/merge gates.

Deliver provider integration, focused tests, a worktree runbook and agent guidance
through a reviewed implementation PR after authorization. Create acceptance.md
when actual implementation evidence exists. Mark only this bounded PRJ-006 slice
Delivered after implementation merge and all acceptance criteria pass. Runtime
checks in independent task worktrees remain separately scoped future work.
