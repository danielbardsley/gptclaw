# TASKS-033: Private Metro sessions

- **Status:** Implementation authorized — implementation and installed rollout verified; final owner/delivery gates pending
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
- [x] T-002: Collect exact runtime security evidence and resolve patched-input or
  explicit runtime-disposition gate before execution. After authorization, spike
  pinned SDK URL/manifest/assets/large bundles and WebSocket behavior with an eligible
  native client; propose exact owned origins/listeners/access scope and measured bounds.
  Obtain owner/operator disposition for changes outside reviewed scope. (MET-003/004/006; AC-003/004/006)
- [x] T-003: Recheck schema reservations; implement opt-in migration/validation,
  canonical-root guard, capability/receipt/descriptor versions and older-provider
  rejection, preserving schema-5 source and all frozen releases. (MET-001/005; AC-001/005)
- [x] T-004: Implement owned user-unit lifecycle, atomic port/cache leases, mutation
  locks, resource/TTL/security-revocation supervision, sanitized logs and typed recovery.
  Test two independent sessions, drift, concurrency, disconnect, crash and expiry.
  (MET-002/006/007; AC-002/006/007)
- [x] T-005: Implement the spike-reviewed streaming/private proxy and operator plan/
  readback. Test large/slow requests, origins/TLS, native reload paths and unowned
  route conflicts. Do not change existing handlers or use a public fallback.
  (MET-003/004; AC-003/004)
- [x] T-006: Add safe observation/CLI endpoint descriptor, minimum source/session
  presentation and reviewed runbook; distinguish all readiness layers and leave
  full native/device/build telemetry to MOB-009. (MET-005; AC-005)
- [ ] T-007 (in progress): Run relevant offline, real rootless protocol/lifecycle and legacy app/
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

## Historical implementation checkpoints

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

The controller source now includes a bounded forge user-service, typed receipts,
sticky paired leases/origins, fresh SDK audit at execution, frozen-provider
launching, source watching with read-only mounts, input/expiry/revocation guards
and exact owned shutdown. Twenty-eight isolated controller cases and fourteen state
cases pass; schema-5 mobile regressions pass. No live supervised session was
started yet. Streaming proxy/private route wiring and installed/lifecycle/device
acceptance remain pending; session capability is still not advertised.

Controller recovery now uses exact registry/generation/unit proof without loading
invalid app metadata. Independent owned cleanup continues after a foreign-handle
conflict; uncertain shutdown records unknown/recovery-required. Activating/restarting
user units block source mutation. Sanitized lifecycle events are bounded and exact
policy revocation has a read-only plan plus explicit apply. All four CI workflows
passed at 62603d4; controller local/CI, live proxy/lifecycle and device work remain
separate unfinished gates. The approved SDK probes do not establish those outcomes.

The broader local gate passed current mobile and Metro suites. One template
snapshot fixture missed the new bundled policy; its provider-input copy and
controller/policy parity assertions were corrected, and all 21 template cases
passed separately. A fresh frozen review snapshot matched source without changing
the installed pointer. The full local gate completed 36 suites / 672 cases, exit 1 solely from that
fixture error; all other suites passed and the corrected complete template suite
passed separately. At 80e28eb dashboard CI passed; the other three workflows were
still running. Final CI and all live lifecycle/private/device gates remain pending.


Streaming proxy source is now wired to owned supervisor cleanup and frozen
packaging. Nineteen real loopback proxy cases, 28 controller cases, 13 protocol
cases, 22 spike cases and 21 packaging cases pass. The first failures identified
a ready-event race and active-client listener-release ordering; corrected tests
pass without resource warnings. All four CI workflows passed at 8278e54 before
this integration. Both retained roots remain clean/schema 5 with eligible read-only
300-second plans; actual opt-in/SDK-proxy/unit/private/client evidence is pending.


Actual loopback user-service rehearsal now passed on fixture one, including both
native targets through the streaming proxy and automatic five-minute expiry with
released listeners/resources. Paired starts/idempotence/independent stop/restart
passed. Fixture two's sampler timed out and expiry required exact reconciliation;
the initial cause remains unresolved, and sanitized failure-stage records are added
for reproduction. Both temporary sessions are now stopped, with source preserved.
Internal control schema 2 guards live mount identities. The two metadata PRs are
draft; installed/private/operator/client/remaining recovery acceptance is pending.
All four CI workflows passed at 5de817a before these latest source guards.

## Earlier route/lifecycle checkpoint

The full real fixture-two SDK/proxy sample now passed and expiry cleaned up both
listeners/resources; the older unresolved recovery case is retained in acceptance.
Route planning and exact preserved-config/TLS observation are implemented and
packaged, with 20 isolated cases. Both real read-only plans succeeded; see the
[concrete operator handoff](operator-plan.md). Operator approval/action, ACL/device
proof, installed/collector parity, renewal/cache bounds and remaining lifecycle
recovery remain pending. Current focused suites pass 105 cases; all four CI jobs
passed at da9cdd8 before this checkpoint. Android Go version and iOS availability
are pending owner input. No capability is advertised prematurely.

The new route-observer supervisor also passed a real 120-second loopback rehearsal
on fixture one: unavailable launch while route-pending, then successful inactive
expiry and absent SDK/network/proxy. This remains distinct from private TLS/device
acceptance. The full offline repository gate subsequently completed with exit 0; see the
acceptance record for actual source verification and remaining separate gates.

Actual exact-owned SDK crash recovery now passed on fixture two within its
120-second original lifetime: one observed automatic restart, same generation,
fresh admission, running recovery and clean successful expiry. Source was preserved
and SDK/audit/network/proxy were absent at completion. Both fixture units are
terminal. The full repository gate and final focused controller suite passed.
Private/operator approval, installed/collector, device, renewal/cache, revocation/
rollback and SSM-disconnect evidence remain open; MOB-003 is not yet implemented.

## Recent implementation checkpoints

The exact two private listeners are owner-approved; operator execution and ACL/
device evidence remain pending. Android is owner-reported Expo Go 57.0.9 / SDK 57
on Android 11. Continue iOS development assuming a recent iPhone and the same Go
version, while keeping physical iOS acceptance pending.

Explicit new-generation renewal, security-unavailable status and bounded exact-owned
inactive-copy pruning are implemented. The 128 focused cases and two real expiry/
retention rehearsals passed; see the acceptance record for revisions and limits.
Positive private renewal, installed/collector parity, SSM disconnect, full recovery/
revocation/rollback, physical checks and merge remain open. The latest published
7fa418c CI is green; current renewal/retention checks are recorded separately.

Both approved one-hour backends are running with exact loopback health and
route-pending observations. The SSM operator action has been requested. The
fixed-owned-origin/default-trust TLS native sampler passes 19 protocol cases;
actual private sampling follows operator readback. No Go launch is offered yet.

The complete renewal/retention offline gate finished with exit 0. The later TLS
sampler separately passed all 20 protocol cases, including successful generation/
expiry binding and physical-acceptance separation. Both real pending-route probes
denied without stopping their owned SDKs. Operator action and final-head CI remain
pending; installed and physical acceptance are still open.

Minimum native collector/frontend observation is implemented and locally verified:
65 affected Python cases, nine frontend tests and the actual portable HTTP/browser
gate passed. Source observations on both running fixtures are read-only and within
budget, with separate route-pending/process/protocol state and no HTTP components
or launch link. Installed/frozen-consumer rollout, private operator/device checks
and final-head CI remain pending. T-006/T-007 remain in progress.

Real format-job attempts are blocked on both active fixtures (exit 1), with clean
source and unchanged owned generation/SDK. The underlying active-session guard
independently returns busy without writes.

The established-session protocol watchdog is corrected and passes 48 controller
cases. Actual cold bundling on the corrected first fixture passed, but rebuild
exposed the pinned CLI's CI-mode watcher disablement. Runtime watch opt-in and
closed stdin/non-TTY output now pass 24 spike cases; corrected live rebuild and
paired private sessions still require verification. Source was exactly restored.

## Current checkpoint

The exact two approved private listeners were added by the SSM operator and
independently verified, preserving the original 443 baseline and Funnel off. Both
fixtures passed native private TLS manifests/bundles/assets/maps and WebSocket
ping/pong. Owner-reported SSM reconnect independently preserved original generation,
expiry and zero restarts. Owner reports denial off-tailnet and under a different
identity; the subsequently supplied wildcard policy allows all same-tailnet traffic,
so the latter test does not establish same-tailnet ACL denial. The owner explicitly
permits all same-tailnet devices; the wildcard policy is accepted unchanged and
off-tailnet denial is the required access boundary. Permitted-phone evidence remains
pending. Positive private renewal passed with a new generation, old entry HTTP 503,
second session/expiry unchanged and both source checkouts clean.

The real Android loopback edit/rebuild/restoration passed, with clean restored source
and the other fixture unchanged. Controller 49, retention 21 and watch/noninteractive
spike 24 focused cases pass. At 9308e0b all four CI workflows passed after a scoped retry of the synthetic
repository-bootstrap failure. New capability/consumer changes require their own CI.
The earlier complete local gate returned nonzero despite all reported suites passing;
a traced retry was interrupted by editing its checker during execution. A complete
frozen-checker gate is still required.
Remaining recovery, installed collector/provider/rollback, physical iOS/Android
acceptance and merge remain open. MOB-003 launch/profile/QR work follows the now-proven
private host protocol foundation. Historical checkpoints remain stage-specific.


At 73913b3 all four CI workflows passed after scoped template retry. The latest full
local checker terminated with exit 143 during worktree tests; no complete local pass
is claimed. Actual second-session private expiry and occupied-proxy denial now pass,
with exact cleanup, prior receipt/source and first generation preserved. Frozen
installed/candidate existing group observations agree (API/DB healthy; pre-existing
web observation-inconsistent). Compatible installed collector/provider rollout and
rollback, remaining recovery/revocation and physical checks remain pending.


Current native checkpoint: the owner’s manual and locally decoded QR query-based
launches failed on Android 11 / Go 57.0.9, including after bundle warmup. Aggregate
diagnostics isolated three generation-guard rejections before any manifest reached
Metro. A guarded session-path entry is implemented and tested; its new physical
launch check remains pending. Runtime/security/route scope is unchanged. No task
or platform is marked accepted from host-only checks. See the latest acceptance
record for exact evidence and limitations.


The slash-normalized path subsequently reached the native manifest, but the owner
received a packager error at an HTTP address on the HTTPS listener. The SDK-57
Android branch confirms a hardcoded HTTP development probe. Exact Go eligibility
now reports this HTTPS incompatibility; physical UI/edit/reload remains unaccepted.
The [transport decision](../034-expo-go-workflow/client-transport-decision.md) is a
reviewable proposal. No transport amendment, listener conversion or MOB-004 build
is authorized by creating it. Independent platform work remains in progress.


The approved HTTP transport amendment is implemented locally with explicit
selection, typed schema 2, retained prior HTTPS ownership and isolated rollback/
protocol/privacy tests. Both approved one-hour HTTP backends are loopback healthy
and Android bundles warm; exact plans are recorded. Operator replacement and
private/native acceptance are still pending. All broader task gates remain open;
no Delivered or physical-certification claim is made. See current acceptance.


## Current task reconciliation (October 14 UTC)

T-003/005/006 implementation is complete with source/CI/installed evidence.
T-002/004/007 retain the remaining private renewal/interruption and physical
recovery evidence; completed subchecks are recorded in acceptance. Actual input
drift shuts down the SDK; a forbidden root environment file also triggers owned
shutdown/re-admission after removal. The failed forbidden-dotenv probe is not a pass. A separate allowed private-file
exclusion probe passes with its marker absent from SDK view and downloaded bundle.
T-008/009 retain the owner matrix, fresh device QR/restart/isolation, exact operator
listener-removal, review/authorized merge and final delivery/retention gates.
Historical checkpoints below/above retain their original observation context;
the current criterion table in acceptance governs present status.


Actual private renewal now passes fresh admission/new generation, unchanged HTTP
origin, stale-entry rejection and 120-second expiry/owned resource removal. The
first app's pending device link was preserved. AC-007 host recovery/rollout evidence
is complete; T-008/009 still retain physical isolation/reconnect, matrix, exact
operator removal and final owner/review/merge/delivery. The latest credential CI
failure and successful isolated/full local checks plus CI retry are recorded
without erasing the initial failure. No additional broad test run is required
absent a code change or new failure.


The owner explicitly selected Android-first delivery on October 14, with iOS
retained as an unsupported physical/client follow-up. The earlier two-platform
planning default no longer blocks this selected slice. Existing Android native
interaction/edit/reload evidence is accepted for that matrix. Fresh inline QR/
restart/isolation/reconnect, operator listener-removal, final owner acceptance and
review/merge/retention gates remain; no Delivered label is applied.


## Corrected Android isolation and recovery checkpoint

T-002 and T-004 are complete for the owner-selected Android-first scope: exact
runtime disposition, private transport amendment/operator readback, bounded
protocol/security and owned lifecycle tests are recorded. Following the connection
capacity correction, the owner reports both fresh apps work on Reload, stopped
app one is unavailable while app two continues working, restarted app one opens,
and both apps work after the single owned SDK crash/automatic recovery. App one's
generation and expiry remain unchanged during crash recovery. Detailed counter
values are not inferred from these reports. Physical expiry and owned-listener
removal are still pending under T-008; final CI, review/merge and delivery remain
T-007/009. Earlier checkpoint sections are historical.
