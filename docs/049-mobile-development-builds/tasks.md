# TASKS-049 — Android development builds

Status: Draft; planning complete, implementation authorization pending.
Owner: Project owner. Date: 2026-10-22 (America/New_York).
[Specification](spec.md) · [Technical design](technical-design.md)

## Planning and authorization

- [x] T1 — Read current-main mobile direction/catalogue, provider contracts and
  SPEC-036 closeout. Select stage-5 MOB-004 and draft requirements/design/tasks.
  Preserve Android-first acceptance and existing owner waivers. No live operations.
- [ ] T2 — Project owner reviews scope and authorizes implementation. Record
  account/project, signing custody/recovery, actual credential privileges,
  attempt/cost ceiling, artifact access/expiry/retention and device decisions
  before their dependent external actions. Implementer validates exact supported
  SDK/dev-client/EAS CLI/cloud image/native demo module matrix. Unresolved external
  choices block external execution; offline implementation can proceed once
  authorized. Map to DB-001, DB-002, DB-003; AC-001–003.

## Implementation after authorization

- [ ] T3 — Allocate unused versioned contracts/profile/capabilities; implement
  source-only opt-in and deterministic identity/public config/native fingerprint.
  Preserve frozen releases, legacy providers, Go and optional backend contracts.
  Add new immutable starter release(s) with explicit generated-native ownership.
  Map to DB-001, DB-003, DB-006; AC-001,003,006.
- [ ] T4 — Implement exact archive staging/inspection, forbidden-file canaries,
  size/path limits, credential boundary, redaction and signing metadata handling.
  Prove actual pinned EAS upload matches reviewed inputs before network submission.
  Map to DB-002, DB-003; AC-002,003.
- [ ] T5 — Implement plan/submit/observe/reconcile/artifact interfaces with durable
  intent/job receipts, locks, admission/budget limits and unknown-outcome recovery.
  Interruptions cannot automatically duplicate external jobs. Map to DB-004; AC-004.
- [ ] T6 — Implement verified artifact/package/certificate handling and separate
  development-client launch admission/serializer. Validate private HTTPS, native
  fingerprint, session generation/expiry and explicit installation evidence.
  Keep Go/Metro/backend lifecycles independent. Map to DB-005, DB-006; AC-005–007.
- [ ] T7 — Adapt synthetic standalone/bound starter demos, including the reviewed
  native module. Preserve typed FastAPI notes/health/docs intentionally; remove
  unrelated demo routes/assets/UI and update imports/tests/config together.
  Publish runbook and frozen generated CI without Expo/signing secrets or automatic
  build submission. Map to DB-006, DB-007; AC-006–008.

## Verification and delivery

- [ ] T8 — Run repository checker and focused schema/build/Metro/Go/backend suites,
  generated frozen quality checks and diff/link checks appropriate to implementation.
  Cover invalid identity/config, legacy refusal, archive/credential canaries,
  interrupted remote responses, duplicate prevention, concurrency, stale native
  fingerprint and safe URLs. Use synthetic remote clients offline. Record exact
  commands/results and PR/CI revision. Map to DB-001, DB-002, DB-003, DB-004, DB-007; AC-001–004,008.
- [ ] T9 — After external and transport prerequisites, install a capable provider
  through the reviewed path. Run bounded authorized EAS job(s), observe recovery,
  verify/install exact APK(s) and exercise physical Android standalone/bound loops,
  native module, JS Fast Refresh/full reload, native-change rebuild refusal and
  replacement, outages/reconnect, persistence and isolation. Record source/config/
  binary/certificate/OS/profile identities, redacted upload evidence, owner device
  actions, account scope and limits. Rehearse capable rollback and owned runtime/
  staging/listener cleanup, preserving unrelated services and retained source/data.
  Map to DB-004, DB-005, DB-006, DB-007; AC-004–008. Do not inherit prior device waivers silently.
- [ ] T10 — Create acceptance tracking from actual evidence; distinguish local,
  CI, remote build, installed provider and physical owner acceptance. Deliver
  reviewable implementation PR, review/merge and owner acceptance. Update catalogue
  only for the delivered Android MOB-004 slice; leave broader MOB-005/006/011 and
  iOS/preview/production open. Map to DB-007; AC-008.

## Current handover

Draft spec/design/tasks and index/catalogue/mobile-sequence links are prepared
for review. Implementation and all external actions remain unstarted. Exact native
matrix and owner account/custody/budget/access/device decisions remain substantive
preconditions, with responsibilities above. Planning verification is documented in
the planning PR; no application tests, EAS jobs, credentials, runtime changes or
physical checks are claimed by this draft.
