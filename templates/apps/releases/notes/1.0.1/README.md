# Private notes

This project runs Next.js and FastAPI in separate rootless containers managed as
one group. Open the private URL returned by the runner. API docs are at
`api/docs` beneath that URL. Create, edit, delete and paginate plain-text notes.

Notes are shared with authorized tailnet viewers and held only in API process
memory. Refresh/web reload retains saved notes; API reload, project restart or
stop/start loses all notes. Unsaved drafts live in browser memory only. Use only
synthetic notes. There is no database, local-storage persistence or authentication.

Use `gptclawctl start/status/restart/stop/test/verify --project-root <root>`.
`logs`, dependency and quality jobs require `--component api` or `--component web`;
dependency changes and formatting require the group stopped. `test` and `verify`
without a component run both component checks and a cross-service smoke test.
Read `api/docs/python-standards.md`. All checks run in exact reviewed containers.
