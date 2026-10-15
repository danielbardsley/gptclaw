# Private mobile Python backends

[SPEC-036](../docs/036-mobile-python-backend/spec.md) adds explicit development
binding between a canonical Expo notes project and a separate Python/FastAPI +
PostgreSQL project. Source support is distinct from installed provider capability
and physical Android acceptance; consult the [evidence](../docs/036-mobile-python-backend/acceptance.md).

## Create and bind

Use a reviewed provider supporting manifest schemas 8/9, group receipt 4 and
catalogue 7. Existing web/API/group/mobile projects retain their versions and
behavior. Neither new starter is the implicit default. Replace the synthetic
example IDs and roots with the exact selected targets.

```bash
gptclawctl new example-backend --template fastapi-postgres --template-version 1.0.0 --local-only
gptclawctl new example-mobile --template expo-notes --template-version 1.0.0 --local-only
gptclawctl db init --project-root /srv/forge/projects/example-backend
gptclawctl start --project-root /srv/forge/projects/example-backend
gptclawctl backend bind --project-root /srv/forge/projects/example-mobile --backend-root /srv/forge/projects/example-backend --api-url https://HOST.ts.net/projects/example-backend/api
gptclawctl backend inspect --project-root /srv/forge/projects/example-mobile
```

Complete each project's existing canonical repository setup before binding.
The CLI requires canonical roots; linked task worktrees remain source-only.
The binding must use the host's exact approved private HTTPS identity and API
prefix, with no query/fragment/credentials. No loopback, arbitrary public URL,
HTTP API or production profile is accepted. The backend ID and Python/PostgreSQL
contract are checked without starting or initializing it.

Binding writes only `.gptclaw/backend.local.json` and
`src/config/backend.generated.ts` in the mobile root. Both are ignored public
configuration, never server credentials. Keep private hostnames out of committed
source and shared evidence. Generated source/CI checks create an unbound synthetic
placeholder when needed; missing binding makes the UI show setup guidance and
perform no API request. The repository-owned contract generator v1 is frozen with
the starter, uses no downloaded generator dependency and refuses stale/breaking
output. To change API contracts, export the real Python OpenAPI, review the native
contract snapshot and regenerate with `node checks/contract.cjs --write` inside the
reviewed Node job; run both Python and native contract checks.

## Run and iterate

Use the existing [Metro/Expo Go procedure](manage-metro.md) and its
current eligibility, security, operator-routing and expiry gates. Binding does
not create a listener, approve an SDK/client combination or expand a Metro HTTP
exception to the application API. Only Android physical acceptance is selected.

Stop Metro before changing the binding. Explicitly restart/reload after a change.
The session fingerprints both local binding and generated public inputs; changed
inputs cannot be treated as the same healthy activation. A running app never
silently switches environment. Backend API/database status and Metro readiness
remain independently observed; the UI displays its actual request outcome.

The Fieldnotes UI provides list/pagination, create/open/edit/save and confirmed
delete. Failed requests retain the editor draft. Uncertain writes require an
explicit refresh before another save; check the saved collection to reconcile a
possibly completed create. No automatic write retry or offline queue exists.
Unsaved edits are in memory and do not survive application relaunch; saved records
are refetched from PostgreSQL. Existing starter limits remain 100 notes, 120 title
characters and 10,000 body characters. Notes are synthetic shared development
records; there is no per-user login or production authorization.

## Verify and recover

Use native format/lint/typecheck/test/security/build/verify jobs and
`test`/`verify` at the backend project root. Backend component dependency/format
jobs require `--component api` and the group stopped. Backend tests use a fresh
owned API/DB-only fixture and existing verified PostgreSQL backup, restore,
rotation and migration checks. The retained compiled native v1 adapter exercises
CRUD before and after an additive schema change without receiving DB credentials.
Generated backend CI runs `python3 checks/verify.py --engine docker` with the
pinned toolchain and disposable PostgreSQL; it requires no web service/browser.

Start orders DB then API, with authenticated schema readiness before publication.
It never initializes missing storage, seeds or migrates automatically. Health,
ready, OpenAPI and bundled docs are under `/projects/ID/api/`; only declared API
paths are routed. An API-only group has no frontend fallback link or web unit.
Database ports stay unpublished. Stop/start/restart of either project leaves the
other project's activation and source intact; backend stop retains data and roles.

Follow the existing [database runbook](manage-development-databases.md) for stopped
writer plans, migration, verified backup/restore, rotation and recovery. Provider
rollback does not undo migrations. Reconcile and stop new contracts with a capable
provider before restoring a reviewed snapshot; retain source/data/roles/backups.
Older providers must refuse new contracts without rewriting them. Do not use reset
or downgrade to make an old provider accept a project. Source/CI tests cannot
establish private device HTTPS access, physical interaction, visual quality or
accessibility. Record those checks separately before marking MOB-010/M1 accepted.
