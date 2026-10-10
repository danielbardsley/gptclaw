# TDD-021: Bundled, exact-release template selection

- **Status:** In review — implemented design
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-021](spec.md) · **Tasks:** [TASKS-021](tasks.md)

## Approach and proposed interfaces

Keep the existing CLI/runtime. Add a strict trusted resolver for a repository-owned
`config/templates/v1.json` catalogue and `schemas/templates/v1.schema.json`.
Store released assets beneath `templates/apps/releases/<id>/<version>/`; freeze
the accepted current Next.js starter as proposed `nextjs@1.0.0`. Replace hardcoded
creation inputs with a resolved validated release. Avoid a second independently
maintained starter copy: migrate current consumers/tests to the released location
or a single reviewed compatibility adapter. Preserve the shared toolchain recipe
and SPEC-020 registry as their own contracts.

Proposed JSON interfaces follow the CLI's existing output convention:

```text
gptclawctl templates list
gptclawctl templates show --template nextjs --template-version 1.0.0
gptclawctl new my-app --template nextjs --template-version 1.0.0
gptclawctl new my-app
```

Require both selection flags together; absence of both resolves the recorded
exact default. No `latest`, ranges, aliases, project-supplied paths or remote
fetches. Discovery parses/verifies bundled data only. Advertise the additive
capability and catalogue schema in provider metadata; retain existing exit codes
and existing result fields, adding exact template identity/provenance fields.

## Catalogue and release identity

Each release records ID/version, description, supported project kind/provider,
manifest schema, required provider compatibility, exact toolchain profile,
data/exposure limitations, and a bounded list of source path/output path/SHA-256
records. Declare only implemented fixed substitutions, such as project ID/name
and base path; never evaluate template expressions or execute generation hooks.
Hash a canonical release descriptor including its inventory, compatibility and
substitution rules, excluding its own digest. Catalogue default is separate from
immutable descriptors, so changing the default does not mutate prior releases.

Validate duplicate/unknown fields, types, safe relative paths, collisions and
reserved generated-output names. Refuse symlinks and files outside the trusted
release directory, including intermediate path symlinks. Bound input sizes/file
counts and verify each listed asset before writes. Require toolchain references
to resolve against the reviewed registry with compatible exact package metadata.
Compare already published release descriptors/assets against the main baseline
in the release check; additions are permitted, mutation/removal of published
versions is rejected. This is a repository/CI review gate, not runtime protection
against an actor who can rewrite both catalogue and its validation code.

## Generation, provenance and legacy compatibility

Validate slug, destination parent, selection and all release bytes first. Generate
in an exclusive task-owned sibling staging directory on the same filesystem.
Validate generated manifest/dependency/toolchain/provenance before publishing.
Use a no-overwrite publication primitive with same-destination serialization;
do not rely on an existence check followed by replacing rename. Recheck parent
identity/path constraints and ownership before publication. Failed staging is
removed only when ownership is proven; otherwise retain the exact owned path and
return a bounded recovery result. Never recursively remove an unknown destination.
Document interruption recovery and test the final-publication race explicitly.

Keep `.gptclaw/template.json` exactly as the runtime provider marker expected by
existing apps. Add `.gptclaw/template-release.json` with schema version, template
ID, exact release version and release digest. This is creation provenance, not
an application integrity lock. Validate metadata shape and identity/compatibility
against bundled known releases without comparing edited app source to starter
hashes. Missing new metadata means legacy, with unknown creation release; do not
rewrite it during start/test/inspect. An unknown future release yields an explicit
unsupported/recovery result, never a fallback to default. Document that rolling
the provider back may not support apps created from later releases; it must leave
their source/state intact and must not restart their services automatically.

Generated manifest remains schema v1. Emit the release's exact supported toolchain
selection, not whichever toolchain is globally default at generation time. Reuse
SPEC-019 frozen installation and existing build/test/typecheck/start operations.
Do not install dependencies or launch an app during `new`.

## Bundles and rollout

Extend provider snapshot inventory/digest to include resolver, schema, catalogue
and every release asset. Installed discovery and creation read their own snapshot,
not the checkout. Ensure source and installed interface output agree for one
snapshot; old snapshots continue to carry their old coherent default/catalogue.
Use the reviewed SPEC-018 provider-refresh path after source review, within its
owned namespace, with no host policy, AWS or Serve configuration changes.
Rollback selects the previous reviewed provider through that same path, preserves
existing snapshots/apps, and records unsupported later releases explicitly.
No automatic project migration or template upgrade is introduced.

## Components and traceability

| Proposed component/change | Requirements | Tasks | Acceptance |
|---|---|---|---|
| Catalogue/schema/release inventory and integrity/immutability validation | CAT-001/002 | T-002 | AC-001/002 |
| CLI list/show and exact/default `new` resolution | CAT-001/003 | T-003 | AC-001/003 |
| Owned staging/publication and provenance validation; legacy compatibility | CAT-003/004 | T-003/004 | AC-003/004 |
| Provider inventory/capability and snapshot compatibility | CAT-005 | T-004 | AC-005 |
| Release guide, focused tests and existing app CI/live acceptance | CAT-006 | T-005/006 | AC-006 |

## Verification and decisions

Use synthetic invalid catalogues and two distinct synthetic releases for failure,
selection, publication race and identity normalization tests. Reuse actual web
quality checks for the released starter. Run repository checks for implementation,
and configure CI to validate released assets and generation against this same
catalogue. Tests must cover installed bundles, not only source imports.

Live acceptance uses one task-owned ephemeral-data app and observation of a second
independent app. Verify private page/assets/health, exact dependency/toolchain
metadata, stop/source retention and unchanged independent service. Record commands,
revision, release digest, timings and outcomes. CI success is separate from live
behavior and Daniel's acceptance; no reboot/replacement/restore is required.

Daniel approved the single-entry scope and exact/default interface by authorizing
implementation. The [runbook](../../runbooks/manage-project-templates.md) documents
the implemented release/recovery workflow.
Implementation settles bounds at 100 files/release, 2 MiB/file, 8 MiB/release,
256 KiB metadata, 48-character IDs/versions and 200-character paths. Fixed
substitutions affect generated manifest identity only; Linux renameat2
RENAME_NOREPLACE publishes under a destination-derived runtime lock. Broader template stacks retain stage-12
or demand-driven ownership; this design supplies registration mechanics only.
