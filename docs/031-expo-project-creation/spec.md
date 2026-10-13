# SPEC-031: Repeatable Expo / React Native project creation

- **Status:** Approved for implementation — work in progress
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Feature:** MOB-001
- **Supporting slices:** TPL-004; PRJ-001/002/003/004/005; SYS-002/003; QLT-001/002/009; DSH-001 inventory compatibility
- **Design:** [TDD-031](technical-design.md) · **Tasks:** [TASKS-031](tasks.md)
- **Direction:** [Mobile sequence](../platform/sequence-mobile.md) · [Catalogue](../platform/features.md)

## Outcome and scope

The development platform can consistently create a new native iOS/Android React
Native application using Expo, Expo Router and TypeScript through the same reviewed
`gptclawctl new` workflow used for web projects. An exact starter release produces
reviewable source, coherent dependency/toolchain pins, standard quality commands,
project guidance and optional private GitHub provisioning. Creating a second app
requires no copied configuration, hand-installed host tools or new account setup.

The project owner requested a MOB-001 specification on October 13, emphasizing
reliable, consistent platform creation. The owner subsequently approved this spec and authorized implementation with
“Ok, let's implement the spec. looks good.” Scope includes the creation foundation
and its supporting interfaces; device/runtime/release follow-ups remain separate.
The mobile sequence is a planning dependency in PR #73; its broader milestones
are not implementation approval. This initiative selects the creation foundation
from sequence stages 1/3, rather than the entire private-device milestone M1.

Include the minimum repository-owned Expo starter, mobile manifest/provider
capability, catalogue integration, dependency/toolchain preparation, Linux-container
quality/bundle verification, repository broker integration, recovery, compatibility
and honest dashboard inventory. A backend is optional future composition: this
slice creates a standalone mobile source project and does not provision or bind an
API/database. Existing FastAPI/PostgreSQL workflows remain available unchanged;
MOB-010 will define their explicit mobile binding and API/DB-only extensions.

Exclude managed Metro sessions/device transport (MOB-002/003), signing/native
compilation and installation (MOB-004/006), backend integration (MOB-010), device
end-to-end acceptance (MOB-011), web hosting (MOB-008), release dashboard state,
EAS accounts/builds/updates, production and public exposure. Generated JavaScript/
asset bundles are not signed application binaries. TPL-004's full native-device
acceptance remains a follow-up; completing MOB-001 does not complete M1 or TPL-004.

## Existing contracts and boundaries

- Provider 1.9.0 currently understands manifest schemas 1–4 and kinds web/API/group.
  It has no accepted mobile creation/quality adapter. Schema 4 requires web/API/DB.
- SPEC-021's immutable catalogue/generation, SPEC-020's toolchain selection,
  SPEC-019's dependency transactions and SPEC-022/023's private repository/broker
  operations are the reuse points. They need bounded mobile extensions, not
  replacement systems. Read current source/runbooks as well as historical designs.
- `new --local-only` remains offline source generation; dependency/toolchain
  acquisition and checks are separate explicit operations. Existing unselected
  `new` continues to select the existing web default.
- Runtime receipts, credentials and data remain outside source. Creation cannot
  stop/start existing apps, allocate HTTP ports or change AWS/Tailscale configuration.
  Native app identities are public metadata, not credentials or store registration.
- Use synthetic fixtures; preserve Shelfmark, Trailboard and unrelated source/data.
  Existing host/client/recovery acceptance and resilience deferrals remain separate.

## Requirements

### EXPO-001 — Exact, immutable native starter

Discover and select a proposed `expo-react-native@1.0.0` release through existing
`templates list/show` and `new --template/--template-version` interfaces. Publish
reviewed source, bounded file inventory/digests, licenses/provenance and a compatible
exact SDK/React Native/React/Router/Node/pnpm/test-tool matrix. No `latest`, ranges,
remote generator or arbitrary template hook runs during creation. Existing releases
and the web default remain unchanged; new starter content needs a new release.

### EXPO-002 — First-class mobile source contract and identity

Add an explicitly versioned mobile manifest with `project.kind: mobile`, supported
iOS/Android targets and standard quality commands. No pretend HTTP health path,
listening port, private app URL or runtime readiness is declared. Validate project,
Expo slug/display name, URL scheme and iOS/Android identifiers consistently. Two
valid project slugs generate distinct development identities by documented fixed
substitution; reject ambiguity/collisions under the provider's known local scope.
Store ownership/availability of production IDs is not inferred. Normal app edits
remain allowed without requiring source bytes to match the original starter.

### EXPO-003 — Deterministic, non-destructive generation

Preserve existing destination/path/no-follow bounds and exclusive staged publication.
Validate release and generated contracts before publishing source. Two creations
from one release have equivalent tracked bytes after documented identity
normalization. Unknown selection, tampering, invalid slugs, occupied destinations,
symlink/race or concurrent creation fail without overwriting content. Interrupted
operations report a recoverable owned outcome; no blind retry/delete/adoption occurs.
`new` creates no node_modules, image, server, route, native binary or external account.

### EXPO-004 — Pinned tools and frozen dependency preparation

Use the reviewed rootless toolchain acquisition and dependency interfaces. New apps
record exact compatible Node/pnpm and dependency policy/profile selections; do not
assume the web pair supports Expo or silently alter that pair. Preparation uses the
lockfile, approved public registry, bounded jobs and recorded receipts. No host
Node/Android/iOS packages, global Expo install or credentials are needed.

Apply SDK compatibility checks to add/update/remove proposals before publication;
unsupported native modules/config plugins or changed policy files fail explicitly.
Preserve transactional recovery and concurrent user edits. A narrow reviewed
installation-script exception, if genuinely needed, must name exact packages and
hashes in the mobile policy; never enable all scripts or weaken web/API policy.
SDK upgrades and native regeneration are separate reviewed work.

### EXPO-005 — Useful native source and standard quality workflow

The starter contains native components, Router navigation, an accessible interactive
screen with a tested state change, safe-area/keyboard conventions, local assets and
strict TypeScript. It contains no web DOM assumptions, fake backend, bundled secrets,
remote runtime fonts or unrelated upstream demo routes. Its purpose is a small
synthetic starter; deliberately retained examples are documented.

Expose format, lint, typecheck, test, build, security and verify through reviewed
container jobs. Format is a source mutation; verification is read-only except owned
ignored artifacts/caches. Tests use Expo-compatible Jest/React Native Testing Library
and verify interaction rather than only snapshots. Build exports both iOS and Android
JavaScript/assets and labels the result as bundles. Verify SDK/dependency coherence,
static app config and absence of unexpected native/generated/authentication material.
No quality command launches an exposed Metro server or uploads source.

### EXPO-006 — Repeatable private repository workflow

Use the activated broker's existing new-project plan/apply/resume semantics and
per-repository credential bindings. Include the exact mobile release, generated
identity and configuration hashes in the plan/fingerprint before remote publication;
changed inputs require a new plan. Retain local-only creation, explicit private
visibility, initial app PR, protections/recorded waiver behavior and interrupted
operation recovery. Repeated creation needs no new PAT, Expo login or signing keys.
Denied provisioning never silently switches account, visibility or credentials.

### EXPO-007 — Generated guidance, CI and future extension contract

Generate adapted repository guidance, README, mobile engineering/style guide,
architecture note, ignored outputs and a pinned minimal-permission PR workflow.
Document how to create, install frozen dependencies, check/edit and recover, what
`build` means and which lifecycle/backend/device commands are not yet supported.
All tooling versions come from the selected release, with no transient remote CLI.
CI runs the same formatter/lint/type/tests/SDK/bundle/security gates without signing,
backend or production credentials. Fork/untrusted PRs receive no broker secrets.

Use Expo continuous native generation as the first ownership model: native source
is derived, absent from the starter and regenerated only through later reviewed
operations. Do not run clean prebuild or delete hand-written native code in this
slice. Dynamic app config and arbitrary config plugins are unsupported initially.
No inherited upstream instructions or automatic agent/plugin configuration may
replace GptClaw's reviewed guidance. Future product adaptation must remove demo
content outside that product's scope and test its actual UI/API behavior.

### EXPO-008 — Honest inventory and capability behavior

A new mobile manifest appears once in dashboard discovery with mobile kind, source/
documentation metadata and repository link when available. Creation/quality support
must be distinct from HTTP lifecycle support. Runtime/launch links clearly say the
mobile development runtime is not yet supported; no fabricated ready/stopped service,
web/API component or URL is shown. Existing dashboard observation payloads remain
bounded and credential-free. Unsupported mobile start/stop/restart/observe/logs and
DB actions fail without reserving ports, generating units or changing a backend.

### EXPO-009 — Provider packaging, compatibility and delivery evidence

Source and installed immutable providers carry the same mobile release, schemas,
policies, tools and capability declarations. No existing manifest/release/data is
rewritten during install or rollback. Older providers explicitly reject new mobile
contracts while preserving source; operators retain the capable snapshot for job
reconciliation. Golden tests exercise two creations, failure recovery and existing
web/API/group/DB regression paths. Record local, CI, installed-provider and owner
acceptance separately, including any unrecorded device/binary capabilities.

## Acceptance criteria

| ID | Required observable evidence | Requirements |
|---|---|---|
| AC-001 | Deterministic list/show; explicit release selection; checksum/schema/path rejection before writes; published release immutability; web default and historical releases unchanged. | EXPO-001 |
| AC-002 | Two mobile manifests validate; distinct normalized identities match static Expo config; source edits remain valid; malformed or colliding identities and unsupported fields are rejected. No HTTP port/route/health contract is generated. | EXPO-002 |
| AC-003 | Two local creations have equivalent normalized tracked inventories. Network/execution/write spies prove no generator/download/start/account mutation during local creation. Destination/race/tamper/concurrency/failure fixtures preserve unrelated content and yield owned recovery results. | EXPO-001/003 |
| AC-004 | Exact profile verified in real rootless jobs; frozen install succeeds from empty project caches and repeats without lock/config changes. Corrupt lock, incompatible SDK/package, script/config-plugin policy violation and interrupted preparation are denied/reconciled without losing edits. | EXPO-004 |
| AC-005 | Both generated apps pass format-check/lint/type/test/security/SDK checks and iOS/Android bundle export. Interaction tests fail on a representative behavior defect; lint/type/style defects are rejected. No signed binary/native-device claim is made from these results. | EXPO-005 |
| AC-006 | Activated broker creates two distinct private mobile repositories with exact starter revisions and initial PRs; bindings and protection/readback or existing explicit waiver evidence match policy. Denial/lost-response/resume fixtures do not duplicate repositories/PRs or publish changed plans. | EXPO-006 |
| AC-007 | Generated guidance/CI/version metadata agree. Final-head CI on a generated mobile repository executes the locked gates with minimal permissions and no secret/native-build dependency; intentional generated-source behavior defect fails its relevant check. | EXPO-005/007 |
| AC-008 | Actual private dashboard shows both mobile source rows with honest runtime unavailability and valid recorded repository links. Existing ready web/API/DB project observations and links remain correct. Mobile lifecycle attempts leave units, ports, routes and data unchanged. | EXPO-008 |
| AC-009 | Source/installed list/show/new/validate/quality agree; capable-provider refresh/rollback preserves existing apps and receipts, with explicit older-provider rejection. Full relevant repository/frontend regression gates and configured CI pass; sanitized evidence records owner confirmation of the creation/edit/check workflow. | EXPO-009 |

## Completion, decisions and follow-ups

Deliver reviewed implementation, immutable release/profile, generated workflow,
focused/golden tests and an Expo-creation runbook through a PR. Prepare owned
synthetic acceptance targets after implementation authorization, record their exact
IDs/source/profile hashes and fixture-retention disposition, and leave existing apps
untouched. Mark only MOB-001 Delivered after merge and AC-001–009 pass; retain
TPL-004's native-device/remaining scope and all M1/M2/M3/M4 work as follow-ups.
No acceptance file exists yet because no implementation checks have been run.

The implementation author must first propose and verify the exact Expo-compatible
matrix, attach the evidence and exact pins to this design/implementation PR before
freezing the release, and obtain disposition for any package-script exception or
change outside the approved scope. Routine compatible pin selection is an
implementation decision, not a separate owner approval gate.
Proposed schema/catalogue version 5 is available at this drafting baseline; recheck
before implementation and choose a new version if another initiative occupies it.
Development IDs use a documented development-only namespace (see design); project
owners choose registered production IDs in later environment/release work.

Next specifications: MOB-002 for owned private Metro/device access, MOB-010 for
FastAPI/PostgreSQL binding, then MOB-004/006 for installed native builds, following
[the mobile sequence](../platform/sequence-mobile.md). The creation initiative
leaves extension points but adds no dummy configuration for those capabilities.
