# TASKS-049 — Android development builds

Status: Implementation authorized October 23; in progress.
Owner: Project owner. Date: 2026-10-22 (America/New_York).
[Specification](spec.md) · [Technical design](technical-design.md)

## Planning and authorization

- [x] T1 — Read current-main mobile direction/catalogue, provider contracts and
  SPEC-036 closeout. Select stage-5 MOB-004 and draft requirements/design/tasks.
  Preserve Android-first acceptance and existing owner waivers. No live operations.
- [ ] T2 — Implementation authorized by the project owner October 23. Record
  account/project, signing custody/recovery, actual credential privileges,
  attempt/cost ceiling, artifact access/expiry/retention and device decisions
  before their dependent external actions. Implementer validates exact supported
  SDK/dev-client/EAS CLI/cloud image/native demo module matrix. Unresolved external
  choices block external execution; offline implementation can proceed once
  authorized. Map to DB-001, DB-002, DB-003; AC-001–003.

## Implementation after authorization

- [x] T3 — Allocate unused versioned contracts/profile/capabilities; implement
  source-only opt-in and deterministic identity/public config/native fingerprint.
  Preserve frozen releases, legacy providers, Go and optional backend contracts.
  Add new immutable starter release(s) with explicit generated-native ownership.
  Map to DB-001, DB-003, DB-006; AC-001,003,006.
- [ ] T4 — Implement exact archive staging/inspection, forbidden-file canaries,
  size/path limits, credential boundary, redaction and signing metadata handling.
  Prove actual pinned EAS upload matches reviewed inputs before network submission.
  Map to DB-002, DB-003; AC-002,003.
- [x] T5 — Implement plan/submit/observe/reconcile/artifact interfaces with durable
  intent/job receipts, locks, admission/budget limits and unknown-outcome recovery.
  Interruptions cannot automatically duplicate external jobs. Map to DB-004; AC-004.
- [x] T6 — Implement verified artifact/package/certificate handling and separate
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

Implementation authorization is recorded. Provider/contracts, new immutable native
starters, CLI/job receipts, deterministic uploads, interrupted-job reconciliation,
artifact signature verification, Android launch admission, private repository
provenance and runbook are prepared on `codex/mob-004-development-builds` for PR #99.
Existing web/API/DB/Go source and installed services are preserved.

Source native component tests and Android unsigned exports pass; full `verify`
stops at an unapproved Zod advisory. The frozen EAS toolchain audit has nine high
vulnerable package entries. No native signing/runtime exception is authorized.
See [acceptance tracking](acceptance.md) and [security disposition](security-review.md).
The broad repository suite remains running. It recorded legacy spike and template
fixture failures; corrected full focused suites pass. Latest CI is not green.
Software implementation of T3/T5/T6 is complete; external acceptance is tracked
separately by T9. T4 remains open for real pinned upload observation.

The owner selected prior-account reuse, Expo-managed signing, willingness to pay
and 30-day retention. The exact account/project/certificate, numeric budget and
actual artifact access remain unresolved. No credentials, billing, cloud jobs,
managed rollout, private listener changes or physical installation were performed.
T2/T7/T8/T9/T10 remain open until their stated gates have actual evidence. No
waivers or catalogue Delivered status are inferred from source implementation.

Budget guidance: recommend starting with Expo Free (15 Android builds/month),
or a $25 total first-month ceiling if paid access becomes necessary. The owner
has not approved that numeric ceiling or added billing details. Expo Starter
is $19/month plus usage with $45 build credit ([pricing](https://expo.dev/pricing),
checked October 23). This recommendation does not authorize payment.

Final focused native suite: 32/32 tests pass at source revision `b871a6b`;
release immutability, local documentation links and whitespace checks pass.
Fresh CI and the broad local run remain pending; no full-check success is claimed.


## Account decision and upstream follow-through — October 23

The owner supplied https://expo.dev/accounts/bardsley, authorized as many builds as
needed and will pay for an account when required. Account selection and free-build
count authorization are resolved; the earlier three-build/$25 suggestions are not
limits selected by the owner. Keep individual operational batches bounded and
within verified free quota; no billing activation or paid spend is inferred.
A focused project-choice question is pending. Signing remains Expo-managed and
retention 30 days. Credentials, certificate, actual access and device acceptance
remain distinct. No secret was requested in chat or inspected.

Public npm metadata was rechecked: latest EAS remains 25.3.0 and pins node-forge
1.4.0. Latest node-forge remains 1.4.0 and its advisory has no patched release.
Latest Expo CLI 58.1.15 still depends on Zod ^3.25.76 and node-forge ^1.4.0;
upgrading SDKs alone is not a verified remediation. No frozen release, lock,
audit gate or runtime was changed. Follow-up needs an upstream-compatible repair
or a concrete reviewed patch; no security exception is authorized by build-count
or payment authorization.
