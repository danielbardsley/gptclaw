# Android development builds

[SPEC-049](../docs/049-mobile-development-builds/spec.md) introduces provider 1.18.0,
manifest 11/12, catalogue 9 and an opt-in SDK-57 development profile. Source
implementation, installed provider, cloud jobs and device acceptance have separate
evidence. Check `gptclawctl --version`; this runbook does not install a provider.
Existing `build` remains unsigned JavaScript/assets. EAS submission is explicit.

## Prepare source and account scope

Choose `expo-development@1.0.0` for standalone native storage checks or
`expo-development-notes@1.0.0` for synthetic notes bound to an independently
managed Python backend. New projects use a distinct `.development` Android package
and `-dev` scheme. Published Go starters and existing source are not migrated.
The new native module is MMKV 4.3.2 with Nitro Modules 0.35.2; generated-native
ownership is required. Handwritten `android/` and `ios/` are refused.

Use the existing private-repository creation flow and canonical project contract;
local-only source creation is supported, but managed build/session execution needs
canonical repository binding. Review account/project ownership and the token's
actual privileges. The owner selected reuse of the previous account, Expo-managed
signing and 30-day retention. Resolve the actual account/project and signing
certificate fingerprint before configuring a project. No account discovery reads
authentication files. Obtain the public signing certificate fingerprint through
the selected owner's credential-management path; do not export private keys here.
Record recovery/rotation ownership with the Expo-managed development key.

Build configuration is bounded static public JSON at
`.gptclaw/development-build.json`. Required fields are defined in
[native_contract.py](../scripts/native_contract.py). Supply platform `android`,
environment `development`, account/project UUID, signing `expo-managed`, SHA-256
signing certificate fingerprint, retention 30 days, access `authenticated`, integer
attempt limit, total budget and per-attempt cost ceiling in cents, credential scope
(`isolated-account` or explicitly `owner-accepted-account-access`), approval ID and
UTC expiry. These are approval metadata, never secrets. A zero-cent budget permits
only explicitly approved free attempts. A paid ceiling must include potential
subscription costs, taxes and other account usage in the owner's billing decision.
The local attempt ledger reserves the selected per-attempt ceiling across all
projects using the same account and approval ID. Budget terms are fixed for that
approval; changed terms require a new recorded approval ID. Failed attempts retain
their reservation. This is not an Expo billing cap or an estimate/guarantee of
service charges. Stop when remaining
quota/cost cannot be established. Do not enable billing from a source plan.

The credential file is separate, mode 0600, owned by forge, outside project roots.
Only the fixed submission/observation container receives it. Do not put token
values into command arguments, source, public logs or acceptance evidence.
Account/project environment variables must be absent for this initial lane;
the pinned worker checks project and account-shared `development` variables and
fails closed without printing their values. Review EAS access settings separately:
an artifact URL is not private merely because the API uses Tailscale.

Configure only source, inspect the plan digest, then explicitly apply it:

```sh
gptclawctl native-build configure --project-root /absolute/canonical/mobile --config-file /absolute/public-approval.json
gptclawctl native-build configure --project-root /absolute/canonical/mobile --config-file /absolute/public-approval.json --apply --confirm-plan DIGEST
```

A journal retains previous/proposed app configuration. Interrupted configuration
fails validation; review the journal and preserve independent edits before a
source PR corrects it. This operation creates no Expo account/key/job/listener.
For the notes variant use `backend bind` from
[the backend runbook](manage-mobile-backends.md), then commit the reviewed public
configuration/generated types. Backend local state and credentials are excluded
from uploads. Generated types are included. EAS compilation needs no tailnet API
access; only the installed client uses the private API.

## Check and submit

Run managed frozen dependency installation and source quality first. Prepare the
native tools in rootless containers; this downloads the frozen EAS CLI lock and
Google apksig library, without Expo credentials or host package installs:

```sh
gptclawctl deps install --project-root /absolute/canonical/mobile
gptclawctl verify --project-root /absolute/canonical/mobile
gptclawctl native-build prepare-toolchain --project-root /absolute/canonical/mobile
gptclawctl native-build plan --project-root /absolute/canonical/mobile
```

The plan requires clean committed source, validates static app/EAS configuration,
refuses source hooks/dynamic config/symlinks/credential canaries and computes a
portable deterministic upload archive. Source/lock/config/native digests are bound
to the plan. The pinned EAS wrapper uploads these exact archive bytes, replacing
its archive creator; it cannot silently include a wider checkout or backend files.
Server-managed compiler image updates mean byte-for-byte binary reproducibility
is not claimed, even with the selected named SDK-57 image and exact Node/pnpm pins.

Submit only after external scope, credential privileges, artifact access and cost
are verified, with no high/critical source or EAS tooling audit findings. The old
Go/source advisory exceptions confer no native signing permission. The October 23
pinned EAS audit has unresolved high findings: see
[the security disposition](../docs/049-mobile-development-builds/security-review.md).
Do not bypass the gate to obtain a binary.

```sh
gptclawctl native-build submit --project-root /absolute/canonical/mobile --confirm-plan DIGEST --credential-file /absolute/private/expo-token
```

Persisted intent precedes the request. One project has at most one unresolved job;
a global submission lock serializes submission requests. Jobs record source,
approval, configuration/archive/native digests and safe remote identities. No
automatic submission, account creation, retry, store upload or update follows.

## Observe and recover

```sh
gptclawctl native-build status --project-root /absolute/canonical/mobile --operation-id OPERATION
gptclawctl native-build status --project-root /absolute/canonical/mobile --operation-id OPERATION --credential-file /absolute/private/expo-token
gptclawctl native-build reconcile --project-root /absolute/canonical/mobile --operation-id OPERATION --job-id JOB_UUID --credential-file /absolute/private/expo-token
```

Local status reads receipts without credentials/network. Remote observation checks
account/project/package/profile/operation message; failure preserves the last
verified state and timestamp. `unknown` blocks another submit. Reconcile the exact
job in the authorized account, never the latest arbitrary job. If the operator
independently proves no remote job was submitted, explicit
`resolve-not-submitted --confirmation OPERATION:PLAN_DIGEST` records that attestation
without refunding the attempt reservation. A false attestation can duplicate jobs;
retain the remote-account readback evidence. To request cancellation of an exact
owned job use `cancel --operation-id OPERATION --confirm-job JOB_UUID` with the
project root and credential file. Poll afterward: cancellation acknowledgement
alone is not finality, a refund or absence of an already created artifact.

## Retrieve, install and launch

```sh
gptclawctl native-build fetch-artifact --project-root /absolute/canonical/mobile --operation-id OPERATION --credential-file /absolute/private/expo-token
```

The adapter revalidates the succeeded remote job, downloads through validated EAS
artifact destinations/redirects with size/deadline bounds, and binds downloaded
bytes to that receipt. Google's pinned apksig verifier checks v2/v3 signatures in
a network-isolated container; a bounded signed manifest parser checks the Android
package. The certificate must match the selected custody record. Unsigned,
foreign-package/certificate or unrelated-job APKs cannot become install eligible.
No signed URL is persisted or printed. `verify-artifact --apk-file PATH` can recheck
only bytes already downloaded and associated with this exact job.

Use the owner's authenticated artifact/transfer path to install the verified APK
on the selected device. Do not uninstall or overwrite another package. Record the
exact installed artifact separately; no device telemetry is inferred:

```sh
gptclawctl native-build installed --project-root /absolute/canonical/mobile --operation-id OPERATION --artifact-sha256 APK_DIGEST --device-os 'Android 11'
gptclawctl native-build launch --project-root /absolute/canonical/mobile --operation-id OPERATION --generation METRO_GENERATION
```

Start Metro separately through its existing owned lifecycle after native-specific
security admission and exact private operator routing. Development clients use
HTTPS only in this implementation; the Go HTTP exception is refused. Launch is
read-only, generation/expiry/fingerprint checked and project-scheme bound. JS
edits reload; native package/plugin/config/SDK/lock changes require a matching
replacement binary and installation report. A development binary does not provide
a standalone preview with Metro stopped. Keep backend health, Metro, remote job,
installation and owner acceptance distinct.

## Retention and rollback

Artifact eligibility expires after the approved maximum 30 days. External EAS
retention/access and local artifact deletion require owner/operator follow-through;
this implementation does not silently delete remote artifacts or signing keys or
schedule a retention automation. Retain private job/budget receipts for recovery.
Clean only known task-owned upload staging after no active/unknown job remains;
verify hashes before removal and preserve any independent/unknown files. Keep
source, synthetic records, signing custody and all unrelated projects/data.

Before provider rollback reconcile in-flight jobs with a capable observer. Block
new submissions; revert source/profile changes through reviewed PRs. Do not
reinterpret newer receipts in an older provider, reverse database schema, delete
keys or assume uninstall revokes a binary. Stop only owned trial Metro/backend
sessions; exact temporary listener removal uses the reviewed operator path with
independent preserved-handler readback. Physical Android loop, module, outage,
replacement-build and backend persistence acceptance remain required.
