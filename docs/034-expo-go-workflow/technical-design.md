# TDD-034: Expo Go compatibility and launch UX

- **Status:** Implementation authorized — not installed capability
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-034](spec.md) · **Tasks:** [TASKS-034](tasks.md)

## Consumer design and eligibility

Consume SPEC-033's versioned read-only endpoint descriptor; do not allocate ports,
run Expo CLI, change Serve or replace lifecycle receipts in a Go launch operation.
Require matching canonical project/session generation, fresh transport readiness,
valid runtime security admission, unexpired session and selected compatible target.
CLI inspection/launch is read-only apart from owned ignored local QR output with
explicit overwrite bounds. Starting/enabling Metro is a separately visible operation.
Unknown provider/descriptor versions return unavailable, not guessed launch data.

Propose a versioned Go profile registry in reviewed platform configuration, separate
from immutable SDK source policy. Bind SDK/core/native graph/config digests, approved
transport type, supported platform/client build/OS ranges and verification date/source.
An exact client build is recorded in live acceptance; proposed certification validity
is seven days with earlier invalidation on relevant input/client changes. Explicitly
label project eligibility versus last physically verified client; the host cannot
read the phone's installed version or continuously certify an App Store update.
Ask the owner to check the installed client on drift/unknown version, with supported,
incompatible or check-required outcomes rather than falsely reporting a device online.
Native changes requiring a new client route to MOB-004 without mutation.

SDK 57 is a starting candidate from the delivered frozen source, not a promise of
Go installability on every OS/device. Recheck the official installer/store metadata
and actual device at implementation. Record acquisition/account/signing requirements
per platform. A paid/account/signed personal Go path is outside this spec; if needed,
prepare the separate MOB-004 scope rather than embedding credentials or extending it
silently. No npx latest tooling, remote generator or opportunistic SDK upgrade.

## Launch payloads and QR

Implement a pure validated serializer with per-platform verified Go URI rules from
the protocol spike. HTTPS Metro transport and the client launch URI are different
fields; a URL prefix swap alone is not proof of correct manifest/assets/WebSocket
origins. Do not use app.json's development scheme as an assumed Go scheme. Exact
SDK/Go behavior must prove manifest mode and signed/unsigned response handling over
the approved private origin, with no TLS exceptions or public QR forwarding page.
Retain no request identity/secret in payloads or logs.

Protect stale payloads across restart and port reuse: a supported client's verified
session-bound entry path/nonce, or a lease/listener policy that prevents reassignment
while issued payloads remain usable, must bind old launch to unavailable/the original
project. A nonce is not an access credential or substitute for tailnet authorization.
Select and prove the mechanism with SPEC-033 before implementation; simply expiring
UI state cannot invalidate a copied QR inside Go. Don't add a redirect/rewriter that
breaks manifests or bypasses client signature checks.

Use a small exact locally rendered QR dependency only after verifying license,
integrity, limits and policy support; no package is selected/installed by planning.
Encode the complete validated client payload, cap input/output size, generate an
accessible label/copy alternative, and decode it in tests. Source code and runtime
client data must never be sent to an external QR service. Store QR output outside
tracked app content; screenshot evidence redacts private owner/device metadata.

Minimum UI change is an eligible native Open in Expo Go action/QR detail on mobile
source rows, labeled separately from web Open app/API docs. Stopped, route-pending,
stale, unsupported client and expired profile states disable it with the provider's
bounded reason. Existing group web/API/DB actions and keyboard/accessibility behavior
remain covered. Full installed device/build/channel telemetry stays with MOB-009;
no device count or phone health is added by a successful host probe.

## Physical acceptance and recovery

Use two approved synthetic canonical projects. Keep the starter's counter/navigation
and local assets deliberately for source/client acceptance; this is not a product
adaptation or backend CRUD demonstration. On actual iOS/Android devices as selected
by the owner, record the exact client/OS, source SDK/lock/config, session generation,
private origin policy and evidence date. Launch both, interact, edit one display/state
behavior reversibly, verify Fast Refresh and forced reload, and restore the edit.
Restore only the exact task-owned diff with before/after identity/hash guards; retain
concurrent edits for review rather than overwrite them. A full reload may reset local
counter state; no database persistence is implied.

Exercise phone backgrounding, Wi-Fi/cellular transition, tailnet loss/rejoin, denied
access, compile error/recovery and Metro restart/expiry, checking intended-session
identity and bounded error UX. Observe another session and existing backend unchanged
when stopping one; do not operate an unrelated backend to prove isolation. Desktop
protocol/browser/QR tests support host implementation but cannot establish native
UI or physical-client support. MOB-011 later adds general native/device automation;
manual owner evidence is required for this bounded initial Go loop.

CI runs profile/serializer/freshness/URL/QR-decode tests, mocked capability mismatch,
secret-pattern/fixture redaction and existing CLI/worktree/dashboard regressions,
with no phone accounts, signing keys or internet-based QR service. Record actual
installed provider/UI parity and physical-device outcomes separately. Rollout uses
reviewed immutable provider/collector/frontend managers; no new route or operator
rights are acquired here. Rollback removes launch/eligibility capabilities and keeps
MOB-002 state/source; any session stop follows its reviewed lifecycle.

## Traceability and decisions

| Requirements | Mechanism / task | Acceptance |
|---|---|---|
| GO-001 | Reviewed source/client/platform profile and freshness; T-002/003 | AC-001 |
| GO-002 | Exact native URI, stale-session binding and local QR tests; T-002/004 | AC-002 |
| GO-003/006 | Read-only CLI, minimal native link UI, privacy/ownership guards; T-004/005 | AC-003/006 |
| GO-004/005 | Actual two-project client interaction/edit/reconnect matrix; T-007 | AC-004/005 |
| GO-007 | Versioned provider/UI parity, safe rollback and closeout; T-006/008 | AC-007 |

Open decisions: final supported physical platform/client matrix (owner/implementer);
exact URI and old-QR isolation mechanism (implementation author after SPEC-033 spike);
local QR dependency pins/licensing (implementation author before review); current
Go acquisition prerequisites (owner after factual device check). Runtime security is
SPEC-033's gate, not a new exception inferred from this consumer. Plan/test serializers
without live accounts while unavailable device prerequisites remain explicit.

Primary references checked October 13:
[Expo Go downloads](https://expo.dev/go) currently list SDK 57 and platform options;
actual phone installation remains an implementation check.
[Expo environment setup](https://docs.expo.dev/get-started/set-up-your-environment/)
distinguishes Go's limited client from development builds.
[Development builds](https://docs.expo.dev/develop/development-builds/introduction/)
are the extension for native requirements outside Go.
[Expo's May 2026 notice](https://expo.dev/changelog/expo-go-and-app-store-may-2026)
records historical store constraints and personal signed Go/account requirements;
it is not evidence of today's client availability.


The owner confirmed whole-tailnet host access on October 14. Go eligibility requires
membership in that development tailnet, with no additional per-device ACL selector.
Private host protocol evidence and session-bound root entry/old-generation denial
now exist for both fixture origins. Exact Go-client nonce preservation, physical
reload/interaction and local QR proof remain required before supported launch claims.


## Selected local QR and acquisition prerequisites

The reviewed exact encoder is `toqr` 0.1.1 (MIT, zero runtime dependencies), already
present in the approved locked Expo CLI graph. The frontend now pins it directly;
`jsqr` 1.4.0 (Apache-2.0, zero runtime dependencies) is a test-only independent decoder.
Registry integrity metadata and installed licenses were inspected; frozen install,
fresh zero-finding audit, exact decode and rendered-SVG checks are recorded in
[QR review](qr-review.md). These do not certify native URI semantics.

`localQr` is pure local rendering with a 512-byte printable-ASCII input limit,
finite matrix/output bounds and a four-module white quiet zone. Generated SVG has
only numeric paths and contains no raw payload markup, external asset or network
reference. Browser/decode tests rasterize the final SVG rather than only checking
its internal matrix. Public launch integration still requires the validated current
provider/target/generation/profile payload; no launch action is enabled by this utility.

The official September 3 notice rechecked October 14 says latest physical iOS Go
requires matching Expo CLI/app login; Android enforcement is described as future.
The candidate iOS profile therefore reports the CLI-login prerequisite as outside
this spec's credential-free scope and points to MOB-004. Keep the iOS native software
path and protocol evidence, without claiming a usable credential-free Go client or
changing SDK/signing/accounts. Android 57.0.9 is still an unverified reported candidate.
