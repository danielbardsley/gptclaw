# SPEC-033 exact SDK loopback spike evidence

- **Observed:** 2026-10-14 UTC / October 13 America/New_York
- **Status:** Two bounded SDK spikes passed; full native/private acceptance pending
- **Source:** codex/mobile-metro; guarded diagnostic changes are being reviewed in PR #78
- **Security:** Exact owner-approved disposition in [security-review](security-review.md); fresh complete audit/lock admission preceded each start.

## Measured result

| Project | Advertised candidate origin | Target | Manifest bytes | Native bundle bytes |
|---|---|---|---|---|
| mob001-accept-one | https://forge-dev-01-4.tail8c3304.ts.net:8443 | android | 1300 | 6441778 |
| mob001-accept-one | https://forge-dev-01-4.tail8c3304.ts.net:8443 | ios | 1296 | 5737192 |
| mob001-accept-two | https://forge-dev-01-4.tail8c3304.ts.net:8444 | android | 1300 | 6441778 |
| mob001-accept-two | https://forge-dev-01-4.tail8c3304.ts.net:8444 | ios | 1296 | 5737192 |

The probe validated SDK-produced launch-asset URLs against the exact HTTPS origin
and requested them through owned loopback publication with a trusted HTTPS proxy
header. Bodies were streamed and hashed, not retained as evidence. This is not
an actual TLS listener or phone result. Both projects remained schema 5; no
live source opt-in was applied. Filtered source hashes match after each spike,
and exact owned containers/networks are now absent.

Effective real-container inspection confirmed memory 1610612736 bytes, CPU quota
100000, PID limit 256, read-only root/workspace/dependencies, and port publication
only on 127.0.0.1. The reviewed command specified one CPU, no extra capabilities,
no new privileges, ephemeral .expo/tmp and an independent 300-second timeout.
Status returned HTTP 200 on loopback. No environment dump or full inspect was
recorded; signing/broker/home/engine socket/data volumes were not mounted.

## Failure and correction

Earlier bounded attempts failed on pinned CLI BAD_ARGS: --offline cannot be
combined with --lan. Offline mode itself forces LAN within the isolated container.
The argv was corrected to start --offline --go --port 8081. No tunnel/HTTPS
bypass, source-only policy change, host-control or permission relaxation was used.
Startup output is now bounded to 64 KiB in memory and never persisted raw;
only fixed failure codes, allowlisted generic terms, exit code and byte count
can enter owned diagnostics. Cold and retry outcomes remain separate records.

## Remaining acceptance

Manifest asset lists were empty in these unchanged starter fixtures. Asset and
source-map origin/read behavior, HMR/reload WebSocket traffic, sustained load,
full two-session supervised lifecycle, expiry/security revocation and compatible
rollout/rollback still need implementation/evidence. Sequential spikes are not
proof of simultaneous session isolation or shell-disconnect survival.
Private listeners/access policy and physical iOS/Android have not been verified.
No route/SDK account/production operation occurred. Keep all full criteria pending.
