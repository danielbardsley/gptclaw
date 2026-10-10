# SPEC-018 acceptance evidence

- **Status:** Implemented on feature branch; live acceptance in progress
- **Owner:** Daniel
- **Date:** 2026-10-09 (America/New_York)
- **Specification:** [SPEC-018](spec.md)
- **Design:** [TDD-018](technical-design.md)
- **Tasks:** [Tasks](tasks.md)
- **Operation:** [Private app runbook](../../runbooks/manage-private-apps.md)
- **Review:** [PR #40](https://github.com/danielbardsley/gptclaw/pull/40)

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
| AC-004 | pending | Daniel confirmed the first private HTTPS page loads and its counter works. Shared loopback ingress forwards page/health plus 18 JS/CSS assets, and the actual Next HMR WebSocket returned 101. The one-time shared Serve-prefix transition and second desktop URL confirmation remain pending. Funnel is off; unrelated routes were not changed by the agent. |
| AC-005 | pending | Editing second-app source produced changed HTML through ingress in 4.995 seconds without unit changes; first content was unaffected; edit restored. Source survived stop/start. Full desktop browser-update and two-app confirmation remain pending. |
| AC-006 | pending | Offline/repository checks and scoped local cleanup passed; runbook and receipt contract written. Generated-app CI and both infrastructure quality workflows passed at `0c9d75b`; review/merge and final owner acceptance remain pending. |
| AC-007 | pending (desktop proof passed) | Actual app/health returned 200 over private HTTPS at `/projects/hello-world/`; Daniel confirmed page load and counter increment. Agent's daemon write was denied; Daniel applied the exact prototype route from his SSM session. Shared-prefix transition removes that prototype path while preserving source; its completion remains pending. |

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
Current services are live development demonstrations from a feature branch,
not accepted merged delivery. Do not mark complete until remaining criteria pass.

## Remaining operator/owner step

The existing prototype URL remains available. The shared loopback router is
verified at 18079; operator action requested but not yet observed:

```sh
sudo tailscale serve --bg --https=443 --set-path=/projects/ http://127.0.0.1:18079/projects/
sudo tailscale serve --https=443 --set-path=/projects/hello-world/ off
```

After observing the exact prefix and absence of the prototype override, verify
both private URLs, browser updates and owner acceptance. Keep unrelated Serve
configuration and active services intact. The agent must not claim that a pending
operator question or elapsed time established this change.

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
checker passed. CI proves source/quality checks, not the pending shared-prefix
operator change or two-app desktop acceptance. No protected apply was dispatched.
