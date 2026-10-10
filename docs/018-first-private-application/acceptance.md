# SPEC-018 acceptance evidence

- **Status:** Delivered — accepted initial single-web workflow
- **Owner:** Daniel
- **Date:** 2026-10-09 (America/New_York)
- **Specification:** [SPEC-018](spec.md)
- **Design:** [TDD-018](technical-design.md)
- **Tasks:** [Tasks](tasks.md)
- **Operation:** [Private app runbook](../../runbooks/manage-private-apps.md)
- **Implementation merge:** [PR #40](https://github.com/danielbardsley/gptclaw/pull/40), `52b57caf1d86e81e1bbb41a77af35ed45e7df1f6` (October 10, 2026 UTC)
- **Last updated:** October 10, 2026 UTC

Daniel authorized “implement the spec.” Tests and services below use synthetic
Hello World sources and the unprivileged forge identity. No AWS infrastructure,
IAM, sudo grant, host package or general Tailscale Unix operator setting changed.
No automatic enrollment credentials, SSH keys or environment dumps are included.

## Criteria

| ID | State | Evidence / remaining work |
|---|---|---|
| AC-001 | passed locally | CLI created/validated `hello-second` and a temporary `workflow-template-check`; existing destination refused without overwrite. Temporary source was removed only after exact file/symlink checks. Offline invalid/symlink/duplicate-ID/no-execution cases pass. The initial Hello World was a prototype subsequently adopted using verified ownership. |
| AC-002 | passed locally/live | Frozen install, manifest build, health tests and TypeScript check passed in the pinned container. Two rootless services are healthy on distinct loopback ports. Cached/repeated start, per-project locking, timeout and failed-health/no-publish behavior verified. |
| AC-003 | passed locally/live | Hello World uses 18080, second app 18081. Stopping the second returned its mapping to 404, removed its listener/activation and retained source; first app health remained 200. Source-preserving warm start and intentional restart passed. Offline port/conflict and unrelated-state preservation tests pass. |
| AC-004 | passed live/owner | Both private pages/counters confirmed; shared prefix, loopback bindings, assets/health/HMR and disabled Funnel verified. Daniel confirmed the second app source edit updated automatically in his desktop browser on October 10. |
| AC-005 | passed live/owner | Daniel confirmed automatic browser update after a source edit; temporary edit restored. All 16 existing first-app source/guidance/manifest files remained byte-identical through stop and start. App-data limits are documented. |
| AC-006 | passed | Implementation and closeout patch/evidence are merged; all three closeout CI workflows and local checks passed. Two-app live workflow, scoped cleanup, source retention and timings are recorded. Daniel requested these two final checks for closeout and confirmed the browser auto-update; both checks passed. Initial slice accepted with recorded timing/host/skill limits. |
| AC-007 | passed live/owner | Initial desktop Hello World proof and shared-prefix transition were confirmed. With provider 1.0.1, managed stop removed the owned service/activation and private app mapping (404), retained source and kept the second app available. Start restored readiness/private routing without an operator command. |

## Executed behavior checks

- Official Node image was fetched and pinned by its observed digest; tool image
  verified Node 24.21.0 and pnpm 12.10.1. Exact npm package metadata selected
  Next.js 16.4.0, React/DOM 19.3.0 and TypeScript 6.0.3; the template has a frozen
  integrity lock. No Node/npm installation ran on EC2 itself.
- The first app was built from the starter, dependencies installed inside a
  bounded rootless container and its owned user Quadlet started. Local health
  identified `hello-world`.
- `tailscale serve` as forge was denied. No privilege workaround was attempted.
  Daniel used his existing SSM operator access for the one selected prototype
  route; subsequent status showed its exact backend and no active Funnel.
- Agent checked private HTTPS page/health (both 200). Daniel reported “Page loads
  and counter works” from his desktop. This is attributed owner browser evidence.
- `gptclawctl new hello-second`, validate and start passed. Dependency preparation,
  build/test/typecheck run only inside rootless containers. The first warm
  stop/start measured 3.226 seconds; repeated start was a no-op in 0.362 seconds.
- Stop preserved second source (verified hash), removed its mapping/listener and
  kept first health 200. Intentional restart recorded separate stop/start
  transitions; local completion measured 4.872 seconds. Its private-route outcome
  correctly remained operator-required while the shared prefix was absent.
- The unprivileged loopback router served page/health and 18 real assets; largest
  observed asset was 1,053,025 bytes. Next.js 16.4 uses the `/_next/hmr` endpoint;
  the initial older-endpoint probe timed out, then the correct endpoint returned
  HTTP 101 through ingress. No request identifier or handshake nonce is retained.
- Stable provider snapshot/launcher was installed only in the owned runtime
  namespace; its version/capability output was observed. No global shell setting
  or host policy was changed.

## Verification, failures and limits

Focused lifecycle/proxy tests cover target validation, source retention, port
conflicts, busy locks, ownership/unit/drop-in refusal, bounded output, unknown
jobs, literal container argv, redirect refusal and failed-health non-publication.
`./scripts/check-repository.sh` passed after correcting a skill resource link
that escaped its package; the guard/test was preserved. Bash syntax, Python
compilation, Git whitespace and relative-link checks are recorded with delivery.

Two implementation issues were corrected before positive checks: builder CPU
flags were changed to the installed Podman's supported period/quota options, and
stable-launcher path resolution now follows its intentional symlink to the
snapshot. Package-manager cache artifacts were excluded from snapshots and
removed only from the newly created template directory. These fixes changed no
host privilege or existing data protections.

No logout, reboot, instance replacement or restore test ran. Source/dependency
caches are on project storage; images and runtime process state are disposable.
No managed app persistence, secrets, database or production capability is claimed.
The running provider code matches the merged implementation; immutable provider
snapshots remain independent of checkout branch changes. Live acceptance and closeout patch CI/merge are now complete for the initial slice. The stable snapshot was refreshed after merge
as recorded below; that snapshot refresh did not restart app containers. The
subsequent explicitly requested stop/start check is recorded in the closeout.

## Two-app desktop confirmation — October 10, 2026 (UTC)

At implementation/evidence revision `797bb56262118553cadac7e75783a57e3dede785`,
Daniel reported “yes, they both work” after being asked to verify both private
pages and their independent counters:

- [Hello World](https://forge-dev-01-4.tail8c3304.ts.net/projects/hello-world/)
- [Hello Second](https://forge-dev-01-4.tail8c3304.ts.net/projects/hello-second/)

This is attributed owner browser evidence, not an agent browser test. Agent
read-only checks after the report observed:

- `tailscale serve status --json`: the only handler is `/projects/`, proxying to
  `http://127.0.0.1:18079/projects/`; the old `/projects/hello-world/` override is
  absent and there is no active Funnel configuration.
- Stable `gptclawctl status --project-root` for each app: ready health, distinct
  ports 18080/18081, and configured private URLs.
- Direct private HTTPS GETs for each page and `api/health`: all four returned 200.

The one-time shared-prefix setup is complete. Subsequent per-app routes are
managed by the unprivileged CLI/router; no per-app Serve command is required.
No daemon configuration was changed by the agent. Both apps remain running.

At that checkpoint, desktop source-update and managed first-app cleanup remained
pending. Both subsequently passed in the closeout below. Initial implementation and closeout patch
review/CI/merge are complete; this initial slice is Delivered.

Initial private-app CI failed before executing the generated app: Docker looks
for Dockerfile by default, while the toolchain uses Containerfile. The workflow
now supplies the explicit file path. This does not change the toolchain pin or
local passing behavior; corrected CI outcome is recorded separately.

## Corrected CI — October 9, 2026 (America/New_York)

At exact implementation revision `0c9d75bc217df7e582d8218d11e6853017e4f798`:

- [Private application workflow #2](https://github.com/danielbardsley/gptclaw/actions/runs/38011996631): passed, including generated app frozen install, health tests, typecheck and build inside the pinned container.
- [Development-host quality #121](https://github.com/danielbardsley/gptclaw/actions/runs/38011996627): passed.
- [Federation quality #28](https://github.com/danielbardsley/gptclaw/actions/runs/38011996620): passed.

The final focused suite has 29 passing cases and the required offline repository
checker passed. CI proves source/quality checks; shared-prefix and two-app desktop
evidence is recorded separately above. No protected apply was dispatched.

## Final implementation review and merge — October 10, 2026 (UTC)

Daniel authorized merging outstanding work and updating project documentation.
At exact PR head `78508711c54e5c03cbbfed6e2edda54dee9fc2c4`, all three checks passed:

- [Private application workflow #4](https://github.com/danielbardsley/gptclaw/actions/runs/38061151048).
- [Development-host quality #124](https://github.com/danielbardsley/gptclaw/actions/runs/38061151046).
- [Federation quality #30](https://github.com/danielbardsley/gptclaw/actions/runs/38061151096).

No submitted reviews or unresolved inline review threads were present. GitHub
accepted the merge with the expected head SHA, producing `52b57caf1d86e81e1bbb41a77af35ed45e7df1f6`.
The checkout was fast-forwarded to that main revision; prior feature branches
were retained. Merge triggered quality workflows, not a protected infrastructure
apply. At that checkpoint the two owner/live checks were still pending; the subsequent
closeout below records their passing outcomes.

### Stable provider reconciliation

Byte comparison found the installed provider's `private_apps.py` predated the
merged start/stop `operation_result` tracking fix. Source command
`scripts/gptclawctl start --project-root /srv/forge/projects/hello-world` ran once:
ready, configured route, `changed: false`, 1.165 seconds. It refreshed the owned immutable provider
snapshot/stable launcher and the shared ingress service through the reviewed
installation path; the ready application container was not restarted. Old
snapshots and unrelated services were retained. Post-refresh byte comparisons passed for all five checked provider/ingress/toolchain
files; both status calls reported ready/configured and all four private page/health
GETs returned 200. The full offline repository checker, whitespace and relative-file
link checks also passed for the documentation/runtime-guidance reconciliation. This is runtime installation reconciliation within
SPEC-018, not a new operator grant or infrastructure deployment.

## Final live checks and port-reuse repair — October 10, 2026 (UTC)

Daniel requested “Do those two checks then so we can close it out.” The exact
port-reuse patch source is `5536c0f3df83ca88d529e01476e1679256f35a61`; the baseline
was main `8b6a6ee3f78fcd78117931bfc7e8206df25bf957`.

### Desktop source update

Only Hello Second's existing `app/page.tsx` heading was temporarily changed to
“Hello Second - live update verified”. The changed private HTTPS HTML was observed
in 0.136 seconds; this is host-observed response timing, not a measured browser
latency. Hello World's page stayed unchanged. Daniel answered “Yes, it updated
automatically” from his desktop. Original second-app bytes were restored only
after checking the file still matched this task's edit; both original pages
again returned 200. No unit edit, app restart or per-app Serve operation was
needed for the source update.

### First-app source-preserving stop/start

The first provider 1.0.0 stop revoked the mapping and removed the owned unit,
but returned a conflict at its final port probe. Status and scoped service/port
checks reconciled it as stopped, source intact and private route 404; the second
page stayed 200. No other process was killed or state overwritten to bypass it.
An isolated TCP test reproduced the probe treating a cleanly closed connection
in TIME_WAIT as occupied. Recovery start through the existing CLI succeeded in
27.966 seconds, including managed preparation/build/readiness.

Provider 1.0.1 probes TCP port reuse with SO_REUSEADDR, while still rejecting an
active listener. Three real-loopback regression cases cover free ports, active
listeners and closed-connection reuse. The closed-connection case failed before
the fix and all three passed after it. A no-op ready start installed the owned
patched provider snapshot; the app container was not restarted by installation.
The actual stop/start test then passed:

- Stop: `gptclawctl stop --project-root /srv/forge/projects/hello-world`,
  operation `8a0fa715a56d44aba776922efae5dfa6`, changed/stopped,
  source retained; 0.866 seconds. Status recorded terminal result passed.
- While stopped: first private page returned 404; second private page and health
  returned 200. Shared Serve prefix stayed configured; only the first app's
  registry mapping/service/activation was removed.
- Start: `gptclawctl start --project-root /srv/forge/projects/hello-world`,
  operation `795e6ce93597465bb2000c714ba9e2b3`, changed/ready,
  private route configured; 3.647 seconds. Status recorded terminal result passed.
- All 16 existing known source/guidance/manifest files matched their pre-test
  SHA-256 fingerprints after stop and start. The adopted prototype lacks a README;
  an initial fingerprint attempt stopped on that absent file before any mutation,
  then used the actual existing file set. Runtime/cache/authentication files were
  excluded. Both private page/health pairs returned 200 after start.

### Verification and delivery boundary

The focused lifecycle/proxy suite passed 32 cases; the full offline repository
checker passed. Tests use isolated loopback sockets, not existing host ports.
Private services remain bound to loopback, Funnel stays off, and both apps remain
running with their original source. No AWS infrastructure, root permission,
operator grant, host package, public route or data deletion changed.
Initial prototype creation/standalone build timings were not captured; the measured
managed recovery start, warm stop/start and private response-edit timings above
are the available speed evidence. There is no acceptance speed threshold.
This closes the two live checks. The patch/evidence merge and CI results below
establish Delivered for this initial slice; retain broader roadmap and host/skill
acceptance separately.

## Delivery closeout — October 10, 2026 (UTC)

[PR #43](https://github.com/danielbardsley/gptclaw/pull/43) merged the provider 1.0.1
repair and live evidence as `fdfaf3d0f911caed9f6efa59cf0d490053597ac9`. At its exact
head `f7ac0472387e4f872073f35347e1b2308dd93610`, all configured PR workflows passed:

- [Private application workflow #8](https://github.com/danielbardsley/gptclaw/actions/runs/38063026085).
- [Development-host quality #131](https://github.com/danielbardsley/gptclaw/actions/runs/38063025958).
- [Federation quality #35](https://github.com/danielbardsley/gptclaw/actions/runs/38063026036).

Daniel's instruction to complete the two checks for closeout, his automatic
browser-update confirmation, and the passing lifecycle evidence fulfill this
slice's final acceptance. All AC-001–007 pass at their stated local/live/owner
levels. SPEC-018 is Delivered; catalogue delivery is limited to its implemented
single-web/Next.js/CLI/private-routing slices. No broader runtime, templates,
data/secrets, production or fresh-client skill acceptance is inferred.
Both synthetic apps remain running on their original private URLs. The installed
1.0.1 provider snapshot matches the merged lifecycle code and remains independent
of checkout branch changes. No host logout/reboot/replacement test was added.
