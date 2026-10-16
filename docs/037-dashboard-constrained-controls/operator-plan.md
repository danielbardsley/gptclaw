# DSH-009 private Metro acceptance operator handoff

- **Status:** Approved additions executed by existing operator and independently verified; removal pending
- **Owner:** Project owner / existing SSM operator
- **Scope:** `mob001-accept-one` and `mob001-accept-two` acceptance only
- **Related:** [Specification](spec.md), [acceptance](acceptance.md), [Metro runbook](../../runbooks/manage-metro.md)

The project owner approved private rollout and these named fixture rehearsals after
the remaining checks pass. Forge does not administer Tailscale. This handoff uses
the existing operator path and grants no new privilege, public exposure or policy
exception. Actual operator execution remains required.

## Observed baseline and preconditions

Read-only Serve inspection on October 15 found Funnel off, TCP 443 with the existing
`/dashboard/` and `/projects/` handlers, and an unrelated private HTTP listener on
8445. Listeners 8443 and 8444 are absent. The canonical configuration digest is
`e2260ad525b61b5f15e51d20e38f3074fda6e555458eb6a939fb827725b33e0a`.
Preserve all three existing handlers, their targets and protocol flags.

The frozen candidate provider produced these read-only plans without changing
source, receipts or Serve:

| Fixture | Plan digest | Private listener | Owned proxy |
|---|---|---|---|
| mob001-accept-one | `9aa9584e17457e51775ca5332b17b1cb00cc6a195625c994cb63213714f774c6` | HTTP 8443 | `127.0.0.1:18601` |
| mob001-accept-two | `3db774203ca5f7f48a35f04938ccded8c534f8364f8274563a4eafd7e3914cb1` | HTTP 8444 | `127.0.0.1:18603` |

These are private tailnet HTTP listeners inside encrypted Tailscale, preserving
the fixtures' already reviewed transport. No TCP 443 replacement or Funnel change
is included. Host routing evidence does not establish phone access or native
client acceptance; those belong to the separate Metro/Go initiatives.

Before operator execution, finish the pending checks, validate the current source
and security admission, and start fresh finite sessions through the reviewed
provider. Confirm each exact owned loopback proxy's generation/protocol health and
expiry. Do not extend the expired old leases. Re-read Serve and require the
baseline above; if it changed, stop and prepare a new exact diff.

## Existing operator action, once backends are ready

Through the existing SSM operator path only:

```sh
sudo tailscale serve --bg --http=8443 http://127.0.0.1:18601
sudo tailscale serve --bg --http=8444 http://127.0.0.1:18603
tailscale serve status --json
```

Verify exact HTTP/root targets on those two ports, unchanged 443 and 8445 handlers,
and Funnel off. Forge independently re-reads the result and records the exact
unchanged plans through `metro route-plan --apply --confirm-plan` if needed.
The supervisor must then verify the real private generation/expiry health before
dashboard controls can report Metro readiness or acceptance can pass.

## Scoped removal after acceptance

First stop each accepted owned session through the reviewed provider and prove its
SDK/network absent and loopback proxy released. Re-read Serve and require each
selected listener still has only the exact owned HTTP/root target above. Then the
existing operator removes only those acceptance listeners:

```sh
sudo tailscale serve --bg --http=8443 off
sudo tailscale serve --bg --http=8444 off
tailscale serve status --json
```

Independent readback must restore the baseline digest above. Preserve all existing
443/8445 handlers, project source/data, policy and operation evidence. Unknown or
changed ownership blocks removal; never reset Serve or remove an unrelated route.
