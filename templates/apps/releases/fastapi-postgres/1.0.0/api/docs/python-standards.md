# Python coding standards

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
status codes. Include paginated notes CRUD with bounded limit/offset, separate health/liveness
and readiness endpoints.
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


## Platform adaptations

Use uv-owned virtual environments with exact runtime/dev/test groups and uv.lock.
Use non-secret typed defaults/configuration documentation; dotenv is unsupported.
Bandit and pip-audit provide static/dependency scanning without a Safety account.
Authentication, data access, outbound aiohttp, caching/Celery and session/browser
protections apply when those separately reviewed features are introduced.
These conventions apply to this generated project, not existing platform scripts.
