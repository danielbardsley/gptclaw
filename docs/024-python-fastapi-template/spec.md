# SPEC-024: Python FastAPI template and supported execution

- **Status:** Draft — planning requested; specification approval and implementation authorization pending
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Primary feature:** TPL-003 — Python API/AI template, initial standalone API slice
- **Supporting slices:** SYS-002/003 (Python/uv), PRJ-001/002/003/009, QLT-001/002/004/008/009, NET-103
- **Design:** [TDD-024](technical-design.md) · **Tasks:** [TASKS-024](tasks.md)
- **Context:** [Delivery sequence](../platform/sequence.md), [manifest contract](../project-manifest.md), [SPEC-018](../018-first-private-application/spec.md), [SPEC-019](../019-project-dependency-policy/spec.md), [SPEC-020](../020-pinned-language-toolchains/spec.md), [SPEC-021](../021-template-catalogue/spec.md)

## Outcome and authorization

The project owner prefers Python with FastAPI for application backends and
requested this specification on October 11. Deliver a versioned, reusable API
starter that can be generated, validated, tested, run privately, edited, inspected
and stopped through the existing GptClaw workflow. A synthetic sample API must
exercise the whole path, rather than leaving a template that the runtime cannot
execute. This prepares a proven API service for later RUN-006 orchestration.

This request authorizes planning and a reviewable planning PR. It does not approve
this draft, authorize implementation, or authorize installing host tools,
changing infrastructure, publishing a service or creating application repositories.
Specification approval, implementation authorization, code review/merge and
behavioral acceptance are separate records.

## Scope and observed starting point

The repository currently supplies an exact-release Next.js catalogue and a
rootless single-web lifecycle provider. Manifest v1 accepts only `kind: web`;
its commands are build/start/test. The toolchain schema and registry support only
Node/pnpm. Dependency preparation, template metadata validation and runtime target
selection assume that stack. These are source observations, not a fresh inspection
of installed host capabilities.

Included:

- One exact-release FastAPI starter, Pydantic request/response models and typed
  non-secret settings, Uvicorn, OpenAPI and interactive private API documentation.
- One exact supported CPython/uv container profile for Linux amd64, with verified
  immutable acquisition, observation-only inspection and reuse receipts.
- A uv dependency-policy adapter: locked restore and typed add/update/remove with
  stopped-project transactions, coherent source/lock publication and recovery.
- Explicit versioned contract extensions and integration with the existing
  catalogue, lifecycle, private ingress, provider snapshots and repository-creation
  template selection. Existing repository/credential policy remains authoritative.
- Ruff formatting/lint, pytest, mypy, a meaningful build/preflight and verify
  workflow, pinned generated-project CI, Python guidance and golden-template tests.
- A stateless synthetic API example and an update loop demonstrated privately,
  alongside an independently running existing Next.js project.

Excluded: TPL-002, RUN-006 service groups, databases/migrations, managed persistent
application data, background workers, runtime secret injection, authentication
starters, AI provider calls/models/GPU tooling, public exposure, production and
new host infrastructure. The API/AI catalogue title does not make an external AI
service necessary to this initial slice. Source/environment retention is not a
promise of application-data persistence. Broader catalogue scopes remain open.

## Requirements

### PYAPI-001 — Reproducible template selection and generation

Provide a named exact FastAPI release through existing templates list/show and
explicit new selection. Generate source, complete manifest/toolchain metadata,
lockfile, adapted guidance, checks and creation provenance without executable
hooks. Discovery and validation perform no fetch, install, import or application
execution. Occupied destinations, unsafe paths, invalid metadata and unsupported
versions fail without replacing source. Keep the current Next.js default and
published release identity unchanged; Python is the preferred backend stack,
not an instruction to change the default web template.

### PYAPI-002 — Verified Python execution profile

Declare and verify exact CPython and uv versions, platform, OCI digests and recipe
identity. All dependency, quality and service operations use that same reviewed
image. Refuse mismatches, unsupported selections, corrupted acquisition and
unverifiable reuse without floating-version fallback or implicit interpreter
downloads. Preserve existing Node profiles and legacy mappings. No host language
or package installation is required for generated apps.

### PYAPI-003 — Controlled dependency lifecycle

Use one `pyproject.toml` and `uv.lock` under a documented platform uv policy.
Routine preparation must detect stale locks and restore the approved dependency
graph without rewriting source or downloading another interpreter. Initial
support is public PyPI wheels with verified artifact hashes; reject source builds,
Git/URL/local dependencies, workspaces, private indexes/auth, project build hooks
and configuration that overrides approved sources or escapes owned storage.
Project execution can run arbitrary Python; metadata validation is not an
executable allowlist or a security boundary.

Typed add/update/remove must publish a validated manifest/lock pair under the
existing project lock, refuse active/busy targets, preserve concurrent edits,
record partial/interrupted outcomes and support scoped recover/abort. A failed
install is not prepared state. Normal service/quality execution cannot silently
resolve dependency changes. Existing pnpm operations retain their behavior.

### PYAPI-004 — Useful, typed sample API and configuration

Provide an application factory, separated routes/models/settings and a stateless
synthetic request/response example with successful, invalid-input and missing-route
behavior. Include health and OpenAPI schema, stable operation identifiers and
no secrets in settings, fixtures, arguments or logs. Typed settings support the
generated project identity/base path and safe non-secret defaults; invalid settings
fail startup clearly. No dotenv loader or unrestricted environment forwarding is
introduced. Returning synthetic data requires no database or runtime credential.

### PYAPI-005 — Managed private lifecycle and source update loop

Support new/validate/start/test/status/bounded logs/restart/stop through the existing
rootless container, Quadlet, locks, ports, resource limits and readiness contracts.
Use one API service per project. Only readiness success publishes its owned route;
failed or interrupted operations retain honest recoverable state. Publish container
ports only on host loopback and mount no host home, credentials or container socket.
Demonstrate supported automatic reload for application source edits, including
recovery after a syntax error. Reload is development behavior; dependency/toolchain
changes require the explicit stopped-project workflow. Stop preserves source and
only removes owned runtime resources/routes. Unrelated projects remain available.

### PYAPI-006 — Correct private routing and API documentation

Serve the API beneath `/projects/<id>/` through the existing prefix-preserving
ingress. Health, endpoints, docs assets, OpenAPI references, query strings and
redirects must work at the returned private HTTPS URL. No ingress-prefix rewrite,
new private service port scheme, Serve reset or broad proxy-header trust is assumed.
Bundle/version the interactive docs assets so runtime docs require no external
CDN. Unknown project paths and stopped/unhealthy targets remain unavailable.

### PYAPI-007 — Python quality and delivery conventions

Expose documented format/lint/typecheck/test/build/verify argument-vector commands
inside the selected container. Formatting is an explicit source mutation; the
other gates check without applying fixes or rewriting dependency files. Provide
Ruff configuration, pytest API/settings/health/contract tests, mypy configuration,
and a Python style guide covering naming, imports, type annotations, model and
route organization, async boundaries and error handling. Verify must run each
required gate and fail on representative formatting, lint, type and API behavior
violations. Build/preflight must catch invalid application construction rather
than merely echo success. Generated PR CI uses the same pins/lock and validates
format, lint, types, tests and build without live host or credential dependencies.

### PYAPI-008 — Versioned interfaces and compatibility

Add explicit supported schema/profile/provider versions; do not insert unsupported
fields into v1 or reinterpret old metadata. Unknown future versions fail clearly
without execution. Keep the published Next.js release, v1 manifest, Node toolchain,
pnpm policy, source and live route ownership valid. Exact selected FastAPI templates
must work through the existing repository-creation generation path when separately
authorized; local-only generation must not require credentials. Do not expand App
permissions, change credential selection or expose repository tokens to containers.
Publish additive capabilities and schema/error/result semantics; serialize all
mutations through existing locks. Runtime receipts/assigned ports stay outside Git.

### PYAPI-009 — Evidence, recovery and honest completion

Use task-owned synthetic fixtures. Record local checks, generated CI, actual EC2
rootless behavior and an authorized client's private docs/API update observations
separately. Cover cold/warm preparation, dependency failure/conflict/recovery,
health failure, interrupted lifecycle, occupied destination and unaffected Next.js
behavior. Document supported pins/limits, timings, retry/recovery and rollback.
Rollback preserves source/lockfiles, unknown resources and unrelated projects;
an older provider must reject unsupported Python metadata/state explicitly.
Mark only the accepted initial TPL-003 slice Delivered after merged implementation
and all required acceptance criteria pass. No implementation acceptance is claimed
by these planning documents.

## Acceptance criteria

| ID | Observable result and evidence needed | Requirements |
|---|---|---|
| AC-001 | Exact release is discoverable offline and generates a valid complete API project; invalid selection/path and destination-race tests preserve existing files. Next.js default and release digests remain unchanged. | PYAPI-001, PYAPI-008 |
| AC-002 | Owned cold acquisition verifies actual Python/uv versions and immutable provenance; warm reuse succeeds. Wrong pin/platform/artifact/image and active switching fail. Dependencies, checks and service report the same profile/image identity. | PYAPI-002, PYAPI-008 |
| AC-003 | Locked sync leaves source/lock hashes unchanged; stale lock, denied sources/config/hooks/builds/downloads fail. Typed add/update/remove, concurrent edit, interrupted publication, recover/abort and failed environment repair are exercised without losing coherent user source. | PYAPI-003 |
| AC-004 | Sample endpoint returns the specified typed synthetic result; invalid input gives the documented validation response; missing route, health, OpenAPI operation/schema and invalid non-secret settings are tested. | PYAPI-004 |
| AC-005 | On EC2, API start/status/logs/test/restart/stop and source reload work within recorded limits. Syntax-error recovery, readiness failure, busy and interrupted operation scenarios preserve honest state. Stop retains source. | PYAPI-005, PYAPI-009 |
| AC-006 | From an authorized tailnet client, docs assets/OpenAPI and a valid/invalid API call work through the returned HTTPS prefix; slash redirects retain correct HTTPS host/path and query strings survive. Docs require no external CDN; spoofed forwarding cannot select an arbitrary redirect host. Stopped/unhealthy/unknown project paths are refused. | PYAPI-006 |
| AC-007 | All documented quality commands and generated PR CI pass under the exact container profile. Deliberate format/lint/type/API defects fail their gates; build catches broken imports/app construction and verify propagates failures. | PYAPI-007 |
| AC-008 | Legacy/current Next.js fixtures pass generation, frozen dependency preparation, build/test and lifecycle regression checks. During live Python operations an independent Next.js service retains its route, resources and health. Repository generation selection passes synthetic integration without credential changes. | PYAPI-008, PYAPI-005 |
| AC-009 | Sanitized acceptance records final revisions, local/CI/live/client results, timings, failure recovery, rollback trial and owned fixture disposition; implementation is reviewed/merged and project owner accepts the initial slice with follow-up scopes named. | PYAPI-009 |

## Decisions, completion and ownership

The draft proposes one wheel-only Linux amd64 profile and explicit FastAPI
selection. Exact Python/uv/framework/check-tool pins, image digests and docs-asset
provenance are intentionally unselected until the implementation pin review; T-002
must record a supported stable combination and verify the pinned executables'
actual behavior before dependent work. This is ordinary technical selection,
not permission to use floating runtime defaults. The existing platform Python
validator environment remains separate and unchanged.

The project owner reviews this scope and authorizes implementation separately.
The implementer owns contract/pin resolution, code/tests, safe fixture lifecycle
and evidence; the project owner supplies independent client observations and final
acceptance. No database or secret dependency is required. If the approved template
cannot fit these boundaries, document the concrete scope change before dependent
work; retain existing infrastructure and service access gates.

Deliver the template, integrated Python profile/policy/contracts, regression and
generated checks, runbooks and an acceptance record. TPL-003 completion means this
standalone API slice only. AI integrations and RUN-006 orchestration need their
own reviewed plans; supporting catalogue features are not closed wholesale.
