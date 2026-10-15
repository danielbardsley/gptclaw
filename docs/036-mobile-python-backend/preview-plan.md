# Fieldnotes private Expo Go preview

Requested by the project owner on October 15, 2026. Confirmed phone: Android 11,
Expo Go 57.0.9, connected to the development tailnet.

Create only these private repositories through the existing managed GitHub App:
- danielbardsley/fieldnotes-api: fastapi-postgres@1.0.0, Python/FastAPI + PostgreSQL.
- danielbardsley/fieldnotes-mobile: expo-notes@1.0.0, native Fieldnotes.

The explicit named workflow-publication policy currently contains only
`gptclaw-shelfmark`, `gptclaw-trailboard`, `mob001-accept-one`, and `mob001-accept-two`.
Read-only `new ... --plan` refused both new names with credential-workflow-policy.
No repository or runtime has been created. Preserve all four existing names;
add only `fieldnotes-api` and `fieldnotes-mobile`. Retain current App grants,
private visibility and PR review policy. No credentials or grant expansion.
The supported policy update requires temporary profile deactivation and verified
helper refresh, then reactivation; preserve the prior profile for recovery.

After that gate and passing source checks: create canonical projects, initialize
only their new synthetic database, start the API through the managed provider,
bind mobile to the existing private HTTPS /projects/fieldnotes-api/api prefix,
and start a supervised two-hour Expo session with the accepted private HTTP
transport inside Tailscale. Existing HTTPS application/dashboard routes and all
other applications/data remain intact. No public tunnel, cloud build or signing.

The next unused sticky Metro slot is 2: SDK loopback 18604, proxy loopback 18605,
private Serve HTTP port 8445. Existing slots 0/1 belong to retained earlier
fixtures and must not be recycled. Capture and apply the exact managed route-plan
only once the new canonical identity/session exists. The existing reviewed SSM
operator path must install only `--http=8445 http://127.0.0.1:18605`, with before/
after readback preserving every port-443 handler and Funnel-off state. Forge
must not improvise sudo or alternative listeners. A final generation-bound Go
link is returned only after host protocol, route and client eligibility pass.

Recovery: stop/reconcile only Fieldnotes using a capable provider; retain source,
synthetic saved records and role files. Remove only the exact owned HTTP 8445
listener through the operator; do not remove unrelated handlers or downgrade DB.
Owner physical/visual acceptance remains separate from host readiness.
