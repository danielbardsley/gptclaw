# Fieldnotes — private native notebook

A warm, accessible synthetic notes fixture for Android Expo Go, Python/FastAPI
and PostgreSQL. Create fastapi-postgres@1.2.0 and expo-notes@1.2.0 independently.
Initialize/start the backend using its own root. Bind the canonical mobile project:

gptclawctl backend bind --project-root MOBILE_ROOT --backend-root BACKEND_ROOT --api-url https://backend.example.invalid/projects/BACKEND_ID/api

Only the exact approved private HTTPS identity is admitted. This local public
binding is ignored; backend credentials never enter mobile configuration. Bind
with Metro stopped, then explicitly start/reload the mobile project. Missing binding
renders a useful setup message and performs no API request. No backend auto-start.
Saved notes persist; unsaved edits survive request failures but not app relaunch.
An uncertain write requires explicit server refresh before another save. No offline
write queue, accounts, signing, real data or production support is included.
Run the generated format/lint/typecheck/test/build/security/verify gates. build
exports JavaScript/assets, not native binaries. Device acceptance is separate.

## Quality workflow

See [quality commands and gates](docs/quality.md). The standard portable entrypoint
is `python3 checks/gptclaw_quality.py verify --engine podman`.
