# Create and check React Native / Expo projects

[SPEC-031](../docs/031-expo-project-creation/spec.md) adds the `expo-react-native@1.0.1`
source starter. Published 1.0.0 remains immutable; 1.0.1 fixes generated CI checkout
permissions. Provider 1.10.1 supports mobile manifest/catalogue schema 5 and native
source quality jobs; consult the acceptance record for actual installed status.
Run as forge with the prepared isolated Python environment and reviewed rootless
Node/pnpm toolchain. No host native SDK, Expo login or signing account is required.

## Exact creation

From a checkout containing this implementation, use `scripts/gptclawctl`, or the
installed stable launcher after its recorded refresh:

```text
/srv/forge/projects/.gptclaw-runtime/v1/gptclawctl
```

Check `--version`, then inspect and select the release explicitly:

```sh
gptclawctl templates show --template expo-react-native --template-version 1.0.1
gptclawctl new example-mobile --template expo-react-native --template-version 1.0.1 --local-only
gptclawctl validate --project-root /srv/forge/projects/example-mobile
```

Use the existing activated GitHub App workflow for a private repository instead of
`--local-only`. First review `new ... --plan`: exact release, identities/destination,
private visibility, initial branch/PR and scope matter. The new repository must be
in the existing explicit workflow-publication policy before a workflow is published;
this does not broaden the App's grants. Existing protections/recorded private-dev
waiver and per-repository credentials retain their actual semantics. Do not infer
protection enforcement from a successful create. Local-only bypasses credentials.
Creation copies verified source and metadata only, performs no package installation,
launches no server and leaves the unselected default as the existing web template.

Development identity derives from the slug: `dev.gptclaw.<slug>` on iOS, with hyphens
converted to underscores in the Android suffix, and scheme `gptclaw-<slug>`. These
are public development IDs, not registered store identity. Static `app.json` and the
manifest must remain consistent. Registered IDs/configuration, backend binding,
Metro transport and signed builds require their later mobile contracts.

## Preparation and quality

```sh
gptclawctl toolchain inspect --project-root /srv/forge/projects/example-mobile
gptclawctl toolchain prepare --project-root /srv/forge/projects/example-mobile
gptclawctl deps status --project-root /srv/forge/projects/example-mobile
gptclawctl deps install --project-root /srv/forge/projects/example-mobile
gptclawctl format --project-root /srv/forge/projects/example-mobile
gptclawctl verify --project-root /srv/forge/projects/example-mobile
```

The reviewed profile is Node 24.21.0/pnpm 12.10.1, with Expo 57.0.28, React Native
0.86.3 and React 19.2.3. The full pinned package matrix is in
[the mobile profile](../config/mobile/v1.json), with frozen inputs and public npm
integrities in the starter lock. Real verification established the isolated pnpm
layout, so no hoisted-layout or install-script exception is enabled. Five named,
exact public transitive lock aliases are allowed only by the mobile profile;
web/API policy is unchanged. SDK/core package changes and unknown native/config
plugins are refused. The initial additional pure-JS allowlist supports exact
`zod@4.3.6`; use typed add/update/remove, not a remote `expo install --fix`.

`verify` runs format-check, lint (warnings fail), strict types, interaction tests,
SDK coherence, security and both iOS/Android exports. Individual test/build/lint/
typecheck/security commands use the same owned bounded jobs. `format` changes
source; public generated metadata and dependency files have separate validators.
Quality can prepare missing frozen dependencies and reports its outcome. Mobile
jobs use no HTTP port or unit and cannot stop a shared backend. `build` emits
JavaScript/assets under ignored `.gptclaw-build/`, not APK/IPA binaries or device
acceptance. Generated CI uses the same exact toolchain and gates.

## Security policy and recovery

Two exact tooling advisory exceptions were explicitly approved by the project owner:
node-forge 1.4.0 / GHSA-86w9-cpqp-85rv and braces 3.0.3 / GHSA-vfj7-8cjw-p6xm. They
expire at the end of October 27, 2026 (America/New_York). They apply only to bounded
source-check/export jobs, with no signing, exposed Metro, device release or production
scope. Unexpected high/critical findings, changed affected versions, incomplete audit
responses, network failure or expiry block security verification. Moderate findings
remain visible. These exceptions do not claim patched packages. The owner owns
follow-through; adopt a patched reviewed release/remove exceptions or obtain a fresh
explicit disposition before expiry. See [the approved security review](../docs/031-expo-project-creation/security-review.md).

On a dependency failure or timeout, inspect `deps status` and recover that exact
recorded operation ID using the existing [dependency runbook](manage-project-dependencies.md).
Conflicting jobs block new work. Recovery/abort preserves concurrent edits; no
unknown container, staging directory or source is deleted. Creation failure reports
an owned retained staging path for inspection; retry at a new empty destination or
follow the reviewed recovery outcome. Repository ambiguity uses its existing typed
resume flow, never blind repeated creation or deletion.

Provider rollback retains source and new-job receipts; older providers reject
schema 5. Reconcile pending mobile jobs using the capable snapshot before selecting
an earlier provider. Use the existing owned refresh path; collector/frontend releases
are refreshed separately through the [dashboard manager](manage-dashboard.md), since
its provider is frozen. The dashboard lists native source with unavailable runtime
and repository links when recorded. It does not claim a running app or invent URLs.

Metro start/stop/restart/status/observe/logs, mobile DB commands, native prebuild,
EAS and store operations are deliberately unsupported in this slice. Keep source
and the small intentional examples for starter verification; replace demo content,
routes, assets and tests against a selected product's spec before product acceptance.
