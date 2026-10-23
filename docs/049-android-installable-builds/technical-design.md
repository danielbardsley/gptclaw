# TDD-049 — Android installable builds

Status: Specification approved; Fieldnotes selected. Exact tooling/interfaces remain subject to validation. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and boundaries

Use EAS as the external native compiler, retaining the existing host as a private
source/Metro/API environment. Do not install Android SDKs, emulators or privileged
host tools. The phone receives an APK; an installed app is not a managed HTTP service.
The preview packages its JavaScript/assets and accesses the independent backend
directly. Metro transport and API HTTPS remain separate validated contracts.

Observed source baseline: manifest 8 represents API/DB-only projects and manifest 9
bound Expo/Metro projects. The immutable Expo notes starter and current exact mobile
quality releases provide frozen dependencies and contract checks, not signed builds.
Use current catalogue/profile sources at implementation; choose fresh versions only
if managed contracts need extension. Never mutate historical schemas or releases.
QLT-001 explicitly defines mobile build as bundle validation; expose native build
submission/status/install instructions separately rather than adding signing to verify.

## Components and changes

| Component | Proposed responsibility | Requirements |
|---|---|---|
| Mobile config/build adapter | Strict development/preview identity, API binding and native-runtime fingerprint; reject production selection. Keep private config ignored. | AB-001, AB-003, AB-004 |
| Exact mobile tooling/release | Review and pin compatible EAS CLI, expo-dev-client and native test dependency in container/user scope; publish a new immutable release when reusable starter changes are required. | AB-002, AB-003 |
| EAS configuration/upload | Reviewed eas.json profiles and explicit upload inventory; exclude unrelated and server material before external submission. | AB-002, AB-004 |
| External-job receipt | App/profile/config/source identity, job/artifact status and integrity metadata in ignored task-owned state; bounded submission and recoverable observation. | AB-005 |
| Runbook and acceptance | Account/signing handoff, authenticated installation, physical scenarios, replacement/recovery and retained-data cleanup. | AB-001–005 |

Prepare a clean snapshot of the selected reviewed revision plus separately validated
public build configuration. Inspect the actual EAS upload inventory, not only
.gitignore. Never mount API/database role files into the build workspace. Hash
private public-config inputs in committed evidence instead of publishing hostnames.
Only the submitting process receives approved EAS credentials; untrusted PR checks
remain unsigned and offline with synthetic configuration.

Propose separate Android package IDs for development and preview, using the same
stable signing identity for successive versions of each variant. The owner reviews
actual values and signing custody. The preview profile uses internal distribution
and a release bundle without developmentClient. Require authenticated artifact
access through Expo project settings; do not infer access privacy from Tailscale.
OTA publishing is disabled/out of scope; installing another binary is the update path.

Persist an intent and source/config fingerprint before submission. On unknown remote
outcome, reconcile the existing remote job before allowing another attempt; no
blind retry. Record confirmed job/artifact identity and terminal status. Do not
claim network submission is exactly-once if the remote API lacks that guarantee.
Unknown state requires explicit reconciliation, with a bounded actionable result.

## Verification and operation

Use synthetic fixtures for profile mismatch, upload exclusions, malformed/stale job
receipts, interruption, remote failure and duplicate refusal. Reuse existing source
quality/contracts and affected historical-provider regressions. No signing token is
needed in PR CI. Check relative links and diff quality for planning changes.

Before rollout, inspect installed capability and scope operator routing separately;
the old temporary Metro listener was removed and is not standing authorization to
recreate it. Before external builds, resolve all spec decisions and inspect current
Expo requirements. Record local/CI/build/install/owner observations separately.

On the selected physical device, install the development client and verify private
Metro/API/native behavior. Install preview, remove Expo Go on the test device with
owner agreement, stop only the owned Metro session, and cold-launch preview. Run
AC-004 scenarios with synthetic records, retaining existing data and shared services.
Repeat from recorded inputs; report reproducibility as traceable inputs and behavior,
not byte-identical signing output unless demonstrated.

Roll back adapter/provider changes through their reviewed versioned path. Retain
signing keys and backend data. For a faulty installed version, use an appropriate
same-key higher-version corrective APK; do not uninstall to bypass version checks
and silently discard app data. Record cleanup ownership before stopping fixtures.
Production authentication, disaster recovery and store release remain excluded.

## Traceability and unresolved choices

| Requirement | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| AB-001 | Strict variant/config admission | T1,T2,T6 | AC-001, AC-006 |
| AB-002 | Account/signing disposition and upload/access controls | T1,T3,T6 | AC-002, AC-006 |
| AB-003 | Native development profile and device trial | T2,T4,T6 | AC-003, AC-006 |
| AB-004 | Bundled preview and physical scenarios | T2,T5,T6 | AC-004, AC-006 |
| AB-005 | Durable job receipt and replacement recovery | T3,T6 | AC-005, AC-006 |

The project owner selected Fieldnotes on October 21. Remaining account/device/
custody/budget decisions belong to the project owner. Exact
version pins, native test module and adapter command/receipt shape belong to the
specification author for review before implementation; no proposed command is an
installed capability. General dashboard automation is a later MOB-009 slice.

References checked in the October 21 planning conversation:
[build profiles](https://docs.expo.dev/build/eas-json/),
[internal distribution/access](https://docs.expo.dev/build/internal-distribution/),
[standalone preview behavior](https://docs.expo.dev/tutorial/eas/internal-distribution-builds/).
Recheck compatibility against the selected exact dependency graph before pinning.
