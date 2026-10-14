# Private Metro operator plan

- **Status:** Approved operator execution and independent exact readback complete; whole-tailnet access approved; physical-device/removal acceptance pending
- **Owner:** Project owner / existing SSM operator
- **Scope:** Retained mob001-accept-one and mob001-accept-two only
- **Observed:** 2026-10-14 UTC
- **Specification:** [SPEC-033 MET-004](spec.md)
- **Runbook:** [Manage Metro](../../runbooks/manage-metro.md)

## Original observed baseline

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

## Corrected bounded backends

Runtime source watching and established-probe supervision were corrected and the
paired fixtures were deliberately refreshed through their owner controller.
Listener commands, sticky origins/ports and reviewed baseline are unchanged.
The first generation is 5863c80222c346e18e49c0f4ea59ba21, expiring
October 14 at 16:52:14 UTC; the second is cbe287fcd42e4cfbbb18d2981be4853f,
expiring at 16:52:49 UTC. Loopback native rebuild/restoration passed on the first,
with both sources/owned sessions preserved. Refresh current health/readback before
operator action; do not infer that these backends are still live after expiry.


## Executed operator plan and current verification

The owner ran the two approved commands and supplied Serve JSON with exact 8443
and 8444 root handlers. Independent readback verifies the recorded plan, preserved
443 handlers/baseline digest above and Funnel off. Both private TLS native protocol
samples passed; both owned sessions also survived owner-reported SSM disconnect and
reconnect with unchanged generation/expiry and zero restarts.

The owner reports denial from a laptop off-tailnet and under a different connected
identity on both health URLs. This is attributed owner evidence. Relevant policy
source/destination selectors and port grants have not been supplied. Preserve that
remaining policy-review item; do not broaden grants or infer permitted-phone access
from host health. Detailed protocol and reconnect evidence is in
[acceptance](acceptance.md). Finite session expiry still applies.


## Owner-supplied current policy

The console policy supplied by the owner grants wildcard source, destination and
IP traffic. It includes these listener ports but does not restrict them to selected
development devices. Admin ownership of `tag:gptclaw-dev` is tag-assignment authority,
not an access restriction. The earlier different-identity failure is not accepted as
proof of same-tailnet ACL denial. The independent off-tailnet test remains attributed
owner evidence. No policy mutation is performed; a restriction needs separately
reviewed selectors and replacement/splitting of the wildcard allowance, preserving
other intended access. See the corrected [acceptance record](acceptance.md).


## Owner-confirmed whole-tailnet scope

After reviewing the wildcard policy, the owner explicitly confirmed: all devices
on this tailnet should have access to the host. The current grant is therefore the
accepted access scope. No restrictive policy proposal/change is required. Denied
access means outside this tailnet; the owner-reported off-tailnet failure applies.
This supersedes the earlier selective-access assumption while preserving physical
client, route-removal and endpoint-expiry checks.

The positive private renewal rehearsal subsequently replaced only the first session
with generation aba2b3b0b860477bbfd1d1f3da0f0bc3, expiring at 17:30:08 UTC. Its
old generation's root entry returns HTTP 503 over default-trust HTTPS. The second
session retains generation cbe287fcd42e4cfbbb18d2981be4853f and 16:52:49 expiry.
Serve commands/handlers/baseline are unchanged; no further operator action is needed.


## Approved HTTP compatibility conversion (October 14 UTC)

The owner approved replacing the two existing HTTPS Metro listeners with private
HTTP on the same ports/proxies; port 443 and all unrelated routes are unchanged.
Installed Tailscale 1.104.1 help and pinned source confirm HTTP listener support.
Current schema-2 plans retain the exact original HTTPS approvals, preserve baseline
d0c41e928966c5d085e704d5826120b76ae4b4af854eb0aa570e447d52db5539,
and emit the exact conversion/rollback commands in the
[HTTP runbook](../../runbooks/manage-metro.md#approved-sdk-57-private-http-operator-conversion).
No listener has been changed by forge. Native/iOS acceptance remains pending.
