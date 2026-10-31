# Private Android emulator testing

GptClaw provides a separate private Android test appliance, `forge-android-01`,
with an API 36 Google APIs x86_64 emulator and KVM acceleration. Application
source, builds, backend and data remain on their existing development host.
Availability and access must be checked; copied guidance does not allocate a
runner or authorize new infrastructure, credentials, SDK terms or billing.

## Arrange access and a test session

Consult the current [GptClaw runner runbook](https://github.com/danielbardsley/gptclaw/blob/main/runbooks/android-emulator-runner.md)
for platform status, recovery and protected lifecycle operations. Record the
assigned private hostname, verified SSH host key, project-approved private-key
path, pinned local ADB executable, inspected x86_64-compatible APK and package ID
in project-local development instructions. Keep keys in ignored owner-only local
storage; never copy another project's private key or commit authentication data.
If no approved key is available, arrange access with the platform owner rather
than changing authorized_keys or provisioning another runner.

This is one shared emulator, initially configured for Dogstats, without per-project
isolation or a scheduler. Agree a test slot and fixture ownership with the project
owner before use; do not overlap another session, replace its APK or reset its
AVD. Other projects need an explicit allocation and handling decision. Use only
synthetic accounts, routes and fixtures; preserve unrelated installed apps/data.

## Connect privately

On the development host, set these shell variables to the approved project-local
values; they contain paths/identifiers, never key contents. Ensure local port
15555 is free or agree a different local port and update the serial consistently.
Keep the following tunnel running in its own terminal:

```sh
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
  -o StrictHostKeyChecking=yes -i "$RUNNER_SSH_KEY" \
  -L 127.0.0.1:15555:127.0.0.1:5555 "forge@$RUNNER_HOST"
```

Do not disable host-key checks. Resolve an unknown or changed key through the
platform owner and the runbook before connecting. Both tunnel endpoints bind to
loopback; never expose ADB, emulator consoles or backend services publicly.
In another terminal, using the project's pinned platform-tools executable:

```sh
"$ADB" connect 127.0.0.1:15555
"$ADB" -s 127.0.0.1:15555 shell getprop sys.boot_completed
"$ADB" -s 127.0.0.1:15555 shell getprop ro.product.cpu.abi
```

Require boot completion `1`, the expected x86_64 ABI and the assigned emulator.
Select `-s 127.0.0.1:15555` on every subsequent device command; never use an
unqualified install, input command, uninstall or global ADB-server shutdown.

## Install, exercise and collect evidence

Inspect APK signature, hash, package/version, x86_64 support, native capability
and private endpoint configuration using the project's reviewed build/artifact
workflow. Preserve existing synthetic data; stop if installation needs an
uninstall, clear-data, downgrade, signature change or unsupported migration.
With approved APK_PATH, APP_ID and an ignored EVIDENCE_DIR already selected:

```sh
"$ADB" -s 127.0.0.1:15555 install -r "$APK_PATH"
"$ADB" -s 127.0.0.1:15555 shell monkey -p "$APP_ID" -c android.intent.category.LAUNCHER 1
"$ADB" -s 127.0.0.1:15555 exec-out screencap -p > "$EVIDENCE_DIR/screen.png"
```

Exercise actual screens with selected-device input commands or a reviewed test
runner. Confirm Android can reach this project's private API/issuer; host-side
HTTP success alone does not establish Android connectivity. APK compilation,
installation, launch, backend interaction and product acceptance are separate
results. Record artifact/source identity, commands, observed behavior and failures
against the project's acceptance criteria. Screenshots/logs must exclude tokens,
action links, personal locations and other sensitive data; avoid full log dumps.

Emulated location is synthetic. GPS accuracy, battery use, background recording,
OS/device recovery and physical accessibility qualification require their own
approved device evidence; emulator results cannot close those gates.

## Finish or handle failure

Disconnect only the selected ADB serial and close your own SSH tunnel. Preserve
the runner disk and existing fixtures on failure; no wipe, cache deletion or
replacement is part of ordinary testing. Coordinate release of the shared slot.

Runner start/stop uses GptClaw's protected GitHub Actions → HCP Terraform → AWS
plan/apply workflow on reviewed main, with android_runner_state running/stopped,
confirmation gptclaw-dev-host and existing environment gates. Inspect the plan
for only the intended runner-state/tag changes; reject host/storage/IAM/ingress
changes or replacement. Use existing authorization for that session or ask the
platform owner to operate it. Never run local apply or direct AWS mutations.

The default workflow state is stopped. A four-hour timer per boot gracefully
stops Android and the instance; allow up to 90 seconds for Android shutdown.
The encrypted disk persists and storage/network charges can remain. Coordinate
an earlier protected stop when finished; do not stop another project's session.
An unexpected disconnect may be the timer, not an app failure. Verify availability
before retrying; never loop start/replacement attempts or change host security.
