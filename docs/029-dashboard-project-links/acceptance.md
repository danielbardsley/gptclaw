# ACCEPTANCE-029: Dashboard project links

- **Status:** Local/CI/private/owner acceptance passed — review/merge pending
- **Owner:** Project owner
- **Date:** 2026-10-12 (America/New_York)
- **Specification:** [SPEC-029](spec.md) · **Design:** [TDD-029](technical-design.md) · **Tasks:** [TASKS-029](tasks.md)

## Criterion mapping

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | Passed local/CI/live | Exact owned app/API/group capabilities; stopped/stale/conflicted cases; live web stop withdraws app link. |
| AC-002 | Passed local/CI/live | Actual fixture repository survives web stop; absent viewer has no enabled logs link or log read. |
| AC-003 | Passed local/CI/live absence | Synthetic preview expiry/revocation/binding/clock cases; actual absent registry is unavailable; no exposure created. |
| AC-004 | Passed local/CI/live | Structural URL validation/spies/text/safe-tabs; actual HTTPS UI and boundary checks. |
| AC-005 | Passed local/CI/live/owner | Owner explicitly confirmed corrected group details and task-owned web, standalone API, group docs and repository navigation. |

## Verification and delivery evidence

Implementation is in [PR #69](https://github.com/danielbardsley/gptclaw/pull/69),
branch `codex/dashboard-specs`. Source is `platform/dashboard/` plus trusted
collector/provider/lifecycle scripts. The current implementation is privately
deployed; review/merge remains pending.

Executed focused checks use the isolated manifest interpreter:

- `scripts/tests/test_project_manifest.py`: 28 tests passed; exact current schema bytes still control full manifest validation.
- `scripts/tests/test_dashboard_inventory.py`: 12 tests passed.
- `scripts/tests/test_dashboard_collector.py`: 5 tests passed, including real Unix HTTP, bounded worker termination/reaping and partial/failure recovery.
- `scripts/tests/test_dashboard_install.py`: 8 tests passed, including owned rollback and separately bounded compiled checksum metadata.
- `scripts/tests/test_dashboard_observation.py`: 9 tests passed, including fixed query/probe bounds and restoration of ordinary lifecycle helpers.
- `scripts/tests/test_dashboard_status.py`: 8 tests passed. The actual four-second default with 20 projects, a hung worker and coalesced readers completed within the 15-second criterion (suite about 6.2 seconds).
- `scripts/tests/test_dashboard_links.py`: 6 tests passed.
- Portable `scripts/tests/check_dashboard.py --engine podman` with verified existing Node/browser images passed frozen install, seven frontend tests, type generation/TypeScript, production build, socket/HTTP and browser checks. Browser cases include keyboard, escaped labels, empty/partial/stale/recovery, zero/null metrics, safe tabs and preview expiry with a twelve-hour wall-clock skew.
- `git diff --check` and `git diff --cached --check`: passed.

All four CI workflows passed on final implementation revision
`7df93cbeedc986c92c5554f2e43fc7b5376dc2a7`:
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38328187626),
[development-host quality](https://github.com/danielbardsley/gptclaw/actions/runs/38328187624),
[Tailscale federation](https://github.com/danielbardsley/gptclaw/actions/runs/38328187633),
and [private applications](https://github.com/danielbardsley/gptclaw/actions/runs/38328187608).
`PATH=/srv/forge/projects/gptclaw/.venv-manifest/bin:$PATH ./scripts/check-repository.sh`
passed the full final offline repository gate (exit 0). Earlier reruns found a cold
forkserver timing assertion or were interrupted (exit 143); none is claimed
successful. The regression now separates one-time bootstrap from the strict
warm-worker termination/reaping assertion.

## Installed/private evidence

The project owner provisioned `/srv/forge/platform` through the reviewed existing
SSM operator path and verified forge access. Observed ownership is forge:forge,
mode 0700, on the existing project volume. No AWS configuration/apply ran.
The owner then replied “done” to the exact reviewed Serve command after loopback
health passed. Read-only inspection and real HTTPS checks verify:

- `/dashboard/` -> `http://127.0.0.1:18200/dashboard/`.
- Existing `/projects/` -> `http://127.0.0.1:18079/projects/` is preserved; Funnel is off.
- Frontend is a rootless forge container, user 1002:1002, publishing only 127.0.0.1:18200. Its two read-only mounts are its immutable `/app` assets and `/run/gptclaw` socket directory.
- Owned user units `gptclaw-dashboard-collector.service` and `gptclaw-dashboard.service` are active; no project/credential/Podman-socket frontend mount exists.
- Actual private HTTPS page/health/snapshot return 200. POST returns 405; arbitrary root query returns 400; invalid Host and cross-origin reads return 403.

Inventory, status and links were activated in that order. Rollback from links to
the status-only release retained inventory/status, then restoring the full release
restored links. A real browser retained rows with “Inventory stale · collector
unavailable” during an ownership-verified collector stop and refreshed on restart.
Frontend/project runtimes/Serve remained intact.

Current full release is
`7ea8b649f931d93480c413f07edc40580ec76015a9a509e55f2071917d25b5a7`;
its exact provider/image/checksum descriptor is retained privately under its
immutable release directory. Frontend image is
`sha256:56cb97c5d887e341f46dd848e859e357957c92951c8c0879e08b97c4b971052c`,
with the prepared persistent manifest interpreter. The installed provider snapshot is
`dad82ad62342c9fd0afea4249d3324ef7e709adec222ed8a7debb83000575e83`.
Actual pair stop/start also passed: the synthetic API remained reachable while
both dashboard services were stopped, then dashboard health recovered.

## Synthetic lifecycle and owner evidence

Task-owned local-only projects are `dsh-accept-web`, `dsh-accept-api` and
`dsh-accept-db` (web/API/PostgreSQL). Existing application data is untouched.
Database fixture initialization required explicit stopped API dependency
preparation; the same allocated operation then resumed and initialized successfully.
No reset/reinitialization or existing-data deletion was used. Record this prerequisite
rather than claiming the first initialization attempt succeeded.

Web CLI stop withdrew its app link while retaining its configured repository link.
CLI start recovered ready state. An explicit restart returned its operation ID and
stop/start transition IDs; the dashboard current-instance counter was measured zero
and uptime reset. The repository fixture destination is the fixture source repository,
`https://github.com/danielbardsley/gptclaw`, recorded in task-owned metadata without Git
configuration or credential reads.

A reversible readiness-only source fault in the synthetic group produced CLI
`degraded` and dashboard API-unhealthy/DB-healthy, with app/docs links withdrawn
in 14.81 seconds. Exact original source bytes were restored in a finally block.
The first immediate recovery deadline was missed during CPU contention. After
the budget correction and full checks completed, a clean repeat observed degradation
in 9.62 seconds and recovery in 14.96 seconds, with all three components healthy and
both app/docs links restored. Neither scenario was caused by a dashboard action.

The owner initially confirmed desktop inventory, keyboard component details and a ready
project link “Works as described”, then identified working groups displaying
observation timeouts. That report required a correction before group acceptance.
The original two-second worker bound was too short on this two-CPU host. Trusted
schema meta-check reuse, one authenticated DB revision read, bounded HTTP probes
and a documented four-second project deadline address that cause. Subsequent
live snapshots showed all 16 rows current (13 ready, 3 stopped), including all four
groups. The owner then confirmed “Group details and all links work” after refreshing
and opening the synthetic web app/repository, standalone API docs and group API docs. The owner explicitly deferred
style/format changes, which are outside this delivery.

Owner URL: `https://forge-dev-01-4.tail8c3304.ts.net/dashboard/`.
Owner acceptance covers the task-owned web app, standalone `/docs`, group `/api/docs`,
configured repository and corrected group details. Review/merge is still required
before Delivered. After owner/browser verification, the three named synthetic runtimes were stopped
through the reviewed CLI; source, restricted runtime credentials/data and ignored QA
evidence are retained. Existing projects and their services/data are untouched. Logs/preview prerequisites remain unavailable;
future live integrations require separately accepted DSH-006/NET-108 scope.
