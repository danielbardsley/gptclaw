# Notes API component

This FastAPI component belongs to the parent two-service notes project. Operate it
through the group root with `--component api`; it is not a standalone project.
Read [Python standards](docs/python-standards.md) and [component guidance](AGENTS.md).

Typed `/api/v1/notes` routes inside the private project prefix support create,
list, get, replace and delete. List responses contain ID/title/90-character preview;
get returns the full body. Titles trim to 1–120 characters, bodies allow 10,000
characters, pages are bounded and the synchronized process store holds 100 notes.
Missing notes return 404, malformed input 422, full capacity 409 and admission 429.
Docs and bundled assets live under `api/docs` and `api/docs-assets` beneath the
parent private URL. Liveness/readiness are `api/health` and `api/ready`.

Notes are synthetic shared data held only in this process's memory. API source
reload, restart, group stop/start or host replacement loses every note. No files,
database, browser storage, credentials or per-user isolation are provided. Logs
contain safe request metadata, never note titles/bodies or raw error internals.

Group verify invokes the exact locked Black/isort/Ruff/mypy/pytest/coverage/Bandit/
audit/build checks. Critical statement and branch coverage must each reach 80%.
Format/dependency mutations require the whole group stopped. Parent `hooks` installs
an explicit container-based group-verify hook; no host language installation is needed.
