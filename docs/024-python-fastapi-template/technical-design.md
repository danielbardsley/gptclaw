# TDD-024: FastAPI on the existing managed runtime

- **Status:** Draft proposal — no implementation authorized or executed
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-024](spec.md) · **Tasks:** [TASKS-024](tasks.md)

## Existing seams and approach

Extend the existing provider with a trusted stack adapter selected by validated
manifest, template/provider marker and toolchain family. Application files cannot
select an arbitrary plugin/module or acquisition command. Reuse `private_apps.py`
for owned jobs, Quadlet lifecycle, ports, locks, state and ingress. Do not add a
second lifecycle manager, Compose stack or control daemon.

Source inspection found these concrete seams:

- `project_manifest.py` loads only `schemas/project/v1.schema.json` and checks
  integer version 1; v1 has web kind and build/start/test only.
- `private_apps.target()` requires the `nextjs-v1` marker. Preparation hashes
  Node dependency files and invokes frozen pnpm install; job/unit generation
  contains pnpm-specific policy arguments.
- `project_toolchains.py` validates only Node/pnpm versions and Node base-image
  origins; its registry, acquisition recipe and executable verifier are stack-specific.
- `project_dependencies.py` supplies the accepted pnpm transaction/policy machinery.
  Reuse its ownership/recovery principles, not pnpm resolution semantics for uv.
- `project_templates.py` and the catalogue schema accept only current web/provider
  metadata and Node engine compatibility. Published release identity must remain frozen.
- `provider_bundle()` explicitly inventories scripts/schemas/config/assets; Python
  files must be included in immutable snapshots and compatibility checks.
- The ingress preserves the full `/projects/<id>/` path. Existing repository
  creation calls the catalogue generator and must retain the selected release.

These are checkout observations. Implementation acceptance must inspect the actual
installed provider/rootless runtime separately and use task-owned synthetic projects.

## Versioned authored contracts

Propose project manifest **v2 for standalone APIs**. Keep the v1 schema and behavior
unchanged. V2 keeps existing identity, one service port/health, private exposure,
base-path and ephemeral-data constraints, with `project.kind: api` and required
build/start/test/format/lint/typecheck/verify argument vectors. No environment maps,
volumes, service arrays, secrets, assigned host ports or install hooks are added.
V2 does not imply a v2 web migration or RUN-006 compatibility. Preserve bounded
YAML parsing, duplicate/unknown-key refusal, safe files, no shell expansion and
cross-field project/base-path consistency. Choose a bundled schema using the
parsed integer version; never fetch a schema from the document or network.

Add **toolchain declaration/registry v2** for the Python family (`python-uv`, one
profile revision, exact `python` and `uv` strings), retaining Node v1 parsing and
its fixed legacy default. Python registry data holds platform, immutable Python
base digest, immutable uv source digest, recipe hash, approved source origins and
fixed executable verification vectors. Resolve family-specific defaults from
trusted registry data, never the current Node global default for an API project.

Add a **catalogue v2** that can represent existing v1 releases and the new Python
release. V1 descriptors/assets/digests remain byte-for-byte unchanged, including
`nextjs@1.0.0` and its default. Validate descriptors according to their declared
release contract; catalogue envelope migration does not rewrite release hashes.
The latest provider must advertise accepted versions and verify the whole
catalogue. An unknown/corrupt v2 catalogue is an error, not a fallback to v1.
Extend the release immutability checker to compare historical identities across
both catalogues and forbid conflicting copies. Keep any retained v1 compatibility
inventory consistent through checked generation, rather than manual divergence.

Proposed new identity: `fastapi@1.0.0`, marker `fastapi-v1`, API manifest v2,
Python toolchain v2 and existing creation-provenance semantics. This is a release
proposal, not an already installed asset. An older provider must reject it while
leaving its files/services intact; the latest provider preserves old Next.js markers.

## Python image and dependency adapter

Build a reviewed toolchain Containerfile from an official Python base digest and
copy uv from a digest-pinned official Astral image. Verify Python/uv executables
inside a bounded no-network container with no project source/credentials mounted;
record provenance and actual image/version receipts using SPEC-020 ownership and
reuse rules. No curl-to-shell installer, project-defined URL, host package install
or automatic interpreter acquisition. Choose and commit exact compatible stable
pins in T-002; no `latest` tags or unverified example digests.

Add a strict Python policy alongside the unchanged pnpm policy. Parse bounded
`pyproject.toml`, `uv.lock` and an exact `.python-version` as data. Cross-check
`requires-python` with the selected interpreter. Initial layout is one non-packaged
application directory, no build system, workspaces or editable/local dependencies.
Dependencies and named development group are exact pinned PyPI packages; require
artifact hashes and supported Linux amd64 wheels for the actual environment.
Reject Git/path/URL/custom index sources, credentials, source builds and configuration
that bypasses policy. Treat unsupported native packages as a compatibility error.

The trusted runner suppresses user/system/project uv configuration discovery,
interpreter downloads, dotenv loading, auth/keyring/netrc and unapproved index
selection. It controls environment/cache paths and validates lock sources and
artifacts as well as CLI settings. Pin-review tests must establish exact flag and
configuration behavior; a project `[tool.uv.sources]` override is not made safe
merely by supplying a default index flag. Do not inherit the host environment.

Use **locked** synchronization that checks lock freshness; `--frozen` alone is
insufficient because it skips that check. Prove no dependency-source writes with
read-only mounts and before/after hashes. Preparation creates an owned project-local
ignored environment/cache with correct forge ownership and no host `.venv` reuse.
Fingerprint source/lock, effective policy, selected image/profile and dependency
subset. Ordinary app/quality jobs invoke prepared environment executables directly
(or a proven no-sync/no-download wrapper); they never implicitly re-lock/install.
The service gets no package-index credentials. The retained cache/venv is disposable
execution state, not persistent application data.

Reuse typed `deps status/install/add/update/remove/recover` semantics with dispatch
on the reviewed Python family. Mutations require stopped/not-busy targets, exact
package/version/dependency-kind input and owned staged resolution. Validate the
candidate graph and locked restore before publication. Recheck original source/lock
hashes; preserve editor changes and record conflict. Use a recovery journal for
multi-file publication; do not call it atomic. Interrupted or partial installation
cannot mark preparation ready. Unknown job outcomes require same-operation
inspection/recovery, not blind retries. Snapshot parsers must reject unsupported
receipt/journal versions without interfering with pnpm projects.

## Starter, quality commands and update behavior

Release assets contain `app/main.py`, `app/api/`, `app/models.py`, `app/settings.py`,
`tests/`, `pyproject.toml`, `uv.lock`, exact interpreter metadata, ignored cache
rules, Python style guide, README/adapted AGENTS guidance, vendored docs assets and
pinned PR CI. The generator writes trusted manifest/toolchain/provider/provenance
metadata through its existing exclusive staging and no-overwrite publication.

The proposed sample endpoint `POST /api/echo` accepts a bounded nonempty message
and returns a typed normalized echo; inputs and responses are synthetic/stateless.
Provide `GET /health`, interactive `/docs`, `/openapi.json` and a small root response
linking docs. Pydantic settings use generated non-secret identity/base-path defaults
and validation; no dotenv or runtime secret interface. Tests cover constraints,
response types, missing routes, app factory/settings failures and contract operation IDs.
Avoid package import side effects that open sockets or start background services.

Required command behavior:

| Command | Proposed implementation and effect |
|---|---|
| format | Prepared environment runs Ruff formatter explicitly; source mutation allowed only for this operation. |
| lint | Ruff formatter check plus lint without auto-fix; reports violations. |
| typecheck | Pinned mypy checks application and applicable test types under committed configuration. |
| test | Pinned pytest with in-process API/settings tests; uses the shared dependency-preparation path. |
| build | No-download Python preflight imports and constructs the app, validates routes and emits/validates OpenAPI into an ignored owned output path; syntax/import/config failures are terminal. No distribution/sdist build required. |
| verify | Repository-owned Python check runner sequentially executes format check, lint, typecheck, tests and build, propagating the first failure; no shell command concatenation. |
| start | Prepared environment runs Uvicorn development reload with fixed app target, container bind/port and owned source watch paths. Host publication remains loopback. |

Add corresponding scoped CLI build/format/lint/typecheck/verify actions for API v2.
Reuse job bounds/results/locks and stopped-target mutation rules; format cannot
mutate active/busy projects. Advertise support rather than claiming these actions
exist today. Existing v1 test/start and pnpm behavior stay supported; v1 unsupported
quality actions return an explicit capability error, not invented command defaults.

Reload watches application source only, excluding venv, caches, generated output
and tests unless explicitly selected. A syntax error must not be reported ready;
status/ingress check current health, and fixing source restores the useful API.
Startup readiness and reload recovery use bounded checks. Toolchain/dependency
changes never alter an active service's selection silently. Build/test do not
start a public listener. No worker group or production server policy is introduced.

## Prefix routing and docs

Mount a child FastAPI application at the generated `/projects/<id>` prefix in a
parent ASGI app. Define endpoint/docs/schema paths relative to the child, so the
existing ingress can keep preserving the full path. Probe the actual prefixed
health path directly on the service port. Do not assume setting `root_path` alone
creates matching prefixed routes or ask ingress to strip paths for every project.

Serve vendored, versioned Swagger UI assets from the child app. Record upstream
source, hashes and required license notices during pin review; docs and API calls
must not depend on an external CDN or AI service. Validate rendered docs schema
URL, static asset paths and OpenAPI server/base-path information through real HTTPS.

Inspect existing ingress header behavior before setting proxy trust. Prefer
path-relative redirects that retain the browser's verified HTTPS origin; sanitize
forwarding data at the owned ingress and configure Uvicorn only for a demonstrated
trusted proxy path if needed. Never infer security from forge-owned rootless
networking or enable wildcard forwarded-header trust by default. Test malicious
forwarding headers and wrong Host values as well as normal slash redirects/query
strings. Serve/backend changes must preserve the accepted Next.js prefix behavior
and unrelated routes; if the existing private prefix is insufficient, return a
concrete scope issue instead of adding a new port/privileged route silently.

## Components, verification and rollout

| Component | Planned change | Requirements |
|---|---|---|
| Project validator/schemas and CLI | Explicit v2 API dispatch, quality commands and honest capabilities/results | PYAPI-005, PYAPI-007, PYAPI-008 |
| Toolchain parser/registry/acquisition and Python recipe | Reviewed immutable Python/uv selection, actual verification and reuse | PYAPI-002, PYAPI-008 |
| Dependency policy/uv adapter | Locked restore, typed transactions, failure/conflict/recovery | PYAPI-003 |
| Catalogue/release checker/generator | Exact FastAPI assets/provenance, frozen Next.js identity and compatible repository selection | PYAPI-001, PYAPI-008 |
| Runtime jobs/Quadlet/provider snapshots | Shared bounded Python lifecycle and owned state, no pnpm assumptions in API paths | PYAPI-005, PYAPI-008 |
| Starter/docs/tests/style guide/generated CI | Typed useful API, non-secret settings, quality and private prefix correctness | PYAPI-004, PYAPI-006, PYAPI-007 |
| Platform tests, runbooks and acceptance | Regression, two-project live/client proof and scoped recovery/rollback | PYAPI-009 |

Run relevant focused offline suites and the existing repository checker in its
prepared Python environment, including manifest/toolchain/dependency/catalogue,
repository-generation and provider-bundle regressions. No application imports or
network are permitted during observation-only validation/discovery tests. Add
negative fixtures whose import/config would leave a marker if executed.

CI builds/verifies the exact image and executes generated Python checks, dependency
policy failures and template generation/immutability. Retain existing Next.js
workflows. CI container tests do not substitute for EC2 Podman/Quadlet checks or a
client's actual private access; record each separately.

For live acceptance, use an explicitly scoped synthetic API and independent
synthetic Next.js target, never mutate existing user apps. Record cold/warm timings,
image/profile/lock identities, loopback publication, limits, health, docs and sample
calls, reload/failure recovery, logs/restart/stop and source retention. Obtain an
authorized client's HTTPS/docs/API observations. Use local-only creation unless a
separate repository fixture is authorized; synthetic repository-selection tests
cover integration without new App permissions or private credential reads.

Roll out a reviewed provider snapshot only after compatibility tests. Updating
active unknown units/routes/state is a conflict. Trial rollback on an owned
stopped API fixture: a supported earlier Python snapshot and matching explicitly
selected source/lock revision restore coherently, or a pre-Python provider refuses
with clear unsupported/recovery state. Preserve v2 files and existing running
projects; do not downgrade them implicitly or reuse Next.js metadata. Cleanup
stops only owned services/jobs/routes, retains source by default and removes only
identified disposable fixture outputs. No volume reset or broad cache/image prune.

## Traceability and decisions

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| PYAPI-001 | Exact catalogue/release, exclusive generation and provenance | T-003, T-006 | AC-001 |
| PYAPI-002 | Python profile/acquisition verifier and receipts | T-002, T-004 | AC-002 |
| PYAPI-003 | uv policy, locked preparation and journaled typed mutations | T-002, T-005 | AC-003 |
| PYAPI-004 | App factory, typed synthetic API/settings and contract tests | T-006 | AC-004 |
| PYAPI-005 | Shared runtime adapter, health and reload/recovery | T-007, T-010 | AC-005 |
| PYAPI-006 | Mounted ASGI prefix, self-hosted docs, tested redirect trust | T-006, T-007, T-010 | AC-006 |
| PYAPI-007 | Quality actions/config/style guide and pinned generated CI | T-003, T-006, T-008 | AC-007 |
| PYAPI-008 | Explicit schema/family dispatch, immutable legacy identity and regression | T-003, T-007, T-009 | AC-001, AC-002, AC-008 |
| PYAPI-009 | Local/CI/live/client evidence, rollout/rollback and acceptance | T-009, T-010, T-011 | AC-009 |

Open technical selections: exact pins/artifact origins/hashes, uv lock/config
allowlist and fixed flags, v2 field/result schemas and whether relative redirects
satisfy all mounted docs paths. Implementer resolves these in T-002/T-003 with
primary sources and executable fixtures; project owner reviews resulting source
through the normal implementation PR. These are proposed decisions. If evidence
requires secrets, source builds, extra host tools, different exposure or multi-service
scope, that is a scope amendment before the dependent action. Independent contract
and starter drafting can continue within the approved boundaries.

Primary documentation checked October 11, 2026; these describe tool semantics,
not installed versions or acceptance of this design:

- [uv container integration](https://docs.astral.sh/uv/guides/integration/docker/): official image-based acquisition and container environment handling.
- [uv locking and synchronization](https://docs.astral.sh/uv/concepts/projects/sync/): locked checks versus frozen reuse and automatic synchronization.
- [uv configuration precedence](https://docs.astral.sh/uv/concepts/configuration-files/): configuration discovery and dotenv control.
- [uv command reference](https://docs.astral.sh/uv/reference/cli/): pin-specific verification source for no-build/download/config flags.
- [FastAPI mounted sub-applications](https://fastapi.tiangolo.com/advanced/sub-applications/): mounted application paths and OpenAPI/docs behavior.
- [FastAPI proxy behavior](https://fastapi.tiangolo.com/advanced/behind-a-proxy/): forwarded-header trust and root-path semantics.
- [FastAPI self-hosted docs assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/): local Swagger UI assets.
- [FastAPI typed settings](https://fastapi.tiangolo.com/advanced/settings/) and [Ruff configuration](https://docs.astral.sh/ruff/configuration/): settings/style foundations; committed pins and tests establish this slice's behavior.
