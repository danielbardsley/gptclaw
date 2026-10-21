# Notes API component

This FastAPI component belongs to the parent Python API/database notes project. Operate it
through the group root with `--component api`; it is not a standalone project.
Read [Python standards](docs/python-standards.md) and [component guidance](AGENTS.md).

Typed `/api/v1/notes` routes inside the private project prefix support create,
list, get, replace and delete. List responses contain ID/title/90-character preview;
get returns the full body. Titles trim to 1–120 characters, bodies allow 10,000
characters, pages are bounded and the transactional database fixture holds 100 notes.
Missing notes return 404, malformed input 422, full capacity 409 and admission 429.
Docs and bundled assets live under `api/docs` and `api/docs-assets` beneath the
parent private URL. Liveness/readiness are `api/health` and `api/ready`.

Notes are synthetic shared development data retained in PostgreSQL. Reload and
stop/start preserve saved records. Credentials are selected read-only runtime
files from the local development store outside Git. NotesService uses SQLAlchemy
transactions and a capacity lock; migrations use explicit Alembic operations.
Readiness checks authenticated connectivity and the declared migration head.
There is no browser persistence or per-user identity. Logs contain safe metadata,
never titles/bodies, passwords or raw error internals.

Group verify invokes the exact locked Black/isort/Ruff/mypy/pytest/coverage/Bandit/
audit/build checks. Critical statement and branch coverage must each reach 80%.
Format/dependency mutations require the whole group stopped. Parent `hooks` installs
an explicit container-based group-verify hook; no host language installation is needed.
