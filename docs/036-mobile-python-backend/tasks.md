# TASKS-036 — Mobile Python backend integration

Owner: Project owner. Status: Implementation authorized; in progress.
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

- [ ] T8: Run relevant repository/generated offline/container checks with meaningful
  failure injection: schema/version/identity/URL rejection before execution, atomic
  generation, stale client/types, breaking API, native state interactions, failed
  start/DB readiness, interrupted ownership, API-only route refusal/fallback, old
  provider refusal and historical stack regressions. Check sanitization and generator
  reproducibility. Record exact commands/results and skipped checks. (AC-001–003,005–007)
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

Implementation is authorized and in verification on the isolated
`codex/mobile-python-backend-spec` branch for PR #83. Exact API/DB-only and native
notes starters, binding, versioned lifecycle/snapshot integration, native UI/client,
contract checks, generated CI and runbook are implemented. See [acceptance](acceptance.md)
for actual local results and explicit remaining CI/installed/device/owner gates.
No installed runtime or existing application/data has been changed. SPEC-035 work
and the original checkout are preserved. Next action: finish local regressions and
publish the implementation for review; do not mark MOB-010/M1 accepted from code alone.
