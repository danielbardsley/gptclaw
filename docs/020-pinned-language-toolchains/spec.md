# SPEC-020: Pinned language toolchains (SYS-002)

- **Status:** Implementation authorized; initial web slice implemented, verification in progress
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Feature:** SYS-002; initial Node/pnpm web slice
- **Design:** [TDD-020](technical-design.md)
- **Tasks:** [TASKS-020](tasks.md)
- **Context:** [Sequence, stage 2](../platform/sequence.md#2-install-the-minimum-supported-execution-environment) · [Architecture](../platform/architecture.md)

## Outcome and scope

A project declares a supported, exact Node/pnpm toolchain and the platform obtains
and verifies it automatically inside a rootless container. New apps need no host
Node/npm installation or manual version switching. One app's version choice
cannot change another app's selected image or the host's tools. Unknown versions
fail clearly instead of fetching latest or silently falling back.

[SPEC-018](../018-first-private-application/acceptance.md) already supplies one
working fixed toolchain. This initiative adds project selection, a supported
profile matrix, verified acquisition/receipts, compatibility migration and
version-aware lifecycle integration. It reuses that runtime and template.
The starting pair observed in source is Node 24.21.0 / pnpm 12.10.1; these are
existing reviewed pins, not a recommendation for an unverified latest release.

Include one versioned project declaration separate from manifest v1, a strict
platform-owned profile registry, initial web profile, automatic container-only
prepare/verification, inspectable results, consistent build/test/start use,
new-project metadata and explicit legacy compatibility. The profile model must
permit a later supported pair without rewriting existing profile revisions;
prove distinct-profile handling in tests. Do not require a new language or
version solely to expand today's scope.

[SYS-003 / SPEC-019](../019-project-dependency-policy/spec.md) owns dependency
sources, hooks, package changes and frozen installation. Its adapter was accepted and merged in PR #46 before this implementation. The
resolver reuses that policy for automatic dependency preparation; it does not
duplicate or loosen dependency rules.

Python/uv is explicitly deferred to the sequence's stage 12, alongside the
selected Python template. Expo and other stacks extend the supported matrix in
their own initiatives. Record those obligations rather than claiming full
multi-language SYS-002 delivery from this initial web slice.

Exclude host tool/profile changes, Terraform installation, arbitrary versions or
image URLs supplied by projects, package-manager self-update, automatic upgrades,
framework/template expansion, shared caches/pruning, databases/secrets, new AWS
resources, production and public exposure. These controls do not isolate hostile
projects sharing forge's identity.

## Requirements

- **LNG-001 — Exact project selection.** Define a strict versioned non-executable
  declaration that selects a supported profile revision and exact Node/pnpm
  versions. Unknown fields/types/profiles, ranges/latest, unsafe paths and
  contradictory package-manager/runtime metadata fail before download or build.
  Keep `.gptclaw/project.yaml` v1 unchanged and its unknown-field rejection intact.
- **LNG-002 — Reviewed support matrix.** Platform source owns immutable profile
  revisions, supported OS/architecture, exact versions, OCI base digest, package
  artifact integrity and version checks. Start from the existing web pair after
  implementation-time verification. Project files cannot supply installer scripts,
  mirrors, fallback versions or arbitrary container images. A newly supported
  pair is an explicit reviewed profile addition with tests and ownership.
- **LNG-003 — Automatic bounded acquisition.** On first use, obtain/build the
  selected image through rootless container operations and verify integrity and
  actual executables before use. Reuse only a matching verified artifact; reject
  conflicting cache/provenance, missing pinned artifacts, integrity mismatch and
  unsupported platforms without fallback. Serialize acquisition of one profile;
  bound jobs/output/time. No host language installs, sudo or credential mounts.
- **LNG-004 — Consistent operation and isolation.** Dependency preparation,
  build/test and the app service use the same selected image/tool versions.
  Integrate with SYS-003 and existing project locks/health/routing. Version changes
  invalidate affected prepared/build state; require the selected app to be
  stopped for a toolchain switch, preserving its source and leaving another app
  unchanged. Package-manager config must not silently select/download a different
  runtime or package manager behind the resolver.
- **LNG-005 — Compatibility and inspection.** New apps receive an explicit
  declaration. Existing SPEC-018 apps without one keep a documented frozen legacy
  selection and are not rewritten by normal start/inspect. Provide explicit
  adoption instructions and observation-only inspection of declared/selected/
  verified state. Record profile/image/version provenance outside authored
  manifests; never imply an image was obtained from an unexecuted plan.
- **LNG-006 — Reproducible verification and ownership.** Record exact resolved
  versions/artifacts, commands, CI and live acceptance. Prove uncached acquisition,
  verified reuse, failure behavior, legacy/new project use and per-project
  selection. A profile upgrade/retirement has compatibility and rollback steps;
  it does not auto-upgrade running apps. Document Python/uv/Expo follow-up owners.

## Acceptance criteria

| ID | Observable result and evidence | Requirements |
|---|---|---|
| AC-001 | Offline validation accepts the exact supported declaration and rejects malformed/unknown/ranged/conflicting selections without network or execution. Manifest v1 validation is unchanged. | LNG-001 |
| AC-002 | A checked-in web profile has verified exact versions, OCI digest and package artifact integrity; actual supported platform is recorded. Unsupported sources/platforms cannot select fallback. | LNG-002 |
| AC-003 | Task-owned uncached preparation succeeds and reports actual versions/image; matching reuse succeeds. Concurrent acquisition is serialized; missing artifact, bad integrity or conflicting cache fails without host installation. | LNG-003 |
| AC-004 | A new synthetic app installs frozen dependencies, builds/tests and runs privately with the selected pair. A toolchain change invalidates only its state; another app's source/image/health/route is unchanged. Distinct-profile selection is exercised with reviewed fixture profiles, even if only one real pair ships initially. | LNG-004 |
| AC-005 | Legacy no-declaration app works with an explicit legacy receipt; new app carries exact metadata. Inspect is observation-only. Explicit adoption preserves source/lockfiles and mismatch errors do not rewrite them. | LNG-001, LNG-005 |
| AC-006 | Focused/local and configured CI checks plus live install/build/test/version evidence pass; Daniel accepts the initial web slice. Matrix, runbook, migration/rollback and later-language responsibilities are merged. | LNG-006 |

## Completion and decisions

Daniel authorized implementation with “Ok, let's implement SYS-002” on October
10 after SYS-003 delivery. The supplementary declaration/profile registry,
container-only execution and existing pair are implemented. Source artifact
integrity and actual installed versions were verified on Linux amd64 before live
app acceptance. [Acceptance evidence](acceptance.md) separates offline tests,
CI, observed EC2 behavior and remaining owner review/merge. Delivered applies
only to the accepted Node/pnpm slice after merge and AC-001–006 pass; later
language support stays explicit.
