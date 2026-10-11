# Private FastAPI starter

Generate with `gptclawctl new my-api --template fastapi --template-version 1.0.0 --local-only`.
Use the returned absolute project path for `--project-root` on validate, start,
status, logs, test, restart and stop. Normal start prepares the verified Python/uv
image, restores the complete locked runtime/dev/test graph and runs build/preflight.
Open the returned private URL and `/docs`; call `/api/v1/echo` with a JSON message
or `/api/v1/examples?limit=2&offset=1`. This is synthetic stateless data.

Use `gptclawctl format --project-root ROOT` explicitly to apply Black/isort.
`lint`, `typecheck`, `test`, `security`, `build` and `verify` use the same target flag.
Verify includes all checks; security queries public advisory data with a finite
request timeout and fails when that service is unavailable. It performs no autofix.
Coverage requires 80% statements and 80% branches across application source.

Application source changes reload automatically; syntax errors make readiness fail
until fixed. Dependency/toolchain changes require stopped-target preparation;
use typed deps add/update/remove/install/recover, never a competing lockfile.
A stop preserves source and the disposable project-local environment/cache.

Read [Python standards](docs/python-standards.md), [configuration](config/environment.example.md)
and [architecture](docs/architecture.md). No dotenv, database, credentials, workers,
AI calls or authentication are present. Liveness is `/health`; readiness is `/ready`.
CORS denies cross-origin calls by default. API logging records safe correlation,
route template, method/status/duration only; requests/responses carry no retained data.

Pre-commit config uses local/system hooks and the same pinned quality runner.
For an explicitly stopped Git project, `gptclawctl hooks --project-root ROOT`
installs a project-local commit hook that invokes verify through an immutable
provider snapshot. It refuses an existing unknown hook and worktree Git files;
there is no host tool install or automatic generation hook. The config can also
be run by the prepared pre-commit tool inside the container. CI runs the gates
directly; no hook or runtime secret is required.
