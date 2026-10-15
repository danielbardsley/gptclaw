# TASKS-037: Dashboard constrained controls

- **Status:** Draft planning package; implementation and rollout pending authorization
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
- [ ] Project owner reviews the detailed proposal and authorizes implementation; record approval separately from planning and later rollout authorization.

Planning checks and PR are recorded in the handover below. The request to draft
plans authorizes this package, not product code changes or runtime operations.

## Implementation in dependency order

### TASK-037-002 — Freeze typed lifecycle/capability contracts

- [ ] Inventory exact current provider/adapters, release pins, runtime/DB/Metro locks, source-handoff guards and receipt consumers before modifying them.
- [ ] Implement versioned capability/preflight/result schemas and matrix for all profiles in CTL-001, including unknown/old provider and missing ownership refusals.
- [ ] Add compatible CLI component restart/rebuild/pause/resume parsing and typed dispatch; preserve existing no-component behavior.
- [ ] Specify canonical target binding/generation/input fingerprints, lock order, exact stage deadlines and pause state/publication semantics in source contracts/runbooks.
- [ ] Test invalid action/component combinations, worktree/checkout/drift/conflict, missing/expired Metro authorization and backward compatibility.

Maps CTL-001/002/007 → AC-001/002/007. Gate: a versioned contract and meaningful
provider tests exist before UI buttons can enable an operation.

### TASK-037-003 — Deliver individual service restarts

- [ ] Add selected-component restart under shared project/DB/Metro locking and durable active-operation guards; reject stopped/paused targets or unavailable dependencies.
- [ ] Preserve sibling instance IDs, existing network/ports/artifacts/source; persist before/after stages and partial/unknown failure receipts.
- [ ] Implement graceful DB restart with identical volume and record retention, conflicts with DB maintenance, dependent health/route rechecks and explicit recovery without cascading.
- [ ] Keep Metro restart within its generation/transport/expiry contract; prove backend and other-session isolation. Warn for ephemeral API loss.
- [ ] Add tests for every declared component, dependency failure, unknown ownership, death during replacement and concurrency with group/CLI/DB/source-handoff actions.

Maps CTL-001/003/006 → AC-001/003/005. Depends on TASK-037-002.

### TASK-037-004 — Deliver remaining project controls

- [ ] Verify start/no-op/stop/restart and partial-group cleanup against shared guard/receipts, source/data retention and dependency/readiness order.
- [ ] Implement rebuild validation/build-before-replace, input revalidation, retained prior artifacts, stopped-project preservation and DB exclusion; inject preparation/replacement/readiness failures.
- [ ] Implement pause/resume only for stateless eligible profiles, typed freeze/unfreeze, paused observations, publication withdrawal/recovery and graceful stop while paused.
- [ ] Test pause/resume partial failures and controller/provider interruption; preserve actual instance counters and refuse paused restart/rebuild or DB/Metro pause/resume.
- [ ] Record explicit recovery steps; do not introduce auto-repair, idle shutdown, dependency upgrades, migrations or data rollback.

Maps CTL-002/006 → AC-002/005. Depends on TASK-037-002/003 so group and component
operations share one ownership and serialization model.

### TASK-037-005 — Deliver private controller and write boundary

- [ ] Implement controller socket/service using validated current identity bindings and immutable provider code; keep collector reads independent and frontend mounts restricted.
- [ ] Add exact route/method/Host/Origin/Fetch Metadata/content-type/CSRF/session checks, strict schema/body limits and no-store responses. Keep GET/HEAD side-effect free.
- [ ] Add 60-second one-time intents with impact/generation binding, durable accepted operation/idempotency records and worker capacity limits; changed bindings or effects require new consent.
- [ ] Implement atomic safe state writes, restart/orphan reconciliation, bounded terminal-result retention and fail-closed capacity/storage behavior; preserve active/unknown records.
- [ ] Test malicious paths/commands/fields, missing/foreign Origin, replay, expired confirmation, changed directory/manifest/runtime, two tabs, retries and direct CLI contention.
- [ ] Inject lost responses, worker/controller death, timeouts and disk/write failures at each side-effect boundary; prove at-most-once dispatch and honest unknown outcomes.

Maps CTL-001/005/006/007 → AC-001/004/005. Depends on TASK-037-002–004.
Gate: backend/security/recovery tests pass before controls can be enabled in a browser.

### TASK-037-006 — Implement reference-derived interaction

- [ ] Add expanded Lifecycle panel/toolbar, integrated component Restart column, inline impact/confirmation, actual stage/result and five-result Recent strip.
- [ ] Render all profile capabilities with explicit disabled reasons; preserve metadata, destinations, full component metrics and stale/last-known semantics.
- [ ] Implement deliberate Start/Resume submission, interrupting-action Confirm/Cancel, generation/expiry invalidation and idempotent operation recovery after reload/lost response.
- [ ] Preserve row disclosure/focus through snapshot updates; do not optimistically change health/links/counters or simulate progress.
- [ ] Add responsive stacking, accessible labels/announcements/focus return, touch targets, contrast and reduced motion using existing React/CSS/fonts.
- [ ] Exclude component stop/pause, remote tasks and all unsupported mock search/filter/rescan/log/preview/type/counter demos.

Maps CTL-004/005/006 → AC-006. Depends on TASK-037-005; synthetic UI scaffolding
can proceed against frozen contracts while backend tests run, but must remain disabled.

## Verification and delivery

### TASK-037-007 — Local and CI evidence

- [ ] Run relevant provider/controller/frontend adversarial and behavior tests, full offline repository gate, changed-shell syntax, diff checks and documentation link review.
- [ ] Run frozen frontend install/test/typecheck/build through existing pinned rootless tools; retain existing snapshot/status/link/Metro/security regressions.
- [ ] Capture deterministic synthetic reference comparisons at 1440/1280/768/390 px and 200% reflow; verify keyboard/confirmation/refresh/focus/targets/contrast and no document overflow.
- [ ] Verify failed/stale/conflicted/unsupported/read-only/controller-unavailable presentation and no mutations from reads/navigation/disclosure; inspect resulting routes and restricted mounts.
- [ ] Obtain applicable final-head CI and record local results separately. Create acceptance.md mapping each AC to actual evidence/pending status; do not claim live/owner acceptance from fixtures.

Maps CTL-001–007 → AC-001–007. Depends on TASK-037-003–006. No Terraform or host
package installation is expected; inspect actual changed scope if that assumption changes.

### TASK-037-008 — Reviewed release and rollback readiness

- [ ] Version provider/control/snapshot contracts and immutable installer descriptor/service/socket ownership; add default-off controls feature flag.
- [ ] Test old/new compatibility, missing controller/provider and disabling writes while reads continue; unknown contracts must never enable buttons.
- [ ] Prove rollout ordering and rollback with active/unknown/paused operation handling, evidence preservation and refusal of incompatible receipt downgrades.
- [ ] Update dashboard/private-app/provider runbooks with exact supported commands, operation retention/deadlines, recovery and no-data-deletion rollback.
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

Prepared spec/design/tasks and attachment reference mapping/captures on
`codex/dsh-009-controls-planning` from initially clean `main`. Only documentation
and inert reference PNGs change. No product code, installed provider, dashboard,
project service, data or infrastructure was changed. Scope direction is recorded;
detailed specification approval, implementation and private rollout remain pending.
Next action: project-owner review of this concrete planning package, especially
rebuild behavior, stateless pause eligibility and individual DB restart impact.
Planning verification: `git diff --check` and `git diff --cached --check` pass;
268 relative documentation links across the six changed Markdown files resolve.
Requirement/criterion/task-ID coverage checks pass (7 requirements, 7 criteria,
9 task groups), accounting for slash-abbreviated references. The initial literal-ID
checker rejected abbreviated references; the corrected checker passed. The attached
reference rendered offline at desktop/narrow sizes; these captures establish reference
appearance only. Runtime/frontend/repository implementation suites, CI, deployment
and owner acceptance were not run for this documentation-only package. The planning
branch is delivered through a PR to main.
