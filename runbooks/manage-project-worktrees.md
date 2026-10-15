# Manage source-only task worktrees

[SPEC-032](../docs/032-branch-worktree-policy/spec.md) supplies the single-host
policy. Run as forge using the reviewed `scripts/gptclawctl` provider or an
updated content-addressed snapshot. Existing unmanaged worktrees are retained;
there is no automatic adoption, agent scheduling or distributed locking.

## Allocate and inspect

Choose an already enrolled canonical project with a valid manifest and an
existing `origin/main`. Inspect its Git status and read its repository/area
guidance first. This workflow leaves dirty canonical source/index files intact.
Plan is read-only, uses the locally observed remote-tracking ref and never
fetches. If a fresh base is needed, separately perform an authorized native
`git fetch origin` from the canonical project with its scoped helper, then plan.

```sh
scripts/gptclawctl worktrees plan \
  --project-root /srv/forge/projects/my-app --task fix-navigation --owner agent-one
scripts/gptclawctl worktrees create \
  --project-root /srv/forge/projects/my-app --task fix-navigation --owner agent-one \
  --base-commit <base_commit-from-plan>
scripts/gptclawctl worktrees status \
  --project-root /srv/forge/projects/my-app --task fix-navigation
```

Use the returned `path` and `branch`; do not invent, move or reuse allocation
paths. Task and owner identities are lowercase slugs, at most 48 characters.
The deterministic 32-hex allocation ID binds the repository and task identity.
A completed task cannot silently be reopened under its removed allocation: choose
another task identity. The initial store bounds retained allocation records to
256; a capacity result requires reviewed maintenance, not global pruning.

Branch names are `codex/<task>-<allocation-id>`. Checkouts live in
`.gptclaw-worktrees/<project-id>/<allocation-id>/` and receipts in
`.gptclaw-runtime/v1/worktrees/v1/`. Receipts bind repository/common-directory,
filesystem identity, base/head, owner and generation. Planning writes neither.
Creation records intent before Git writes and refreshes only the selected owned
canonical Git helper to the reviewed snapshot; there is no credential scope change.
Only recognized owned pre-commit hooks can be adapted to the invoking checkout.
Unknown hooks/configuration are conflicts requiring explicit reviewed changes.

A short nonblocking per-project lock serializes managed mutations. `busy` means
retry after observing status. Ownership remains in the receipt after the process
exits; an old PID or timestamp never authorizes takeover. These are cooperating
same-user controls: manual Git edits can bypass locks and will require reconciliation.

## Work, check and publish

Read guidance again inside the allocated checkout, including applicable ancestor
and nested files. Edit only that task checkout. Each has independent HEAD/index
and files; Git refs, objects, canonical helper and configuration remain shared.
Do not copy ignored environments, keys, dependency caches or application data.

The task checkout is source-only. Managed start/stop/test/verify, dependency,
toolchain, hook and database operations reject it before runtime mutation.
Existing hooks also reject runtime verification of task source rather than verify
the canonical checkout. Do not bypass these hooks to claim task verification.
Read-only manifest validation and reviewed offline/source checks may run locally
when that project's guidance and tool availability permit them, with task-local
outputs. General container build/test jobs and parallel preview/databases need
separate scope; they are not provided here.

Publication is a separate authorized Git action; allocation/handoff never pushes,
opens a PR or merges. Native Git fetch/push from the task directory uses the
canonical repository's existing singleton credential helper. Managed membership,
exact remote, enabled binding and supported configuration are checked before
credential issuance. Do not borrow the GptClaw SSH identity for applications.

When a PR is explicitly requested, use the existing scoped `credentials
pull-request` command with the canonical project root and exact returned task
branch. Review it through the normal repository workflow. Integrate accepted
source into the canonical checkout only under existing merge/update authority,
preserving dirty source and runtime/data procedures; hot reload follows canonical
files. Worktree commands never perform that integration.

## Handoff and resume

Record actual source head and observed dirty presence before releasing ownership.
Optional check reports are bounded synthetic labels, `passed`/`failed`/`skipped`,
and explicitly attributed to the owner; the provider does not execute or attest
them. A checks JSON file contains a list, for example:

```json
[{"check":"source-check","result":"passed","source":"owner-reported"}]
```

```sh
scripts/gptclawctl worktrees handoff \
  --project-root /srv/forge/projects/my-app --task fix-navigation --owner agent-one \
  --generation <current-generation> --checks-file /absolute/task-owned/checks.json \
  --remaining canonical-runtime-check
scripts/gptclawctl worktrees resume \
  --project-root /srv/forge/projects/my-app --task fix-navigation --owner agent-one \
  --generation <handoff-generation> --target-owner agent-two
```

Handoff increments generation and releases the current owner; resume names both
expected former owner and explicit target owner, then increments again. Old
owner/generation requests fail. `resume` from an active state is explicit crash
recovery transfer, never inferred from inactivity; the head must still match the
recorded head. Dirty files remain in place. Drift requires inspection and a
handoff by the recorded owner before transfer; no automatic reset/stash is used.

By default publication is `not-observed`, even when cached tracking refs exist.
Use `handoff --published` only after an authorized push: the provider verifies
the exact current remote branch head using scoped API access. `--pr <number>`
verifies repository/head/base identity and records open/closed/merged evidence.
These flags read remote state and never publish or merge. Keep outstanding work
as slug labels (`--remaining` can repeat), not prompts, secrets or source excerpts.

## Preview cleanup, retain work and recover

```sh
scripts/gptclawctl worktrees cleanup \
  --project-root /srv/forge/projects/my-app --task fix-navigation --owner agent-two \
  --generation <released-generation> --head <recorded-head>
```

After reviewing the exact allocation/retention result, repeat with `--apply` only
when removal is authorized. Apply locks and rechecks the current head, identities,
released ownership, all dirty/untracked/ignored presence and active Git operation.
Source-only guards prevent managed runtime jobs from occupying task checkouts.
Ignored output or data also prevents removal; inspect it without printing secrets
and remove only task-owned disposable files under existing authorization.

Retention needs current canonical commit ancestry, verified squash-merge PR/head/
merge evidence included in handoff, or a fresh exact remote branch head. A cached
remote-tracking ref and a local task branch alone are insufficient. No network
or ambiguous PR/ref state means retain work. Cleanup removes only this clean
checkout with non-force Git removal; it retains its local/remote branch and
receipt tombstone. Remote deletion and branch retirement are separate operations.

An interrupted create can be retried with the same task/owner/base; known intent
reconciles a matching branch/check-out without allocating duplicates. Interrupted
removal can be retried with the same owner/generation/head only when the exact old
registration/path is absent and its branch still matches. Status is read-only
and reports conflicted/interrupted observation honestly. Preserve partial receipts,
source and branches after other failures; do not run global prune, reset, clean,
forced checkout, forced removal or broad filesystem deletion to resolve them.

## Guidance adoption and rollback

[Agent worktree guidance](../templates/agents/worktrees.md) is an inert adoption
reference. Review additions to a project's own AGENTS.md under its normal PR
workflow; allocation does not overwrite guidance or installed host policy.
Verify adopted guidance in a fresh task before claiming acceptance.

Rollback is a reviewed code revert while retaining allocations/branches/receipts.
Keep managed source paths excluded from dashboard discovery and runtime entry
points. Do not downgrade an enrolled helper to code lacking membership guards
while managed allocations remain; retain the guarded snapshot until reviewed
reconciliation. No rollback deletes task work, app source or database data.
