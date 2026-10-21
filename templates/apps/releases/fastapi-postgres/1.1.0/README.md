# Private Python notes backend

FastAPI and PostgreSQL with no web frontend. Select fastapi-postgres@1.0.0
explicitly. Use gptclawctl db init, start/status/stop with this project root;
start never migrates, seeds or recreates data. Stop retains persistent records.
Use --component api for dependency/quality operations. test/verify run isolated
PostgreSQL persistence, migration and recovery checks. Bind an expo-notes project
explicitly; Metro and backend lifecycles remain independent. Notes are synthetic,
shared, unauthenticated development records. Production is outside this starter.

## Quality workflow

See [quality commands and gates](docs/quality.md). The standard portable entrypoint
is `python3 checks/gptclaw_quality.py verify --engine podman`.
