# Notes project guidance

Read `api/AGENTS.md` and `api/docs/python-standards.md` for Python work and
`web/AGENTS.md` for frontend work. Use the group runner with the repository root;
components cannot be started independently. Dependency/format jobs require the
whole group stopped and an explicit component. Notes are synthetic shared data
stored in the project-owned PostgreSQL database. Use only the platform database
operations for migration/reset/restore; never log payloads or credential values.
Local development credentials are selected read-only runtime files outside Git.
