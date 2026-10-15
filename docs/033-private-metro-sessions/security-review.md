# SPEC-033 runtime advisory disposition

- **Status:** Approved scoped temporary disposition — actual SDK evidence pending
- **Owner:** Project owner
- **Observed:** 2026-10-13 (America/New_York)
- **Scope:** Exact locked SDK-57 native-development graph, private bounded Metro only
- **Expiry:** End of October 27, 2026 (America/New_York)

## Actual evidence

Fresh source-only pnpm audit in the existing rootless Node 24.21.0/pnpm 12.10.1 image
returned two high and three moderate findings, with no critical finding. Exact high
findings match the prior graph, but the prior exceptions do **not** cover Metro:

| Advisory | Exact package | Current upstream disposition |
|---|---|---|
| [GHSA-86w9-cpqp-85rv](https://github.com/advisories/GHSA-86w9-cpqp-85rv) | node-forge 1.4.0 | No patched version listed October 13; malformed RSA signature verification. |
| [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) | braces 3.0.3 | No patched version listed October 13; nested-pattern stack exhaustion. |

Static inspection of the installed exact @expo/cli 57.0.29 confirms that manifest
signing returns null without the matching project signing configuration/EAS project
ID; offline mode avoids fetching a development certificate. This is code-path
inspection, not native-client or exposed-service acceptance. Existing source config
has no EAS project ID, update signing certificate or private key. No credential
file was opened, no signing bypass implemented, and no Metro process started.

The frozen lock digest is enforced by the proposed runtime policy. Eight offline
admission tests passed: unapproved/source-only policies, future/expired approval,
changed graph/version, unknown high/critical, duplicate/omitted findings and broadened
exceptions all fail. The earlier null approval correctly blocked runtime admission. The owner now
approved the exact reviewed exceptions/fixtures; fresh audit and all controls
remain enforced before execution.

## Approved bounded scope

Allow only the two exact advisory/package/version tuples above for private native
Metro, through October 27, conditional on implementation and verification of all
controls below. Do not suppress moderate findings or accept another high/critical
finding, changed version/graph, incomplete audit or expiry. Keep source-only policy
files and published template releases unchanged. This proposal is not production,
EAS Update, custom signed client, certificate verification or public service approval.

The initial spike is loopback only, on the two exact retained synthetic roots.
Its helper permits at most 300 seconds and has no Tailscale administration, private
proxy or device-launch behavior. Its read-only plan and actual unapproved start
denial were verified. Twenty-one additional offline tests cover source filtering,
symlink/hardlink/FIFO/traversal/size limits, exact fixture/origin scope, prepared
dependency admission, security expiry, isolated resources and owned cleanup.
Ten further synthetic loopback protocol tests cover a 3 MiB streamed response,
size/header/deadline limits, malformed/truncated data, redirects and foreign/encoded
credential URLs. The spike probes both target manifests/bundles and manifest-listed
assets, retains hashes/counts rather than raw manifests, and never claims physical
or private-route acceptance. These are local preflight tests, not proof of actual
SDK protocol or deployed limits.

Required controls for this initial SDK spike:

- Fixed offline Expo argv and reviewed public environment only; no EAS/update
  signing/project configuration, credential home, broker/signing material or engine
  socket. Do not disable TLS or native signature validation to make a client load.
- Container 1 CPU/1536 MiB/256 PIDs, a 300-second spike bound initially, then bounded
  reviewed supervised sessions with maximum eight hours and earlier security expiry.
- Filtered read-only source/dependency view, ephemeral .expo state, no durable device
  identifiers, and owned bounded caches/logs. Developer source patterns are owned
  inputs; no API accepts arbitrary remote glob expressions or proxy targets.
- Loopback-only publication on 18600–18630 (even ports); a fixed advertised host
  forge-dev-01-4.tail8c3304.ts.net with candidate port 8443–8450; no caller-supplied
  proxy target or private listener operation. Podman independently enforces timeout
  and security expiry if the controlling shell disconnects. No persisted SDK logs.
- Before any subsequent private exposure: private origin/Host validation, verified
  protocol routes, bounded streaming/WebSockets and caller-supplied-target rejection.
  These additional controls still require implementation/verification; operator
  listener/access scope is a separate decision. No public tunnel/Funnel fallback.
- Fresh complete audit/lock admission before start/renewal, bounded supervision that
  revokes runtime on approval expiry/drift, and unit/integration evidence for these
  failures. Unknown processes/source edits/data are preserved during reconciliation.

The initial controls exist in scripts/metro_spike.py and scripts/metro_security.py
and have offline negative-path evidence; actual SDK/resource/cleanup behavior
remains unproven until the authorized spike runs. The separate policy now records the verified owner approval timestamp;
source-only exception files are unchanged. Subsequent supervised/private controls remain requirements, so
approval alone cannot establish readiness or permit unimplemented exposure. Native
Go compatibility and physical iOS/Android testing remain separate acceptance gates.

Removal owner: project owner. Adopt a patched reviewed graph/new immutable release
and remove exceptions, or obtain fresh concrete disposition before expiry. Expiry
blocks new runtime and revokes existing sessions; it never silently extends to an
eight-hour lease. No standing exception is inherited by another client/release mode.

## Approved acceptance targets

Reuse only the retained synthetic mob001-accept-one and mob001-accept-two
canonical source roots for the bounded protocol/device fixtures, preserving Git
history/private PRs and restoring only task-owned edits. No new GitHub grant/repository
or data deletion is proposed. Exact new private listeners/access selectors are
prepared after local protocol evidence and still need the reviewed operator path;
this proposal does not let forge administer Tailscale.

## Approval provenance

The project owner explicitly instructed “Give approval due the exceptions please”
in the monitoring chat after the exact linked review and pending decision were
identified. The authorized relay was verified against that user message, not
inferred from a heartbeat or general implementation goal. Approval timestamp: 2026-10-13T23:46:56Z.
Source chat: 01a1375a-3836-70b1-bd8b-be3ed5ed52a3; user-message ID
01a137a9-7a18-7852-a95b-30db1e88e468. This approves the two exact exceptions through
October 27, the retained fixtures and an initial loopback-only spike of at most
five minutes. Later private sessions still require verified controls, at most eight
hours and separate operator listener approval. No public, signing, production,
infrastructure or deployment-gate bypass scope was granted.

## Runtime source watching and noninteractive input

Pinned @expo/cli 57.0.29 source in instantiateMetro.js explicitly disables watch/
reloads when its boolish CI flag is true. Supervised development SDK sessions
therefore use CI=false; audit/source/spike jobs retain CI=1. This implements the
already approved source-edit development loop rather than extending advisory,
account or exposure scope. The pinned interactive utility additionally requires
stdout.isTTY. Runtime Podman has no interactive/TTY flags; its launcher explicitly
uses stdin DEVNULL and bounded piped non-TTY output. Offline Go mode, telemetry/
dotenv disabling, public-only configuration, readonly mounts, internal network,
loopback publishing and all resource/TTL limits are preserved. No package or
advisory exception changed. Focused tests verify watcher opt-in/default separation,
unchanged bounds and actual closed-input/non-TTY behavior.
