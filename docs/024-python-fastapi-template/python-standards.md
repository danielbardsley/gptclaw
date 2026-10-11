# Python standards for the TPL-003 starter

- **Status:** Draft application of project-owner-supplied standards to SPEC-024
- **Owner:** Project owner
- **Date:** 2026-10-11 (America/New_York)
- **Specification:** [SPEC-024](spec.md), PYAPI-010 · **Design:** [TDD-024](technical-design.md) · **Tasks:** [TASKS-024](tasks.md), T-012
- **Source:** [Supplied python.md](references/python.md), content preserved with trailing whitespace normalized
- **Original attachment SHA-256:** `7fb1cb14ef380270960173f58549d7e00c0656e01d0ad9a8e49f61c61d9c0bcb`

- **Archived source SHA-256:** `5013e1fd0c6881f23caf61ab784e773d239a934b4c4dff5bb48a93e0d7eb1d75`

## Scope and precedence

The project owner requested these coding standards be incorporated into TPL-003.
The supplied document is source material for the generated Python project.
The adapted coding standards below become the proposed template contract;
implementation authorization, runtime permissions and product scope remain
governed by SPEC-024.

During implementation, put the reusable guide in each generated project's
`docs/python-standards.md`, link it from adapted AGENTS.md and README, and commit
the enforceable configuration in `pyproject.toml` and generated CI/pre-commit
configuration. Catalogue release assets/versioning protect this content alongside
the code. Future changes get a new template release and an explicit adoption
workflow for existing projects; no automatic rewrite of user source/guidance.
This initiative applies to generated API code, not a wholesale refactor of
GptClaw's existing Python platform scripts.

## Coding and design contract

Use object-oriented domain/application service design with cohesive single
responsibility, SOLID principles, composition and injected collaborators. Keep
FastAPI route functions thin adapters to a tested service object. Use patterns
when they solve a concrete problem; the stateless sample needs no empty repository
class or speculative persistence layer. Methods should ideally stay under 20
lines; review larger methods for cohesion rather than imposing a mechanical
line-count rejection. Code must be complete, readable and reviewable, with minimal
meaningful comments and predictable behavior.

Use a `src/<package>/` layout with domain, services, api and utility boundaries,
mirrored tests, and top-level config/docs. Reserve the repository boundary for
future real data access; do not generate unused modules. Separate application
construction, Pydantic models/settings and structured logging. Public modules,
classes and functions have Google-style docstrings. Keep architecture decisions
and setup/API examples in docs; do not duplicate rules between guides and AGENTS.

Follow PEP 8, using a shared proposed 79-character code-line limit in Black/isort/
Ruff; explicit reviewed ignores cover formatter conflicts and unavoidable literals.
Use complete parameter/return and class-attribute annotations, modern unions and
other appropriate features of the selected supported Python version (at least
3.10), Pydantic/dataclasses for data structures, context managers, pathlib,
f-strings and simple comprehensions. Avoid bare except, complex comprehensions,
unnecessary inheritance and untyped business boundaries. Do not claim support
for every Python 3.10+ interpreter: the runtime uses one exact reviewed version.

Async I/O uses async/await, appropriate async context managers and asyncio.gather
when concurrency is justified. Do not block the event loop or create unnecessary
async wrappers for pure computation. Prefer aiohttp when an outbound async HTTP
integration is later introduced, with finite timeouts and mocked integration tests;
this stateless sample makes no external requests. Profile before optimizing;
use appropriate collections/generators and pagination. Caching, database pooling,
Celery and circuit breakers apply when those dependencies exist and require their
own runtime scope, not placeholder infrastructure in this template.

## API, logging and security contract

Use versioned `/api/v1/` routes inside the managed project prefix, Pydantic request/
response models, OpenAPI examples/stable operation IDs and correct HTTP methods/
status codes. Include a paginated static synthetic list endpoint with bounded
limit/offset, a typed echo endpoint, separate health/liveness and readiness endpoints.
The provider probes readiness; startup/configuration failures cannot appear ready.

Provide standard-library JSON logging with meaningful levels and boundary exception
mapping. Domain errors use typed custom exceptions and documented safe responses.
Request/response middleware logs generated request ID, method, route template,
status and duration, not bodies, headers, query values, credentials or personal
identifiers. Handle unmapped routes without logging untrusted path contents;
validate/reject untrusted request-ID input or generate a fresh ID. Test exception
and sensitive-input cases; no raw traceback details in API responses.

Validate bounded inputs and paginate list responses. Default CORS grants no
cross-origin access; any later explicit origin allowlist is validated non-secret
configuration, never wildcard credentials. Include compatible security headers
and an OWASP-informed review of this sample's attack surface. An app-local,
bounded in-memory limiter demonstrates finite request admission and a tested 429
response; it is single-process development behavior, not distributed protection.
Do not key it on untrusted forwarded client identity or add Redis. Test admission,
state bounds, recovery and independence of health/readiness probes.

Authentication/authorization, password hashing with bcrypt/argon2, parameterized
SQL, pooling and CSRF/template-engine protections are requirements for future
features that introduce identities, databases or browser sessions. The sample
has none, so do not add fake auth, password storage or SQL. Use secrets for future
cryptographic randomness, never ordinary random. Log no sensitive data, commit
no secrets and grant containers no host credentials. Dependency changes remain
explicit pinned, scanned, tested and reviewed operations.

## Automated gates and test conventions

| Gate | Required behavior |
|---|---|
| format | isort then Black explicitly format the selected project's source/tests. |
| lint | isort/Black check-only plus Ruff lint; Ruff formatter/import fixes do not compete with the chosen tools. Include annotation/docstring/style and bare-except checks where the pinned rule set supports them. |
| typecheck | Strict mypy for the source, with typed fixtures/tests and narrowly documented compatibility exceptions. |
| test | pytest plus coverage.py (directly or via pinned pytest-cov). At least 80% statement and 80% branch coverage across declared critical source modules; zero tests/coverage is a failure. |
| security | Bandit static checks and a pinned dependency-vulnerability audit of the already locked/installed graph; no automatic fixes or dependency resolution. Zero unreviewed findings; narrow documented suppressions require review. |
| verify / CI | Required formatting, imports, lint, types, tests/coverage, security and application build checks; failures propagate without source/lock rewrites. |
| pre-commit | Versioned config uses the same pinned tools/commands via the reviewed container workflow. Hook installation is an explicit project-local action, never automatic scaffold/host installation. No floating remote hooks or extra tool downloads. |

Critical coverage explicitly includes domain/service logic, models/settings,
versioned endpoints, exception/logging middleware, pagination, request admission
and readiness. Record statement/branch results and test outcomes, not just a
single repository-wide percentage. Tests mirror source modules, use synthetic
fixtures/factory_boy factories where model construction benefits, parametrize
edge cases and exercise injected collaborators, startup/shutdown and API boundaries.
Mock external services; introduce integration tests with any real external dependency
later. Coverage never substitutes for meaningful invalid-input/error/security tests.

Seed negative examples for missing annotations/docstrings, wrong import order,
format/lint/type failures, leaked logging fields, unversioned routes, readiness
failure, insufficient coverage and static/vulnerability findings. Tool-conflicting
rules must be narrowly configured/tested, not hidden with global ignores. Runtime
local/CI evidence stays distinct from private-client acceptance.

## Explicit adaptations and conditional work

| Source section / instruction | Application to SPEC-024 |
|---|---|
| Core principles; Code structure and design | Adopted via service objects, DI, src boundaries and review; method length is an ideal, not a rigid cap. |
| Python standards | Adopted through code/guide, strict types and formatter/linter config. Modern features are bounded by the exact selected interpreter. |
| Dependencies: venv/Poetry, requirements/Poetry lock and separate files | uv creates the owned virtual environment; `pyproject.toml` has runtime dependencies and separate dev/test groups under one exact `uv.lock`. This is the explicit TPL-003 equivalent; no competing handwritten requirements/Poetry locks. |
| Dependencies: python-dotenv and .env.example | Deferred: the current managed runtime forbids dotenv/auth files and implicit environment forwarding. Use typed non-secret defaults and `config/environment.example.md` documenting each setting, type, default and future env name. No `.env`/`.env.example` generation, dotenv dependency or loading in this slice. Future secret/config work must define its own reviewed materialization path. |
| Error handling and logging | Adopted through JSON logs, exception mapping, safe middleware fields and sensitive-output tests. |
| Security best practices | Adopt applicable validation, headers, rate limiting and scans now. Auth/password/SQL/CSRF protections remain conditional on features that need them. |
| Testing requirements | Adopted with pytest, fixtures/factories, parametrization, mirrored tests and measurable critical coverage. |
| API development | Adopted through FastAPI/Pydantic, versioned methods/contracts, pagination, CORS, middleware and liveness/readiness. |
| Async programming | Guidance applies; sample has no external I/O. aiohttp is conditional on a later outbound integration, not an unused dependency. |
| Performance and optimization | Adopt measurement/data-structure/pagination guidance. Redis/Celery/pooling/circuit breakers need actual dependencies and separately reviewed scope. |
| Documentation | Adopt Google docstrings, setup/endpoint examples, annotations, architecture records and a versioned guide. |
| Quality tools: Black, isort, Ruff/pylint, mypy | Adopt Black + isort + Ruff lint + mypy. No Ruff formatting or duplicate pylint stack. |
| Quality tools: pre-commit, Bandit, coverage.py | Adopt through the selected container and explicit hooks; coverage and static scans gate CI. |
| Quality tools: Safety | Safety's current scan workflow requires authentication. Initial proposed equivalent is pinned pip-audit against the public PyPI advisory service without credentials. Resolve pins/service/data/timeout/failure behavior in T-002; do not silently skip scanning. Safety account integration remains deferred pending explicit secret/service scope. |
| Delivery standards | Adopt full working code, complete dependencies/setup/examples, reviewable changes and compatibility tests. |
| Frontend integration (when applicable) | Self-hosted docs assets are the current browser surface. General JS/CSS, CSRF and Jinja2 guidance is retained for future frontend/session/template features rather than adding them here. |

The standards remain the project owner's supplied preferences. The uv, dotenv and
Safety mappings above are explicit draft adaptations to this platform, visible
for scope review; no tool substitution or future integration is presented as
implemented or as literal compliance with those original mechanisms. PYAPI-010 /
AC-010 requires the generated guide/config/gates to preserve this disposition.
