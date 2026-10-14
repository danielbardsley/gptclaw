# Private Metro operator plan

- **Status:** Exact two listeners approved by project owner; operator execution/readback pending
- **Owner:** Project owner / existing SSM operator
- **Scope:** Retained mob001-accept-one and mob001-accept-two only
- **Observed:** 2026-10-14 UTC
- **Specification:** [SPEC-033 MET-004](spec.md)
- **Runbook:** [Manage Metro](../../runbooks/manage-metro.md)

## Observed baseline

Read-only Tailscale 1.104.1 Serve readback has only TCP 443 with:

- /projects/ → http://127.0.0.1:18079/projects/
- /dashboard/ → http://127.0.0.1:18200/dashboard/

Funnel is off. Ports 8443 and 8444 have no Serve listeners. The baseline canonical
JSON digest is d0c41e928966c5d085e704d5826120b76ae4b4af854eb0aa570e447d52db5539.
This is route configuration evidence, not an ACL readback or proof of a permitted
phone. The repository owns enrollment as tag:gptclaw-dev, but has no authoritative
tailnet access policy source. The operator must confirm the existing permitted
development-owner device selector and its TCP 8443/8444 access to this node,
including denied unpermitted access. Do not add a wildcard grant to make tests pass.
If a policy change is needed, prepare its concrete selectors and review it separately.

The official [Serve command reference](https://tailscale.com/docs/reference/tailscale-cli/serve)
supports choosing an HTTPS listener port and background serving. The installed
combined stdout/stderr help confirms --https and --bg. Actual TLS/native behavior
on these two ports still requires operator/device acceptance; help alone is not
that evidence.

## Exact change and verification

Require fresh tailscale serve status --json to match the baseline before adding
listeners. First verify each owned loopback proxy healthy and its finite expiry.
The source provider's metro route-plan --project-root ROOT emits exact commands
and a digest. --apply --confirm-plan DIGEST records the unchanged plan locally;
it neither runs sudo nor changes Tailscale or access policy. An occupied unrecorded
listener blocks, even if its target appears identical.

The project owner approved these exact two private listeners in this session on
October 14. The existing SSM operator adds only these absent listeners after the
bounded backends are healthy:

~~~sh
sudo tailscale serve --bg --https=8443 http://127.0.0.1:18601
sudo tailscale serve --bg --https=8444 http://127.0.0.1:18603
tailscale serve status --json
~~~

Expected root-origin routes:

| Project | Private origin | Owned loopback proxy |
|---|---|---|
| mob001-accept-one | https://forge-dev-01-4.tail8c3304.ts.net:8443 | 127.0.0.1:18601 |
| mob001-accept-two | https://forge-dev-01-4.tail8c3304.ts.net:8444 | 127.0.0.1:18603 |

Preserve every other handler/listener and keep Funnel off. No Serve reset, shared
port-443 change, public/LAN listener, host permission change or AWS mutation.
If the baseline changed, rerun the planner and review the new concrete diff.

The supervisor independently verifies exact recorded Serve ownership, preserved
baseline handlers and default-trust HTTPS generation/expiry health every ten seconds.
Config-only success cannot report private transport ready. Missing, foreign, stale,
wrong-generation, TLS-failed, stopped or expired paths are unavailable.
Host TLS health does not prove phone permission, complete native delivery or a
device online. Physical iOS/Android, bundle/asset/map/WebSocket and denied access
checks remain separate acceptance evidence.

## Owned removal and rollback

Stop the selected session through its capable owner provider first. Verify its
SDK/network absent and proxy port released; the retained Serve listener then has
no backend and cannot serve another project (sticky origins are not recycled).

Read the current Serve configuration. Remove a listener only when its HTTPS/root
handler exactly matches the owned proxy above, with no additional handlers or
unrelated target. The scoped operator removal is:

~~~sh
sudo tailscale serve --bg --https=8443 off
sudo tailscale serve --bg --https=8444 off
tailscale serve status --json
~~~

Keep all original flags, including --bg, when disabling a background listener.
Remove only the chosen owned listener(s); preserve port 443 and all unrelated
entries. Roll back before selecting an older provider incapable of schema-6 recovery.
Keep source, metadata journals, typed receipts and retained fixture PRs. If ownership
or shutdown cannot be proved, report recovery required and preserve unknown state.

## Approved preparation readback

Both unchanged plans were recorded locally against the baseline above; no Serve
mutation was performed. Plan digests:

- mob001-accept-one: 8eee01ff184d09eae0fb5669287f68b7a4e1f8c56791b4c59b37987b47dad4c9
- mob001-accept-two: a504772bb9c0d8d2d104be338ad7c6931eaed8c780292da5d8dbd5f90c089e15

The retained fixture PRs now declare 3,600-second finite sessions:
[one PR #2](https://github.com/danielbardsley/mob001-accept-one/pull/2)
at 982f38983fb5ccca6b01d157e563fd837a7a801d and
[two PR #2](https://github.com/danielbardsley/mob001-accept-two/pull/2)
at 53f7fc7875b91bc644dcc7ece54c4c27ca242f22. Validation passed for both;
only the declared TTL changed. Actual backend health/expiry is checked separately
before asking the operator to add the approved listeners.
