# TDD-049 — Android development builds

Status: Approved for implementation; implementation in progress. Owner: Project owner. Date: 2026-10-22 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Approach and baseline

Add an external-build adapter alongside mobile source quality and owned Metro.
Keep three independent lifecycles: external EAS jobs, Metro and optional hosted
FastAPI/PostgreSQL. Installation is owner-reported evidence, never a runtime unit.
Reuse canonical-root checks, project locks, atomic receipts, dependency/toolchain
selection and explicit backend binding from existing providers. Inspect current
main and installed capabilities again at implementation; no version numbers are
reserved by this plan.

Current mobile-v1 explicitly excludes native additions and Metro/Go contracts
select Go mode. Publish new profile/schema/capability versions for development
builds rather than weakening mobile-v1 or interpreting Go receipts differently.
Allocate unused versions after checking all source contracts. Existing generated
apps require an explicit source-only migration plan and PR; no automatic upgrade.

Use EAS cloud Android compilation with a development-client/internal APK profile.
Select an exact compatible `expo-dev-client`, EAS CLI and native demonstration
module during implementation, retaining SDK 57 if supported. CI must verify the
matrix before live authorization. Keep `app.json` and permitted public build
metadata deterministic; avoid arbitrary dynamic app config or dotenv loading.
If the pinned CLI requires executable app config, review an isolated deterministic
resolver with no credentials and captured allowlisted inputs before adopting it.

## Components and proposed interfaces

These are design responsibilities, not claims that commands already exist.
Implement CLI names/help only after inspecting `gptclawctl`'s existing parser.

| Component | Planned responsibility | Requirements |
|---|---|---|
| Versioned manifest/schema and mobile profile | Explicit Android development identity, EAS project/account, public profile, optional backend and native compatibility; legacy refusal | DB-001,003,006 |
| New build adapter and CLI integration | Read-only plan, explicit submit, observe, reconcile and verified artifact retrieval; bounded remote subprocess/client | DB-002,004,005 |
| Build staging and upload policy | Tracked clean revision exported into private task-owned staging; archive inventory/digests and forbidden-file checks before credential handoff | DB-003 |
| Owned build receipts outside checkout | Source/config/archive/native digests, operation ID, remote job identity and state; no secret values or install bearer URLs | DB-004,007 |
| Development-client Metro/launch adapter | Separate native mode, compatible-binary evidence, generation/transport checks and read-only launch payload | DB-005,006 |
| New immutable mobile starter release(s) | Dev-client dependency, frozen build config, ignore policy, native-module demo and optional typed notes binding | DB-001,003,006,007 |
| Offline tests, generated CI and runbook | Failure/recovery, native-change classification, archive safety, installation and operational evidence | DB-001–007 |

## Planning, submission and state

A plan validates canonical identity and a clean committed revision, then snapshots
required tracked mobile inputs into a mode-0700 staging directory. Refuse symlinks
or external paths; prevent archive traversal and unrelated repository roots.
Derive the native fingerprint and resolved public configuration without secrets.
Compare the actual EAS upload archive to the approved inventory, not merely a
separate hand-built approximation. EAS CLI archive preparation must be proven
credential-free under the pinned tool; if not possible, use a separately reviewed
minimal credential boundary without granting source code credential access.

Persist a digest-bound operation intent under existing owned runtime storage.
Submit under a short-lived credential boundary only after account/profile/digest,
approval and concurrency/budget checks are fresh. Record the remote job ID; all
subsequent observation uses that account/project/job. Restrict remote responses,
URLs, output sizes and timeouts. Release the global submission lock after durable
job recording but keep project active-job admission until reconciliation/finality.

State progresses from planned to submitting to queued/running and a terminal
succeeded/failed/cancelled result. An ambiguous request or corrupt receipt produces
unknown/recovery-required and blocks submit. Do not promise EAS exactly-once
submission: reconcile using durable operation metadata and remote job inspection;
if association cannot be proven, require owner/operator resolution. Observation
can fail without erasing the last verified remote state; expose its age.

A succeeded job records safe artifact identity and expected package/signing metadata.
Retrieve only from validated EAS destinations, verify downloaded APK bytes/hash and
package/certificate using a reviewed user/container tool, and compare to custody
records. Keep raw credential-bearing artifact URLs in restricted ephemeral storage.
Owner installation records artifact digest and observed version/device separately.
No dashboard device-online indicator or build-submission control is added.

## Private development loop

Use a new dev-client launch serializer bound to native fingerprint, project scheme,
Metro generation, explicit transport and finite session expiry. Keep Go serializers
and their security/transport admission independent. Prefer a tested HTTPS route;
check Android trust, manifests/assets and WebSocket reload on the physical device.
Any new native network security policy is part of the native fingerprint and
review, never a global cleartext/TLS bypass. Listener work remains an exact reviewed
operator action preserving HTTPS 443 handlers and Funnel-off state.

The bound fixture uses SPEC-036 public development binding and generated types.
It makes no EAS build-time calls to the private backend: cloud compilation must
succeed without tailnet/backend access. Only the owner's tailnet device connects
to the backend at runtime. EAS receives approved public URL/config values but no
DB role files or backend credentials. An unbound fixture exercises the same binary
and Metro path without backend assumptions.

Native-dependency/plugin/SDK/config changes require a new matching binary;
JavaScript edits only change bundle freshness. Installation evidence is explicit
and may become stale; neither a remote build nor a bundle fingerprint proves the
installed device binary. Verify the selected native module beyond Go's module set
on-device, then demonstrate compatibility refusal and replacement installation.

## Verification, rollout and recovery

Offline synthetic tests cover malformed contracts, legacy behavior, no implicit
execution, archive canaries/path safety, public-config limits, credential redaction,
concurrency and every interrupted submission boundary. Use a fake EAS client for
failure injection; no paid jobs or real credentials in ordinary CI. Generated
project checks include frozen dependencies, exact native matrix, bundle/contract
quality and profile/config consistency. Existing Go/source/backend tests remain.

After implementation review/merge, install a capable provider through the existing
reviewed procedure and compare source/installed contracts. External acceptance
waits for the spec's account/signing/budget/upload decisions and exact native
transport scope. Run an authorized real job, verify/install its APK, execute both
standalone and bound loops and a native-change replacement build. Record local,
CI, remote job, installed provider, device and owner results independently.

On failure stop new submissions, reconcile active jobs and retain receipts/source.
Revert source/profile changes through targeted PRs; keep a capable observer for
in-flight jobs. Signing rotation/revocation and remote cancellation use only their
reviewed account scope. Never delete a key or assume uninstall revokes a binary.
Provider rollback neither reverses DB schema nor removes installed apps. Stop only
owned temporary Metro/backend fixtures using existing lifecycle interfaces; retain
source and synthetic data unless separate cleanup authorization covers deletion.
Remove exact temporary operator listeners and independently read back preserved
handlers. Retain/redact artifacts and dispose of task-owned upload staging per the
owner's recorded policy.

## Traceability and pending decisions

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| DB-001 | Versioned opt-in/canonical identity/legacy tests | T2,T3,T8 | AC-001 |
| DB-002 | Scoped account/custody decision and credential boundary | T2,T4,T8 | AC-002 |
| DB-003 | Frozen matrix, staging, exact archive inspection | T2,T3,T4,T8 | AC-003 |
| DB-004 | Durable intent, bounded submission and reconciliation | T5,T8,T9 | AC-004 |
| DB-005 | Artifact identity and private native launch | T6,T9 | AC-005,007 |
| DB-006 | Native fingerprint, module and isolated device loop | T3,T6,T7,T9 | AC-006,007 |
| DB-007 | Versioned delivery, capable rollback and evidence | T7,T8,T9,T10 | AC-008 |

The project owner resolves account, custody, budget, access and device decisions
before external execution. The implementer resolves exact supported tool/module/
image pins before real builds, with a spec amendment if SDK migration is needed.
Transport exceptions require concrete owner scope. Offline work can proceed after
implementation authorization while external decisions remain pending.

## Primary sources checked October 22, 2026

These establish service behavior, not compatibility of this repository's exact
SDK-57 pins. Revalidate the pinned tools and account settings at implementation.

- [Development builds](https://docs.expo.dev/develop/development-builds/introduction/): own native client and development workflow.
- [Android APKs](https://docs.expo.dev/build-reference/apk/): directly installable APK versus store-oriented AAB and development-client build profiles.
- [Upload ignore policy](https://docs.expo.dev/build-reference/easignore/): `.easignore` takes precedence over `.gitignore`; missing native directories are generated by Prebuild.
- [App variants](https://docs.expo.dev/build-reference/variants/): separate native identities for development variants.
- [Local builds](https://docs.expo.dev/build-reference/local-builds/): local compilation is a distinct toolchain path, excluded here.

## Implementation selections — October 23

Provider 1.18.0 adds project schemas 11/12 and catalogue 9 with
`expo-development@1.0.0` and `expo-development-notes@1.0.0`. Mobile profile 2
retains SDK 57 and selects expo-dev-client 57.0.20, MMKV 4.3.2 and Nitro Modules
0.35.2. The separate npm integrity lock freezes EAS CLI 25.3.0. EAS uses named
`ubuntu-26.04-jdk-17-ndk-r27b-sdk-57`, with exact Node/pnpm overrides; Expo
documents minor image updates, so this is not a byte-identical compiler promise.

The credential boundary is a fixed container wrapper for the pinned CLI. It
replaces that exact version's archive function with the pre-inspected deterministic
archive and rejects inherited account/project development variables. Static
app.json, exact trusted plugins and absence of package/config hooks prevent local
application code evaluation in that boundary. A version change requires wrapper
review/tests. Read-only mounts, ephemeral home and bounded outputs separate it
from source jobs and Metro. No signing keys or credentials enter the upload.

A separate pinned JDK/apksig 8.13.0 container verifies APK v2/v3 signatures,
while a bounded binary manifest parser checks package identity. Downloaded bytes
are tied to the exact observed job; installation remains explicit owner evidence.
Tool images require matching ownership labels and recipe digests. Native Metro
session schema 3 and control schemas 4/5 select development-client mode and HTTPS;
legacy Go contracts remain unchanged. Native audit admission has no Go exceptions.

Local audit evidence blocks signing/submission and native runtime admission; see
[security disposition](security-review.md). Source component tests and unsigned
exports cannot establish that those gates passed. [Acceptance](acceptance.md)
records observed checks separately from remaining cloud/device/owner acceptance.
