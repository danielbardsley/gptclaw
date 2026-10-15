# TASKS-036 — Mobile Python backend integration

Owner: Project owner. Status: Implementation merged; remaining native/final acceptance pending.
Date: 2026-10-15 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md)

## Planning and implementation gates

- [x] T1: Inspect mobile creation/Metro/Go, persistent backend contracts, actual group
  routing and existing planning; draft the Python/Android-first scope and visual direction.
- [x] T2: Project owner authorized implementation in this chat after PR #83 opened.
  Source baseline and SPEC-035 allocations checked; selected unused
  project schemas 8/9, catalogue 7, provider 1.14.0 and repository-owned client generator v1.
  Python/uv and Expo/Node profiles and historical contracts remain unchanged.
  Planning, review, merge, runtime rollout and final acceptance stay distinct. (MB-007)

## Implementation after authorization

- [x] T3: Implement strict opt-in mobile binding/public-config validation and API/DB-only
  contracts; extend capability/receipt validation, declared-component lifecycle,
  readiness, gateway routing and minimal inventory links. Preserve unbound mobile,
  old-provider refusal and all historical web/API/group/DB behavior. (MB-001,002,004)
- [x] T4: Publish a new exact Python/PostgreSQL backend starter using existing database
  ownership, init, roles, migration/backup/recovery and portable tests. Keep notes v1,
  prefixed docs/health/security; no web component or implicit data mutation. (MB-002,003,006)
- [x] T5: Verify/pin contract generator and produce reproducible typed client output,
  contract drift checks and old-v1-client fixture; implement bounded network calls,
  cancellation, errors and explicit uncertain-write recovery. (MB-003,004)
- [x] T6: Build the native notebook list/editor, tokens and all empty/loading/error/
  reconnect/save states; draft retention, delete confirmation, keyboard handling,
  accessibility, large text and reduced motion. Remove unrelated starter screens/
  routes/assets/tests and update imports/OpenAPI together; retain notes and operational
  docs/health/security intentionally for this synthetic demonstration. (MB-004,005,007)
- [x] T7: Publish immutable bound-mobile release and provider snapshot packaging;
  update guidance, pinned CI and runbooks for explicit generation/binding, public
  config, independent operation, database recovery and compatibility. Preserve the
  default web selection and existing published releases. (MB-007)

## Verification and delivery

- [x] T8: Run relevant repository/generated offline/container checks with meaningful
  failure injection: schema/version/identity/URL rejection before execution, atomic
  generation, stale client/types, breaking API, native state interactions, failed
  start/DB readiness, interrupted ownership, API-only route refusal/fallback, old
  provider refusal and historical stack regressions. Check sanitization and generator
  reproducibility. Exact results and the corrected worktree timing-test rerun are
  recorded in acceptance.md; final remote CI remains T10. (AC-001–003,005–007)
- [ ] T9: After scoped rollout, verify installed/source parity and current device/client
  eligibility; execute physical Android CRUD, validation/pagination, saved-data
  persistence through reload/restarts/relaunch, offline/API/DB recovery, uncertain
  writes and independent-service isolation. Rehearse additive migration with retained
  v1 client and verified backup/recovery; rehearse capable-provider rollback without
  data/schema downgrade. Record screenshots and owner visual review plus physical
  keyboard/TalkBack/large-text/targets/contrast/reduced-motion checks. Stop owned trial
  runtimes/routes; record source/data retention disposition. (AC-002–007)
- [ ] T10: Open review PR; record platform/generated CI, review, merge, installed rollout
  and device/owner acceptance separately. Create sanitized acceptance evidence mapped
  to each criterion; update catalogue/M1 only on actual completion. Keep full environment,
  iOS, signed-build, offline-sync, production and broader native-test scope pending.
  (AC-008; all requirements)

## Current handover

Implementation and local verification are complete on the isolated
`codex/mobile-python-backend-spec` branch for PR #83. Exact API/DB-only and native
notes starters, binding, versioned lifecycle/snapshot integration, native UI/client,
contract checks, generated CI and runbook are implemented. See [acceptance](acceptance.md)
for actual local results and explicit remaining CI/installed/device/owner gates.
No installed runtime or existing application/data has been changed. SPEC-035 work
and the original checkout are preserved. Next action: review the published implementation and final CI, then perform the
scoped installed/device acceptance in T9. Do not mark MOB-010/M1 accepted from code alone.


Preview requested October 15: phone versions/tailnet confirmed by owner. Main
conflicts resolved in f064cac; combined-head checks pending. Exact new-repository
workflow policy and one new private sticky Metro slot are proposed in
[the preview plan](preview-plan.md); await named approval before those mutations.

Owner approved the exact two names/private route. The first named-policy update
refused the old four-name capacity without modifying the policy; the original
active profile was restored. Versioned six-name compatibility is now part of
preview preparation. Focused mobile/backend (12) and corrected manifest (28) pass.


Private preview rollout: both approved canonical repositories and their initial
PRs now exist; both generated CI workflows passed. Stable 1.14.0 is installed with
matching source capabilities, new API/DB group Ready, HTTPS health/list probes
passed, installed binding verified, and Metro process/protocol Ready. Exact 8445
route plan is recorded; operator execution/readback and a current Go link remain
pending. Current session expires October 15 at 12:09 p.m. Eastern. T9/T10 stay
open for physical acceptance, review/merge and remaining evidence.


Operator handoff completed: independent readback verifies the exact owned 8445
route with full baseline/Funnel preservation. Installed Metro and Android Go
launch are Ready/available for the current bounded generation. Owner device/
visual acceptance and remaining T9/T10 gates stay open.


October 15 owner feedback after the QR handoff: “That works perfectly.” Basic
Android Expo Go preview is now confirmed by the owner, with positive overall
feedback. T9 remains partly complete: separately enumerated native/recovery/
accessibility scenarios and screenshots are unrecorded; T10 review/merge and
final acceptance remain pending. See the acceptance record for evidence limits.


Merge checkpoint — October 15: the project owner instructed “Merge everything
into main.” All four workflows passed on final PR head `d206ef2` before
[PR #83](https://github.com/danielbardsley/gptclaw/pull/83) merged as `bdd2d7e`.
The review/merge portion of T10 is complete. Remaining enumerated T9 device,
recovery and accessibility checks and final integration acceptance stay open;
MOB-010/M1 are not marked Delivered. Earlier pending-merge notes are historical.
