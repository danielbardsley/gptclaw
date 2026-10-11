# Develop a private two-service project

[SPEC-025](../docs/025-multi-service-projects/spec.md) implements the initial
Next.js/FastAPI group in provider 1.7.0. Run as forge; the source runner or an
installed capable immutable snapshot must advertise manifest v3/group receipts v2.
Existing web v1/API v2 projects retain their single-service behavior.

## Create and operate

From GptClaw with its prepared validator environment:

```sh
scripts/gptclawctl new my-notes --template notes --template-version 1.0.0 --local-only
scripts/gptclawctl validate --project-root /srv/forge/projects/my-notes
scripts/gptclawctl start --project-root /srv/forge/projects/my-notes
scripts/gptclawctl status --project-root /srv/forge/projects/my-notes
scripts/gptclawctl logs --project-root /srv/forge/projects/my-notes --component api --lines 40
scripts/gptclawctl test --project-root /srv/forge/projects/my-notes
scripts/gptclawctl verify --project-root /srv/forge/projects/my-notes
scripts/gptclawctl restart --project-root /srv/forge/projects/my-notes
scripts/gptclawctl stop --project-root /srv/forge/projects/my-notes
```

`--local-only` on creation avoids GitHub repository operations even if an opt-in
credential profile is active. Application repository creation needs its own scope;
exact grouped selection also works through the existing reviewed generation path.

The project has `web/` and `api/` source roots and one `.gptclaw/project.yaml`.
Read root and component guidance before editing. Component metadata is owned by
group generation; do not fabricate independent project manifests or operate the
components as separate projects. The runtime derives component IDs/contracts from
the group. One group lock serializes jobs and lifecycle mutations.

Start prepares exact frozen dependencies and builds components serially, creates
an owned internal rootless network, starts API then web after readiness, and publishes
one private path only when both are ready. The returned actual node URL serves UI,
`api/v1/notes` and bundled `api/docs` beneath the same project prefix. There are no
new Serve commands or public URLs. Resource bounds per component are 1 CPU,
1536 MiB and 256 PIDs; the two service ceilings sum to 2 CPU/3072 MiB/512 PIDs.
Build/quality jobs remain serial, with 300-second per-job bounds and 120-second
readiness waits per service. Test tooling has separate bounded containers; check
actual host capacity before running it alongside live projects.

Status reports component health, image/profile identity, last operations, stage
receipts and group route outcome. Ready requires current API and web readiness.
An API outage makes group access return unavailable; fixes recover readiness.
Logs are explicitly component-scoped, bounded and redacted. Source edits reload the
selected component; dependency/toolchain changes never happen implicitly.

## Dependency and quality operations

```sh
scripts/gptclawctl stop --project-root /srv/forge/projects/my-notes
scripts/gptclawctl deps status --project-root /srv/forge/projects/my-notes --component api
scripts/gptclawctl deps add --project-root /srv/forge/projects/my-notes --component api --package itsdangerous --version 2.2.0
scripts/gptclawctl deps remove --project-root /srv/forge/projects/my-notes --component api --package itsdangerous
scripts/gptclawctl format --project-root /srv/forge/projects/my-notes --component api
scripts/gptclawctl toolchain inspect --project-root /srv/forge/projects/my-notes --component web
```

Use the existing [dependency](manage-project-dependencies.md),
[Python](manage-python-apis.md) and [toolchain](manage-project-toolchains.md)
policies. Mutations require the whole group stopped, no unresolved jobs and an
explicit component. Component dependency recovery uses its recorded operation ID
through the same group selector; status/inspect do not install or resolve. Preserve
concurrent edits and reconcile pending transactions before service startup.

API quality includes the inherited Python standards, types/docstrings, format/import
checks, Ruff, mypy, pytest/critical statement and branch coverage each >=80%, Bandit,
locked dependency audit and build. Web retains type/test/build gates. Unsupported
component quality actions fail explicitly. Group test/verify runs both components
and isolated API/Node OpenAPI/CRUD checks; generated CI additionally runs real browser
CRUD, refresh/data lifetime, failed draft, safe text and keyboard/responsive checks
in the digest-pinned browser image. See `checks/verify.py` in generated source.
The browser pins follow [official Playwright Docker guidance](https://playwright.dev/docs/docker).
Public advisory unavailability is a failed scan. No application/credential source
is mounted into browser tooling.

## Data, recovery and rollback

Notes are shared synthetic demo data held only in one API process's memory.
Refresh and web-only source reload retain saved notes. API reload/restart, group
restart/stop-start and host replacement lose them. Drafts are browser-memory only;
refresh can lose unsaved work. There is no database, file storage, browser storage,
authentication or per-user isolation. Do not put real personal notes in this demo.

Stop revokes routing before attempting web then API cleanup, removes only owned
runtime resources and retains source/locks/dependency caches/port reservations.
Partial cleanup remains a failed receipt, with both component attempts reported.
On timeout/lost output inspect status and stages for the same root; do not submit
blind duplicate starts, cancel unresolved jobs, take another process's port or
remove unknown units/networks. A partial/interrupted group must be reconciled with
its explicit stop before a new start. Dependency jobs have their own typed recovery.

Rollback stops the named group using a capable provider first, preserves source,
then restores a reviewed earlier provider revision. Older providers reject v3;
they cannot operate groups or interpret new group receipts. Keep the capable
snapshot for reconciliation. Do not rewrite a group into old metadata, reset Serve,
prune shared images/caches, remove unknown resources or change host/IAM settings.
Ephemeral notes cannot be restored. CI/local checks, live behavior and independent
browser/project-owner acceptance remain distinct evidence.
