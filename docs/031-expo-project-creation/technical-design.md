# TDD-031: Expo creation through the existing project platform

- **Status:** Delivered — implementation merged and owner accepted
- **Owner:** Project owner
- **Date:** 2026-10-13 (America/New_York)
- **Specification:** [SPEC-031](spec.md) · **Tasks:** [TASKS-031](tasks.md)

## Approach and existing integration points

Extend the current resolver/generator, validator, Node toolchain/dependency policy,
GitHub broker and provider bundle. Publish `expo-react-native@1.0.0` with provider
marker `expo-v1`; do not call `create-expo-app` at user creation time. A versioned
upstream scaffold may be used once during reviewed release authoring, with its
origin/licenses recorded, then reduced to the specified starter and frozen locally.
Upstream generated agent/plugin configuration is not automatically adopted.

Creation remains source-only. Explicit dependency/quality operations use bounded
rootless jobs, and repository provisioning follows existing broker operations.
There is no Metro daemon, service/route reservation, native compilation or EAS
call. The proposed sequence is:

```text
exact release + slug -> resolve/verify bundled assets
                    -> derive static public identities
                    -> stage source + manifest + toolchain + provenance
                    -> validate -> exclusive non-overwrite publication
                    -> local result OR existing private repository/initial PR flow

explicit preparation/check -> approved pinned rootless job -> bounded receipt
mobile manifest discovery  -> source inventory + unsupported runtime explanation
```

Planning baseline: `scripts/project_templates.py` merges catalogues 1–4 and has
provider-specific generation/validation branches; its generic fallback assumes
Next.js. `private_apps.quality_app()` reserves HTTP runtime state, so mobile quality
must be dispatched before that path. `project_toolchains.selection()` currently
ties Node selection to the dependency policy's pnpm version. The mobile extension
must select a compatible policy/profile explicitly, without changing web defaults.
Repository plans/fingerprints and immutable provider inventories must include new
identity inputs. Dashboard discovery currently treats manifest schema support as
runtime support; mobile needs separate capability semantics.

## Proposed user interface

Retain existing selection flags and stable structured results; new commands are
illustrative interfaces to implement, not currently installed capabilities:

```text
gptclawctl templates show --template expo-react-native --template-version 1.0.0
gptclawctl new example-mobile --template expo-react-native --template-version 1.0.0 --local-only
gptclawctl new example-mobile --template expo-react-native --template-version 1.0.0 --plan
gptclawctl new example-mobile --template expo-react-native --template-version 1.0.0
gptclawctl validate --project-root /srv/forge/projects/example-mobile
gptclawctl toolchain inspect --project-root /srv/forge/projects/example-mobile
gptclawctl deps install --project-root /srv/forge/projects/example-mobile
gptclawctl verify --project-root /srv/forge/projects/example-mobile
```

The no-local-only form retains current activated-broker behavior and policy
preconditions; it does not create EAS projects. Keep the unselected web default.
Use the existing typed format/lint/typecheck/test/build/security/verify verbs.
Local new/validate/discovery acquire no tools or credentials. Quality may prepare
frozen dependencies only through the existing explicit job contract; results must
state any preparation performed and selected image/profile.

## Manifest, catalogue and identity

Propose project/catalogue schema 5, without edits to published 1–4 contracts.
Manifest fields are a strict object: `schema_version`, `project` (id/name/kind),
`mobile` (fixed adapter `expo-v1`, targets `ios`/`android`, static config path
`app.json`) and standard `commands` argument vectors. Toolchain and template
provenance use existing `.gptclaw` sidecars. There is no `service`, `exposure`,
`data` or backend selector in this slice. The validator accepts only supported
fixed targets/paths, bounded strings/argv and no secrets/environment maps.

Generation writes static JSON config without evaluating repository JavaScript.
Identity mapping: display name follows the existing slug-to-title rule; Expo slug
is the project ID; URL scheme is `gptclaw-<id>`; initial iOS bundle ID is
`dev.gptclaw.<id>`; Android application ID is
`dev.gptclaw.<id with hyphens replaced by underscores>`. Apple permits hyphens but
not underscores in bundle IDs; Android permits underscores but not hyphens in
application-ID segments. Existing slug grammar contains no underscores, making
the Android mapping unambiguous, while iOS preserves the slug. These are
explicit development identities, not a claim of domain ownership, Apple/Google
registration or production uniqueness. Reject conflicts within known owned project
metadata; do not scan credentials, unrelated roots or external stores. Later
registered ID selection belongs to MOB-005/006, not a required flag here.

Document exactly which bytes vary: project manifest id/name and the named static
JSON identity fields. App edits remain valid after creation; provenance continues
to identify original release bytes rather than freezing the current checkout.
Generation fails before publication on invalid/mismatching identity/config,
provenance, lock, policy or toolchain references. Extend catalogue substitutions
with typed fixed fields, never expression evaluation or arbitrary templates.

Add a mobile catalogue extension with exact policy/toolchain references, SDK
compatibility metadata, targets, creation/quality capabilities and explicit absent
runtime/build-release capabilities. Preserve current default and inventories;
recheck version 5 availability before code work. Extend published-release
immutability checks and provider packaging together.

## Starter and exact tool/dependency support

Proposed minimal layout:

```text
.gptclaw/                 manifest, provider/release, toolchain/policy metadata
src/app/                 Router layout and two small native screens
src/components/          repository-owned interactive accessible example
src/config/              public configuration validation only
assets/                  local icons/images with provenance
tests/                   behavior tests, outside the Router app directory
checks/                  fixed bounded quality orchestration
app.json                 static development identity/targets
package.json             exact versions and standard scripts
pnpm-lock.yaml           complete frozen dependency graph
pnpm-workspace.yaml      reviewed linker/script policy
AGENTS.md, README.md      commands, limitations and product-adaptation guidance
docs/                    architecture and mobile engineering standards
.github/workflows/       pinned least-permission PR verification
```

Select one exact SDK/React Native/React/Router/Jest/Testing-Library matrix and a
compatible Node/pnpm profile, verifying official Expo compatibility and actual
rootless jobs. Record real versions/digests before release freeze; no invented
pins, floating generator or automatic package-manager migration. Pin Expo CLI
through the Expo package and diagnostic tooling explicitly. EAS CLI is not needed
in this creation slice. If current Node/pnpm policy works, reuse it; otherwise add
an explicitly versioned mobile policy/profile with compatible selection dispatch.
Do not retarget existing projects or mutate registry entries already published.

Use a reviewed pnpm layout proven with the chosen SDK (propose hoisted as the
initial conservative layout). Frozen installation disables arbitrary scripts,
remote config hooks, exotic/unapproved sources and dotenv/auth forwarding. Check
SDK package compatibility against a frozen reviewed matrix, with a pinned diagnostic
job during release verification. If a diagnostic needs network, bound/report that
access and fail on unavailable required evidence; do not fetch an unpinned tool or
silently fix dependencies. Package add/update/remove must stage/review/check before
publishing coherent source and report unsupported SDK/config-plugin changes.

Native directories are derived under Expo continuous native generation and absent
from the starter. Do not expose prebuild/clean regeneration in platform commands.
A checked-in/hand-edited native tree or dynamic app config produces an explicit
unsupported result for this adapter, without deletion. Future native support must
add its own ownership and preservation contract.

## Quality jobs and artifacts

Add a mobile dispatcher using shared path/lock/job/receipt mechanisms. Do not call
HTTP `reserve()` just to get a job descriptor. Give jobs deterministic project/
operation ownership, no port/unit/ingress state, finite CPU/memory/PID/time/output
limits and the exact verified image. Mount only the selected source/cache inputs;
no forge home, credentials, runtime data or engine socket. Reuse dependency staging,
source-digest guards and interrupted-operation reconciliation. A timed-out unknown
job blocks conflicting work until its owned outcome is reconciled.

Use Expo-compatible Jest and React Native Testing Library for interaction/navigation
coverage, ESLint/Prettier and strict TypeScript. The starter has a small synthetic
state example, no remote backend fixture disguised as a real integration. Quality
runs static public-config checks, SDK/lock coherence, secret-pattern/dependency
checks and explicit iOS/Android bundle export. `build` means JS/assets, not APK/IPA.
Store outputs in ignored project-owned directories; do not promise byte-identical
bundle artifacts where tool output embeds paths/timestamps. Determinism acceptance
concerns normalized source, dependency inputs, selected tools and recorded outcomes.
CI uses equivalent reviewed container inputs/actions, not broad cloud credentials.

Initial proposed bounds reuse the current single-job 1 CPU/1536 MiB/256 PID and
300-second ceilings, with serial quality/bundle steps. Measure cold-cache install
and both exports before committing release support; any required bounded change
is recorded and reviewed, never an unbounded retry or host resize. Template file
bounds stay within existing catalogue limits unless reviewed evidence requires an
extension. Local/golden checks run without a serving Metro listener.

## Repository and dashboard integration

Repository plans must bind release digest, normalized mobile identities, policy,
toolchain and destination so reviewed generation matches published source. Existing
create/resume/binding/initial-PR logic stays authoritative. Use a single scoped
GitHub credential handoff; no Expo credentials. Denial or ambiguous remote response
preserves journal/source for existing typed recovery; never delete a remote repo as
rollback. Two real private fixture repositories are acceptance targets only after
implementation/live scope is authorized; retain/archive them according to the owner
instead of silently deleting them.

Inventory safely validates schema 5 and shows a mobile source row. Separate
`creation/quality support` from `development runtime support` in provider/collector
capability data. Prefer an additive optional capability declaration with backward
compatibility; version payloads explicitly if new distinctions require it. Existing
schemas 1–4 retain their accepted meaning. Mobile status is unavailable because the
runtime adapter is absent, not a timed-out/stopped HTTP process. Keep repository
links independent of runtime readiness and private app/API-doc links unavailable.
Add only the minimal display/validation changes; no Metro/device/build telemetry.

## Components and traceability

| Component / proposed change | Requirements | Tasks | Acceptance |
|---|---|---|---|
| New schema/catalogue/release and typed substitutions | EXPO-001, EXPO-002 | T-002, T-003, T-004 | AC-001, AC-002 |
| Resolver/generator, staging/publication, provenance | EXPO-001, EXPO-003 | T-004 | AC-001, AC-003 |
| Node/toolchain policy selection and mobile dependencies | EXPO-004 | T-002, T-005 | AC-004 |
| Mobile job dispatch, native source, tests and bundles | EXPO-005 | T-003, T-006 | AC-005 |
| GitHub plans/broker/initial PR and interrupted recovery | EXPO-006 | T-007 | AC-006 |
| Generated guidance/workflow/runbook/adaptation conventions | EXPO-007 | T-003, T-008 | AC-007 |
| Provider capabilities, collector/frontend compatibility | EXPO-008 | T-009 | AC-008 |
| Immutable bundles, compatibility/regressions and acceptance | EXPO-009 | T-010, T-011, T-012 | AC-009 |

## Rollout, verification and remaining decisions

Deliver source/CI checks first, then prepare/install a reviewed immutable provider
through the existing owned refresh path. A dashboard collector using a frozen
provider must receive a separately prepared owned release with schema-5 capability;
refreshing the CLI alone does not refresh that collector. Record both exact release
identities and use the existing dashboard activation/rollback runbook. No AWS,
host-policy, mount, Serve or security-control change is required.

Verify source and installed creation/checks twice, generated-repository CI, actual
private dashboard inventory and observation-only checks on existing live apps.
Provider and dashboard rollback select retained reviewed snapshots independently;
mobile source may be unsupported by the older snapshots and must remain intact.
Before rolling back while a mobile job is unresolved, reconcile it with the capable
snapshot. Rollback does not undo app commits, dependency edits or remote creation.

| Decision / unknown | Owner and resolution gate |
|---|---|
| Exact SDK/package/toolchain matrix and script exceptions | Implementation author collects compatibility and real-job evidence; record exact verified pins in the implementation PR before freeze (T-002). Owner disposition is needed for any policy exception or scope change, not routine version selection. |
| Manifest/catalogue version and additive capability encoding | Implementation author rechecks reservations and consumer compatibility before T-003, T-009; retain schemas 1–4 and version any breaking payload change. |
| Resource bounds for cold install and bundle jobs | Implementation author measures T-002, T-006; any changed ceiling is concrete scope review before live verification. |
| Private fixture names and provisioning authority | Project owner selects/authorizes exact two names in T-011; existing broker policy and retained-fixture waiver gates apply. No account setup is presumed necessary. |

Primary technical references checked October 13, 2026:
[create-expo-app](https://docs.expo.dev/more/create-expo/),
[Expo CLI export](https://docs.expo.dev/more/expo-cli/#exporting),
[unit testing](https://docs.expo.dev/develop/unit-testing/),
[Router tests](https://docs.expo.dev/router/reference/testing/),
[ESLint/Prettier](https://docs.expo.dev/guides/using-eslint/) and
[continuous native generation](https://docs.expo.dev/workflow/continuous-native-generation/),
[Apple bundle identifiers](https://developer.apple.com/documentation/bundleresources/information-property-list/cfbundleidentifier)
and [Android application IDs](https://developer.android.com/build/configure-app-module).
These inform the proposal, not proof that the tools or mobile adapter are installed.


## Implementation decisions recorded October 13

Implementation authorization was supplied by the project owner. Verified the SDK-57
matrix against the integrity-checked Expo package and official starter metadata:
Expo 57.0.28, React Native 0.86.3, React 19.2.3, Router 57.0.26, TypeScript 6.0.3,
Jest 30.5.2/jest-expo 57.0.6, React Native Testing Library 14.1.0 and ESLint 9.39.5.
The initial ESLint-10 trial was incompatible with the React plugin; the final exact
9.x pin passed. Reused Node 24.21.0/pnpm 12.10.1 and the existing verified image.
Real frozen installation/export established isolated dependency layout with install
scripts disabled, so no hoisted layout or script exception was required. Five
exact public lock aliases are validated only for mobile; web policy remains intact.
Details and the pure-JS addition allowlist are in config/mobile/v1.json.

Both native-target exports passed; full source verification passed with the owner's
two exact temporary advisory exceptions, which remain visible and expire October 27.
See security-review.md. Controlled user-event timers and a finite 15-second Jest
case deadline remove dependence on native press timer scheduling under bounded CPU;
assertions/coverage remain enforced. Generated/installed/CI evidence is recorded separately in acceptance.md; all
technical checks passed; implementation merged and owner confirmation is recorded.

Platform verify and golden verification execute serial individually bounded steps
under one operation lock, retaining the existing 300-second job limit. A combined
verification trial timed out under concurrent host checks; the per-step interface
keeps failures attributable without increasing a job's resource/time ceiling.

The owner subsequently approved the exact four-name profile/fixture extension and
archived-binding preservation with “Yes, all approved.” Provider 1.10.1 introduces
credential profile 4 (maximum four names), while profile 3 retains its two-name
bound. Tokens/App grants are unchanged. No wildcard or 64-name scope is included.
Schema/activation/helper compatibility and isolated singleton-token tests precede
actual policy activation and private repository creation.


### Acceptance corrections

Actual private repository CI found a checkout UID mismatch hidden by the earlier
golden helper's Docker flags. Published expo-react-native@1.0.0 remains unchanged;
1.0.1 adds the runner UID/GID to the generated Docker workflow. Future exact creation
should select 1.0.1. The updated golden driver executes the generated workflow command
itself on Docker, and applies the production broker guidance adaptation before all
format/quality checks. A single extra blank line in that adaptation was removed.
Existing private acceptance projects retain 1.0.0 provenance and receive ordinary
reviewed workflow/guidance edits; neither their release metadata nor protected SDK/
toolchain/advisory files is rewritten. Exact package/profile selections are unchanged.
