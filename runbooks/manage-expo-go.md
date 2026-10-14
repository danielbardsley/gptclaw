# Open a managed mobile project in Expo Go

The combined provider and Go dashboard are installed; final owner acceptance and
merge are tracked in [SPEC-034 acceptance](../docs/034-expo-go-workflow/acceptance.md).
Use a capable provider whose `--version` reports `expo_go_launch_schemas: [1]` and
`metro_session_schemas: [1,2]`. A missing capability makes launch unavailable.

The verified client matrix is Android 11 / Expo Go 57.0.9 / the exact SDK-57
starter, using private HTTP over authenticated, encrypted Tailscale. The owner
confirmed both starter projects, native interaction, Fast Refresh, full reload
and network/compile recovery. Compatibility expires after seven days and earlier
on relevant source/client/config/transport drift. Check your phone’s installed
version: the host does not detect it. iOS is uncertified and its current CLI-login
prerequisite is outside this credential-free scope; MOB-004 is a separate workflow.

Inspect compatibility without starting or renewing Metro:

```sh
gptclawctl go inspect --project-root /absolute/canonical/project --platform android --client-version 57.0.9 --os-version 11
```

Obtain the current generation from `gptclawctl status --project-root ...`. A Ready
private Metro session and an eligible client profile are separate prerequisites.
The [Metro runbook](manage-metro.md) owns session and operator route operations.
Launch inspection does not create either prerequisite.

```sh
gptclawctl go launch --project-root /absolute/canonical/project --platform android --client-version 57.0.9 --os-version 11 --generation CURRENT_GENERATION
```

The result contains the exact `exp://.../_gptclaw/metro-session/GEN` launch URI
and its finite expiry. Open it in Expo Go or copy it into Enter URL. On the private
dashboard, a compatible current mobile row offers Open in Expo Go (Android);
its details offer Copy Expo Go URL and a locally rendered QR. With Tailscale
connected, scan it in Expo Go. No external QR service, Expo login or phone/device
telemetry is used. The nonce is a generation guard, not an access credential.

Stopped/expired/stale/unready sessions and expired/unsupported compatibility have
no available launch action. A saved old link cannot open a replacement generation
or a different project. After an explicit restart/renewal, obtain the new current
link; a copied old QR remains invalid. Disconnecting Tailscale prevents packager
access; rejoin the same development tailnet and reload the intended current app.
Compile errors remain visible in Go; restore the source and reload. Fast Refresh
may retain local component state; full reload resets the starter counter.

Rollback selects an immutable HTTP-capable provider/collector without Go launch
schema support, withdrawing launch actions while retaining owned Metro and source.
Do not select an older HTTPS-only provider over active schema-2 sessions. Session
stop/recovery remains the Metro owner interface. Preserve existing web/API/DB
services, port-443 HTTPS handlers and all source/data.

The project owner requested restoration of HTTPS when a compatible official Go
release ships. Follow the [recorded restoration gate](../docs/034-expo-go-workflow/client-transport-decision.md#approved-decision-and-https-restoration-follow-up):
verify shipped client/SDK compatibility and native HTTPS status/bundle/assets/reload,
then use the reviewed two-port operator conversion. SDK-58 Go drops SDK-57 support;
a store update alone does not authorize source migration or automatic conversion.
