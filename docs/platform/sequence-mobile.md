# GptClaw mobile application delivery sequence

- **Status:** Proposed delivery order; planning only, not implementation authorization
- **Owner:** Project owner
- **Last updated:** 2026-10-21 (America/New_York)
- **Catalogue:** [Platform features](features.md)
- **Related direction:** [Platform architecture](architecture.md) · [General sequence](sequence.md)

## Outcome and milestones

Deliver iOS and Android **React Native applications using Expo and TypeScript**,
with optional FastAPI backends backed by managed PostgreSQL. Reuse the platform's
project creation, repository, quality, runtime and private-access contracts.
The first milestone is a native app on an actual device reading and writing
synthetic data through a private API, with persistence across backend restart.
Web preview is optional and cannot establish native acceptance.

| Milestone | Completed stages | User-visible outcome |
|---|---|---|
| M1 — Private development | 0–4 | Create a mobile project, start its owned Metro session and backend, open it on a tailnet device, edit and reload it, and retain API data through backend restart. |
| M2 — Installable applications | 5–6 | Repeatedly build and install Android/iOS development and preview binaries from reviewed revisions. A preview binary works with Metro stopped and the appropriate backend running. |
| M3 — Controlled updates | 7 | Publish compatible preview updates with an observed rollback path and environment separation. |
| M4 — Product release | 8 | Deliver a separately deployed production API/database and explicitly authorized store testing/submission/release for the native app. |

The stages specify ordering and exit evidence, not approved schemas, installed
commands or production designs. Each selected coherent slice still needs a
numbered specification, technical design, task list and recorded acceptance.
Local tests, CI, merge, private rollout, native installation and owner acceptance
are distinct gates. Public exposure, account changes, paid builds, credential
setup and store publication require their concrete scope to be authorized.

## 0. Reuse the delivered platform and record its limits

| Existing capability | Reuse and boundary |
|---|---|
| FND-001–006; AGT guidance/skills | Use the existing private host, protected volume, unprivileged forge account, repository/area instructions and planning/PR workflow. Do not rebuild the foundation. Remaining host/client acceptance stays recorded separately. |
| PRJ-001/002/003; SYS-002/003 | Reuse versioned validation, the installed provider, immutable template catalogue and pinned dependency/toolchain policies. MOB-001 delivers schema-5 mobile source creation/quality using exact Node 24.21.0/pnpm 12.10.1. Planning readback sees stable 1.10.1 and main source 1.11.0 with PRJ-006; implementation must preserve both mobile and canonical-worktree contracts. Neither provides an accepted Metro session. Recheck installed capability at rollout. |
| PRJ-004/005; PRJ-006 | Reuse private repository creation, explicit credential bindings, branches/worktrees and owned-operation locking. Repository credentials do not become Expo, Apple or Google credentials. |
| TPL-003; RUN-006/011 | Reuse FastAPI, ordered group lifecycle and PostgreSQL persistence/migrations/recovery. Current schema 4 and `notes-postgres@1.0.0` require web + API + DB; an API/DB-only shape is an extension, not an existing capability. SPEC-026 is delivered; SPEC-025's historical closeout still lists review/merge as pending. |
| NET-101–103; DSH-001–003 | Reuse private HTTPS API routes, inventory, observations and safe links. Metro transport, WebSocket behavior and native launch links have not been accepted through this routing path. |

Evidence and operational interfaces: [private apps](../../runbooks/manage-private-apps.md),
[FastAPI](../../runbooks/manage-python-apis.md), [groups](../../runbooks/manage-multi-service-projects.md),
[databases](../../runbooks/manage-development-databases.md),
[templates](../../runbooks/manage-project-templates.md),
[toolchains](../../runbooks/manage-project-toolchains.md),
[SPEC-026 acceptance](../026-development-databases/acceptance.md) and
[SPEC-027–029](../README.md).

Keep the existing Shelfmark and Trailboard applications/data unchanged; acceptance
uses newly owned synthetic fixtures. Persistent DB data/role files stay outside
source checkouts and mobile bundles. Local native backups share the project volume;
this plan does not claim host-loss recovery. The general sequence's owner-directed
RES deferral remains in force; retain existing snapshots and protection, with a
separate recovery decision before production.

## 1. Establish mobile identity, environments and supported contracts

**Features, in order:** MOB-005 → mobile slices of PRJ-001, SYS-002/003,
SEC-003 and PRJ-002. Design alongside TPL-004 and MOB-010; implement providers
before the template and dashboard consumers.

Define project identity, iOS bundle ID, Android package ID, URL scheme, supported
platforms and explicit backend binding. Distinguish four independently observed
objects: mobile source, an optional Metro session, hosted backend components and
external build/release jobs. An installed native application is not a container;
stopping Metro must not stop a shared backend or mark an installed app unavailable.
A mobile project without a backend must also be supported.

Extend versioned schemas, provider capabilities/receipts and catalogue contracts;
do not add mobile fields to schemas 1–4 or model Metro as a ready Next.js service.
Keep existing web/API/DB behavior and older-provider rejection tests. Choose an
exact supported Expo SDK/React Native/React/Node/pnpm/Expo CLI/EAS CLI matrix from
current compatibility evidence; acquire tools inside reviewed containers or user
scope. Do not assume the web profile's versions work with Expo.

Define local/development/preview/production configuration. API base URLs, application
IDs and channel names are non-secret client configuration. Compiled client values
are extractable; `EXPO_PUBLIC_*` cannot carry secrets. Use explicit permitted
configuration rather than enabling unrestricted dotenv/credential forwarding.

**Exit evidence:** schema/adapter compatibility tests; deterministic public config
for each profile; rejection of missing or mismatched backend/environment bindings;
no implicit production selection, source-secret upload or unrelated runtime mutation.

## 2. Connect the native client to FastAPI and PostgreSQL

**Features, in order:** MOB-010 with QLT-008 → mobile backend slices of RUN-006/011,
TPL-003, PRJ-003 and QLT-007. RUN-012's broader seed lifecycle is not a prerequisite;
reuse SPEC-026's explicitly owned synthetic seed operations.

Declare the relationship between mobile and backend project IDs. Prefer independent
mobile and backend lifecycles with an explicit binding; a shared product repository
is allowed when its specification justifies the release model. Reuse OpenAPI to
validate or generate a typed TypeScript client with a reviewed, pinned tool.
Specify absolute private HTTPS URLs, API prefix handling, request timeouts, validation,
loading/error/retry behavior and contract compatibility across client versions.
Native requests must not depend on browser same-origin cookies or desktop loopback
URLs. Optional Expo web requires a separate, restricted CORS configuration.

For the first integration fixture, the existing web/API/DB template can supply the
private API unchanged, retaining its web component because current route readiness
requires it. Then deliver the API/DB-only backend shape through a reviewed schema,
readiness, template and ingress extension; reuse database roles, data ownership,
backup/migration gates and recovery code. Avoid a second database lifecycle manager.
Remove unwanted starter routes/UI only after replacement contracts work; record
purposeful demo retention in the synthetic starter fixture.

**Exit evidence:** client/API schema checks; device-compatible HTTPS endpoint;
synthetic CRUD and backend restart persistence; migration compatibility with an
older installed client; inaccessible DB host ports; neither DB credentials nor
server-only secrets in JS, assets, app configuration, logs or binaries. Public or
real-user authentication remains a stage-8 gate, not a promise made by this demo.

## 3. Deliver the React Native template and repeatable creation

**Features, in order:** TPL-004 with TPL-008/QLT-005 → PRJ-003/PRJ-009 →
MOB-001 with PRJ-002/004/005 → mobile QLT-001/002/009 and MOB-011 foundations.

Publish an immutable Expo Router + React Native + TypeScript template release,
frozen lockfile, exact compatible toolchain and mobile coding/style guidance.
Include native navigation, accessible forms, keyboard/safe-area behavior,
API loading/failure states and optional backend binding. Use native components;
web export is not the product's primary runtime. Define continuous-native-generation
versus checked-in native-source ownership before regeneration; never overwrite
hand-edited native code to update dependencies.

Integrate creation/validation/dependency operations with existing catalogue and
repository workflows, retaining a local-only mode. Proposed mobile commands must
be specified and tested before runbooks advertise them. Expo dependency changes
need SDK/native compatibility checks, reviewed installation scripts/config plugins,
lockfile review and a clear indication when a new native build is necessary.
Do not weaken the existing installation policy globally to accommodate Expo.

Add pinned CI actions with minimal permissions, formatter/linter/type checks,
React Native component/unit tests, API contract checks, bundle generation and
secret/dependency checks. Untrusted PRs receive no signing, EAS or backend secrets.
Extend golden generation tests and source-retaining fixture cleanup.

**Exit evidence:** two independently generated projects pass checks from frozen
inputs, create reviewable private initial PRs, keep distinct IDs/configuration and
reject incompatible SDK/dependency changes. Record native acceptance as pending
until stage 4; successful bundle generation alone is insufficient.

## 4. Run Metro privately and complete the first device loop

**Features, in order:** MOB-002 with RUN-002/003/004/005, NET-104 and a Metro-specific
NET-102 slice → MOB-003 where compatible → MOB-011 with QLT-004.

Manage Metro as an owned rootless/user-service session with allocated loopback
ports, resource/time/log bounds, disconnect survival, status and scoped stop/restart.
Reuse existing ownership and locks; do not leave a terminal server as the runtime.
Provide a tested tailnet-only transport for bundle/asset requests and WebSocket
reload traffic. Select a dedicated private HTTPS route/port or validated proxy
contract after a device spike; do not assume `/projects/<slug>/` forwarding is
compatible with Expo's advertised URLs. Generate accurate launch links/QR payloads
for the selected Expo Go or development-client mode. All host services remain
loopback-bound; devices join the approved tailnet. Administrative Tailscale changes
use the reviewed operator path; no public security-group listener is needed.

Expo Go is an optional quick feedback path for a compatible SDK/native-module set.
Check device/account requirements at specification time. If a required module or
transport cannot work with Expo Go, complete the stage-5 development-build slice
before accepting M1; do not add a public tunnel as an automatic fallback.

**Exit evidence (M1):** actual device loads the native UI and assets over tailnet,
reads/writes via private API, reconnects after interruption, observes a source edit
through Fast Refresh and reload, and retains data after backend restart. Backend
failure shows a useful native error and recovers. Two sessions have separate ports;
stopping one leaves the other and a shared backend intact. Exercise phone network
changes/tailnet loss and explicitly report supported platforms. iOS and Android
coverage is required before claiming both; a single-platform slice stays labeled.

## 5. Produce signed development builds

**Features, in order:** scoped SEC-001/002 and MOB-005 credential handling →
MOB-004 with the build slice of MOB-006, SEC-006/007 and PRJ-002.

Use EAS cloud builds as the proposed first cross-platform compiler; native tools
need not be installed on the EC2 host. iOS local compilation/simulation requires
an appropriate macOS/Xcode environment. A local Android build lane is optional
separately reviewed scope, not permission for host package installs or privileged
emulators. Device testing runs on an owner device or a declared remote test runner.

Before the first external job, record the selected Expo account/project, Apple and
Google account ownership as applicable, device enrollment, credential storage and
rotation, source-upload contents, costs/bounds and authorized build profiles. Scope
EAS tokens to the selected workflow/account capabilities; do not claim GitHub
broker tokens can authorize it. Exclude authentication files, runtime state, private
role files, local caches and unrelated project sources from build uploads.

Build jobs record the source revision, profile/platform, public-config digest,
runtime identity and remote job/artifact identity. Bound concurrent submissions,
retain resumable job status and avoid duplicates after task interruption. A later
RUN-009 queue may generalize this; a platform-wide queue is not a prerequisite.

**Exit evidence:** install the project's own development binary on each supported
platform, load its owned Metro session and private API, test a selected native module
and prove that native dependency changes request a new binary. Verify signing/access
boundaries, redacted logs, failed-build behavior and recovery without duplicate jobs.
No store submission follows automatically from a successful build.

## 6. Deliver preview binaries and dashboard integration

**Features, in order:** preview/internal-distribution slice of MOB-006 and MOB-005 →
MOB-011 native end-to-end gates → MOB-009 with DSH-001/002/003/007 adaptations.
MOB-008 universal web preview is an optional parallel slice after native acceptance.

Provide installable Android/iOS preview artifacts tied to exact reviewed revisions,
separate from development-client binaries. Configure authorized artifact access
and retention; an internal-distribution link is not automatically private because
the API uses Tailscale. Enforce the selected EAS access settings and iOS device/
provisioning rules. Installed preview apps can use the private backend while the
tester is on tailnet; they do not need Metro running.

Native test coverage must exercise navigation, synthetic CRUD, app termination/
relaunch, backend restart persistence, offline/error/reconnect and platform-specific
accessibility. Choose a pinned device automation runner in the specification;
unit tests and Playwright web checks do not replace native acceptance. Exercise
both platforms and assign an owner/device path for any manual checks.

Extend dashboard adapters with honest distinct states for Metro, hosted API/DB and
remote builds. Display safe launch/install destinations, build freshness and explicit
unavailable reasons; compiled native apps must not appear as stopped HTTP services.
Handle offline EAS/API observations without fabricating device presence or readiness.
Install/QR links need their own reviewed scheme/access validation. Dashboard build
submission buttons remain separate DSH-009 control work.

**Exit evidence (M2):** create, start, inspect, stop, edit, check, build and install
using documented reviewed interfaces; previews work after Metro stops, retain data
through API restart and have accurate private dashboard destinations. Repeat with
a second app without changing the first. Web preview, if selected, additionally
passes base-path/asset/CORS tests and stays private under the existing ingress model.

## 7. Add compatible over-the-air updates

**Features, in order:** MOB-007 with MOB-005, SEC-006/007 and PRD-008's mobile slice →
MOB-009 release/channel observations.

Separate development, preview and production channels and enforce native-runtime
compatibility. Bind update metadata to source, environment and API contract version.
Changing native code/configuration requires an appropriate new binary rather than
assuming a JavaScript update can carry it. Stage preview updates on installed apps,
observe acceptance, then rehearse rollback/roll-forward and interruption handling.
Older installed clients must remain supported during API/schema rollout.

**Exit evidence (M3):** a compatible preview update loads on actual devices; an
incompatible runtime is refused; a failed update is recoverable on the next launch;
preview publication cannot target production accidentally. Record a rollback drill
and the limits of recovery for clients already offline. Production update promotion
remains explicitly authorized and gated by stage 8, with version/channel provenance.

## 8. Release a product with its production backend

**Features, in order:** TPL-009, SEC-010 and QLT-008 production identity/compatibility →
PRD-001/002/003/005/006/007 with SEC-008 and QLT-007 → PRD-004/008/009 →
MOB-006 store-submission slice and AGT-007 → authorized MOB-007 production updates.

Specify product authentication/authorization, device session storage/logout,
production API availability, data handling, monitoring and recovery. The initial
synthetic CRUD fixture does not provide these. Production clients cannot depend
on the development host or a developer tailnet; select the intended user network
model and stable HTTPS endpoint. If serving public users, deploy an authenticated
production API with a separately managed database, identities, state, backups and
migration gates. Do not substitute Funnel for production backend hosting. Permanent
AWS infrastructure changes use committed code → GitHub Actions → HCP Terraform → AWS.

Choose the product pipeline, build provenance, signing custody, version/build-number
rules, store metadata/privacy declarations and TestFlight/Google Play testing path.
A new binary may need to be built for production config/signing; promote an identical
artifact only where the platform and profile permit, recording the exact identity.
Build, upload, beta distribution, store review and final release are separate states
and approvals. Rehearse backward-compatible API/database rollout and mobile update/
backend rollback coordination; store binaries are not instantly revocable everywhere.
Production promotion credentials remain in protected workflows, unavailable to
ordinary development containers/tasks.

**Exit evidence (M4):** accepted native iOS/Android binaries use the intended
production API and persistence with tested authentication and recovery; store-test
installation and end-to-end smoke checks pass; the owner authorizes the exact store
submission/release. Record backend, binary, update and schema identities together.
Expo/EAS, Apple/Google and AWS acceptance are separate evidence, not one deploy flag.

## Proposed specification groups and decisions

**First selected specification (October 13):** [SPEC-031](../031-expo-project-creation/spec.md)
selects MOB-001 and its minimum template/schema/toolchain/quality/repository
prerequisites from stages 1/3. It deliberately closes creation before private
Metro/device and backend integration; M1 remains incomplete. The owner subsequently approved implementation; source
creation/quality/private-repository implementation merged in PR #73, and the owner
confirmed acceptance October 13. MOB-001 is Delivered; M1 remains incomplete. [Evidence](../031-expo-project-creation/acceptance.md)
records actual checks and scope. Other roadmap stages retain their separate gates.

**Current delivered slices:** [SPEC-033](../033-private-metro-sessions/spec.md)
(MOB-002) and [SPEC-034](../034-expo-go-workflow/spec.md) (MOB-003) are merged and
installed through [PR #78](https://github.com/danielbardsley/gptclaw/pull/78).
The owner-selected Android 11 / Expo Go 57.0.9 matrix passes two-project native
load/edit/reload, private stop/restart/crash recovery and expiry isolation. iOS
remains explicitly unsupported/follow-up. Both temporary runtimes and owned listeners are absent after owner-executed SSM
cleanup and independent preserved-route readback. Catalogue state is Delivered
for this Android-first scope. Source, receipts/history and existing apps/data
are retained.

The Metro provider precedes its Go consumer. Concrete runtime security and private
operator routing remain separate gates. Private HTTP compatibility is bounded to
the approved SDK/client inside encrypted Tailscale; restore HTTPS only through the
recorded shipped-client/SDK/native-validation gate. Backend binding/persistence,
signed development clients, accounts, public exposure and full M1 remain separate
MOB-004/005/010/011 work; this delivery adds none of them.

**Owner-accepted Android backend slice (October 21):**
[SPEC-036](../036-mobile-python-backend/spec.md) implements MOB-010 with
Python/FastAPI and PostgreSQL, API/DB-only lifecycle, explicit development binding
and native synthetic notes. Implementation merged in PR #83. The project owner
accepted the Android-first slice and Android M1 with explicit remaining manual-
evidence waivers in [the closeout](../036-mobile-python-backend/closeout-2026-10-21.md),
carried by PR #91. Automated/host and owner-reported physical results remain
distinct from waived device/screenshot checks. Both trial runtimes are stopped
with source/data retained; owner-supplied final Serve JSON confirms the temporary
private listener is removed and both HTTPS 443 handlers are preserved. The initial restore failure remains documented despite the
successful full rerun. Python remains the application backend default.

The next selected planning slice is [SPEC-049](../049-mobile-development-builds/spec.md):
Android-first stage-5 development builds (MOB-004 with minimum MOB-005/006
credential/environment/build prerequisites). Its specification, design and tasks
are Draft; implementation and external operations are not authorized. Account,
signing custody, source-upload, budget and artifact-access decisions precede live
EAS work; iOS, standalone previews and store distribution remain separate.
SPEC-036 acceptance does not establish iOS, signed-build or production readiness. Fastify remains optional.

**M1 spans stages 1–4 across compatible initiatives:** SPEC-031 begins with
creation; subsequent TPL-004, MOB-002/005/010/011 slices add the private runtime,
backend and native acceptance. Design the interfaces together and deliver each
provider before its consumers. Backend support precedes integration/device
acceptance but is not required for standalone source creation. Bring only the
stage-5 build slice forward if the device spike requires a development client.
Subsequent initiatives can cover development builds, preview/dashboard delivery,
updates and product production separately. Catalogue status follows each selected
specification; this roadmap authorizes no installation.

| Decision | Owner and next decision point |
|---|---|
| First product and first acceptance devices | Project owner selects the product/device availability when commissioning the first specification; target iOS and Android, label any initial platform limitation. |
| SDK/toolchain and private Metro transport | Specification author validates current Expo compatibility and actual device transport during stages 1/4; the owner reviews the selected contract. |
| Backend topology | Propose separately managed mobile and API/DB projects; first fixture may reuse the existing three-service template. Review a shared repository only for a justified common product lifecycle. |
| EAS account, signing custody, budget and external upload | Project owner resolves before stage 5; plan cloud builds first, with no assumed credentials, subscription or host native toolchain. |
| Production audience, identity and store distribution | Project owner resolves in the product production specification before stage 8; private development does not select these. |

Broader RES work, service history, Slack, all dashboard controls and general runtime
garbage collection are independent tracks, not prerequisites for M1. Production
recovery requirements must be explicitly satisfied in stage 8 regardless of those
earlier deferrals. Preserve existing live applications and unrelated work through
all implementation, fixture cleanup and acceptance.

## Primary references checked for this plan

Technical guidance was checked October 13, 2026. Recheck versions, account/device
rules and distribution settings when writing the corresponding specification.
The stage design above is a proposal derived from current platform contracts.

- [Expo development builds](https://docs.expo.dev/develop/development-builds/introduction/): native development clients and cloud versus local compilation.
- [Expo CLI](https://docs.expo.dev/more/expo-cli/): Metro, device launch and development-session behavior.
- [Expo client environment variables](https://docs.expo.dev/guides/environment-variables/) and [EAS environments](https://docs.expo.dev/eas/environment-variables/): public bundle configuration versus server/build credentials.
- [EAS internal distribution](https://docs.expo.dev/build/internal-distribution/): install artifacts, access settings and iOS device provisioning.
- [EAS runtime versions](https://docs.expo.dev/eas-update/runtime-versions/): native compatibility, new binaries and update rollout/rollback.
