# TASKS-037: Dashboard constrained controls

- **Status:** Implementation authorized — work in progress
- **Owner:** Project owner
- **Date:** 2026-10-15 (America/New_York)
- **Specification:** [SPEC-037](spec.md) · **Design:** [TDD-037](technical-design.md)
- **Visual reference:** [Reference mapping](reference.md)

## Planning and authorization

### TASK-037-001 — Prepare reviewable scope

- [x] Inspect root/area guidance, clean initial Git status, index/catalogue and current dashboard/provider contracts.
- [x] Record the owner's direction: project controls plus individual service restarts; exclude remote task opening entirely.
- [x] Inspect supplied HTML as reference data; capture desktop/narrow rendering in an offline isolated browser and document supported adaptations.
- [x] Draft linked requirements, design, tasks and acceptance mapping; update index/catalogue to Draft.
- [x] Project owner authorized implementation October 15: “Implement the spec for DSH-009. Finish when all acceptance criteria are met.” Private rollout and actual owner acceptance remain separate gates.

Planning checks and PR are recorded in the handover below. The initial drafting request authorized this package; the later implementation
instruction and separate PR-publication approval are recorded in SPEC-037.

## Implementation in dependency order

### TASK-037-002 — Freeze typed lifecycle/capability contracts

- [x] Inventory current provider/adapters, release pins, runtime/DB/Metro locks, source-handoff guards and receipt consumers before modification.
- [x] Implement versioned capability/preflight/result schemas and matrix for all profiles in CTL-001, including unknown/old provider and missing ownership refusals.
- [x] Add compatible CLI component restart/rebuild/pause/resume parsing and typed dispatch; preserve existing no-component behavior.
- [x] Specify canonical target binding/generation/input fingerprints, lock order, exact stage deadlines and pause state/publication semantics in source contracts/runbooks.
- [ ] Test invalid action/component combinations, worktree/checkout/drift/conflict, missing/expired Metro authorization and backward compatibility.

Maps CTL-001/002/007 → AC-001/002/007. Gate: a versioned contract and meaningful
provider tests exist before UI buttons can enable an operation.

### TASK-037-003 — Deliver individual service restarts

- [x] Add selected-component restart under shared project/DB/Metro locking and durable active-operation guards; reject stopped/paused targets or unavailable dependencies.
- [x] Preserve sibling instance IDs, existing network/ports/artifacts/source; persist before/after stages and partial/unknown failure receipts.
- [ ] Implement graceful DB restart with identical volume and record retention, conflicts with DB maintenance, dependent health/route rechecks and explicit recovery without cascading.
- [ ] Keep Metro restart within its generation/transport/expiry contract; prove backend and other-session isolation. Warn for ephemeral API loss.
- [ ] Add tests for every declared component, dependency failure, unknown ownership, death during replacement and concurrency with group/CLI/DB/source-handoff actions.

Maps CTL-001/003/006 → AC-001/003/005. Depends on TASK-037-002.

### TASK-037-004 — Deliver remaining project controls

- [ ] Verify start/no-op/stop/restart and partial-group cleanup against shared guard/receipts, source/data retention and dependency/readiness order.
- [ ] Implement rebuild validation/build-before-replace, input revalidation, retained prior artifacts, stopped-project preservation and DB exclusion; inject preparation/replacement/readiness failures.
- [ ] Implement pause/resume only for stateless eligible profiles, typed freeze/unfreeze, paused observations, publication withdrawal/recovery and graceful stop while paused.
- [ ] Test pause/resume partial failures and controller/provider interruption; preserve actual instance counters and refuse paused restart/rebuild or DB/Metro pause/resume.
- [x] Record explicit recovery steps; do not introduce auto-repair, idle shutdown, dependency upgrades, migrations or data rollback.

Maps CTL-002/006 → AC-002/005. Depends on TASK-037-002/003 so group and component
operations share one ownership and serialization model.

### TASK-037-005 — Deliver private controller and write boundary

- [x] Implement controller socket/service using validated current identity bindings and immutable provider code; keep collector reads independent and frontend mounts restricted.
- [x] Add exact route/method/Host/Origin/Fetch Metadata/content-type/CSRF/session checks, strict schema/body limits and no-store responses. Keep GET/HEAD side-effect free.
- [x] Add 60-second one-time intents with impact/generation binding, durable accepted operation/idempotency records and worker capacity limits; changed bindings or effects require new consent.
- [x] Implement atomic safe state writes, restart/orphan reconciliation, bounded terminal-result retention and fail-closed capacity/storage behavior; preserve active/unknown records.
- [x] Test malicious paths/commands/fields, missing/foreign Origin, replay, expired confirmation, changed directory/manifest/runtime, two tabs, retries and direct CLI contention.
- [ ] Inject lost responses, worker/controller death, timeouts and disk/write failures at each side-effect boundary; prove at-most-once dispatch and honest unknown outcomes.

Maps CTL-001/005/006/007 → AC-001/004/005. Depends on TASK-037-002–004.
Gate: backend/security/recovery tests pass before controls can be enabled in a browser.

### TASK-037-006 — Implement reference-derived interaction

- [x] Add expanded Lifecycle panel/toolbar, integrated component Restart column, inline impact/confirmation, actual stage/result and five-result Recent strip.
- [x] Render all profile capabilities with explicit disabled reasons; preserve metadata, destinations, full component metrics and stale/last-known semantics.
- [x] Implement deliberate Start/Resume submission, interrupting-action Confirm/Cancel, generation/expiry invalidation and idempotent operation recovery after reload/lost response.
- [x] Preserve row disclosure/focus through snapshot updates; do not optimistically change health/links/counters or simulate progress.
- [x] Add responsive stacking, accessible labels/announcements/focus return, touch targets, contrast and reduced motion using existing React/CSS/fonts.
- [x] Exclude component stop/pause, remote tasks and all unsupported mock search/filter/rescan/log/preview/type/counter demos.

Maps CTL-004/005/006 → AC-006. Depends on TASK-037-005; synthetic UI scaffolding
can proceed against frozen contracts while backend tests run, but must remain disabled.

## Verification and delivery

### TASK-037-007 — Local and CI evidence

- [ ] Run relevant provider/controller/frontend adversarial and behavior tests, full offline repository gate, changed-shell syntax, diff checks and documentation link review.
- [x] Run frozen frontend install/test/typecheck/build through existing pinned rootless tools; retain existing snapshot/status/link/Metro/security regressions.
- [x] Capture deterministic synthetic reference comparisons at 1440/1280/768/390 px and 200% reflow; verify keyboard/confirmation/refresh/focus/targets/contrast and no document overflow.
- [x] Verify failed/stale/conflicted/unsupported/read-only/controller-unavailable presentation and no mutations from reads/navigation/disclosure; inspect resulting routes and restricted mounts.
- [ ] Obtain applicable final-head CI and record local results separately. Create acceptance.md mapping each AC to actual evidence/pending status; do not claim live/owner acceptance from fixtures.

Maps CTL-001–007 → AC-001–007. Depends on TASK-037-003–006. No Terraform or host
package installation is expected; inspect actual changed scope if that assumption changes.

### TASK-037-008 — Reviewed release and rollback readiness

- [x] Version provider/control/snapshot contracts and immutable installer descriptor/service/socket ownership; add default-off controls feature flag.
- [x] Test old/new compatibility, missing controller/provider and disabling writes while reads continue; unknown contracts must never enable buttons.
- [ ] Prove rollout ordering and rollback with active/unknown/paused operation handling, evidence preservation and refusal of incompatible receipt downgrades.
- [x] Update dashboard/private-app/provider runbooks with exact supported commands, operation retention/deadlines, recovery and no-data-deletion rollback.
- [ ] Obtain private installation/rollout authorization for the prepared reviewed release; do not infer it from this planning request.

Maps CTL-007 → AC-001/005/007. Depends on TASK-037-007.

### TASK-037-009 — Live acceptance and delivery

- [ ] After rollout authorization, activate reviewed releases/flag through existing owned paths; preserve private access, all unrelated services/routes and data.
- [ ] On owned synthetic single web/API, ephemeral group, web/API/DB, API/DB and Metro fixtures, execute applicable project actions and each individual restart; capture before/after sibling identities and real readiness/route evidence.
- [ ] Verify actual DB record/volume retention, ephemeral API warning/loss, dependency/DB failure recovery and Metro/backend independence; prove stateless freeze/unfreeze and DB/Metro unsupported refusals.
- [ ] Verify lost response/reload reconciliation, default-off/disable behavior and recovery-first rollback with real owned receipts and no unrelated changes.
- [ ] Project owner checks desktop/narrow/keyboard/actual zoom and confirms usability/design/results; record actual owner acceptance separately from automation.
- [ ] Finish evidence, reviewable implementation PR and merge; update index/catalogue Delivered only when all required criteria pass. Preserve explicit remote-task exclusion and deferred profile capabilities.
- [ ] Remove only task-owned disposable fixtures through reviewed lifecycle, retain required evidence, and hand over Git state/remaining work.

Maps CTL-001–007 → AC-007 plus live portions of AC-002/003/005/006. Depends on
TASK-037-008. Planning/implementation/CI/rollout/owner acceptance remain distinct.

## Current handover

Implementation is underway on `codex/dsh-009-controls`, based on the planning
package in PR #85 and implementation draft PR #86. Typed provider controls, durable guards/reconciliation, a separate
private controller, frontend routes/panel, default-off release wiring and synthetic
behavior/browser tests are implemented. [Acceptance evidence](acceptance.md) records
actual completed checks and the remaining local/CI/runtime/owner gates. The intermediate offline gate passed 874 cases; native single-service checks and
synthetic browser controls checks passed. The real-container group run passed and
cleaned its owned resources. The API/DB native run also passed record/volume/credential
retention and peer isolation, then removed its owned runtime resources. Final
repository/CI gates continue.
The controls candidate and compatible read-only rollback are staged without activation,
and the installer now refuses an older stable provider before changing services. No deployed service has been changed for this feature. Continue from current files/test logs;
do not treat the initial local checks as final-head or live acceptance.
