# SPEC-049 — Android development builds (MOB-004)

- **Status:** Draft; specification requested, implementation not authorized.
- **Owner:** Project owner
- **Date:** 2026-10-22 (America/New_York)
- **Features:** MOB-004; minimum development-profile, credential and build-job
  slices of MOB-005/006, SEC-001/002/006/007 and PRJ-002.
- **Design:** [TDD-049](technical-design.md) · **Tasks:** [TASKS-049](tasks.md)
- **Direction:** [Mobile sequence, stage 5](../platform/sequence-mobile.md#5-produce-signed-development-builds)

## Outcome and selected scope

Create, install and repeatedly use a project's own signed Android Expo development
client with an owned private Metro session and optional private FastAPI backend.
The owner can edit JavaScript and reload without rebuilding the binary; changing
native dependencies or native configuration explicitly requires a compatible new
binary. Builds have reviewed source inputs, bounded external execution and
recoverable job tracking. A development client remains dependent on Metro for
this development loop; this feature does not promise a standalone preview app.

Select Android first, consistent with SPEC-033/034/036's accepted device scope.
Use EAS cloud compilation, an installable APK and a new owned synthetic fixture.
Support both a standalone mobile project and an explicitly bound Python backend.
The bound fixture demonstrates native CRUD and persistence with existing contracts;
it does not reopen or silently strengthen SPEC-036's owner-accepted waivers.

Include source-only opt-in, a development-specific native identity/profile,
reviewed credential handoff, upload inspection, remote build receipts, read-only
job observation, artifact verification, device installation and development-client
launch. Preserve immutable starters and existing Expo Go behavior. Full environment
management, preview binaries, OTA updates, store submission, production and iOS
remain separate features/slices. Exclude public tunnels, new infrastructure,
host Android SDK/emulator installs, existing-app migration, real-user data,
application authentication, automatic CI build submission and dashboard build buttons.

## Observed baseline and prerequisites

Current main's [mobile profile](../../config/mobile/v1.json) pins Expo 57.0.28,
React Native 0.86.3, React 19.2.3, Node 24.21.0 and pnpm 12.10.1. It declares
`unsupported_native: true`; its dependency policy does not admit a development
client. This is a source baseline, not a supported EAS compiler matrix.
[Metro opt-in](../../scripts/metro_contract.py) selects `expo-go`; the
[Go adapter](../../scripts/expo_go.py) validates that mode. A development-client
adapter and compatible versioned contracts must therefore precede native launch.

SPEC-031/033/034 provide creation, owned Metro and Android Go; SPEC-036's
[October 21 closeout](../036-mobile-python-backend/closeout-2026-10-21.md)
records Android M1 acceptance with explicit waivers. Existing Go private HTTP
approval is limited to its exact SDK/client/session scope; it is not permission
to reuse cleartext transport for a new native binary. API routes remain HTTPS.
Installed capability, active listeners, account availability and signing custody
have not been inspected for this planning task.

## Requirements

### DB-001 — Explicit opt-in and compatible native identity

Introduce a versioned development-build capability without changing published
schemas, profiles or releases in place. Select canonical project, Android platform,
`development` environment, EAS account/project, distinct Android development package,
URL scheme and optional explicit backend binding. No default account/project,
production fallback or executable configuration/environment discovery. Build
preparation must not start Metro or the backend. Older providers refuse unsupported
contracts before mutation; unbound, Go and web/API/DB projects retain behavior.

### DB-002 — Reviewed account, signing and credential boundary

Before account/project creation, credential setup, source upload or paid/external
jobs, record the exact owner-authorized scope: Expo account/project, signing-key
custodian and recovery procedure, permitted credential reference, build count/cost
ceiling, access/retention policy and Android device. Prefer owner-managed EAS
signing for this new development-only identity, subject to owner selection.
Verify available token privileges; do not assume per-project token scoping exists.
A credential with broader account access requires explicit disposition or an
isolated account. GitHub/AWS credentials never substitute for Expo credentials.

Inject only the required Expo credential into the submission/observation boundary;
exclude it from source jobs, Metro, bundle compilation environment, receipts and
logs. Private keys/keystores stay in the selected signing custody and out of the
repository/upload/evidence. Untrusted PR jobs receive no external-build secrets.
Revocation/rotation blocks further submissions without stopping unrelated runtimes.

### DB-003 — Frozen, inspected build inputs

Build only a clean reviewed committed revision from the canonical project, with
exact dependency lock, native-module/config-plugin allowlist, SDK/client/EAS CLI
matrix and immutable cloud build image selection where supported. Record any
service-managed inputs that prevent byte-for-byte reproducibility. Use generated
native directories with explicit continuous-native-generation ownership for the
new fixture; refuse hand-edited native sources rather than overwriting them.

Inspect the exact upload archive before transmission. Include only required
mobile source and reviewed build configuration. Exclude Git/auth files, dotenv,
backend source/state/data/role files, caches, local runtime records, backups and
unrelated projects. Preserve required generated API types. A checked ignore file
alone is insufficient: archive inventory, size limits and synthetic forbidden-file
canaries must pass. Any archive/config change invalidates the reviewed plan.
Only allowlisted public client configuration enters the bundle; private API
hostnames require explicit upload disclosure and sanitized public evidence.

### DB-004 — Bounded, resumable build jobs

Separate plan, explicit submit, observe and artifact retrieval. Bind an operation
to source commit, archive/config/native-input digests, platform/profile, account/
project, tool matrix and approval scope. Permit one active submission per project
and one platform-wide submission at a time in this initial lane; enforce approved
attempt/cost limits before each submit. Persist intent before the request and
remote job ID as soon as known. A timeout after possible submission is `unknown`,
not failed permission to retry: reconcile the remote job or require an operator
resolution before another submission. Provider restart never resubmits implicitly.

Observe queued/running/succeeded/failed/cancelled/unknown independently of Metro,
backend and device state. Build success means an artifact exists; it does not mean
installed or accepted. Capture bounded redacted errors and safe remote identifiers;
no tokens or bearer artifact URLs in committed evidence. Cancellation, where
supported, targets only the exact owned remote job and does not imply cost refund.

### DB-005 — Verified installation and private native launch

Verify job/project/profile identity, APK hash, package ID and signing certificate
fingerprint before offering the artifact for owner installation. Use the approved
artifact access/expiry policy; an EAS install URL is not inherently tailnet-private.
Expose no public install link in the dashboard or source. Record installation
separately from build completion; do not uninstall or replace an existing app.

Launch the matching development client through a validated project scheme and
owned generation-bound Metro destination. Prefer private HTTPS and prove status,
bundle, assets and reload/WebSocket behavior on the actual device. If unavailable,
prepare a scoped native transport exception for review; the Go HTTP exception
cannot be inherited. No public tunnel fallback. Expired, stopped, reused-origin,
foreign-project or incompatible-binary launch data must be unavailable. Read-only
launch inspection must never start a session or change routing.

### DB-006 — Native compatibility and independent lifecycle

Track the binary's native fingerprint from exact dependencies, plugins, native
configuration, SDK and package identity. JavaScript-only changes can reload;
native changes invalidate launch eligibility until a matching binary is installed.
Choose one compatible native module outside the accepted Go module set for a
small synthetic device demonstration, without permissions or external services
unless separately authorized. Missing/stale binary evidence reports unknown or
rebuild-required; it never certifies device presence from an EAS job result.

Prove standalone launch, bound FastAPI CRUD, source edit/Fast Refresh/full reload,
app relaunch, tailnet interruption/reconnect and Metro restart. Stopping Metro
leaves the backend/data and other projects intact; stopping the backend leaves
Metro intact and shows a recoverable native connection error. Saved synthetic
records survive backend restart. No implicit database migration, reset or seed.

### DB-007 — Delivery, recovery and evidence

Deliver versioned provider/contracts/profile, new immutable opt-in template
release(s), meaningful offline and generated-project CI checks, and a runbook.
Keep source and installed behavior consistent. Rollback blocks new submissions
and launch certification without deleting remote jobs, signing material, APKs,
source or data. Reconcile in-flight jobs through a capable observer before provider
rollback; database rollback remains independent. Preserve legacy Go sessions and
all unrelated applications/listeners. Cleanup only owned temporary runtime and
upload staging; artifact/key retention follows the recorded owner decision.

## Acceptance criteria

| ID | Observable result and evidence required | Requirements |
|---|---|---|
| AC-001 | Standalone and bound fixture plans validate; legacy schemas/Go and old-provider refusal pass. Wrong account/project/profile/native identity/backend fail before upload or mutation. | DB-001 |
| AC-002 | Owner records account, custody/recovery, credential privileges, budget, artifact policy and device scope. Synthetic credential canaries stay out of source, logs, upload and bundle; revocation blocks submit. | DB-002 |
| AC-003 | Exact SDK/native/client/CLI/cloud matrix is recorded and real build preparation passes. Frozen archive determinism, drift, symlink/escape, forbidden-file canary and config-secret refusal checks pass. | DB-003 |
| AC-004 | Mock remote failures cover concurrent submit, budget exhaustion, interruption before/after remote acceptance, restart, redaction and reconcile without duplicates. Authorized real job resumes observation to its correct final artifact or failure. | DB-004 |
| AC-005 | Owner installs verified signed APK on the recorded physical Android device; correct private native link opens UI/assets. Wrong/stale artifact, generation and access links fail safely. No public listener or unrelated route change. | DB-005 |
| AC-006 | Device proves native-module behavior, JavaScript reload without rebuild, native-change rebuild refusal and operation after installing a compatible replacement. Record exact binary/module/OS/profile identities. | DB-006 |
| AC-007 | Standalone and bound private native loops, outage/reconnect, lifecycle isolation and backend restart persistence pass with synthetic data. Record device actions separately from automated host tests. | DB-005,006 |
| AC-008 | Relevant local/generated CI and installed parity pass; capable rollback and owned cleanup preserve source/data, other services and Go. Implementation merges and owner accepts this Android scope with retained evidence. | DB-007 |

## Decisions and completion

Planning is authorized by the request to write this specification. Review and
implementation authorization remain pending. No account, credential, build,
installation or listener operation is authorized by this document's existence.

| Decision | Proposed default / owner and next action |
|---|---|
| Platform/device | Android-first; project owner confirms actual device/OS before physical acceptance. iOS needs a separate scoped plan and account/device prerequisites. |
| Expo account/project and signing | Project owner selects exact isolated development scope and managed-signing custody/recovery before setup or external execution. |
| Spending and artifact sharing | Project owner supplies attempt/cost ceiling, access, expiry and retention before first upload/job; unresolved values block external execution, not offline implementation after authorization. |
| Exact compiler/client/module pins | Implementer verifies SDK-57 cloud support and selects exact compatible CLI/dev-client/module/image pins in the reviewed implementation. SDK migration requires a scope amendment if current pins cannot build. |
| Private transport | Implementer proves HTTPS with the new binary. Project owner reviews any required bounded exception; existing Go approval does not apply. |

Complete only when AC-001–008 have recorded outcomes and owner disposition,
implementation is merged, and Android acceptance passes. Create acceptance tracking
when executed evidence is available. Full MOB-005/006/011, iOS, preview/M2, updates
and product production remain open regardless of this slice's delivery.
