# SPEC-021: Versioned template catalogue

- **Status:** Draft — scope approval and implementation authorization pending
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Feature:** PRJ-003, initial supported web-entry slice
- **Design:** [TDD-021](technical-design.md) · **Tasks:** [TASKS-021](tasks.md)
- **Direction:** [Sequence](../platform/sequence.md) · [Catalogue](../platform/features.md)

## Outcome

A developer can discover the supported application templates, inspect an exact
release and create a private app from it with recorded provenance. The first
entry packages the existing Next.js/TypeScript starter. Repeated creation from
one release produces the same reviewed source, dependency pins and toolchain
selection apart from documented project identity substitutions.

Daniel requested a PRJ-003 specification. This authorizes planning only. The
proposed first-entry scope needs Daniel's review; implementation is not approved.

## Scope and existing dependencies

Include a versioned, repository-owned catalogue, read-only discovery, exact
release selection in local project creation, release integrity checks, generated
provenance, installed-provider packaging and compatibility with existing apps.
Reuse the delivered SPEC-018 runtime/manifest/private routing, SPEC-019 dependency
policy and SPEC-020 exact Node/pnpm toolchain registry. Their accepted initial
slices provide the required web path; separate host/agent acceptance stays open.

The existing CLI copies `templates/apps/nextjs` and requires the exact legacy
marker `{ "provider": "nextjs-v1" }`. There is no catalogue selection today.
This initiative adds selection without creating a second runtime or inserting
unsupported template fields into manifest v1.

Exclude API, Python, Expo, static-site, CLI and multi-package templates, external
registries/downloadable plugins, arbitrary generators, automatic app upgrades,
GitHub provisioning/credentials, databases/secrets, public sharing, production,
and a dashboard. Broader PRJ-003 coverage follows reviewed stack initiatives.
QLT-001/002 style guides and generated PR workflows remain separate work;
existing template build/test/typecheck checks are reused here. RES work remains
deferred under Daniel's current direction until a useful application exists.

## Requirements

- CAT-001: List supported template IDs and releases, identify the default, and
  show each exact release's description, stack, runtime compatibility, toolchain
  reference, data/exposure limits and provenance. Discovery is observation-only:
  no project execution, container acquisition, network access or runtime changes.
- CAT-002: Publish immutable reviewed releases with an explicit catalogue schema,
  unique IDs/exact versions, bounded safe file inventory, content digests and
  documented identity substitutions. Invalid metadata, paths, duplicate entries,
  missing files, integrity failures and unsupported compatibility fail before
  creating a destination. New release content requires a new version.
- CAT-003: Extend `new` with explicit template/version selection. No-selection
  creation keeps working using the catalogue's recorded default. Unknown,
  unavailable, ranged or mismatched selections fail without fallback. Existing
  destinations and unrelated files are never overwritten; partial generation
  cannot be mistaken for a complete app and has an owned recovery outcome.
- CAT-004: Generated apps retain manifest v1, the dependency policy and exact
  supported toolchain declaration; record selected release and content digest
  separately from the legacy runtime provider marker. Keep existing legacy apps
  runnable without edits or fabricated provenance. Reject malformed or conflicting
  new metadata before lifecycle execution. App source edits remain allowed;
  provenance identifies the starter, not the current application's file hashes.
- CAT-005: Source and installed immutable provider bundles carry the same release
  catalogue, assets and validation rules. Existing snapshots remain internally
  consistent; a new default affects only future creation. No existing app changes
  template or toolchain implicitly, including after a provider update or rollback.
- CAT-006: Document release addition, default changes, compatibility, failure
  recovery and rollback. Verify the selected real web release through existing
  quality and private lifecycle interfaces; demonstrate release selection with
  distinct synthetic offline releases without claiming additional supported stacks.

## Acceptance criteria

| ID | Required observable evidence | Requirements |
|---|---|---|
| AC-001 | List/show return deterministic JSON with exact releases/default/limits; unknown selection fails. Tests observe no execution, acquisition or writes. | CAT-001 |
| AC-002 | Validator rejects duplicate IDs/versions, unknown schema/keys, unsafe/symlink/escaping paths, missing or altered content and incompatible toolchains before destination creation. Historical release alteration fails the release-immutability check. | CAT-002 |
| AC-003 | Explicit/default creation succeeds; two distinct offline release fixtures select different known bytes. Same release generates equivalent source after documented identity normalization. Existing destinations, invalid options and concurrent same-destination requests preserve unrelated content. Injected generation failure leaves a documented recoverable owned outcome. | CAT-002/003 |
| AC-004 | New app has valid manifest, exact toolchain and release provenance; edited source still validates. Legacy marker-only app validates/tests/starts without metadata rewriting. Conflicting or malformed new provenance is rejected. | CAT-004 |
| AC-005 | Source and installed bundle list/show/create agree for the same release. Default/provider transition and rollback leave existing app source, toolchain declarations and unrelated service state unchanged. | CAT-005 |
| AC-006 | A task-owned selected web app passes frozen dependency preparation, build, tests/typecheck, private page/health and scoped stop/source retention. An independent app stays available. Record local checks, CI, timings, exact revisions and Daniel's acceptance separately. Runbook/release guide clearly name unsupported stacks and recovery steps. | CAT-006 |

## Completion and ownership

Daniel owns scope/default/release review and acceptance. Deliver the catalogue,
schema/resolver, CLI integration, bundled release assets, focused tests and guide
through a PR. Record sanitized evidence in `acceptance.md` during verification.
Only mark the initial PRJ-003 web slice Delivered after implementation merge and
all criteria pass; retain broader stacks as named follow-ups. No deployment or
operator infrastructure action is required by this draft.

The proposed initial catalogue ID is `nextjs`, exact release `1.0.0`, using the
current accepted starter/toolchain bytes at implementation baseline. This is a
proposal, not a claim that a catalogue release already exists. Daniel should
confirm this bounded initial scope when reviewing the plans.
