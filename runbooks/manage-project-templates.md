# Manage the bundled template catalogue

Use the reviewed installed `gptclawctl` or the repository's `scripts/gptclawctl`.
Provider 1.3.0 adds catalogue schema 1. Discovery reads bundled metadata/assets;
it does not fetch packages, execute a project or start containers.

```bash
gptclawctl templates list
gptclawctl templates show --template nextjs --template-version 1.0.0
gptclawctl new my-app --template nextjs --template-version 1.0.0
```

Both selection flags are required together. Omitting both uses the catalogue's
exact default. Unknown IDs/versions and ranges fail without fallback. `new`
creates source only; use the existing [private app workflow](manage-private-apps.md)
for validate/test/start and the returned private URL. The initial catalogue has
one Next.js/React/TypeScript web release with ephemeral application data. API,
Python, Expo, static-site, CLI and multi-package releases are unsupported.

The runtime marker `.gptclaw/template.json` retains its legacy meaning. The new
`.gptclaw/template-release.json` records the original release ID/version/digest;
it does not lock current app source to starter bytes. Existing marker-only apps
retain unknown release provenance and run without automatic source migration.
Exact toolchains and dependencies retain their [toolchain](manage-project-toolchains.md)
and [dependency](manage-project-dependencies.md) workflows. A supported subsequent
toolchain change does not rewrite creation provenance.

## Adding a release or changing the default

Submit a reviewed repository PR. Add assets at
`templates/apps/releases/<id>/<version>/` and a descriptor in
`config/templates/v1.json`; its shape is defined by
`schemas/templates/v1.schema.json`. Record source/output mappings, SHA-256 of
all listed files, exact supported toolchain reference, stack/compatibility and
limits. Generation performs only the three fixed identity substitutions into the
manifest: project ID, display name and base path. No hooks or template expressions
execute. Each release is bounded to 100 files, 2 MiB per file and 8 MiB total;
the catalogue/schema inputs are bounded to 256 KiB. Release IDs and versions are
bounded to 48 characters; paths to 200. New output names must avoid reserved
metadata/cache/credential paths and directory/file collisions.

Compute the descriptor digest with `project_templates.digest` over its canonical
JSON object excluding `digest`. Validate using the prepared manifest environment:

```bash
.venv-manifest/bin/python scripts/check-template-releases.py --baseline main
.venv-manifest/bin/python scripts/tests/test_project_templates.py
```

The baseline comparison rejects mutation/removal of published releases, even if
the author recomputes hashes. CI compares against the PR base or preceding main
commit. Change content, compatibility or substitutions by adding a new exact
release. Change the catalogue default in a separate reviewed edit without changing
old descriptors. Update shared toolchain support through its own reviewed registry;
other stacks need their runtime/schema specification before registration.

Run repository checks and the actual generated app quality checks. Include release
selection, private route/health, independent-app preservation and owned cleanup
acceptance; a fixture release does not prove support for a new real stack.

## Failure recovery and rollback

Generation uses a same-destination lock, an exclusive sibling
`.gptclaw-create-<operation-id>` staging directory and Linux atomic no-replace
publication. A concurrent creator cannot overwrite even an empty destination.
Failures after staging return `retained_staging`; hard interruptions may leave a
staging directory without a result. Staging is never a complete published app.
No automatic recursive cleanup or adoption is performed. Reconcile an exact
operation-owned staging path and its contents before an explicitly scoped cleanup;
never remove a project destination or infer ownership solely from its name.
If the destination does not exist, a fresh request may generate a new stage;
if it exists, inspect it and do not retry with replacement behavior.

Installed immutable provider snapshots contain their own catalogue and assets.
The reviewed provider-refresh path changes future command resolution without
rewriting existing apps or automatically restarting them. Retain prior snapshots
and use that path to select a reviewed prior provider for rollback. A provider
cannot support releases absent from its bundle: unknown provenance fails rather
than selecting the default. Rollback to a pre-catalogue provider has no provenance
validation capability and must be reviewed for the apps involved. Retain their
source/state and avoid automatic service restarts. Template upgrades are explicit
reviewed source changes; there is no automatic template migration command.
