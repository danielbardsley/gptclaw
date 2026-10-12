# ACCEPTANCE-029: Dashboard project links

- **Status:** In progress — local evidence; CI, installed/private and owner gates pending
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-029](spec.md) · **Design:** [TDD-029](technical-design.md) · **Tasks:** [TASKS-029](tasks.md)
- **Source:** isolated `codex/dashboard-specs` branch, [PR #69](https://github.com/danielbardsley/gptclaw/pull/69); committed integrated revision to be recorded

## Criterion mapping

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | Passed locally | Exact web/API/group route paths are capability-bound; stopped/stale/conflicted/unrouted fixtures disable links. Actual API and group docs capability was observed from fixed private paths. |
| AC-002 | Passed locally; live conditional | Repository independence and missing metadata pass. Synthetic bound viewer capability generates only the opaque same-origin destination; actual absent viewer is unavailable and no log reader exists. |
| AC-003 | Passed locally; live pending | Six link tests cover active/expired/revoked/stale/absent/wrong-project/forbidden previews. Browser expiry uses collector time plus elapsed time. No real registry/exposure is created; installed absence evidence remains. |
| AC-004 | Passed locally | Backend/rendering URL tests reject credentials, unsafe schemes/ports/query/fragment/traversal/encoding; pure link projection execution/network spies pass. Browser tabs use noopener/noreferrer and labels render as text. |
| AC-005 | Pending live/owner | Production browser tests pass for enabled/disabled links, unavailable explanations, repository survival and expiry. Owner navigation to task-owned real app/API/group docs and recorded repository remains; future viewer/registry live integration is explicitly separate. |

## Executed verification

Using `/srv/forge/projects/gptclaw/.venv-manifest/bin/python -B` in the isolated
project-volume worktree:

- `scripts/tests/test_dashboard_observation.py`: seven tests passed.
- `scripts/tests/test_dashboard_status.py`: eight tests passed, including actual bounded multiprocessing workers and timeout handling.
- `scripts/tests/test_dashboard_links.py`: six pure destination/capability/security tests passed.
- Inventory/collector/release suites passed (12/5/7 tests respectively).
- `scripts/tests/check_dashboard.py --engine podman --reuse-node-image localhost/gptclaw-node:24.21.0-pnpm12.10.1 --reuse-browser-image <verified pinned browser image> --output <task-owned output>` passed frozen install, seven frontend tests, type generation/TypeScript checking, production build, actual socket/HTTP and browser acceptance.
- `PATH=/srv/forge/projects/gptclaw/.venv-manifest/bin:$PATH ./scripts/check-repository.sh`: full offline repository gate passed; ignored task-owned log retained.
- `git diff --check`, changed Python parsing and checker shell syntax passed.

A live read-only pool on the existing 13-project inventory returned current
ready/stopped states for every project, including both PostgreSQL-backed groups
and the web/API group, in about five seconds. It observed exact standalone/group
docs capabilities. No lifecycle operation or application dataset mutation was
used for this measurement; it does not replace the required task-owned lifecycle
acceptance or owner desktop evidence.

Initial concurrent native reads exceeded the per-project deadline under process
startup/CPU contention. Trusted forkserver preloading, scoped inspection reuse and
CPU-aware concurrency resolved this without enlarging the two-second limit.
Unknown/timeouts were kept unavailable, never claimed healthy.

## Remaining delivery

Final integrated CI results and committed source/release/image/provider identity
remain to be recorded. `/srv/forge/platform` is still an operator prerequisite;
no installed dashboard/private Serve/owner acceptance is claimed. After the base
is provisioned through the reviewed operator path, roll out inventory, status and
links in order, verify owned listeners/mounts/Funnel-off/rollback and explicit
synthetic target degradation/recovery. Complete owner browser checks and reviewed
merge before marking Delivered. Preserve all existing projects/data and unrelated
configuration. Future logs/preview integration requires accepted DSH-006/NET-108
prerequisites and new live evidence; unavailable adapters satisfy only the initial
explicitly scoped behavior.

## Integrated revision evidence

Implementation revision `83f28412c3218684e55a5c004b7de5bd762223e1` passed all four
GitHub Actions workflows: [dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38317412620),
[development-host quality](https://github.com/danielbardsley/gptclaw/actions/runs/38317412699),
[Tailscale federation quality](https://github.com/danielbardsley/gptclaw/actions/runs/38317412793),
and [private applications](https://github.com/danielbardsley/gptclaw/actions/runs/38317412651).
No protected deployment/apply was invoked.

A task-owned collector with both status/links enabled and the actual production
frontend on loopback completed integrated HTTP/browser checks: all 13 inventory
rows were current, 10 ready and 3 stopped, with 13 enabled private app/docs links.
The actual group panel displayed live web/API/DB status and timing/counters, and
its API-doc link matched the owned prefix exactly. No real logs/preview link was
enabled; no preview was created. The screenshot is ignored task-owned evidence.
The exact QA socket lock and container ownership label proved cleanup authority;
only those QA services were stopped/removed. Existing application data/services
and Serve handlers were preserved.

This strengthens local/integrated evidence and does not satisfy installed main
service, operator Serve, owner desktop, lifecycle recovery or merge gates. The
base directory remains operator-required and the goal remains incomplete.

The portable production browser gate also passed with `Date.now()` shifted twelve
hours in the browser. Preview withdrawal still followed collector time plus elapsed
time without reload, and repository navigation remained available.
