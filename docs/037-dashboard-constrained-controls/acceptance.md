# SPEC-037 acceptance evidence

- **Status:** Private acceptance in progress; delivery incomplete
- **Owner:** Project owner
- **Date:** 2026-10-15 UTC
- **Specification:** [SPEC-037](spec.md) · **Design:** [TDD-037](technical-design.md) · **Tasks:** [TASKS-037](tasks.md)
- **Implementation:** [Draft PR #86](https://github.com/danielbardsley/gptclaw/pull/86), branch `codex/dsh-009-controls`

Implementation, PR publication, and private rollout/fixture acceptance were separately
authorized by the project owner. Remote task opening remains excluded. Owner flow
acceptance, final review/merge and catalogue delivery remain separate gates.

## Acceptance map

| Criterion | Observed evidence | Remaining |
|---|---|---|
| AC-001 | Capability/refusal and compatibility tests cover every profile/action, source/worktree/identity/lease conflicts, old providers and unsupported combinations. Actual managed Metro Start no-op, component/project restart and Stop passed. | Complete deployed non-Metro matrix and final-head CI. |
| AC-002 | Native-container tests passed for all five non-Metro profiles, including running/stopped rebuild and stateless freeze/resume. Actual API Start/no-op passed; interrupted Pause was explicitly reconciled and the same instance resumed. | Full corrected private lifecycle matrix and paused rollback refusal. |
| AC-003 | Five native profiles verify sibling/data/volume/epoch retention and ephemeral API loss. Actual Metro restarts retained absolute expiry/transport and the other session/backend peer. Actual Metro Stop released owned handles. | Deployed individual WEB/API/DB restarts, persistent notes and dependency-route recovery. |
| AC-004 | Strict socket/frontend tests and ten actual HTTPS negative cases passed. The frontend has only immutable assets and a read-only socket-directory mount. | Passed on the current installed release; retain final regression evidence. |
| AC-005 | Automated worker death, timeout, storage, contention and idempotency tests pass. Actual unknown Pause blocked CLI/rollback; exact reconciliation did not replay effects. A lost, never-admitted Stop request was resolved by retiring its controller with no record/journal/guard. | Final actual browser/reload result and remaining fixture operations. |
| AC-006 | Full synthetic browser suite passes all viewports, focus, confirmations, lost-response recovery, stale/busy/unsupported states and unchanged real metrics. Actual private confirmation displayed correctly. | Owner desktop/mobile/keyboard/zoom acceptance. |
| AC-007 | Private rollout and real read-only rollback executed. Broad local gate passed 888 cases/46 suites; focused final-code and frozen frontend checks pass. | Remaining private matrix, persistent-data rollback, final-head CI, owner acceptance and review/merge. |

## Verification

The original complete local repository checkpoint `7e295de` passed 882 cases in
46 suites. A later complete `./scripts/check-repository.sh` passed **888 cases in
46 suites**, including repository invariants, in 2,275 seconds. That run started
at `f5f99c6` and the worktree changed while live corrections landed; it is broad
regression evidence, not an exact-revision gate. Its durable scope/result records
are task-private. Exact-head CI is recorded separately below.

Relevant focused checks passed after corrections:

- Provider controls: complete 21-case run plus the additional completion-write-failure test; the broad gate ran all 22. Failure after replacement preserves an unknown guard, refuses a new mutation and reconciles without another replacement.
- Controller: 15 cases, including exact 60-second intent timing, one-time/idempotent admission, capacity/storage failures, stale generation, socket adversarial requests, completed-row publication and failed spawn/recovery.
- Observer: 12 cases, including schema-7 API docs/health and real paused-state projection. Status: 8 cases. Immutable installer: 11 cases, including exact-provider ordering, unknown/paused refusal, disablement and controls-only collector budget removal on rollback.
- Frozen frontend: 21 tests, route generation/typecheck, production build, real Unix socket/HTTP and complete synthetic browser suite. The latest full run used the pinned rootless Node/pnpm/browser images; no host packages or dependency pins changed.
- Native optional harness: single API, single WEB, WEB/API, API/DB and WEB/API/DB passed applicable lifecycle/rebuild/retention/isolation checks and task-owned runtime cleanup. Its finite systemd/Serve adapter is explicitly separate from actual private/systemd acceptance. The adapter now models a frozen container as an active unit.
- Actual HTTPS rejects missing/foreign Origin, missing cookie/CSRF, duplicate JSON keys, invalid UTF-8, malformed JSON, extra command field, command component and oversized body (expected 400/403/413). The peer instance stayed unchanged.
- Diff whitespace, changed-shell syntax and documentation links were checked. No Terraform apply, AWS mutation, host package install, public exposure or production operation occurred.

All four CI workflows passed `8cb6e0a`; its first mobile bootstrap attempt timed
out downloading pnpm, and the same-revision failed-job rerun passed without a pin
change. At implementation checkpoint `16ee8a5`, [dashboard #108](https://github.com/danielbardsley/gptclaw/actions/runs/38812934274)
passed; all jobs in [application #211](https://github.com/danielbardsley/gptclaw/actions/runs/38812934300)
and the quality job in [development host #310](https://github.com/danielbardsley/gptclaw/actions/runs/38812934170)
passed. Protected plan/apply jobs were skipped. [Federation #214](https://github.com/danielbardsley/gptclaw/actions/runs/38812934311)
was pending at the last observation. Final publication/CI remains a delivery gate.

## Actual private rollout and recovery

The original read-only dashboard was `35507309…` with stable provider 1.14.0.
Approved rollout upgraded the owned stable launcher/ingress through a disposable
API peer, then activated immutable controls releases using provider 1.15.0.
All ten pre-existing managed container IDs/states and the original private Serve
handlers remained unchanged through the observed upgrades.

Current implementation checkpoint:

- Controls release: `c636c3bcf09306a2d14c755c748a16ffd1e185248e6939eba9d98f6a987caff3`.
- Compatible read-only rollback: `230a0ff5e1d77717ed075327dea5cbb26a5125577dbae9d6aa0644df7fb08a2f`.
- Frozen provider: `234f928b41d91a3bff55cb9c0af13111936f6a2ffd6c5b6308e8c41d3598b3a8`.

Real activation exposed and corrected four integration issues: Next removes the
public base path before invoking route handlers; frontend JSON reserialization
erased duplicate keys; two-CPU concurrent inspection needed finite loaded-read
headroom; and published schema-7 APIs incorrectly entered a group-only docs branch.
The resulting gates use strict raw JSON, an exact internal-route normalization,
two incremental capability readers with a twelve-second deadline, and controls-only
status readers (two/eight seconds). Private transport/browser write deadlines are
30/35 seconds. Health freshness, native lifecycle deadlines, capacities and leases
remain unchanged. A fresh intent includes its server preflight time; older/missing
snapshots cannot revoke that proof, while newer changed generation or expiry does.
Submission still rechecks source/runtime identity before dispatch.

API Pause `5bbacc84eafb4948b7d5bef0833a5983` froze the existing instance, then
retained an honest unknown/guard because real Podman reports `Paused=true` and
`Running=false` while systemd stays active. Corrected provider/observer checks and
fixtures now recognize that state. The unknown blocked both managed rollback and
the stable CLI's conflicting restart. The exact operation was explicitly reconciled,
and a separate reviewed Resume returned the same instance ready. It was not replayed.

An actual compatible read-only rollback also passed. New writes were disabled,
the controller retired, and API/peer instance identities and operation evidence
were retained. An unavailable Stop response for UUID
`1fd5587004804828b763999213b831ab` had no controller record, native journal or guard
after controller retirement, proving it was never admitted and could no longer run.
Only its task-owned observation client was then retired. Controls were restored
through the reviewed manager for remaining acceptance; no native mutation was retried.
Persistent-note rollback evidence is still pending.

## Actual Metro evidence

The owner-approved retained synthetic roots are `mob001-accept-one` and
`mob001-accept-two`. Both began clean; their prior leases were expired/stopped.
Fresh finite sessions reached loopback protocol readiness. The existing SSM operator
added only private 8443/8444 handlers to owned proxies 18601/18603. Independent readback
proved exact additions, unchanged 443/8445 handlers and Funnel off; both actual
private route/protocol observations became ready. [Operator handoff](operator-plan.md).

On the original test lease, these dashboard operations passed:

| Operation | ID | Actual result |
|---|---|---|
| Start no-op | `b42ced7bf3454839a919c786ec05f2e3` | Same Metro generation and expiry. |
| Restart METRO | `b2ebf5e1399c45169b112c96405333a0` | New generation; identical absolute expiry/transport. |
| Restart project | `902d2e88d6b34dc9823f1196a6b9894d` | New generation; identical absolute expiry/transport. |
| Stop on a separate finite generation | `c9d7f4ca80bf4c7f94a652ae6e3bb9f4` | Stopped; owned SDK/audit/network absent and proxy released. |

The other session generation/expiry and backend peer identity/readiness stayed
unchanged. The original leases expired normally without extension. The separate
finite generation used for the remaining Stop test did not renew either old lease.
Both fixtures are now inactive, and owned handles/proxies are absent. The existing
operator has been asked to remove only temporary handlers 8443/8444; independent
baseline restoration is pending. This establishes host/private Metro control behavior,
not physical phone, Expo Go or native client acceptance from other initiatives.

## Remaining private evidence and delivery

Fresh disposable sources exist for single API, single WEB, ephemeral WEB/API,
API/DB, WEB/API/DB and an API isolation peer under task-owned `dsh009-ctl-f6a20747-*`
roots. Both persistent databases initialized successfully using the reviewed API
component dependency-install prerequisite. A failed first initialization retained
its allocation and resumed with the same initialization ID; no reset or reallocation
was used. Full deployed profile operations and persistent-note evidence remain pending.

The final real private HTTPS browser passed at the installed copy-corrected release:
component confirmation and Confirm focus, Cancel focus returned to the enabled
initiator or documented result-region fallback, 1440/390 layout without document
overflow, no browser errors and **zero lifecycle operation submissions**. Cropped
captures contain only the synthetic peer panel. The final frontend has exactly
read-only immutable `/app` assets and `/run/gptclaw` socket-directory mounts.
The project owner requested changes during usability acceptance: the confirmation
button hover colors were incorrect. The shared neutral hover rule overrode the
destructive button background while retaining white text. Explicit neutral Cancel
and dark-red Confirm hover states are implemented; the existing browser suite now
checks 4.5:1 text contrast while each is hovered. The complete pinned frontend test/typecheck/build, real socket/HTTP and browser
gate passed, including the hover contrast checks. Installation and owner recheck
remain pending. Owner desktop/mobile/keyboard/actual-zoom acceptance
is still open.
The neutral unavailable-action copy passed the pinned production build and is installed.

Keep final-head CI, actual lifecycle/data/rollback, owner acceptance and merge distinct.
Generated logs/captures and operation metadata remain in ignored/private task output;
no credentials, authentication material, environment dumps or real datasets appear
in this record. Only synthetic fixtures were mutated; unrelated project identities,
data, handlers and access remain protected.
