# Private notes

This project runs Next.js, FastAPI and PostgreSQL in separate rootless containers managed as
one group. Open the private URL returned by the runner. API docs are at
`api/docs` beneath that URL. Create, edit, delete and paginate plain-text notes.

Notes are shared with authorized tailnet viewers and stored in the project's
PostgreSQL database. Saved notes survive API reload, group restart and container
replacement. Unsaved drafts live only in browser memory. Use synthetic notes;
authentication/accounts and per-user isolation are outside this development slice.
Initialize the database explicitly with `gptclawctl db init --project-root <root>`
before first start. Migration/reset/restore are reviewed plan/apply operations;
ordinary startup never deletes data or changes schema.

Use `gptclawctl start/status/restart/stop/test/verify --project-root <root>`.
`logs`, dependency and quality jobs require `--component api`, `web`, or `db` for logs;
dependency changes and formatting require the group stopped. `test` and `verify`
without a component run both component checks and a disposable real database/browser workflow.
Read `api/docs/python-standards.md`. All checks run in exact reviewed containers.

This release retains notes across API reload and project restart. Database initialization,
migration, backup, restore and reset use the reviewed platform DB workflow. Local
backups share the project volume and provide no proven host-loss recovery.

## Quality workflow

See [quality commands and gates](docs/quality.md). The standard portable entrypoint
is `python3 checks/gptclaw_quality.py verify --engine podman`.
