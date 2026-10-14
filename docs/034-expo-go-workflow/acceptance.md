# SPEC-034 acceptance tracking

- **Status:** In progress — Android native edit/recovery and installed rollback verified; final owner/delivery gates pending
- **Owner:** Project owner
- **Observed:** October 14, 2026 UTC
- **Specification:** [SPEC-034](spec.md) · **Design:** [TDD-034](technical-design.md) · **Tasks:** [TASKS-034](tasks.md)
- **Implementation:** [draft PR #78](https://github.com/danielbardsley/gptclaw/pull/78),
  changes following 9308e0b; installed as the combined provider; not merged.

## Criterion mapping

| Criterion | State | Evidence and remaining work |
|---|---|---|
| AC-001 | Passed (Android-first) | Android 11 / Go 57.0.9 / SDK 57 private HTTP is physically verified, with finite seven-day certification and tested unsupported/input/client drift gates. Owner selected Android-first delivery; iOS is uncertified with its account prerequisite outside scope. |
| AC-002 | Passed (Android-first) | Owner confirms both fresh locally rendered QR images open the correct native apps after restart. Encoding, foreign origin, generation/expiry/port-reuse and privacy rejection plus independent PNG decode pass. Further runtime failure/reconnect remains AC-005. |
| AC-003 | Passed | Read-only inspect/launch and minimum Open/copy/QR UI preserve existing links and fail closed on missing/stale capability. Portable browser tests and installed CLI/collector parity pass; launch performs no hidden runtime/route/account action. Physical product QR is separately pending under AC-002. |
| AC-004 | Passed (Android-first) | Owner confirms both Android projects’ native UI/assets/counter/navigation, state-retaining Fast Refresh and restored-source full reload. Owner accepted the Android-first scope; iOS remains unsupported/follow-up. |
| AC-005 | Passed (Android-first) | Prior network/tailnet/background/compile recovery passes. Earlier stop/reload isolation failed because app two also could not reload. The installed capacity correction now has owner-confirmed loading for both fresh sessions; the owner reports Reload still works and the repeated physical stop/isolation check passes. The owner confirms native reconnection after app-one restart and post-crash Reload of both apps. Owner separately confirms expired app one is unavailable while app two remains usable; the physical expiry check passes. |
| AC-006 | Passed | Profile/serializer/privacy/ownership/worktree/legacy/collector/package regressions and portable QR/browser/type/build gate pass. Installed public projections and source-exclusion canary remain free of fixture secrets/device data. Implementation CI passes at 92119fb; final merge/delivery is separately AC-007. |
| AC-007 | In progress | Source/frozen launch parity verified. Stable rollout, capable rollback and implementation CI pass. Merge and owner matrix/retention acceptance remain. |

## Verification

`python -B scripts/tests/test_expo_go.py` in the prepared Python 3.12 environment
passes fourteen focused cases. The candidate policy reports every platform as
uncertified; no verification date is fabricated. The seven-day maximum certification
age is recorded for future physical evidence, not exercised as accepted certification.

Direct source inspection and the immutable provider's `go inspect` agree for both
actual approved canonical roots with Expo Go 57.0.9 / Android 11 supplied as caller
metadata. Both sources are eligible, both Metro sessions are Ready, and both clients
remain check-required with launch unavailable. CLI duration is 0.767 / 1.173 seconds.
The exact frozen candidate is
`269d34ea87b35eea8cadd75deaa882c585148fd682f9d9ee82d5f0b59e7afb41`.
Timing metadata is excluded from semantic equality; the first harness incorrectly
included that existing CLI field and was corrected. No stable pointer selection,
source change, SDK upgrade, account setup or Tailscale mutation occurred.

Official [Expo Go download metadata](https://expo.dev/go) and
[linking documentation](https://docs.expo.dev/linking/into-your-app/) were rechecked
October 14: SDK 57 is offered, and `exps` denotes HTTPS. This does not verify Go
57.0.9's private nonce/signature/reload behavior and does not authorize advertising
an unproven launch payload. No local QR dependency has been selected yet.

The owner confirms all devices on the development tailnet are permitted. The current
wildcard grant is accepted unchanged. Off-tailnet denial is owner-reported; physical
client membership/access still requires the real device checks.

## Remaining work

Prove exact Go-client launch rules and stale-session binding; implement/verify local
QR and minimum dashboard launch UX; acquire exact iOS physical evidence when a device
is available; complete Android interaction and both-platform recovery checks. Then
verify installed provider/consumer parity and rollback, CI, reviewed merge and owner
acceptance. Retain synthetic counter/navigation/assets for this deliberately scoped
starter/client test; this is not a product or backend CRUD acceptance claim.


## Local QR and current iOS prerequisite checkpoint

The exact reviewed encoder/test decoder are pinned and described in
[QR review](qr-review.md). Thirteen frontend tests, type checking, production build
and the complete portable socket/HTTP/browser gate passed. The final SVG independently
decodes after actual browser rasterization; fresh complete frontend audit has zero
findings. No Go product link or native-device certification follows from these checks.

The official [September 3 Expo login notice](https://expo.dev/changelog/expo-go-57-login)
rechecked October 14 says latest iOS Go requires matching CLI/app account login, with
Android enforcement described as future. The candidate iOS profile now explicitly
reports that prerequisite as outside the credential-free scope and routes to MOB-004.
Fifteen focused inspection cases pass, including acquisition/login-bypass rejection.
The owner requested continued iOS software development; the native protocol/software
path remains, with physical/client acquisition and any separate credential/build scope
pending. No account credential or login was installed.

An Android candidate launch-rule check was requested using current session-bound
private URLs; no device answer has arrived. The second session subsequently reached
its original expiry and became unavailable, with exact owned cleanup verified. The
first candidate remains finite. These are implementation prerequisites and pending
owner evidence, not completed physical criteria.


Updated source/frozen inspection parity passed on both actual fixtures for Android
57.0.9 / Android 11 and the assumed iOS client/OS input. Android remains check-required;
iOS returns the explicit out-of-scope CLI-login reason; Metro separately shows the
first Ready and the second expired. Frozen candidate
`2e51878ec8cea1c71a405969cc5c8f9dc423acc25a77cda228cd9f7683ccf3da` matches source;
observations took 0.735–1.107 seconds. Immutable dashboard release
`953e8e25851985e8ad1be08eeb791392fa9e93d85477abd0f84bfefcebf46a78` was prepared
with existing status/link flags; no stable pointer or active dashboard selection had
changed at this checkpoint. Preparation is not installed acceptance.


## Android launch failure and transport correction (October 14 UTC)

The owner’s Android 11 / Expo Go 57.0.9 launch of the exact 8443 query-based URL
failed with `java.io.IOException: Failed to download remote update`. The phone
browser could reach the private health endpoint. Warming the unchanged generation’s
6,441,560-byte Android bundle reduced the host download to 2.398 seconds, but the
owner’s retry still failed; cold compilation alone is not an explanation or fix.

A fresh bounded diagnostic generation, 4778c48ab0fc418eb19c6c0dc034797e, then used
a locally rendered QR, independently decoded before presentation. The owner
reported the same error. Before that attempt, no resources or rejections were
counted. Afterwards, there were exactly three `stale-launch` rejections and zero
forwarded manifest/bundle/asset requests. All other fixed rejection counts were
zero. The failure reaches the proxy and fails the generation guard before Metro;
this does not establish an SDK, account, TLS or bundle failure. No request URL,
query, header, token, IP or device identifier was captured.

The adapter now accepts only the exact current session-bound path
`/_gptclaw/metro-session/GENERATION/` and maps that entry to the SDK’s `/` manifest
route. SDK bodies, MIME boundaries, signatures and origin-root resource URLs are
unchanged. Old/wrong/malformed paths, conflicting generation queries and unbound
`/manifest` or `/index.exp` aliases fail closed. The previous exact query entry
remains available for historical host probes; it is not a verified Go launch rule.
Twenty-five real loopback proxy tests and twenty protocol tests pass at this
checkpoint. Native success, two-project interaction and reload acceptance remain
pending until the corrected path is actually tested on the owner’s device.

Diagnostics are bounded in-memory aggregate counters, exposed only through the
existing private origin at `/_gptclaw/metro-transport`. Keys are fixed rejection
enums, resource categories and HTTP status classes; counters saturate at 2^53−1.
Health response shape is unchanged. Nothing is persisted and no per-request
identity or raw payload is logged. Reading counters is not device-online evidence.
The first diagnostic session was replaced through its reviewed owner controller
with fresh security admission; the second project and shared routes were preserved.


### Normalized path follow-up

The owner also reported the same download error for the slash-terminated session
path on generation 99e19c05970a41e69a8ce781adc6cef7 (expiry 18:47:43 UTC). Before
that attempt, agent probes had one successful manifest and four deliberately
rejected stale/alias entries. Afterwards, stale-launch rose from four to eight,
with no additional forwarded resource. This candidate did not pass native launch.

Targeted inspection of Expo’s public Android
[Kernel.getManifestUrlFromFullUri](https://github.com/expo/expo/blob/11342ecad05c78851da27ca0ea587f3f214af361/apps/expo-go/android/expoview/src/main/java/host/exp/exponent/kernel/Kernel.kt#L506)
found explicit removal of nonreserved query parameters and the final trailing
slash. This explains both rejected candidate forms; it is source evidence, not
an exact binary fingerprint of the owner’s app. The adapter now accepts the exact
current generation path with or without one trailing slash. New candidates/probes
use the form without a trailing slash. Both map only to the SDK root; old/wrong
generations, extra segments or duplicate/conflicting generation queries remain
rejected. Twenty-five proxy cases pass, including both normalized forms with
unchanged multipart body and signing header. Native retry remains pending.


## Native manifest reached; SDK-57 development probe uses HTTP

On generation 5eb678adae594bab80daac2d9bd5be92 (expiry 18:56:37 UTC), the owner
reported that the app opened, then “Packager is not running.” The reported address
is `http://forge-dev-01-4.tail8c3304.ts.net:8443`. Agent comparison shows one new
successful manifest and no forwarded bundle/status request. The native entry-path
guard is passed; counter/navigation/assets, edit and reload are not accepted.
The agent's HTTPS `/status` probe returns 200 and exactly `packager-status:running`;
the manifest's launch asset is HTTPS on the owned origin and the SDK is running.

The official SDK-57 Android branch at 0607af7a70d0ea3e58a6d55824aac5cfd3e78613
uses HTTP unconditionally for its development packager probe. The newer main-source
HTTPS-origin fix cannot be assumed present in the owner’s installed client. Go
inspection therefore now reports the exact Android client unsupported for the
approved HTTPS transport, with no launch certification or implicit fallback.
Sixteen focused eligibility/CLI cases pass, including refusal to bypass this known
transport prerequisite. [The concrete transport decision](../034-expo-go-workflow/client-transport-decision.md)
records alternatives; no listener/profile transport change or client build is applied.

At c8d03a1, the prepared immutable dashboard release is
8950b4549e6ad51b827eb374a3c628062ec5a37e0309f98a12783586cacad3ec, with provider
b99f07397268d3e4d4793a64220c9a2d405fd9349cfdce63e25c0d9a03b2597c. Both fixtures'
source/frozen inspection behavior matches, excluding only separately measured
command duration (one 0.587/0.822 s; two 0.788/1.242 s). The initial strict full-JSON
comparison failed because elapsed durations differ; the corrected behavior check
passes. One is Ready, two is Expired, and launch availability is false. This snapshot
precedes the newly recorded Android incompatibility; its new profile still requires
frozen parity. Stable launcher and active dashboard were not selected or restarted.


The normalization correction c8d03a13ce7105f3f4738fa7fa8540d2278d0547 now has
all four CI workflows passing: dashboard 38611095207, development host 38611094360,
private applications 38611094365 and Tailscale federation 38611094314. No protected
AWS deployment/apply was invoked. The later unsupported-client profile is verified
with sixteen local eligibility/CLI cases and immutable-provider behavior parity on
both actual approved fixtures at provider
0d693ff3f11fb696e5f7b0840b876e1a6fffb9d5824ab92d0c7dccb226ce3b98. That profile’s
CI is not inferred from c8d03a1. Source and snapshot both report Android unsupported
for the current HTTPS boundary, with launch unavailable; one remains Ready and two
Expired. Active dashboard and stable launcher remain unchanged.


## Approved HTTP implementation and loopback preparation

The owner explicitly approved Metro-only private HTTP over encrypted Tailscale.
Source now has an explicit `--metro-transport tailnet-http` lifecycle selection,
schema-2 HTTP receipts/descriptors/route approvals, strict same-node/scheme resource
validation, HTTP-aware health/WebSocket probes and native collector projection.
Legacy HTTPS stays schema 1; old providers reject schema 2. Exact conversion retains
the original HTTPS approval and history, rejects unowned bindings, keeps private
readiness false before operator execution and gates rollback recording until HTTP
is removed/replaced. No native launch certification follows from host tests.

Focused checks pass: 26 proxy, 22 protocol, 49 controller, 15 state, 24 route, 17 Go
inspection, 9 native collector and 22 mobile-source cases. The first new collector
case used the wrong function name; correcting the test to the existing `project`
function gives all nine passes. This is local verification; latest HTTP CI remains
pending. The previous normalization revision's four CI workflows passed separately.

An actual attempt to change the running first session's transport in place was
rejected with conflict and preserved its generation. Through the owner lifecycle,
only that SDK was stopped and replaced; the expired second SDK was independently
started. Fresh admitted one-hour HTTP loopback sessions are:

| Project | Generation | Expiry UTC | Android bundle bytes | Bundle SHA-256 |
|---|---|---|---:|---|
| mob001-accept-one | 788e407115ff4ad3802c475453062cd3 | 20:04:04 | 6441558 | 207c54fa52af4c5734b680baca48d932e1ab6f646095d6558c53ecc8253e95c8 |
| mob001-accept-two | 9d717649f4c64a56b7b3a96fa9575e97 | 20:05:42 | 6441558 | 5a452b481fa7a893548e9851bc7c5f1806e36270c254e19f2a820f0932b6c4c1 |

Both session-path manifests are 200 / 1,299 bytes over the owned loopback proxies,
with advertised HTTP bundle targets. Both Android bundles are warm. Exact conversion
plans are recorded (one 9aa9584e17457e51775ca5332b17b1cb00cc6a195625c994cb63213714f774c6;
two 3db774203ca5f7f48a35f04938ccded8c534f8364f8274563a4eafd7e3914cb1).
Current Serve remains HTTPS; private HTTP route state is therefore unavailable as
expected. Baseline handlers and Funnel-off state are independently verified.
Operator conversion, private HTTP/device checks, source/frozen final parity,
installed rollout/rollback, full Go consumer implementation and delivery remain open.


## Operator HTTP conversion and independent private readback

On October 14 the project owner reported execution of the exact approved two-port
SSM conversion. Independent readback verifies HTTP on TCP 8443/8444, their exact
owned loopback proxies, unchanged original dashboard/project baseline digest
`d0c41e928966c5d085e704d5826120b76ae4b4af854eb0aa570e447d52db5539`, and Funnel off.
Both current generations retain their original expiry and report Ready. Private
HTTP native manifests return 200 / 1,299 bytes for each project. Fresh `exp://`
path-bound candidates were sent for physical Android acceptance; that owner check
is pending. This establishes private transport readback, not native UI acceptance.


## Android native acceptance and bounded Go consumer (October 14 UTC)

The project owner confirms both current private HTTP candidates opened correctly
in Expo Go 57.0.9 on Android 11, including the requested native counter, navigation
and local icon checks. On each app, the agent changed only the heading in
`src/app/index.tsx`; the owner confirmed automatic Fast Refresh while count 3
was retained. Exact hash-guarded originals were restored and each checkout is
clean. The owner confirmed full reload restored the normal heading and count 0.
An owner-supplied screenshot corroborates the restored native starter screen;
it is not a binary fingerprint or additional platform certification.

On app two the owner confirms background/foreground, Wi-Fi/mobile-data transition
with Tailscale connected, failed reload while disconnected, and successful intended
app reload after reconnect. A brief task-owned syntax error in app one produced
the native compile error while app two remained usable; exact source restoration
and native reload/counter recovery were confirmed. These are owner reports,
separate from agent protocol checks. Physical restart/stale QR/expiry checks,
installed rollout/rollback and final delivery remain pending.

Both sessions also pass agent private HTTP probes for iOS/Android manifests,
bundles over 2 MiB, local icon, source maps, and `/message` and `/hot` WebSocket
upgrade/ping-pong. Android bundles are 6,441,558 bytes; iOS bundles 5,737,498 bytes;
source maps are 12,348,959 / 11,366,453 bytes. iOS host-protocol checks do not
establish physical iOS support. The sampler's prior fixed label said private TLS
for these HTTP probes; transport was independently verified HTTP and the label
is corrected in source.

The reviewed Android profile now records actual physical validation at `2026-10-14T19:33:39.053597+00:00`,
expiring `2026-10-21T19:33:39.053597+00:00` (seven days). It binds the unchanged exact SDK/source policy,
locked graph, static public config/toolchain contract, Android 11, Go 57.0.9 and
approved private HTTP. New source/client/config/transport or stale/future evidence
withdraws launch eligibility. iOS remains uncertified and reports its CLI-login
prerequisite outside this credential-free scope; no device/version assumption
is treated as acceptance. No automatic recertification or SDK migration occurs.

Source implements explicit read-only `go launch --generation`, exact owned-origin/
generation/expiry serialization, finite profile freshness and minimum dashboard
Open/copy/local-QR controls. No launch operation starts Metro, provisions a route,
logs into Expo or collects phone identifiers. Stale collector/layer/session/profile
states withdraw links and QR. Existing app/API/repository links remain covered.

Local checks pass 26 Go, 6 Go collector, 9 native collector, 10 observation and
21 provider-packaging cases. The dashboard portable gate passes 17 frontend tests,
typecheck, production build, independent rendered SVG decode and browser UI checks
including native Go controls and stale/hostile payload withdrawal. The first decode
check failed because its expected payload retained the old query form; both the
producer and independent assertion now use the proven session path and pass.
The full local repository gate was attempted but terminated with SIGTERM/143
after its completed suites passed; it is not recorded as a full pass. CI at
885a4d9 passes dashboard 38622460470 and private applications 38622460506.
Development-host 38622460480 and federation 38622460457 failed solely because
the Metro capability assertion still expected `[1]` instead of `[1,2]`; that
assertion is corrected. Latest consumer CI remains pending. No protected apply ran.

Source/frozen Go behavior matches on both real approved roots at provider
`9f574ef13547d7b83cd0370719a4cd076765c2514feb5316c18d06984deeda6e` (before
the subsequent consistent-reason validation). App one is compatible/stopped with
launch unavailable; app two is compatible/Ready and its exact generation-bound
payload matches. Elapsed command duration is excluded from behavioral equality.
The retained HTTP-capable, Go-disabled rollback provider is
`a99e4012c3b0232ddf0dffc3ef7161e34f2eed20976ac9a6bcf9bd11a812963c`.
Stable launcher/dashboard remain unchanged at this checkpoint.


## Installed collector correction, rollout and recovery checkpoint

All four CI workflows pass at implementation 78a9d45b344cd3655c72ef719ebb4c88e178d79b:
dashboard 38627048749, private applications 38627048657, development host
38627048864 and federation 38627048631. No protected AWS apply ran. Later
collector/cleanup corrections below require their own final CI.

Actual installation exposed two missed boundaries: the collector entrypoint
hard-coded only schemas 1–4, and provider observation sent a reduced native
projection where StatusStore expected the typed descriptor. Source now reads
capabilities from its bundled read-only CLI and hands the typed session descriptor
to the collector; the public native projection remains unchanged and removes
origin/transport details. Six collector cases and ten observation cases pass,
including CLI-capability parity and the real provider-to-StatusStore handoff.
Nine native projection and six Go projection cases also pass. The portable
dashboard install/test/type/build/socket/QR/browser gate passes again (17 frontend
cases). Earlier readiness harness attempts failed; the harness also initially
assumed a non-null observation and an inactive session whose old TTL had not
elapsed. Those task-harness assumptions are corrected and not product successes.

New immutable paired candidates retain the original snapshots unchanged: Go
provider 4791d30c239a6b145ea108d564b259c69b2b34102f355d3e96515f47c2c53959 /
dashboard a17ec4fb9f9b5ba6dba0cd5bc872eb2848abd30818947b70f2eba83d0bd40a35,
and HTTP-capable Go-disabled provider cc9850dcbc31cc30d838e99ad9ed6600a60db2f713cbce9be61e42f3f0a1ab2d /
dashboard 833e14ab9ccf727ff97824f73646b10187cd452d879e504bdb2981f55e95dfd5.
The disabled candidate is a new snapshot built from a task-owned copy of the
previous HTTP provider plus the two collector corrections; no old snapshot was
modified. Actual install → Go enable → Go-only rollback → roll-forward passed.
Installed CLI launch, live collector Ready/Go launch and withdrawal during rollback
were verified. Both session generations/expiries, canonical sources, group behavior,
original HTTPS handler baseline and Funnel-off state were preserved throughout.

Effective metadata on the owned second SDK verifies read-only source/dependency
mounts/rootfs, 1 CPU/1536 MiB/256 PIDs, loopback-only publish, internal network,
log driver none and offline/no-dotenv/no-telemetry/ephemeral HOME predicates.
Only necessary metadata and boolean fixed-environment predicates were inspected;
no environment, credential, control token or SDK-output dump was recorded.

The original second generation 9d717649f4c64a56b7b3a96fa9575e97 expired normally
at its one-hour bound with absent SDK/network/proxy and clean source. A subsequent
explicit ten-minute installed-test generation e18a2397bd4f4acc8f914f8453a969fd
ended recovery-required with sanitized owned-cleanup/conflict, although all resources
and listeners were independently absent. Exact owned recover-stop reconciled the
receipt. An inspect/auto-removal race is a possible cause, not a proven trace.
Cleanup now accepts a failed removal command only after independent absence is
proven, while foreign/unknown replacements still block. All 51 controller cases
pass, including both absence and foreign-replacement regressions. A new-runtime
expiry check remains required before claiming that intermittent path fixed live.

The owner later reported neither old app link could download. At that time app
one was intentionally stopped and app two's original URL was obsolete after its
finite expiry/rehearsal replacement; this is not confirmation that the other app
remained usable during the earlier stop window. Following that response, app one
was explicitly restarted (ed16a0fa76ca4e879505c670d3a03c9e, expiry 21:25:12 UTC).
The second bounded rollout generation is b015056fcff54f35a85a7f92393a87c9,
expiry 20:32:13 UTC. Both Android bundles are warm and unchanged at 6,441,558 bytes.
Cold compilation briefly made the first protocol layer unavailable; subsequent
process/protocol/route observations are Ready. Current dashboard QR/copy and
intended native restart confirmation have been requested; no owner result is
assumed. Stable Go installation at this checkpoint precedes the cleanup race fix.


## Final corrected source verification checkpoint

At 92119fb3f4a699e9c2c9a4b444e183f2d369ccf9 all four CI workflows pass:
dashboard 38632684998, development host 38632685434, private applications
38632685022 and federation 38632685026. Protected plan/apply did not run.
The final source is installed as combined provider
69061bff1ab378e044a4684090ead61f6a94cd87f4899b475beb61ede98cb473 with dashboard
1ac5111f34b77a179a88ffe5ce014358a1a573d34a4f8e86e8779ea062fda2c4.
Actual installed collector verifies the current first app Ready with its exact
generation-bound Go action. Source and installed inspection are identical on
both real fixtures excluding command duration: one Ready/launch available;
two Expired/launch unavailable.

After exact owned reconciliation of the prior second receipt, one explicit
120-second updated-runtime rehearsal ran at generation
9ece4e2f6a604fffbc354ad0d77b58f4. It became Ready, then automatically ended
Expired / operation passed. SDK container, isolated network and both loopback
listeners were independently absent. The original canonical source is clean;
first-session generation/expiry and the original HTTPS/Funnel baseline are
unchanged. This is a real successful updated-cleanup expiry case; the two
earlier ambiguous cleanup outcomes remain recorded above.

The project owner has been asked to confirm refreshed dashboard QR/copy and
intended first-app native restart. The first session remains bounded until
21:25:12 UTC; no response is assumed. The previous second-app QR prompt expired
with its stated 20:32 UTC session; test only a current available dashboard action.
An Android-first matrix decision is also pending: iOS remains unverified with
its CLI-login prerequisite outside this scope. Final owner acceptance, operator
owned-listener removal evidence, review/merge and delivery records remain open.
No catalogue entry is marked Delivered.


## Current recovery status (October 14, 20:58 UTC)

See [the paired runtime admission evidence](../033-private-metro-sessions/acceptance.md#admission-drift-and-environment-file-denial-october-14-2058-utc).
App one recovered after the source guard rejected a task-owned environment-file
fixture; its current Ready generation/expiry remain unchanged. App two is expired,
so its old manual/QR links cannot download. The report that neither app downloaded
is retained as a failed/obsolete-link observation, not proof of physical isolation.
Current dashboard QR/copy/native restart confirmation and the explicitly selected
platform matrix are pending. No expired prompt is an acceptance result.


The [private renewal rehearsal](../033-private-metro-sessions/acceptance.md#positive-private-renewal-and-finite-replacement-october-14-2114-utc)
passes actual HTTP transport retention, a fresh bounded generation, old entry
rejection and automatic cleanup. This is host/protocol evidence; it does not
replace the pending physical restart/crash/expiry and product QR checks.


## Owner resumed device checks and selected Android-first delivery

On October 14 the owner requested fresh sessions and inline QR codes after other
work delayed the earlier prompts. The owner explicitly selected Android-first
release with iOS retained as a follow-up. Prior expired QR prompts are not counted
as physical evidence. Two fresh one-hour sessions are being prepared under the
existing exact runtime/private-listener scope. The owner did not report execution
of the listener-removal command; defer that operator step until device checks
finish and independently read back its result. No Tailscale mutation or new
permission is inferred from the reply.


Both [fresh owner-requested QR sessions](../033-private-metro-sessions/acceptance.md#fresh-owner-requested-qr-sessions-october-14-2122-utc)
are Ready with warm Android bundles and independently decoded local PNGs. Physical
scan/intended-app restart confirmation is pending; no delivered or device result
is inferred from PNG rendering. The owner-selected Android-first matrix is
accepted, while iOS remains unsupported/follow-up.


## Owner QR acceptance and failed reload isolation (October 14, 5:57–6:08 p.m. Eastern)

The project owner confirms both fresh QR images open the correct native home,
local icon, navigation and working counter after restart on the selected Android
matrix. This is physical QR/restart evidence for generations c5ad655350a04e11a5b478c45e0a9ceb
and dc40a59da6f1445e838fabf899c55b41, separate from local PNG decode.

Before the isolation mutation, both host route observations intermittently failed
while their owned SDKs remained up with zero restarts. Aggregate diagnostics showed
connection-bound rejections and established proxy socket counts 7/8, without
recording peer/device identities or request data. Only app one was then stopped:
its SDK/network/proxy were absent, while app two's generation, expiry, input/unit
identity and original HTTPS/Funnel baseline were unchanged. App-two private manifest
probes failed. The owner confirms both native reloads failed with “Failed to download
remote update.” App one's failure is expected; app two's failure means this physical
isolation check fails and is not accepted as other-app availability.

A capacity correction keeps eight total active slots, limits forwarded native
requests to seven and reserves a slot for fixed health/diagnostic work. Under
pressure it reclaims only proxy-owned incomplete-header connections older than one
second, before any SDK request is forwarded, and rechecks the shared bound after
cancellation. Complete requests are preserved. Diagnostics expose bounded aggregate
capacity counts only. Twenty-eight proxy tests pass, including native saturation,
idle-header reclamation, resource bounds and privacy; 51 controller and 22 protocol
cases pass. This fix is prepared, not yet counted as installed/native acceptance.

All four CI workflows pass at prior documentation head e67ce44: dashboard
38639886338, private applications 38639886322, development host 38639886301 and
federation 38639886350. Protected infrastructure actions were skipped. The capacity
fix needs new-head CI, installed verification and repeated device isolation/recovery.


## WebSocket reservation installed; device retry pending (October 14)

At implementation head `22a458b`, the proxy retains eight total connections,
reserves one for control requests and limits WebSockets to four within seven
forwarded native slots. The regression holds four upgraded WebSockets while the
current manifest and health requests succeed; all 29 proxy cases pass. Its first
run exposed a missing test-server behavior, corrected before installation; that
failed run is not counted as success.

Immutable provider `960457be4f02e2aef1bc604009a8e79a901557ba751ce3445345601a7943d96b`
was selected through the reviewed provider path. Both fresh one-hour sessions
serve 6,441,558-byte Android bundles through the private HTTP listeners. A real
private app-one check held four upgraded WebSockets open concurrently: its current
Android manifest and diagnostics returned 200, with active=5, native=4,
websockets=4 and limit=8. All four test connections were closed afterward. This
proves the installed capacity reservation; it does not prove the phone failure
is resolved.

Fresh app-one generation `06f4d67221ff4d26bf2d14d12b433d35` expires at
7:32 p.m. Eastern; app-two generation `00b5662918864f26829652ccb881412e`
expires at 7:34 p.m. Eastern on October 14. Both locally rendered QR PNGs were
independently decoded to their complete current launch payloads. Source checkouts
and the original HTTPS/Funnel baseline remain unchanged. Phone scan/reload,
repeated isolation/recovery, owned listener removal and final CI/review/delivery
remain pending; neither feature is marked Delivered.


## Owner confirms fresh native loading after capacity correction

On October 14 at approximately 6:42 p.m. Eastern, the project owner confirms
“Both apps work again” for the exact app-one generation
`06f4d67221ff4d26bf2d14d12b433d35` and app-two generation
`00b5662918864f26829652ccb881412e`. This accepts native loading/operation
with the revised installed proxy on the selected Android matrix. Aggregate
transport observations independently show additional successful manifest and
bundle responses for both sessions, with unchanged generations/expiry and no
stale-launch, foreign-origin or credential-header rejection. Bounded connection
rejections still occur; successful loading is not evidence that every reconnect
request succeeds.

The owner's statement does not separately confirm Expo Go Reload, stop/isolation,
crash or expiry recovery. Those checks remain pending and the earlier failed
isolation result remains recorded. No completion, merge or Delivered claim follows
from this loading confirmation.


## Owner responds to the corrected-session Reload check

At approximately 6:47 p.m. Eastern on October 14, the project owner responds to
the explicit request to use Expo Go Reload in each current app: “Both apps still
appear to work.” This is the owner's reported Reload result for generations
`06f4d67221ff4d26bf2d14d12b433d35` and
`00b5662918864f26829652ccb881412e`; it does not independently report a
specific counter value or establish stop/isolation, crash or expiry recovery.
The app-one-only stop check proceeds separately, with app two's existing
session retained.


The repeated app-one-only stop completed at 6:47 p.m. Eastern with phase stopped,
operation_result passed and the owned SDK, network and both loopback listeners
absent. App two retains generation `00b5662918864f26829652ccb881412e`,
expiry, input digest and unit digest; its transport remains available and three
private Android manifest probes pass. The original HTTPS/Funnel baseline is
preserved. This is host evidence only; the corresponding device isolation result
remains pending.


## Owner confirms stopped-project isolation after the correction

On October 14 at approximately 6:50 p.m. Eastern, in response to the explicit
Reload check for stopped app one and unchanged app two, the project owner reports:
“Ok app one no longer works, app two still does.” This accepts the intended
physical isolation result: stopped generation
`06f4d67221ff4d26bf2d14d12b433d35` is unavailable, while running generation
`00b5662918864f26829652ccb881412e` remains usable. No additional counter
value or interaction detail is inferred. This successful repeat supersedes the
current isolation failure state without erasing the earlier failures.
A new app-one-only finite restart/reconnect and subsequent expiry check remain;
app two's existing session and expiry are retained.


App one was restarted separately into generation
`8989c4bc00f749c6b3712439415aae76`, with a 15-minute lifetime expiring at
7:06 p.m. Eastern. Its private Android manifest and 6,441,558-byte bundle pass;
the former generation entry returns 503. App two retains its existing generation,
expiry, input/unit digests and available private transport. Existing HTTPS/Funnel
handlers remain unchanged. The new physical reconnect and expiry checks are
pending; host payload rejection alone is not native evidence.


## Owner confirms intended-session restart; bounded crash check started

At approximately 6:57 p.m. Eastern on October 14 the project owner reports:
“App one ready for recovery - I opened it and it worked again.” This accepts
native reconnection to restarted app-one generation
`8989c4bc00f749c6b3712439415aae76`; it does not infer a counter value.
The owner leaves the app open for the previously described bounded recovery check.

After rechecking exact receipt/generation, active unit-file ownership, admission,
clean source and exact SDK container ownership, one synthetic SDK crash was
injected on app one only. Automatic recovery and the corresponding physical
Reload result remain pending; app two is not stopped or restarted.


The same owned app-one generation recovered automatically after exactly one
unit restart. At 6:58 p.m. Eastern its private Android manifest returned 200 and
the warm 6,441,558-byte bundle matched the pre-crash bundle digest. The generation
and 7:06 p.m. expiry were unchanged; app two's generation/expiry/input/unit digests
and available private transport were preserved. Existing HTTPS/Funnel handlers
remain unchanged. This is actual installed recovery evidence; the owner's
post-crash native Reload and subsequent physical expiry results remain pending.


## Owner confirms post-crash native recovery

In response to the explicit request to Reload both current apps after app one's
synthetic SDK crash, the project owner reports: “App one and two both work.”
This accepts native recovery using app one's unchanged generation/link and
continued app-two usability. No detailed counter value is inferred. The separate
after-7:07 p.m. Eastern expiry check remains pending; no renewal or restart extends
the fixed 7:06 p.m. app-one deadline.


All four CI workflows pass at `4ceb99b0916b674a9a2c5241ccedfd7c17213aa8`:
[dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38650749393),
[private applications](https://github.com/danielbardsley/gptclaw/actions/runs/38650749488),
[development host](https://github.com/danielbardsley/gptclaw/actions/runs/38650749490)
and [federation](https://github.com/danielbardsley/gptclaw/actions/runs/38650749404).
This is the revised proxy plus the earlier isolation/restart evidence head; pending
new evidence edits still require their final published-head checks. CI does not
substitute for physical expiry or operator removal.


## Fixed app-one expiry verified on the host

At 7:06 p.m. Eastern, generation `8989c4bc00f749c6b3712439415aae76`
expired automatically with operation_result passed. The SDK, audit container,
network and both loopback listeners are absent. Transport/launch availability
is withdrawn; source and the actual installed CLI launcher refuse the expired
generation with matching category `mobile-unsupported`. App two retains its
original generation/expiry/input/unit identity and its private Android manifest
returns 200; both source checkouts and original HTTPS/Funnel handlers remain
unchanged. No renewal, manual stop or source deletion produced this expiry.

The long-lived read-only waiting observer exited with SIGTERM/143 before returning
a result; it is not counted as success. A bounded read-only reconciliation of the
same generation independently verified the terminal state and resource absence.
The first PATH-based CLI check could not find a command; the installed store
launcher was resolved and checked separately. Neither interrupted attempt is
reported as passing. Physical expiry confirmation remains pending.


## Owner confirms app-one physical expiry

In response to the after-expiry phone check, the project owner reports:
“App one no longer works after expiration.” This accepts native unavailability
for expired generation `8989c4bc00f749c6b3712439415aae76`. No particular
error message is inferred. The owner has not separately reported app two's
post-expiry Reload result; that final physical isolation item remains pending.
A current independent host probe verifies app two still serves its private
Android manifest with its original generation and 7:34 p.m. Eastern expiry;
original HTTPS/Funnel handlers are preserved. The host result does not substitute
for the remaining phone report.


## Owner confirms final physical expiry isolation

The project owner separately reports “App two still works” after the prior
“App one no longer works after expiration.” Together these accept the final
physical expiry isolation: expired app-one generation
`8989c4bc00f749c6b3712439415aae76` is unavailable while unchanged app-two
generation `00b5662918864f26829652ccb881412e` remains usable. No specific
counter value or error wording is inferred. The selected Android 11 / Go 57.0.9
physical load/edit/reload/network/compile/stop/restart/crash/expiry matrix now passes.
iOS remains unsupported/follow-up, as selected by the owner.

Owned temporary runtime/listener cleanup, final published-head CI, owner delivery
acceptance and review/authorized merge remain separate gates. Neither feature is
marked Delivered before those gates complete.


## Owned temporary runtimes cleaned up before operator removal

After completed physical expiry isolation, the owner provider stopped only app-two
generation `00b5662918864f26829652ccb881412e`, with stopped/passed outcome.
App one retains its expired generation/state and original expiry evidence. Both
SDK/audit containers, networks and loopback listeners are absent. Source checkouts,
metadata/history and exact HTTP Serve handlers are retained; no source or data was
deleted. App-two listener removal is requested through the reviewed SSM operator
path; execution/readback remains pending. Forge performs no Tailscale mutation.
