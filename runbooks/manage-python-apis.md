# Managed Python FastAPI APIs

Provider 1.6.0 adds the standalone `fastapi@1.0.0` template. It uses Python
3.13.16 / uv 0.13.0 on Linux amd64, verified immutable OCI images and wheels.
It leaves the Next.js default, legacy manifest/Node profile and pnpm workflow intact.
[Specification](../docs/024-python-fastapi-template/spec.md) and
[standards](../docs/024-python-fastapi-template/python-standards.md) define the slice.

## Create and operate

Use the reviewed source or installed snapshot launcher from the
[private app runbook](manage-private-apps.md). Check `--version` for API/quality
capabilities. Creation with `--local-only` avoids GitHub credentials/repository
creation; separately authorized managed repository creation retains this exact
explicit template selection.

```sh
scripts/gptclawctl new my-api --template fastapi --template-version 1.0.0 --local-only
scripts/gptclawctl validate --project-root /srv/forge/projects/my-api
scripts/gptclawctl toolchain inspect --project-root /srv/forge/projects/my-api
scripts/gptclawctl start --project-root /srv/forge/projects/my-api
scripts/gptclawctl status --project-root /srv/forge/projects/my-api
scripts/gptclawctl logs --project-root /srv/forge/projects/my-api --lines 40
scripts/gptclawctl restart --project-root /srv/forge/projects/my-api
scripts/gptclawctl stop --project-root /srv/forge/projects/my-api
```

Use the returned private HTTPS URL. `/docs` loads bundled Swagger assets and
`/openapi.json`; `POST /api/v1/echo` takes `{"message":"synthetic example"}`.
`GET /api/v1/examples?limit=2&offset=1` demonstrates pagination. Liveness is
`/health`; readiness is `/ready`, probed directly and before Python ingress
forwarding. Docs slash redirects are relative and preserve query strings.
There is no CDN, database, auth/session, external AI call or application data store.

Uvicorn reload watches `src`; ordinary edits update the API without rebuilding
or rewriting units. A syntax/config error becomes unhealthy until corrected.
Dependency, toolchain and manifest changes use a stopped selected project and
explicit preparation/restart. Stop preserves source and disposable local caches.
Another project's image, service, source and route ownership are not changed.

## Contracts and installation policy

API `.gptclaw/project.yaml` uses schema 2 with `kind: api`, one service, private
exposure and ephemeral application data. Required vectors add format/lint/types/
security/verify to build/start/test. Web manifest v1 remains unchanged. Toolchain
sidecar v2 references one exact reviewed Python/uv profile. The v2 catalogue is
an extension merged with the v1 catalogue; v1 remains authoritative for the web
default and published web descriptors. Missing/corrupt unknown versions do not
fall back to a different stack. Provider snapshots bundle the complete contracts.

One `pyproject.toml`, `.python-version` and `uv.lock` define dependencies.
Runtime dependencies and separate dev/test groups are exact pinned, publicly
resolved PyPI packages. Only wheel installation is supported: no source builds,
Git/URL/path sources, workspaces, custom indexes/auth, dotenv, build hooks or
project `[tool.uv]` overrides. The lock may contain hashed PyPI source-artifact
metadata, but `--no-build` prevents source execution. Actual locked sync proves
compatible wheels and checks freshness; it never rewrites source/lock files.
Read-only dependency mounts and hashes verify that property.

The controlled runner disables config discovery, interpreter downloads, keyring
and dotenv loading; it chooses explicit cache/environment/interpreter paths and
mounts no host home/credentials/socket. Observation-only inspection/discovery
parses data and never imports source. These controls are not a security boundary
between hostile projects sharing forge's identity, nor an executable allowlist.

```sh
scripts/gptclawctl deps install --project-root /srv/forge/projects/my-api
scripts/gptclawctl deps add --project-root /srv/forge/projects/my-api --package itsdangerous --version 2.2.0
scripts/gptclawctl deps update --project-root /srv/forge/projects/my-api --package itsdangerous --version 2.1.2
scripts/gptclawctl deps remove --project-root /srv/forge/projects/my-api --package itsdangerous
scripts/gptclawctl deps status --project-root /srv/forge/projects/my-api
```

These versions are synthetic operation examples, not a recommendation to downgrade
an application dependency. Canonical lowercase/hyphen package names and exact
numeric versions are required; groups are runtime, development (`dev`) or test.
uv add/update uses `--raw --no-sync` to avoid writing source/index overrides, then
candidate lock/policy/locked restore must pass. Intentional changes stage and
journal publication, preserve concurrent edits, and invalidate preparation/build.
Review resulting source/lock diffs and rerun checks before start. A multi-file
publication is recoverable rather than atomic.

## Quality, hooks and failure handling

`format` explicitly runs isort then Black. `lint` checks formatting/imports plus
Ruff; `typecheck` uses strict mypy; `test` runs pytest and independently requires
80% critical statement and branch coverage. `security` runs Bandit and a pinned
pip-audit check against public PyPI advisories, without install/resolution/autofix.
It has finite request/job bounds and reports unavailable data as failure. `build`
constructs the app and validates/emits OpenAPI without starting a listener.
`verify` runs these required gates. Every action accepts the same `--project-root`.
Only format applies fixes; dependency files stay read-only in ordinary API checks.

Use `gptclawctl hooks --project-root ROOT` explicitly for a stopped ordinary Git
checkout. It refuses existing unknown hooks/symlinks and Git worktree files;
an identical installed hook is a no-op. The hook invokes verify through an
immutable provider snapshot, so no host pre-commit/Python app tools are installed.
The generated pre-commit config also uses local/system pinned checks; CI runs the
same quality runner directly, without hooks, credentials or extra tool downloads.
Factory-boy's dynamic export has one narrow typed-factory suppression; the model
boundary remains explicitly typed. No blanket lint/type/security ignores apply.

A busy job or unknown outcome is preserved. Inspect status and the recorded
operation ID; use `deps recover --project-root ROOT --operation-id ID`, or its
explicit `--abort` to retain coherent current source. Failed uv resolution cannot
be guessed/retried as successful; abort preserves editor changes. Interrupted
publication resumes only matching saved/current hashes. Unknown objects, units,
routes or receipts are conflicts, never permission to overwrite/prune/reset them.

Rollback uses a still-reviewed provider/profile and explicitly selected matching
source/lock revisions for an owned stopped target. A pre-Python provider rejects
API v2 without converting it to web or deleting files. Keep the validator environment
referenced by running immutable snapshots; branch/worktree cleanup is not safe
while those snapshots depend on its Python path. No reboot, infrastructure,
public exposure or broad cache removal belongs to this workflow.
