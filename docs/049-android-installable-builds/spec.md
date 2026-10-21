# SPEC-049 — Installable Android development and preview builds

- **Status:** Approved; Fieldnotes selected. Reversible build preparation may proceed; external account/signing/build operations await the concrete decisions below.
- **Owner:** Project owner
- **Date:** 2026-10-21 (America/New_York)
- **Features:** MOB-004, initial Android development/preview slices of MOB-005/006;
  supporting signing/upload custody and native acceptance slices of SEC-001/002 and MOB-011.
- [Design](technical-design.md) · [Tasks](tasks.md) · [Mobile sequence](../platform/sequence-mobile.md)

## Outcome and scope

Build and install one existing Expo application's own signed Android development
client, then a standalone internal-preview APK. The development client loads its
owned private Metro session; the preview launches with Expo Go absent and Metro
stopped, using the selected private Python API/PostgreSQL backend over Tailscale.
Repeat the build/install from recorded reviewed inputs. A signed native build is
separate from the existing quality command that validates JavaScript/assets.

The project owner reviewed and approved this specification on October 21 and
selected Fieldnotes. Proceed with reversible build preparation for the existing
Fieldnotes mobile/API projects. External build jobs, account changes, signing
setup, paid usage and runtime operations still depend on the concrete account,
custody, budget and operational scope recorded before those actions.

Reuse delivered creation/Metro/Go and the Android M1 backend slice accepted in
[SPEC-036 closeout](../036-mobile-python-backend/closeout-2026-10-21.md), including
its manual-evidence waivers and unexplained initial restore failure. Do not reopen
closed tasks or represent waived tests as passed. New binary behavior needs its
own installation evidence. Reuse the merged QLT-001–010 source contracts, retaining
their outstanding rollout/adoption evidence separately.

Include public development/preview config, app identities, bounded EAS cloud
builds, signing custody, authenticated artifact access, job provenance, installation
instructions and recovery. CLI/runbook delivery is sufficient; dashboard build
controls, a general secret registry and a general job queue are not prerequisites.
Exclude iOS, stores/TestFlight/Play submission, OTA updates, production profiles,
public APIs, new AWS infrastructure, user authentication and real-user data.
No automatic migration/adoption of existing apps or edits to published starters.

## Requirements

### AB-001 — Explicit app and profile identity

Select the exact mobile project/repository/revision, Android device matrix and
backend binding. Define distinct development/preview application IDs, labels and
launch schemes so installations can coexist. Materialize only validated public
API configuration; reject missing, mismatched or production bindings before upload.
Stopping Metro must not stop or misreport the independently hosted API/database.
Unbound mobile projects and historical schemas retain their existing behavior.

### AB-002 — Build and signing boundary

Use EAS cloud builds with an exact reviewed CLI/SDK/native dependency matrix and
frozen inputs. Before the first external operation, record the authorized Expo
account/project, key ownership/storage/backup/rotation, permitted source upload,
artifact access/retention and build budget/concurrency. Never reuse repository
credentials for EAS or place signing/server credentials in source, bundles or logs.
Inspect the upload manifest before submission; exclude runtime data, role files,
authentication files, local caches and unrelated source. Internal artifacts require
authorized Expo sign-in; obscurity of an install URL is insufficient access control.

### AB-003 — Own development client

Produce a signed Android development-client APK, install it on the declared device,
and open the owned private Metro session and API. Verify edit/reload and one selected
native-module capability unavailable in the accepted Expo Go client. A change to
native dependencies/config requires a new compatible binary; source reload cannot
claim to install native code. Preserve existing Expo Go operation.

### AB-004 — Standalone preview installation

Produce a signed internal-preview APK with bundled JavaScript/assets and no
development-client launcher dependency. With Expo Go absent and Metro stopped,
install, cold-launch, navigate and perform synthetic API CRUD. Verify relaunch and
backend restart persistence, offline/error/reconnect, uncertain-write recovery,
keyboard and accessibility behavior. Network features still require Tailscale and
a reachable backend; preview is not an offline-sync or production availability promise.

### AB-005 — Provenance, bounded jobs and recovery

Record source SHA, lock/toolchain/profile/public-config and native-runtime identity,
remote job/artifact identifiers and integrity metadata without secrets/private URLs.
Allow one active submission for the selected app/profile; recover existing job
status after interruption rather than blindly resubmitting. Surface failed/unknown
jobs accurately. Document same-key compatible replacement and recovery limits;
an older binary must not be described as universally installable over a newer
Android version. Preserve installed data, signing material and backend data during
failures, provider rollback and owned-fixture cleanup.

## Acceptance criteria

| ID | Observable result and evidence | Requirements |
|---|---|---|
| AC-001 | Deterministic distinct identities/config; invalid/mismatched/production inputs refused before external calls; historical and unbound-project regressions pass. | AB-001 |
| AC-002 | Owner dispositions recorded; synthetic upload/credential exclusion checks pass; selected remote artifact requires sign-in; no credentials in bundle or sanitized evidence. | AB-002 |
| AC-003 | Physical Android development-client install, private Metro/API access, edit/reload and selected native capability pass; incompatible native change requests rebuild. | AB-003 |
| AC-004 | Physical preview install and cold launch with Expo Go absent/Metro stopped; CRUD, relaunch, persistence, outage/reconnect, uncertain-write and accessibility scenarios recorded separately. | AB-004 |
| AC-005 | Interrupted/failed-job tests recover the existing job without duplicate submissions; exact provenance and compatible replacement drill recorded; unrelated apps/data preserved. | AB-005 |
| AC-006 | Repeat from recorded reviewed inputs and install the resulting build; local/CI, external build, physical install and owner acceptance each reported with limits. | AB-001–005 |

## Decisions and completion

The selected app is Fieldnotes: `danielbardsley/fieldnotes-mobile`, with its existing
independent Fieldnotes Python API/PostgreSQL backend. Both canonical repositories
and existing data are retained. The mobile checkout was clean when inspected for
this approval; no EAS configuration was found among its inspected project files.
The project owner selected the `bardsley` Expo account and Expo-managed Android
signing keys in this chat. No account credentials were requested or inspected.
The exact Expo project/link, key backup/rotation/access disposition, acceptance
device (previously Android 11) remain to be confirmed before external work.
The owner authorized starting free-only on October 21. Use the available free
Android allowance, one active medium-worker build at a time; no subscription
upgrade, paid build, paid retry or overage is authorized. Stop on exhausted or
unverifiable allowance rather than incurring a charge. These remaining decisions
do not reopen specification approval or the Fieldnotes selection.
The specification author must validate exact EAS/native tool versions and the
selected native-module test before implementation; no EAS CLI is assumed installed.
Planning and offline design refinement can proceed without these account actions.

[Build-tool review](build-tool-review.md) records current preparation evidence and
the proposed, unapproved native-build advisory exception.

Deliver reviewed contracts/adapters, documented build/install/recovery interfaces,
meaningful tests and an acceptance record. Mark only this Android slice Delivered
after implementation merge and actual installation/owner acceptance. Full MOB-005,
MOB-006 store distribution, iOS and production remain separately scoped.
