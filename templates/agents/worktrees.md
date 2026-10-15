# Agent worktree policy adoption

This is an inert reference for projects using the reviewed PRJ-006 provider, not
an installed policy or automatic repository update. Adapt it in the project's
normal reviewed guidance PR, preserving applicable local and nested guidance.

Before task work, inspect canonical Git status and the active specification,
design/tasks. Use the reviewed worktree plan/create interface on the enrolled
canonical project, recording the selected task, owner and base commit. Read
applicable ancestor/repository/area guidance again from the allocated checkout.
One task checkout has one current owner; use explicit handoff/resume with the
observed generation to transfer it. Do not edit another agent's checkout, take
over from age/PID alone, or switch/reset/stash/clean shared canonical source.

Edit and run authorized source-only checks in the assigned checkout. Report
actual commands/results and limitations. Managed runtime, dependency, database
and container quality commands operate on the canonical project only after
explicit reviewed source integration; task worktrees provide no independent
preview, route, project identity or persistent data. Never bypass a hook to claim
checks ran on the task source. Keep credentials, ignored environments and data
out of source and handoff reports.

Publishing a task branch, opening/merging a PR and updating canonical source
remain separately governed actions. Use the exact enrolled scoped Git helper,
not unrelated credentials. Record source head, dirty presence, reported checks,
remaining work and verified remote/PR state; do not infer publication from a
local branch. Preserve unfinished work and existing runtime/data bindings.

Preview cleanup for the exact released allocation. Apply only within existing
removal authority when clean including ignored/untracked files and retention is
verified outside the checkout. Retain branches/receipts; no forced removal,
branch deletion, global prune or timer-based cleanup. Preserve unknown worktrees,
hooks/configuration and guidance, and report conflicts for scoped reconciliation.

Use the [operator runbook](../../runbooks/manage-project-worktrees.md) for actual
interfaces, interrupted-operation recovery, adoption and rollback. This policy
coordinates cooperating agents under one user identity; it grants neither new
permissions nor isolation from hostile code.
