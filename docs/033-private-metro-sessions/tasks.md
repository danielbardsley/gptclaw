# TASKS-033: Private Metro sessions

- **Status:** Implementation authorized — scoped runtime disposition approved; spike passed; transport/lifecycle pending
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-033](spec.md) · **Design:** [TDD-033](technical-design.md)

## Planning and implementation

- [x] T-000: Read delivered MOB-001/PRJ-006, mobile catalogue/sequence, current
  lifecycle/ingress/security contracts and official references; draft separate plans.
  Read-only source/installed capabilities inspected; no Metro/client/route mutation.
- [x] T-001: Owner reviews lifecycle/private-transport scope and proposed bounds,
  platform matrix and operator/security decisions, then authorizes implementation.
  Planning/merge approval alone does not enable a Metro service or extend exceptions.
- [ ] T-002: Collect exact runtime security evidence and resolve patched-input or
  explicit runtime-disposition gate before execution. After authorization, spike
  pinned SDK URL/manifest/assets/large bundles and WebSocket behavior with an eligible
  native client; propose exact owned origins/listeners/access scope and measured bounds.
  Obtain owner/operator disposition for changes outside reviewed scope. (MET-003/004/006; AC-003/004/006)
- [ ] T-003 (in progress): Recheck schema reservations; implement opt-in migration/validation,
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

T-000 and T-001 are complete. T-002 is in progress: fresh exact audit evidence,
a separate approved scoped runtime policy, fail-closed admission tests and a bounded
loopback SDK-spike helper and sanitized native protocol probes are prepared.
The original full offline gate passed. Current focused source/admission/protocol
suites cover 59 cases (18 opt-in cases plus two source-job guards). CI passed
at fb7f4b2; the final source-job guard revision still needs its CI result. Schema-6 source opt-in, canonical guarded migration, non-HTTP source consumers
and older installed-provider rejection now have evidence; typed session receipt/descriptor validation now has 14 offline cases; execution,
observation wiring and installed capability remain pending. The exact runtime exceptions/retained fixtures are now approved and recorded.
Two authorized exact-SDK loopback spikes passed on the retained fixtures; both
native manifests and bundles over 2 MiB were served with verified source/cleanup.
See [measured SDK evidence](sdk-spike.md). Existing assets, source maps and reload/HMR handshake/ping checks passed on both
fixtures with exact source/cleanup proof. Sustained native reload, supervision,
private operator scope and physical evidence remain pending. Bounded sequential Metro probes were started/stopped; no persistent Metro service,
private route or account change has been made. See [security proposal](security-review.md) and
[acceptance tracking](acceptance.md). Other implementation tasks remain open.

Implementation authorization: the active owner goal requires MOB-002 followed by
MOB-003 with all acceptance criteria met. Runtime advisory exceptions and exact
operator routes are not inferred from this general authorization. Device
prerequisites have been requested; independent source implementation continues.

Owner-reported device prerequisites relayed with authorization: Android 11 on the
development tailnet, with Expo Go reported up to date. Exact model/build/client
version and actual loads/reloads remain unverified; no iPhone is confirmed. This
does not remove iOS criteria or establish physical-device acceptance.
