# Fieldnotes Android build-tool review — October 21, 2026

Owner: Project owner. Status: preparation verified; exception proposal below is
not approved. [Specification](spec.md) · [Tasks](tasks.md)

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

## Proposed temporary exception — decision pending

| Field | Proposed disposition |
|---|---|
| Owner | Project owner |
| Exact scope | Only the pinned, patched EAS 25.3.0 graph and reviewed Fieldnotes Android development/preview snapshots, under `bardsley`, within verified free allowance. |
| Findings | [node-forge GHSA-86w9-cpqp-85rv](https://github.com/advisories/GHSA-86w9-cpqp-85rv), affecting RSA signature verification; [braces GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm), affecting deeply nested pattern processing. |
| Reason | No patched package version was available; begin the selected private Android install trial with Expo-managed remote keys. This is a risk acceptance proposal, not a vulnerability fix. |
| Limits | Rootless bounded process, reviewed committed source/known patterns, authenticated artifact access, one job at a time, no iOS/local-keystore import/export, no OTA/store/production operation. These constraints do not prove affected code unreachable. |
| Expiry | 2026-10-28T04:00:00Z (October 28, midnight America/New_York). |
| Removal | Owner/operator stops new signed builds at expiry; author replaces affected dependencies when patched, regenerates the frozen graph, re-audits and verifies the build/install path before removing the exception. No automatic renewal. |

No native-build exception is installed or presumed approved. Offline source
preparation can continue. Device sign-in, exact Expo project/free-quota/artifact
access/key custody checks, job submission/recovery and actual install evidence
remain separate gates. Prior source-only exceptions and acceptance waivers stay
unchanged.
