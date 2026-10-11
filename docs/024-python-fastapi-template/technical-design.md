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
build/start/test/format/lint/typecheck/security/verify argument vectors. No environment maps,
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
application in a `src/<package>/` layout, no build system, workspaces or editable/
local dependencies. Set the application import path explicitly to that source tree;
never discover executable path hooks. Runtime, dev and test dependency groups are
exact pinned PyPI packages under one uv lock; require
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

Release assets contain `src/<package>/main.py`, domain/services/api modules,
Pydantic models/settings, structured logging/middleware, mirrored tests,
`pyproject.toml`, `uv.lock`, exact interpreter metadata, ignored cache rules,
`docs/python-standards.md`, architecture notes, `config/environment.example.md`,
README/adapted AGENTS guidance, explicit pre-commit config, vendored docs assets
and pinned PR CI. The generator writes trusted manifest/toolchain/provider/
provenance metadata through existing staging/no-overwrite publication.

Apply the [owner-derived standards disposition](python-standards.md) to this
release. The typed `EchoService` owns normalization/business logic; FastAPI route
functions inject it and remain thin adapters. Public symbols have complete types
and Google docstrings. Composition/DI and meaningful unit tests demonstrate the
object-oriented standard; no empty repository layer or fake persistence. The
src layout remains a non-packaged app with an explicit controlled import path.

Proposed endpoints inside the mounted child app:

- `POST /api/v1/echo`: bounded nonempty message and typed normalized response.
- `GET /api/v1/examples`: static synthetic records with validated bounded
  limit/offset and explicit page metadata; no database.
- `GET /health`: liveness; `GET /ready`: readiness of initialized configuration/
  application service. The manifest/provider probe `/projects/<id>/ready`.
- `/docs`, `/openapi.json` and a small root response linking self-hosted docs.

Pydantic settings use generated non-secret identity/base-path and validation;
configuration documentation lists types/defaults and future environment names,
without generating/loading dotenv files or forwarding host variables. Tests cover
models, sample service via injected dependencies, API status/operation identifiers,
pagination, startup/shutdown and invalid settings/readiness. Importing modules
opens no sockets or background jobs.

Use standard-library JSON logging with request IDs generated/validated at the
boundary, safe domain exception mapping and appropriate levels. Log only method,
route template, status, duration and safe correlation, never raw paths/query values,
headers, bodies, personal data or tracebacks exposed to clients. Unmatched routes
use a fixed safe identifier. Test malformed/secret-like input and exception output.

Middleware denies cross-origin access by default and adds docs-compatible security
headers. Implement finite in-process request admission with bounded storage,
recorded limits and a tested 429 response. Health/readiness remain useful during
API admission pressure. Avoid attacker-selected/untrusted forwarded identities;
this single-process development limiter is not a distributed quota guarantee.
Document its reset/reload semantics and test memory/admission bounds, recovery and
unaffected second-project behavior. No Redis/auth/password/SQL/session features
are added. Applicable OWASP and async/design conventions require recorded review
alongside automated checks; future dependencies must satisfy their conditional
standards before use.

Required command behavior:

| Command | Proposed implementation and effect |
|---|---|
| format | Prepared environment runs isort then Black explicitly against source/tests; source mutation allowed only for this operation. |
| lint | isort/Black check-only plus Ruff lint without auto-fix; use Black-compatible isort and narrowly reconciled Ruff rules. Shared proposed PEP 8 line limit is 79. |
| typecheck | Strict pinned mypy checks fully annotated source and typed tests/fixtures, with narrow documented library exceptions. |
| test | Pinned pytest/coverage.py with mirrored API/service/settings/middleware tests, synthetic fixtures/factory_boy and parametrized failures. Enforce at least 80% critical statement coverage and 80% critical branch coverage; missing/empty data fails. |
| security | Bandit plus pinned dependency audit of exact prepared/exported locked packages, without resolving/installing/fixing dependencies or transmitting source/secrets. Bounded public advisory access; findings or unavailable data fail explicitly. |
| build | No-download Python preflight imports and constructs the app, validates routes and emits/validates OpenAPI into an ignored owned output path; syntax/import/config failures are terminal. No distribution/sdist build required. |
| verify | Repository-owned Python runner executes format/import checks, lint, types, tests/coverage, static/dependency security and build; propagate failures without shell concatenation or source fixes. |
| start | Prepared environment runs Uvicorn development reload with fixed app target, container bind/port and owned source watch paths. Host publication remains loopback. |

Add corresponding scoped CLI build/format/lint/typecheck/security/verify actions for API v2.
Reuse job bounds/results/locks and stopped-target mutation rules; format cannot
mutate active/busy projects. Advertise support rather than claiming these actions
exist today. Existing v1 test/start and pnpm behavior stay supported; v1 unsupported
quality actions return an explicit capability error, not invented command defaults.


Keep Black/isort/Ruff/mypy/pytest/coverage.py (and any pytest-cov), factory_boy,
Bandit, audit and pre-commit exact-pinned in dev/test groups. Generate pre-commit
local/system hooks that invoke the same prepared-container commands; no remote
floating hooks, hidden virtualenv downloads or automatic `.git/hooks` writes.
Document an explicit opt-in hook install/run workflow. Apply Google docstring/
annotation/style checks where supported and test conflicting formatter/linter
settings rather than globally suppressing them. Review method cohesion/design
and blocking async calls; lint does not prove these properties.

Initial audit proposal uses pip-audit against public PyPI advisory data, fulfilling
the supplied Safety scanning intent without a Safety account/runtime secret.
Inspect pinned scan/export behavior in T-002: use the complete exact locked graph
(runtime/dev/test) and disable dependency resolution/build/install/autofix. Network
is restricted to approved advisory origins, transmits only public package names/
versions, has finite timeout/output and reports unreachable data as a failed gate.
Offline tests use synthetic vulnerability responses. Review any ignored finding
with ID/reason/owner/expiry in source; no blanket ignore or silent pass. Actual
Safety integration needs separately scoped authentication/data handling.

Coverage configuration names the critical source modules explicitly: domain/
service, models/settings, API routes/middleware, pagination/admission and readiness.
Record and enforce statement/branch thresholds independently; do not let unrelated
code or test files inflate them. Generate meaningful edge/error fixtures including
missing types/docstrings, logging leaks, wrong import order, sub-threshold branch
coverage, known static/dependency findings and failed advisory access. Tests and
CI must show that each gate can fail before accepting the template release.

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
| Starter/docs/tests/style guide/generated CI | Owner-derived service design, versioned typed API, safe logs/admission/settings, quality/security/coverage, pre-commit and private prefix | PYAPI-004, PYAPI-006, PYAPI-007, PYAPI-010 |
| Platform tests, runbooks and acceptance | Regression, two-project live/client proof and scoped recovery/rollback | PYAPI-009 |

Run relevant focused offline suites and the existing repository checker in its
prepared Python environment, including manifest/toolchain/dependency/catalogue,
repository-generation and provider-bundle regressions. No application imports or
network are permitted during observation-only validation/discovery tests. Add
negative fixtures whose import/config would leave a marker if executed.

CI builds/verifies the exact image and executes generated Python checks, coverage/
security/standards failures, dependency policy failures and template generation/
immutability. Advisory lookup is the explicit bounded network check; no account or
runtime secret is required. Retain existing Next.js
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
| PYAPI-010 | Versioned owner guide, injected service/src layout, safe logs/versioned API/admission and automated standards gates | T-006, T-008, T-012 | AC-004, AC-007, AC-010 |

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

Additional primary sources checked October 11 for the standards adaptation:

- [Black](https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html) and [isort Black compatibility](https://pycqa.github.io/isort/docs/configuration/black_compatibility.html): formatter/check semantics and compatible import formatting.
- [Bandit](https://bandit.readthedocs.io/en/latest/) and [pre-commit](https://pre-commit.com/): source scanning and explicit local hook configuration.
- [Safety scan workflow](https://docs.safetycli.com/safety-docs/safety-cli/scanning-for-vulnerable-and-malicious-packages): authentication precedes current scanning; account use is not assumed authorized.
- [PyPA pip-audit](https://github.com/pypa/pip-audit): public advisory audit and resolution controls; actual pinned behavior remains an implementation gate.
