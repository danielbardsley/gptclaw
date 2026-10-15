# Manage private TypeScript APIs

[SPEC-035](../docs/035-typescript-api-template/spec.md) adds the initial stateless
TPL-002 slice in source provider 1.13.0. Verify `gptclawctl --version` reports
manifest 7 and catalogue 6 before selecting this template; an older installed
provider cannot discover or run it. Use the reviewed repository launcher until
an installed snapshot includes this change.

```bash
scripts/gptclawctl templates show --template fastify --template-version 1.0.0
scripts/gptclawctl new my-api --template fastify --template-version 1.0.0 --local-only
scripts/gptclawctl validate --project-root /srv/forge/projects/my-api
scripts/gptclawctl verify --project-root /srv/forge/projects/my-api
scripts/gptclawctl start --project-root /srv/forge/projects/my-api
```

The exact Node 24.21.0 / pnpm 12.10.1 toolchain and existing dependency policy
supply all commands without host packages. Installation disables package hooks
and restores the lockfile; dependency changes use the stopped-project
[dependency workflow](manage-project-dependencies.md). Local generation needs no
repository credentials. Creating an application GitHub repository is separately
scoped under the [repository workflow](manage-project-repositories.md).

The returned private URL ends in `/projects/my-api/`. Append `live`, `ready`,
`docs/`, `openapi.json`, `api/v1/examples?offset=0&limit=2` or `api/v1/echo`.
Echo accepts POST JSON `{"message":"hello"}`; request and response schemas drive
validation and OpenAPI. Documentation assets are bundled, with no runtime CDN.
The synthetic list and echo retain no application data. PostgreSQL and migrations
are explicitly deferred by the project owner's initial scope choice.

Managed development uses Node watch mode. Source edits reload the service; a
syntax error can interrupt readiness until corrected. Dependency, toolchain and
manifest changes use the stopped-project workflow. Use bounded `logs`, `status`,
`restart` and `stop` from the [private app runbook](manage-private-apps.md).
Stop revokes the owned route and retains source. Services publish only on host
loopback through the existing private ingress; no new Serve setup or public
exposure is needed. An unavailable shared ingress remains an operator action,
not permission for agents to change host configuration.

`lint`, `typecheck`, `test`, `build`, `security` and `verify` are check commands.
`format` intentionally writes source and requires a stopped service. Tests require
80% line and branch coverage for loaded critical source modules; build compiles
strict TypeScript and constructs the API. `security` queries public npm advisories
and fails on high/critical findings or advisory-service failure. Containerfile
builds the compiled server with the same Node/pnpm versions; it does not deploy it.

When adapting the starter, replace synthetic routes, schemas, examples and tests
with the approved product behavior. Keep useful health and private docs support.
Do not treat starter sample tests as product acceptance.

## Verification and rollback

From the prepared manifest environment:

```bash
.venv-manifest/bin/python scripts/tests/test_project_fastify.py
.venv-manifest/bin/python scripts/check-template-releases.py
.venv-manifest/bin/python scripts/tests/check_fastify_template.py /tmp/unique-api-check --engine podman --image localhost/gptclaw-node:24.21.0-pnpm12.10.1
```

The last command requires an absent task-owned destination and an existing pinned
image. It generates two synthetic projects, checks frozen restore and quality,
rejects injected defects, publishes temporary loopback container ports and checks
reload/error recovery and independence. Containers are stopped afterward; the
synthetic source/evidence stays in the selected directory. These container checks
do not prove installed Quadlet/private HTTPS or project-owner acceptance.
Rollback uses a reviewed revert and the previous provider snapshot. Preserve
existing generated projects and immutable published releases; never remove source
or unknown runtime resources as a rollback shortcut.
