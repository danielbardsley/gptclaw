# Development API design

The parent ASGI application mounts one child API at its managed project prefix.
The ingress preserves that prefix. Thin `/api/v1` routes inject EchoService;
Pydantic models validate requests/responses and settings. A single-process fixed
window provides constant-memory admission; health/readiness are exempt. Middleware
logs allowlisted metadata and adds security headers. Swagger assets are bundled.
Slash docs redirects are relative, so forwarded/Host headers cannot change their origin.

This is a non-packaged src application with an explicit source import path. NotesService uses an injected Database boundary, parameterized SQL and bounded
PostgreSQL pooling; mutations are transactional. Alembic schema changes are explicit
managed operations. Local credential files are loaded lazily and never logged.
Introduce authentication/external I/O only with its reviewed runtime capabilities and applicable coding standards. Measure before
optimizing, avoid blocking async I/O, and use bounded/mockable collaborators.
