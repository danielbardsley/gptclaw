# TASKS-033: Private Metro sessions

- **Status:** Draft — planning only
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-033](spec.md) · **Design:** [TDD-033](technical-design.md)

## Planning and implementation

- [x] T-000: Read delivered MOB-001/PRJ-006, mobile catalogue/sequence, current
  lifecycle/ingress/security contracts and official references; draft separate plans.
  Read-only source/installed capabilities inspected; no Metro/client/route mutation.
- [ ] T-001: Owner reviews lifecycle/private-transport scope and proposed bounds,
  platform matrix and operator/security decisions, then authorizes implementation.
  Planning/merge approval alone does not enable a Metro service or extend exceptions.
- [ ] T-002: Collect exact runtime security evidence and resolve patched-input or
  explicit runtime-disposition gate before execution. After authorization, spike
  pinned SDK URL/manifest/assets/large bundles and WebSocket behavior with an eligible
  native client; propose exact owned origins/listeners/access scope and measured bounds.
  Obtain owner/operator disposition for changes outside reviewed scope. (MET-003/004/006; AC-003/004/006)
- [ ] T-003: Recheck schema reservations; implement opt-in migration/validation,
  canonical-root guard, capability/receipt/descriptor versions and older-provider
  rejection, preserving schema-5 source and all frozen releases. (MET-001/005; AC-001/005)
- [ ] T-004: Implement owned user-unit lifecycle, atomic port/cache leases, mutation
  locks, resource/TTL/security-revocation supervision, sanitized logs and typed recovery.
  Test two independent sessions, drift, concurrency, disconnect, crash and expiry.
  (MET-002/006/007; AC-002/006/007)
- [ ] T-005: Implement the spike-reviewed streaming/private proxy and operator plan/
  readback. Test large/slow requests, origins/TLS, native reload paths and unowned
  route conflicts. Do not change existing handlers or use a public fallback.
  (MET-003/004; AC-003/004)
- [ ] T-006: Add safe observation/CLI endpoint descriptor, minimum source/session
  presentation and reviewed runbook; distinguish all readiness layers and leave
  full native/device/build telemetry to MOB-009. (MET-005; AC-005)
- [ ] T-007: Run relevant offline, real rootless protocol/lifecycle and legacy app/
  dashboard/credential/worktree regressions and CI. Package a combined source/
  installed provider and any frozen collector update; prove parity and recovery.
  (MET-001–007; AC-001–007)

## Private acceptance and delivery

- [ ] T-008: Select exact synthetic fixture roots/retention and device matrix with
  owner; use the reviewed operator path for the approved private listeners. Verify
  two-session isolation, actual permitted/denied device transport, Fast Refresh/reload,
  expiry/reconnect and rollback with existing apps/data untouched. Record each
  platform/client version and owner acceptance separately. Native-client acceptance
  may be coordinated with SPEC-034 after this provider is available; if blocked on
  MOB-004, keep actual device criteria pending. (MET-001–007; AC-001–008)
- [ ] T-009: Record sanitized acceptance/runbook/retention and final revision/CI,
  complete review/authorized merge, mark only MOB-002 Delivered once all criteria
  pass, and stop only owned temporary sessions/remove only approved owned routes.
  Preserve source/receipts/data and remaining M1/MOB features. (AC-008)

## Handover

Only T-000 is complete. Two planning sets were requested; approval/implementation,
runtime security disposition, private operator scope, measured transport and native
device evidence remain future work. No runtime/exposure/account changes were made.
