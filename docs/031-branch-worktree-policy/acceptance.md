# SPEC-031 acceptance evidence

- **Status:** Implementation verification in progress; private/owner acceptance pending
- **Owner:** Project owner
- **Evidence date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-031](spec.md) · **Design:** [TDD-031](technical-design.md) · **Tasks:** [TASKS-031](tasks.md)
- **Delivery:** [PR #74](https://github.com/danielbardsley/gptclaw/pull/74), unmerged implementation update
- **Revision context:** Working tree on `codex/prj-006-spec`, based on planning commit `933779b9d204572827897aac44642375b2706929`; final committed revision/CI are recorded only after observation.

## Criterion mapping

| Criterion | State | Evidence or limitation | Remaining action and owner |
|---|---|---|---|
| AC-001 | passed | Real isolated Git: read-only plan, two distinct task branches/checkouts from the recorded base, preserved dirty canonical bytes/index, invalid IDs/paths/base/collisions/occupied refs and unsupported states rejected, duplicate create reconciled. | Retain regression checks in CI. |
| AC-002 | passed | Real child processes edit independent files/indexes. Same-project lock contention returns busy; another project progresses. A killed mutator retains creation intent and retry reconciles one allocation. Explicit ownership transfer succeeds; stale owner/generation fails. | Retain regression checks in CI. |
| AC-003 | pending | Synthetic broker plus real local Git verifies exact singleton repository scope, remote-head readback/revocation, disabled binding and forged/config/moved-membership denial before issuance. Recognized hooks migrate; an actual task hook process returns source-only before runtime execution. | Authorize named private fixture and prove native scoped fetch/push; project owner. |
| AC-004 | pending | Local task/component guards deny runtime/dependency/database execution. Managed and moved task roots are absent from inventory. Existing web, Python and group regressions passed; complete repository/database regressions are being verified. | Final repository/CI checks and independent live private-app observation; project owner/implementation agent. |
| AC-005 | passed | Producer handoff records actual head, dirty presence and attributed check/remaining labels; consumer resumes the same head and preserved dirty source. Stale owners/ref changes fail. Local and remote-observed publication differ; no automatic canonical integration or merge. | Owner acceptance of live handoff belongs to AC-007. |
| AC-006 | passed | Active, dirty, ignored/untracked, unpublished, moved/tampered and busy-Git checkouts are retained. Exact clean released checkout removal leaves branch, tombstone and other checkout intact. Lost create/removal responses reconcile. Squash retention revalidates PR head/merge against canonical ancestry. | Live cleanup only within explicit named-fixture scope. |
| AC-007 | pending | Focused isolated tests passed and documentation/runbook/adoption guidance exist. No infrastructure, production, runtime activation or installed-host-policy changes were made. | Final repository checks, final-revision CI, named private exercise, fresh-task guidance verification, owner acceptance and merge remain separate gates. |

## Executed verification

Tests run as forge using the existing Python 3.12 manifest environment with
synthetic repositories/configuration/tokens in task-owned temporary directories.
No real App key/token values are used in tests or evidence.

- `.venv-manifest/bin/python -B scripts/tests/test_project_worktrees.py`: the
  initial 20-test corrected suite passed. The expanded 25-test suite passed
  within the complete repository check (131.896 seconds); subsequent final
  snapshot-hook checks are listed below.
- `.venv-manifest/bin/python -B scripts/tests/test_project_worktrees.py Tests.test_actual_hook_process_refuses_task_before_runtime Tests.test_recognized_hook_migrates_and_task_never_verifies_canonical`:
  both passed after ensuring owned hook migration selects the guarded snapshot.
- `.venv-manifest/bin/python -B scripts/tests/test_project_worktrees.py Tests.test_actual_killed_mutator_recovers_durable_intent`:
  passed after reporting known creation intent without a checkout as interrupted.
- `.venv-manifest/bin/python -B scripts/tests/test_private_apps.py`: passed.
- `.venv-manifest/bin/python -B scripts/tests/test_project_python.py`: 25 passed.
- `.venv-manifest/bin/python -B scripts/tests/test_project_groups.py`: 16 passed.
- `PATH="$PWD/.venv-manifest/bin:$PATH" ./scripts/check-repository.sh`: running;
  no whole-gate result is claimed yet.
- `bash -n scripts/check-repository.sh`: passed.
- `git diff --check` and `git diff --cached --check`: passed at the recorded
  local checkpoints; final staged/link checks are pending.

The first focused run failed two hook tests because synthetic `.git/hooks` had
not been created; fixture setup was corrected and both passed. An added killed
mutator test initially expected `creating` where status reported a conflict;
known durable intent is now reported as interrupted and the corrected test passed.
The first invocation also accidentally discovered the imported broker test class;
test discovery was corrected to import its module instead. These fixture/status
failures do not establish live failures or acceptance.

Terraform validation/tests were not run: this change does not edit infrastructure.
No deployment, merge, public exposure or owner acceptance is claimed.

## Private readiness and remaining work

Read-only enrollment metadata includes two old PRJ-005 verification records whose
checkout no longer exists. The absent `gptclaw-prj005-one` root was not recreated,
auto-adopted or removed from enrollment. Do not treat enrollment metadata alone
as proof that a live checkout exists.

The alternative enrolled synthetic app `gptclaw-trailboard` passes read-only
worktree planning. Its existing upstream branch configuration is retained; known
provider dependency caches are excluded from nested-source-repository detection.
No task allocation, helper/hook change, remote write, app/database operation or
checkout removal has occurred there. A named-target question proposes two Git-only
synthetic task branches, retaining branches/receipts and removing only clean released
test checkouts. This authorization remains pending; no answer is inferred.

After authorization, use the operator runbook for the two-task exercise, native
scoped fetch/push, producer/consumer handoff and cleanup/retention disposition.
Observe a separate existing app without mutation. Verify adopted guidance in a
fresh task and record actual project-owner acceptance. Keep the guarded helper/
provider snapshots while managed allocations exist; rollback must retain paths,
branches and receipts and preserve runtime/discovery exclusions.
