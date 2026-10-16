# SPEC-037 acceptance evidence

- **Status:** Technical and owner usability acceptance passed; operator cleanup and delivery pending
- **Owner:** Project owner
- **Date:** 2026-10-16 UTC
- **Specification:** [SPEC-037](spec.md) · **Design:** [TDD-037](technical-design.md) · **Tasks:** [TASKS-037](tasks.md)
- **Implementation:** [PR #86](https://github.com/danielbardsley/gptclaw/pull/86), branch `codex/dsh-009-controls`

Implementation, PR publication and private rollout/fixture acceptance were separately
authorized. Remote task opening remains excluded. Owner usability acceptance,
review/merge and catalogue delivery remain separate gates.

## Acceptance map

| Criterion | Observed evidence | Remaining |
|---|---|---|
| AC-001 | Profile/action capability and refusal tests, unsafe/source/worktree/identity/lease cases, changed bindings and compatibility passed. All five deployed application profiles and managed Metro operations passed. | None for the technical contract. |
| AC-002 | Local failure/order/recovery tests and all deployed project actions passed: Start/no-op, Stop, Restart, running/stopped Rebuild and eligible same-instance Pause/Resume. Persistent Pause/Resume refused without effects. | None for technical lifecycle acceptance. |
| AC-003 | Deployed independent WEB/API/DB/Metro restarts preserved siblings, persistent notes/storage identity and the isolation peer. Ephemeral API warning/loss and Metro lease/backend independence passed; dependency/DB-failure recovery tests passed. | None for technical isolation/data acceptance. |
| AC-004 | Strict socket/frontend and ten actual HTTPS adversarial cases passed. Final installed frontend has only read-only immutable assets and socket-directory mounts. | None for the technical boundary. |
| AC-005 | Contention, idempotency, timeout, worker/controller death, storage and retention tests passed. Actual unknown Pause, lost admission response, disconnected rebuild client and browser receipt reload were resolved without replay. | None for technical recovery acceptance. |
| AC-006 | Synthetic reference/viewport/focus/contrast/response-loss regressions passed. Real private confirmation/Cancel, reload recovery and both owner-requested visual corrections passed browser checks. | None. The project owner accepted all requested checks after both corrections. |
| AC-007 | Local/focused/frontend checks, exact implementation CI, all deployed fixture matrices, persistent-note rollback and deployment/isolation audit passed. | Operator route cleanup, review/merge and final delivery records. Subsequent documentation changes require their applicable checks. |

## Local and CI verification

The exact original checkpoint `7e295de` passed the complete repository gate with
882 cases in 46 suites. A later `./scripts/check-repository.sh` passed **888 cases
in 46 suites** in 2,275 seconds. That run started at `f5f99c6` and its worktree
changed while live corrections landed; it is broad regression evidence, not an
exact-revision gate. Exact implementation CI is recorded separately below.

Focused checks passed after the relevant corrections:

- Provider controls: 22 cases, including completion-write failure after replacement preserving an unknown guard and reconciliation without another replacement.
- Controller: 15 cases covering one-time 60-second intents, idempotency, capacity/storage, generation changes, adversarial sockets, spawn failure and recovery.
- Observer: 12 cases, including schema-7 API docs/health and real paused-state semantics. Status: 8 cases. Immutable installer: 11 cases, including exact-provider ordering, unknown/paused refusal, disablement and compatible rollback.
- Pinned rootless frontend: 21 tests, type generation/typecheck, production build, real Unix socket/HTTP and complete synthetic browser acceptance. The latest sizing correction reran the full gate, including mixed-link height/font/padding checks at 1440/1280/768/390/720 CSS px and confirmation hover contrast.
- Optional native harness: single API, single WEB, WEB/API, API/DB and WEB/API/DB passed lifecycle/rebuild/retention/isolation checks and owned runtime cleanup. Its finite systemd/Serve adapter is separate from the actual private/systemd evidence below.
- Actual HTTPS refused missing/foreign Origin, missing cookie/CSRF, duplicate JSON keys, invalid UTF-8, malformed JSON, extra command field, command component and oversized body (400/403/413); the peer instance remained unchanged.
- Diff whitespace, changed-shell syntax and initiative relative links passed. No Terraform apply, AWS mutation, host package install, public exposure or production operation occurred.

All four applicable workflows passed implementation revision `4ced498`:
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38823534624),
[application](https://github.com/danielbardsley/gptclaw/actions/runs/38823534635),
[development host](https://github.com/danielbardsley/gptclaw/actions/runs/38823534623)
and [federation](https://github.com/danielbardsley/gptclaw/actions/runs/38823534621).
All four also passed `66ef219` before the sizing correction. All four final-head
workflows passed evidence checkpoint `1911452`: dashboard (38825155832), application
(38825155870), development host (38825155846), federation (38825155860). These
results precede the subsequent owner-acceptance documentation update.

## Actual private fixture matrix

All operations used reviewed frozen CLI preparation or the actual private HTTPS
control endpoints with session/CSRF proof and durable UUIDs before submission.
No mutation was automatically retried. Canonical receipt readback confirmed **51
distinct successful dashboard operations**: 45 application-profile operations,
four Metro operations and two additional rollback-fixture Start/Stop operations.
The separately reconciled interrupted Pause remains a failed historical result.

| Owned synthetic profile | Successful canonical operations | Verified behavior |
|---|---:|---|
| Single API (`fastify`, schema 7) | 9 | Start/no-op; same-instance Pause/Resume; API restart; whole restart; running rebuild; Stop; stopped rebuild. |
| Single WEB (`nextjs`, schema 1) | 9 | Same project matrix plus independent WEB restart. |
| Ephemeral WEB/API (`notes`, schema 3) | 10 | Both independent restarts preserve siblings; WEB restart retains the note, API restart gives the recorded in-memory-loss warning and clears it. |
| API/DB (`fastapi-postgres`, schema 8) | 8 | DB/API restart, whole restart and rebuild preserve the note and persistent identity; Pause/Resume refused without effects. |
| WEB/API/DB (`notes-postgres`, schema 4) | 9 | Each DB/WEB/API restart preserves siblings and the note; persistent identity retained; Pause/Resume refused without effects. |
| Managed Metro (schema 6) | 4 | Start no-op; Metro restart; whole-project restart; Stop, with transport/lease/backend isolation. |

Persistent profiles retained volume generation, epoch and migration revision.
Running Rebuild retained the actual DB instance and stored note; stopped Rebuild
left every component stopped. Stateless Pause/Resume retained native instance IDs,
with actual publication/readiness withdrawal and recovery. The paused rollback
attempt was refused with `control-paused` without changing the frozen instance.

Application source, manifest, lock and metadata retention checks passed. The
reviewed Next development server rewrites generated `web/next-env.d.ts`. For the
ephemeral group, replacing only that hash with the pinned template hash exactly
reconstructs the complete original 75-file fingerprint; all other hashes match.
Persistent WEB checks allowed only the same exact known generated-content transition
and required every other hash unchanged. Runtime admission still fingerprints this
file strictly; no product source-fingerprint exclusion was introduced.

All five application fixture runtime sets are now absent through reviewed Stop;
source and persistent synthetic data remain retained. Successful task-owned generated
recovery copies were removed only after stopped-state, journal and ownership checks.
The unchanged API isolation peer remains ready for the owner's final check. Its
instance identity/readiness was checked throughout, and its actual private health
endpoint returned 200 afterward. All ten pre-existing managed runtime IDs/states
and the existing 443/8445 route configuration remained unchanged.

## Installed release, rollback and recovery

- Controls release: `19d2c1df51679e7a49df3bbdb5f5c18068c48195ca6eba7423260326225a5dad`.
- Compatible read-only rollback: `316f7c8db6c4c41f5b99a328a63099109df4637c3a0126c4d09e1d154b5b76b2`.
- Frozen provider 1.15.0: `234f928b41d91a3bff55cb9c0af13111936f6a2ffd6c5b6308e8c41d3598b3a8`.

The approved rollout upgraded only the owned stable launcher/ingress before controls
activation; the manager requires their exact frozen provider. Final readback proved
all three dashboard services active, all operations terminal, the exact stable CLI
and only read-only `/app` assets plus `/run/gptclaw` socket-directory mounts.

Persistent-note rollback passed on the owned API/DB fixture. Writes were disabled,
the compatible read-only release activated, and the controller became inactive.
The read-only proxy hid control routes with 404; the rehearsal's initial expected
503 was corrected after observing that deliberate default-off boundary. The same
API/DB and peer instances, note, database identity and **51 operation-record hashes**
were retained. Controls were restored to the corrected release; the note and
instances remained intact, then the fixture's separate Stop succeeded. No data
rollback, source restore, migration or project restart was used to roll back controls.

Actual recovery evidence remains distinguishable from successful operations:

- Pause `5bbacc84eafb4948b7d5bef0833a5983` froze its existing API instance, then retained an honest unknown/guard because real Podman reports `Paused=true, Running=false` while systemd stays active. Corrected provider/observer checks recognize this state. CLI restart and rollback were blocked; exact explicit reconciliation and a separate Resume retained the same instance. Fresh corrected Pause/Resume later passed.
- Stop UUID `1fd5587004804828b763999213b831ab` received an unavailable response. After disabling writes and retiring its controller, no controller record, native journal or guard existed, proving it was never admitted and could no longer run. Its observation client was then retired; no native action was replayed.
- WEB rebuild `7b289a920e5441af9f05aed4f5f37ae0` continued after its observation client ended. A later client observed that same completed UUID, verified receipt-generation continuity and replacement creation time, and submitted only the unfinished subsequent actions.
- A real browser seeded an already completed API receipt UUID into the normal recovery key. Two reloads fetched the same succeeded receipt and bounded Recent results with zero POSTs. This is actual receipt recovery, not a claim of injecting a new lost mutation response.

## Metro and scoped route cleanup

The explicitly approved retained roots are `mob001-accept-one` and
`mob001-accept-two`. The existing SSM operator added only private HTTP handlers
8443/8444 to owned proxies 18601/18603. Independent readback verified exact additions,
unchanged 443/8445 handlers and Funnel off; both private protocol/routes reached ready.

| Operation | ID | Actual result |
|---|---|---|
| Start no-op | `b42ced7bf3454839a919c786ec05f2e3` | Same generation and absolute expiry. |
| Restart METRO | `b2ebf5e1399c45169b112c96405333a0` | New generation; unchanged absolute expiry/transport. |
| Restart project | `902d2e88d6b34dc9823f1196a6b9894d` | New generation; unchanged absolute expiry/transport. |
| Stop on a separate finite generation | `c9d7f4ca80bf4c7f94a652ae6e3bb9f4` | Stopped; owned SDK/audit/network absent and proxy released. |

The other session and backend peer identities/health remained unchanged. Original
leases expired normally without extension; the separate finite Stop generation did
not renew either old lease. Final readback proved both fixtures inactive, owned
handles absent, proxies free and retained Git sources clean. This is host/private
Metro evidence, not physical Expo Go/native-client acceptance from other initiatives.

The existing operator still needs to remove only 8443/8444 and return readback per
the [operator handoff](operator-plan.md). The expected restored baseline digest is
`e2260ad525b61b5f15e51d20e38f3074fda6e555458eb6a939fb827725b33e0a`.
Current readback still matches the exact approved additions, with Funnel off.
Forge has not administered Tailscale or removed unrelated handlers.

## Presentation and owner acceptance

Reference-derived synthetic browser checks passed layout, focus/keyboard, Confirm/
Cancel, stale/busy/unsupported/failure states, unchanged real metrics, reduced motion,
contrast and all required viewport/reflow proxies. Actual private confirmation,
Cancel/focus return and 1440/390 layout passed with zero lifecycle submissions.
The 720 CSS px proxy does not substitute for the owner's actual 200% zoom check.

The project owner requested two corrections; both are implemented and installed:

- Confirmation hover: the shared neutral hover rule washed out the red confirmation button while leaving white text. Explicit neutral Cancel and dark-red Confirm states passed real private contrast checks (15.11:1 and 7.19:1).
- Quick-link sizing: mobile CSS gave only clickable anchors a 44 px minimum while unavailable spans retained 24 px. All quick-link pills now share mobile minimum dimensions. The full frontend gate and real read-only Fieldnotes API/Mobile checks passed equal heights/fonts/padding at 1440/1280/768/390/720 CSS px: 24 px desktop, 44 px mobile, no overflow and zero mutation requests. Only the two requested rows' link regions were captured.

On October 16 UTC, the project owner answered **“Accept — all checks completed”**
to the superseding recheck covering both corrections, desktop/mobile, keyboard,
actual 200% zoom and the Restart API → Cancel flow. This is owner-reported usability
acceptance, distinct from automated browser evidence, and supersedes the earlier
limited phone sizing confirmation.

After acceptance, the reviewed stable provider 1.15.0 stopped the retained synthetic
peer `dsh009-ctl-f6a20747-peer` once. Receipt
`1fbaef3f239a48a4b2b416751b8401e6` passed with `state=stopped`,
`changed=true`, and source retained; subsequent status confirmed stopped, no busy
operation and the same passed operation ID. Scoped native inspection found no peer
container, and its private publication returned 404. This CLI cleanup is additional to the
51 successful dashboard operations above.

Scoped operator removal of temporary 8443/8444 handlers and review/merge remain
open. Keep catalogue status In progress until merged implementation and required
acceptance pass. Generated evidence is task-private/ignored; no credentials,
environment dumps or real datasets are committed.
