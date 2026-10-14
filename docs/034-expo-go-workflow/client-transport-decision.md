# SDK-57 native transport decision

- **Status:** Private-HTTP Metro amendment approved by the project owner; implementation/operator execution pending
- **Owner:** Project owner
- **Observed:** October 14, 2026 UTC
- **Scope:** Retained mob001-accept-one and mob001-accept-two development fixtures
- **Plans:** [SPEC-033](../033-private-metro-sessions/spec.md) · [SPEC-034](spec.md)

## Concrete failure

On Android 11 / Expo Go 57.0.9, the corrected generation-bound launch path reaches
and accepts the private HTTPS manifest. The owner then sees “Packager is not
running” at `http://forge-dev-01-4.tail8c3304.ts.net:8443`. The native attempt added
one successful manifest and no bundle/status request to the proxy. Independently,
the actual HTTPS `/status` endpoint returns HTTP 200 and exactly
`packager-status:running`; the manifest advertises an HTTPS launch asset on 8443.
The owned Metro process remains healthy. This is a client transport mismatch,
not a stopped packager or a failed source bundle.

The current official [SDK-57 Android source](https://github.com/expo/expo/blob/0607af7a70d0ea3e58a6d55824aac5cfd3e78613/apps/expo-go/android/expoview/src/main/java/host/exp/expoview/Exponent.kt#L286)
constructs `http://$debuggerHost/status` unconditionally in development mode.
The [upstream origin fix](https://github.com/expo/expo/pull/48275), merged into
main on August 6, preserves the bundle origin/scheme, but is absent from that SDK-57
branch. Main-source behavior is not proof of a shipped SDK-57 client fix.
The [official download page](https://expo.dev/go) still lists SDK 57 as latest;
no compatible client replacement has been verified. Updating project JavaScript
or warming the bundle cannot change the installed client's native probe.

Read-only Go inspection now reports this exact Android client unsupported under
the currently approved HTTPS profile. No launch certification is recorded.

## Proposed ways forward

| Choice | Concrete outcome | Scope requiring approval |
|---|---|---|
| **Keep Expo Go using private HTTP over Tailscale (recommended for this Go milestone)** | Deliver Metro's native development protocol over HTTP inside the authenticated, encrypted development tailnet. Keep project source/SDK/client and the existing dashboard/web/API TLS routes. | Amend MET-003 and the Go transport profile; replace only the two owned Metro HTTPS listeners with private HTTP listeners on the same 8443/8444 ports through the SSM operator. |
| Keep HTTPS and plan MOB-004 | Use the project's own development client with verified native TLS/bundle/reload support. This also supports future native modules outside Go. | A separate development-build specification and review of compilation, exact dependencies, artifact/signing custody and any required account/toolchain acquisition. This document does not authorize building or installing it. |
| Keep the present boundary pending a verified upstream client | Continue independent platform implementation with Go launch unavailable and physical criteria pending. | No transport or build scope change. A future compatible client/SDK change still needs exact compatibility/security review; no automatic upgrade. |

## Exact scope of the recommended choice

Only the two already owned Metro listeners change:

| Listener | Current | Proposed |
|---|---|---|
| TCP 8443 | Private HTTPS → 127.0.0.1:18601 | Private HTTP → the same owned loopback proxy |
| TCP 8444 | Private HTTPS → 127.0.0.1:18603 | Private HTTP → the same owned loopback proxy |

Traffic remains within the existing encrypted Tailscale network; application-layer
TLS is removed for these development Metro listeners. All devices on this tailnet
remain permitted under the owner's accepted policy. This is an explicit change to
SPEC-033's “tailnet-only TLS access” requirement, not a TLS-certificate bypass.
Port 443 `/dashboard/` and `/projects/`, app/API/database routing, Funnel-off state,
AWS, production, SDK/native source, account/signing and dependency exceptions are
unchanged. There is no public tunnel, LAN binding or new port allocation.

After scope approval, implement and test the versioned transport/profile and exact
operator replacement/rollback plan before asking the existing SSM operator to run
it. Validate the recorded current handlers and owned backends first; stop/reconcile
only the selected owned sessions during conversion. Forge gains no administration
rights and runs no privileged command. No Serve reset or unowned handler replacement.
Preserve session-generation entry checks, fixed Host/origin validation, credential
exclusion, streaming/resource bounds, fresh security admission and finite expiry.
Old providers must reject any transport they do not understand. No automatic renewal.

Verify actual native status/bundle/assets/reload channels on both fixtures, restored
Fast Refresh edits, session isolation, network/reconnect/expiry and installed provider
parity; repeat the applicable privacy/ownership/legacy tests. The owner accepts the
actual supported platform matrix. iOS's current login/acquisition limitation and
unavailable physical device remain separate; this choice does not waive them.

Rollback uses the capable owner interface to stop/reconcile only these sessions,
then the operator restores only their HTTPS listeners and the compatible HTTPS
provider/profile. Preserve source/receipts and every unrelated handler/data store.
HTTP Go links become unavailable after rollback; do not claim older clients work.

## Decision needed

Choose the exact private-HTTP Go amendment, a separately specified MOB-004 client
path, or retention of the present HTTPS boundary. No dependent conversion, native
build, account setup or SDK upgrade occurs before that scope is selected.


## Approved decision and HTTPS restoration follow-up

On October 14, the project owner explicitly approved private HTTP over the encrypted
development tailnet for only Metro listeners 8443/8444, preserving HTTPS on the
dashboard/project routes. Implement and verify the operator plan before execution;
this approval includes the exact conversion scope above, not an SDK upgrade or
a native client build. Physical acceptance is still required.

**Follow-up owner: project owner / platform maintainer.** Revisit this temporary
compatibility transport when an official Go release includes the upstream scheme/
origin fix. Expo's [SDK-58 beta notes](https://expo.dev/changelog/sdk-58-beta) list
proxy/tunnel origin handling improvements and state that store Go moves to SDK 58
after its stable release, dropping SDK-57 support. Do not assume a Go app update
alone makes the retained SDK-57 projects compatible.

Restore HTTPS when a shipped client compatible with the approved project SDK
passes real native manifest, HTTPS packager-status, large bundle, assets, sustained
WebSocket/Fast Refresh and reload checks. If the client only supports SDK 58, first
review a new pinned starter/lock/security/client matrix and source migration; this
HTTP amendment does not authorize it. Record exact client/OS/SDK versions and
separate platform evidence. Then use the reviewed owner-controller/operator path
to stop/reconcile only the two owned sessions, remove only their HTTP listeners,
restore HTTPS on 8443/8444, verify preserved port-443 handlers/Funnel-off state, and
update the versioned transport/profile and remove the HTTP compatibility path.
Old HTTP launch payloads must become unavailable; retain source and receipts.

This is a recorded release-triggered follow-up, not an automatic upgrade, policy
change, scheduled monitor or claim that a particular release date is confirmed.
