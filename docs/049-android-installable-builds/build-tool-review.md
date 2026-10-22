# Fieldnotes Android build-tool review — October 21, 2026

Owner: Project owner. Status: temporary native-build exception approved October 22
for the exact scope and unchanged October 28 expiry below. [Specification](spec.md) · [Tasks](tasks.md)

## Observed preparation

The owner selected Fieldnotes, Expo account `bardsley`, Expo-managed Android keys
and free-only setup/builds. No paid upgrade/overage is authorized. No source upload,
key creation, remote native build or installation has been performed. The host had
no existing Expo session; a device-authorization request was started with protected
local state. Browser authorization remains pending. No passwords/tokens were read
or placed in evidence.

[Fieldnotes PR #2](https://github.com/danielbardsley/fieldnotes-mobile/pull/2) contains
static variant/public API validation, exact expo-dev-client 57.0.20, committed-source
upload preparation, isolation tests and an operating guide. Commits `5083cd4` and
`e06625d` are source preparation only. Canonical source/runtime/data are unchanged.

Executed local checks: frozen scripts-disabled dependency install; formatting,
lint, typecheck; nine native Jest tests; seven Node configuration/contract/security
tests; iOS and Android JavaScript/assets export; eight separate variant/upload
isolation tests using pinned Node with host Git; diff and documentation links.
All final runs passed. Initial lint failures (explicit Node globals) and the first
Git-dependent test attempt in the Git-free minimal container were corrected before
these passing runs. No signed native binary or iOS device acceptance is claimed.

The scoped GitHub App denied the proposed Actions workflow edit. Only this task's
workflow change was removed; the remaining branch published successfully without
permission changes. Snapshot tests ran locally and are not in hosted CI; the
existing source workflow still runs its configuration tests. CI results are separate.

## Exact tool inputs and audit

EAS CLI 25.3.0 was installed in task-owned temporary storage from public npm metadata,
using the existing rootless Node 24.21.0 / pnpm 12.10.1 image. No host packages or
privileged tools were installed. SDK 57.0.28's bundled metadata declares
expo-dev-client ~57.0.20; Fieldnotes pins 57.0.20 with frozen lockfile inputs.

Compatible EAS transitive overrides were applied for joi 17.13.8, minimatch 5.1.9,
nanoid 3.3.20 and tar 7.5.22. The patched CLI starts and reports 25.3.0. Its exact
retained package-lock SHA-256 is
`08e4b5b107da32b518212323717acf2e28be24e456a53b8ca95d65281a76dec7`.
This is task-owned tooling provenance, not a delivered general tool installer.

The initial EAS npm audit reported 15 high, 16 moderate, one low and zero critical
package findings. After compatible patches it reports 11 high, 15 moderate, one low
and zero critical. The remaining high dependency chains have two distinct direct
causes: braces 3.0.3 and node-forge 1.4.0. Public npm latest metadata returned those
same versions; no patched version was available for either at this check.

Fieldnotes' source security gate passes using its existing two exceptions, whose
scope is `source-check-and-export`, expiring 2026-10-28T04:00:00Z. The node-forge
reason explicitly says “No signing or release verification in this source-only
adapter.” That earlier exception does not approve this new signing workflow.

## Temporary exception — owner approved October 22

| Field | Proposed disposition |
|---|---|
| Owner | Project owner |
| Exact scope | Only the pinned, patched EAS 25.3.0 graph and reviewed Fieldnotes Android development/preview snapshots, under `bardsley`, within verified free allowance. |
| Findings | [node-forge GHSA-86w9-cpqp-85rv](https://github.com/advisories/GHSA-86w9-cpqp-85rv), affecting RSA signature verification; [braces GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm), affecting deeply nested pattern processing. |
| Reason | No patched package version was available; begin the selected private Android install trial with Expo-managed remote keys. This is a risk acceptance proposal, not a vulnerability fix. |
| Limits | Rootless bounded process, reviewed committed source/known patterns, authenticated artifact access, one job at a time, no iOS/local-keystore import/export, no OTA/store/production operation. These constraints do not prove affected code unreachable. |
| Expiry | 2026-10-28T04:00:00Z (October 28, midnight America/New_York). |
| Removal | Owner/operator stops new signed builds at expiry; author replaces affected dependencies when patched, regenerates the frozen graph, re-audits and verifies the build/install path before removing the exception. No automatic renewal. |

The project owner instructed: “Approve the temporary exception and continue with
the free Fieldnotes build” on October 22. This explicitly approves only the
listed Fieldnotes Android scope, limits, expiry and removal step. It does not
change the original source-only exception or authorize paid usage. Record this
review with the external-job evidence; no new security suppression is installed. Device sign-in, exact Expo project/free-quota/artifact
access/key custody checks, job submission/recovery and actual install evidence
remain separate gates. Prior source-only exceptions and acceptance waivers stay
unchanged.


## October 22 continuation

The owner reports signing in to Expo and authorizes continuation with the free
Fieldnotes build. Verify the host CLI session separately: browser sign-in alone
is not evidence that the device grant has completed. The original October 21
preparation observations remain historical. External build results will be
recorded separately after project/access/quota checks and source inspection.

## First external job — October 22

The host device grant completed as `bardsley`; the owner then explicitly resumed
free-only build submission after clarifying that device authorization happens on
the Expo website. A fresh usage query reported account plan Free, Android 0/15 and
total 0/30 used. This task enforces one active build despite any account-wide
concurrency entitlements. No paid plan, upgrade or overage was selected.

Created EAS project `aa3e7457-b41f-449b-9f66-ea95139c74e3`,
[`@bardsley/fieldnotes-mobile`](https://expo.dev/accounts/bardsley/projects/fieldnotes-mobile).
Set only its internal distribution privacy to PRIVATE, then independently read
that value back. Authenticated-download behavior still needs artifact acceptance.
The development environment had no Plain text or Sensitive EAS variables; only
explicit EXPO_NO_DOTENV and EXPO_NO_TELEMETRY profile inputs were loaded.

Signing custody: the project owner controls `bardsley`; Expo generates/stores the
Android keystore remotely. No local key export/backup file is created for this
private trial. Retain the remote key for same-identity replacement; rotation/export
is a separate owner-directed procedure, never automatic on rebuild. Artifact
retention will be recorded from the actual job expiration metadata. Android 11 is
the existing accepted device baseline; installation observations remain separate.

The installed provider validated the canonical Fieldnotes backend binding without
starting or modifying the backend. Snapshot preparation used mobile source
`e06625deb1a0624469cbd71db7d93c740f0f3b02`; development snapshot commit
`8ecf61d5004ff14c2e5086e4bc4434862840335f` and config digest
`f6751e3a2de80687c599632108ad9973c88ccf68dc181aca9c264f9cb129d7f0`.
EAS archive inspection matched all 31 input-file hashes. EAS also generates its own
shallow Git metadata: one snapshot commit, only the reviewed input tree, a local
file:// origin, sample-only hooks and no symlinks. The product repository's history,
authentication files, backend/database state and dependency cache are not uploaded.

The first offline snapshot install lacked registry policy metadata and refused;
a network-enabled, frozen, scripts-disabled container install then passed its
supply-chain checks, reusing all 1,037 cached packages without tarball downloads.
No admission rule was disabled.

A fresh quota/privacy/no-active-jobs check preceded the persisted submission intent
`43f8b362-9d57-43ca-86e9-840437c008c2`. Expo generated the development keystore in
the cloud, accepted the 291 KB source archive and queued
[development job d89b3748](https://expo.dev/accounts/bardsley/projects/fieldnotes-mobile/builds/d89b3748-fce7-4406-b51e-b9496e367d51).
Its initial observed status was NEW. This is a submitted job, not a successful
binary or physical install. Job metadata is retained outside source for resumption;
unknown outcomes must be reconciled by the saved intent/job ID before retrying.

## Install-stage failure and verified correction — October 22

The first development job spent about 20 minutes in queue, then failed in the
Install dependencies phase with ERR_PNPM_IGNORED_BUILDS. Its frozen install and
package-age/supply-chain checks had passed; pnpm then refused unrecorded skipped
hooks for @parcel/watcher 2.6.0 and unrs-resolver 1.12.2. Initial source checks
used --ignore-scripts and did not reproduce EAS's normal frozen install behavior.
The uploader also omitted the committed workspace policy (which originally only
specified the root package and minimumReleaseAge 1440).

Fieldnotes commit `2cb3e0a8ea36d864799f0e1e0802ae5c4257d861` retains that package-age
rule, explicitly sets allowBuilds false for those two packages and requires the
exact workspace policy in uploads. No script is enabled, no version is changed
and no strict admission rule is disabled. Fourteen local configuration/job/upload
refusal tests plus lint passed. A fresh rootless `pnpm install --frozen-lockfile`
without --ignore-scripts passed with the corrected policy, reusing all 1,037 cached
packages. Android `expo prebuild --platform android --no-install` also passed in a
separate disposable source copy; no Android SDK/JDK was installed and no local
native compilation is claimed.

Both corrected EAS archives match 34 reviewed files and isolated Git provenance.
The development snapshot is `a1a11e8a1e398228ac16ed0e4b4b865dc7e089f2`; preview is
`c6aa8fbc22820dd9bb56e199af8bc344f5191ed6`. The original failed job and source
snapshots remain preserved; only their obsolete task-owned dependency copies were
removed to reclaim root-disk headroom. The fresh install-check dependency copy was
also removed after native generation completed. No user project data was deleted.

The first job was independently reconciled to ERRORED before retrying. Fresh
account checks still reported Free and all 15 Android builds available, so this
install-stage failure did not reduce the observed allowance. A new persisted
intent `21e3f300-98f1-4749-91c9-556ddd1a1853` submitted
[corrected development job c789df30](https://expo.dev/accounts/bardsley/projects/fieldnotes-mobile/builds/c789df30-82ca-4849-ad8d-e1a2f1b4ebe5).
It reused the existing remote keystore, uploaded 298 KB and entered IN_QUEUE.
No duplicate retry, paid usage or second simultaneous job was submitted. The
corrected preview is inspected but remains unsubmitted until development is terminal.
