# SPEC-034: Compatible Expo Go development workflow

- **Status:** Approved for implementation by active goal — acceptance pending
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Feature:** MOB-003 — Expo Go workflow
- **Supporting slices:** Mobile dependency compatibility; safe launch links; narrow native interaction acceptance
- **Design:** [TDD-034](technical-design.md) · **Tasks:** [TASKS-034](tasks.md)
- **Dependencies:** [MOB-001](../031-expo-project-creation/acceptance.md), [MOB-002 / SPEC-033](../033-private-metro-sessions/spec.md), [mobile sequence](../platform/sequence-mobile.md)

## Outcome and scope

For an explicitly verified Expo SDK/native-module/client/transport combination, the
owner can open a project in Expo Go from a safe private launch link or QR, use its
native UI, edit source and observe Fast Refresh/reload, and recover from device/network
interruptions. Repeat for a second project without new platform account credentials
or hand-configuring Metro URLs. Unsupported combinations give a precise reason and
point to the separately scoped development-build workflow (MOB-004).

The owner requested separate MOB-002/003 plans and subsequently explicitly
authorized their ordered implementation through the active goal. SPEC-033
owns Metro/session/routes/operational descriptor; this spec consumes that interface
and owns Go compatibility, launch UX and physical client acceptance. Implement the
MOB-002 provider and verify host/private protocols first; final native acceptance
can be coordinated between the two without requiring a Delivered label to start
this consumer. No second Metro manager, port registry or Tailscale control path.

Include the delivered standalone source starter, two sessions/projects, an explicit
per-platform eligibility matrix, bounded Go launch/QR UX and physical iOS/Android
interaction/edit/reconnect evidence. A first-platform delivery may be owner-selected
and must remain labeled; support for both requires both devices. Exclude signed
personal Expo Go/development clients, EAS/Apple/Google account or credential setup,
SDK/native-module migration, public tunnels, backend CRUD/binding, store/update
operations, product acceptance and full MOB-009 telemetry. This alone cannot close
M1's API/database persistence or TPL-004's broader template/device scope.

## Baseline and compatibility risk

MOB-001's exact starter is Expo 57.0.28/React Native 0.86.3/React 19.2.3 with static
public IDs and source-only checks. It has not been accepted in Expo Go on a physical
device. The official Go download page observed October 13 lists SDK 57 and platform
install selections; that is not proof of actual installed client availability,
OS/account eligibility or private transport on an owner's phone. Store availability
can change independently of the source SDK. Do not promise old physical-iOS Go builds
or infer emulator availability means a phone can install the same client.

Source-only advisory exceptions do not cover running Metro; SPEC-033's fresh runtime
security/admission gate remains mandatory here. Planning does not expand it.

## Requirements

### GO-001 — Explicit, evidence-backed compatibility

Maintain a reviewed versioned profile of exact source SDK/lock/native-module/config
inputs, client build/version, OS/platform, acquisition source and validated transport.
Separate project eligibility from owner-reported installed client version and recorded
physical validation. Unknown, stale or unsupported combinations fail with a useful
reason; source lint/bundle success is insufficient. Expire certification on relevant
SDK/native/config/transport/client change and a finite freshness policy. Do not
silently downgrade/upgrade dependencies, alter IDs/plugins, install older unverified
clients, extend runtime exceptions or claim unsupported native capabilities.

### GO-002 — Safe launch and local QR

Derive platform-appropriate Expo Go launch payloads from SPEC-033's current, owned,
ready descriptor and reviewed compatibility profile. Bind payloads to project,
session generation, approved origin/mode, verified target and expiry. Avoid loopback,
LAN/public-relay hosts, wrong-session/client URIs and caller-supplied URLs. Encode
correctly for the actual verified client; don't infer URI schemes from the project's
custom scheme. Render QR locally using pinned reviewed tooling; no third-party QR
service, secrets/account tokens or unreviewed downloads. Unready/stale/expired sessions
must not offer available launch links; stale QR/bookmarks cannot reconnect to another
project after port reuse. Copy/open guidance remains available if camera scanning
is unavailable. A QR image is not authorization or evidence of a loaded device.

### GO-003 — Repeatable bounded workflow

Offer explicit Go compatibility inspection and launch/QR presentation through reviewed
CLI and minimum dashboard link integration, without implicitly starting a server,
provisioning routes or setting up accounts. Expose running session, Go eligibility
and missing device/tailnet prerequisites separately. Preserve existing Open app and
API-doc semantics; native launch is clearly labeled. The client is a preinstalled
owner-selected Go app, not an HTTP service or project container. No online-device
count/status is fabricated. Runtime controls continue through SPEC-033 only.

### GO-004 — Physical native edit loop

On each claimed platform, open both synthetic projects, verify native navigation,
local assets and accessible counter interaction, perform a reversible TypeScript/UI
edit through the canonical checkout and observe Fast Refresh; then force a native
reload. Restore the fixture change. Distinguish refresh state retention from full
reload; do not require state persistence that the fixture doesn't implement. One
session's stop/restart must not alter the other project or an existing shared backend.
Record client/OS/SDK and owner evidence, not only Jest screenshots or web rendering.

### GO-005 — Failure and reconnect behavior

Exercise unsupported SDK/native module/client, malformed/expired launch payload,
wrong target/origin, permission/tailnet/TLS loss, application background/foreground,
phone network change, Metro stop/restart/crash/expiry and source compile errors. Show
useful bounded reasons without public fallback, disabling TLS or silently launching
a different project. Reconnect/reload the intended session after recovery; stopping
Metro leaves source and independently running backends intact. Build-required status
routes to MOB-004 planning, not an implicit build/account/signing operation.

### GO-006 — Privacy, ownership and future client boundary

Use public config only; no private API/signing/GitHub credentials or owner device
identifiers enter generated source, launch payloads, receipts, request logs or evidence.
Do not collect Expo Go local device lists. Store only bounded, non-identifying owner
reported platform/client evidence outside public source when needed; sanitize records.
Use project/native-mode eligibility with canonical-root controls, preserving task
worktree source-only behavior and frozen releases. A future development client uses
its own compatibility and launch-mode contract; Go approval never certifies it.

### GO-007 — Compatibility rollout and delivery

Ship profile/launch serializers/QR dependency policy with a versioned capable provider
and required frozen frontend/collector updates; retain old source/runtime behavior.
Old or missing capability means launch unavailable. Profile/SDK updates use reviewed
new versions, with expiry/drift/revalidation rather than silently recertifying devices.
Rollback removes Go launch capability while preserving source and managed Metro;
stop/revoke sessions only through their owner interface if separately required.
Keep local/CI, installed launch tests, acquisition/operator prerequisites and owner
physical acceptance distinct. Mark each platform supported only with actual evidence.

## Acceptance criteria

| ID | Required evidence | Requirements |
|---|---|---|
| AC-001 | Exact eligibility profile and actual installed client/OS matrix; unsupported, unknown, version/native/config changes and expired evidence deny certification without editing source or acquiring credentials. | GO-001 |
| AC-002 | Verified native launch payload/QR opens the correct private project on each claimed platform; encoding, foreign origins, generation/expiry/port-reuse, no secrets and local QR generation are tested. | GO-002 |
| AC-003 | CLI/dashboard expose Go eligibility separately from Metro, preserve web/backend links, fail safely on missing capability and perform no hidden start/route/account operation. | GO-003/006 |
| AC-004 | Two projects load native UI/assets and respond to interaction on real devices; a restored source edit Fast Refreshes and full reload works on each claimed platform. Record actual versions and owner confirmation. | GO-004 |
| AC-005 | Network/tailnet/background/TLS/compile failures and Metro restart/expiry yield honest unavailable/error behavior; intended-session reconnect works with other app/backend/source intact. | GO-005 |
| AC-006 | Privacy/ownership, source/worktree/legacy regression, profile drift, minimum dashboard browser and QR decode tests pass; no device data, tokens or public tunnel appears in source/logs/artifacts. | GO-006 |
| AC-007 | Source/installed/CI launch behavior agrees; capable rollout/rollback preserves Metro/source, implementation merges and owner accepts the supported matrix with retention/runbook records. | GO-007 |

## Completion and open decisions

Deliver this draft for owner review; implementation begins only after authorization
and SPEC-033's provider/security/private transport preconditions. Verify current
physical-client acquisition and exact installed versions before publishing supported
platform claims. If a platform cannot use Go, keep its Go acceptance pending/unsupported
and scope MOB-004 separately; do not count a signed personal Go build as a credential-
free success. Capture the final platform preference, real devices and fixture-retention
scope before live tests. Existing retained MOB-001 synthetic fixtures may be reused
only through approved owner scope, with preserved source/private PRs and other apps.
No application or store account setup is presumed necessary or authorized by planning.


## Approved SDK-57 Go transport amendment (October 14 UTC)

The project owner approved replacing only the two owned Metro listeners 8443/8444
with private HTTP over the authenticated, encrypted development Tailscale network.
For these Go sessions this supersedes application-layer TLS in MET-003; port-443
dashboard/project and app/API routes retain HTTPS. No public/LAN exposure, account,
SDK migration, native build or expanded dependency exception is authorized.
Explicit versioned session/route/profile contracts must distinguish the transport;
legacy HTTPS receipts remain valid and older providers reject unknown contracts.
Exact owned replacement/readback/rollback goes through the SSM operator after
source checks and healthy bounded backends. Preserve finite expiry, source/data,
stale-generation guards, fixed origins and every unaffected handler. All physical
acceptance and platform-matrix criteria remain required.

The owner also requested restoration of HTTPS when a compatible official Go client
ships. [The release-triggered follow-up and decision](../034-expo-go-workflow/client-transport-decision.md#approved-decision-and-https-restoration-follow-up)
requires native HTTPS status/bundle/assets/reload checks and SDK/client compatibility
before conversion. SDK-58 Go drops SDK-57 support; no automatic source upgrade or
TLS restoration from a store release alone.
