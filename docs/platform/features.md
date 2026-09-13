# GptClaw Platform Feature Catalogue

- **Status:** Directional backlog; not a specification
- **Last updated:** 2026-09-13
- **Architecture:** [GptClaw platform architecture](./architecture.md)

## 1. How to use this catalogue

This catalogue records capabilities that may become part of GptClaw. Entries
are intentionally smaller than full specifications and do not contain binding
acceptance criteria or implementation authorization.

When the owner selects a feature or coherent feature slice:

1. Assign the next initiative number.
2. Create `docs/NNN-kebab-case-name/`.
3. Write `spec.md`, then `technical-design.md`, then `tasks.md`.
4. Review consistency with the platform architecture and prior accepted work.
5. Implement only after the owner approves the specification.
6. Add `acceptance.md` when the feature is verified.
7. Whenever a feature's PR has merged and the feature is complete, update this
   catalogue as part of completion: mark it Delivered, link its specification,
   merged PR, and acceptance evidence, and update the catalogue date. Do this
   without waiting for a separate reminder. If implementation is merged but
   acceptance is still pending, record the actual status and remaining checks;
   merging a PR alone does not establish completion.

Feature IDs remain stable even if names, grouping, or delivery order changes.

### Status vocabulary

| Status | Meaning |
|---|---|
| Delivered | Implemented and accepted by a numbered specification. |
| Deployed | Installed in the target environment; final acceptance is still pending. |
| Candidate | Intended direction but not yet specified. |
| Draft | Selected for a numbered specification under review; not approved for implementation. |
| Planned | Specification approved; design/tasks under review or awaiting implementation authorization. |
| Optional | Useful capability that should be implemented only when demanded. |
| Deferred | Deliberately postponed until its dependencies or use case exist. |

Priority indicates suggested sequencing, not authorization.

## 2. Delivered foundation

| ID | Feature | Status | Evidence |
|---|---|---|---|
| FND-001 | Pipeline-managed EC2 development host | Delivered | SPEC-001 |
| FND-002 | Encrypted persistent project volume | Delivered | SPEC-001 |
| FND-003 | Tailscale-only SSH with SSM recovery | Delivered | SPEC-001 |
| FND-004 | Remote ChatGPT/Codex project connection | Delivered | SPEC-001 |
| FND-005 | Repository-specific host Git credential | Delivered | SPEC-001 |
| FND-006 | HCP Terraform AWS workload identity | Delivered | SPEC-001 |

## 3. Resilience and host safety

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| RES-001 | Automated EBS snapshots | 1 | Planned | Terraform creates a tagged lifecycle policy for the project volume with retention. Silent DLM failures are accepted; no monitoring or notifications. Implementation in progress: [SPEC-002](../002-automated-ebs-snapshots/spec.md). |
| RES-002 | Restore drill | 1 | Candidate | Periodically prove that a recent recovery point can create an inspectable replacement volume without risking the live volume. |
| RES-003 | Backup freshness indicator | 2 | Candidate | Dashboard shows last successful recovery point, age, retention class, and restore-test result. |
| RES-004 | Host replacement rehearsal | 3 | Candidate | Exercise compute replacement, Tailscale re-enrollment, Git credential recreation, and Codex reauthentication. |
| RES-005 | Host configuration drift detection | 3 | Candidate | Compare declared bootstrap/tool profile with observed packages, units, mounts, and security settings. |
| RES-006 | Disk capacity guardrails | 2 | Candidate | Warn, prune safe caches, and stop risky builds before the persistent volume fills. |
| RES-007 | Platform export | 4 | Optional | Export non-secret manifests, project inventory, and recovery metadata for off-host safekeeping. |

## 4. Agent configuration and consistent delivery

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| AGT-001 | Reviewed host `AGENTS.md` | 2 | Deployed | Policy and installer merged in [PR #6](https://github.com/danielbardsley/gptclaw/pull/6); approved policy installed and verified on the existing host on 2026-09-12. Automatic first-boot integration merged in [PR #7](https://github.com/danielbardsley/gptclaw/pull/7), but has not been applied to a new instance. Fresh-task loading, live rollback verification, and new-host acceptance remain pending. [SPEC-003](../003-reviewed-host-agents/spec.md) · [Acceptance evidence](../003-reviewed-host-agents/acceptance.md). |
| AGT-002 | Repository `AGENTS.md` template | 2 | Planned | [SPEC-004](../004-repository-agents-template/spec.md) implemented and merged in [PR #9](https://github.com/danielbardsley/gptclaw/pull/9) on 2026-09-12. Template, GptClaw guidance, offline checks, and rollback rehearsal are complete; CI and fresh-task remote acceptance remain pending. [Acceptance evidence](../004-repository-agents-template/acceptance.md). |
| AGT-003 | Nested guidance pattern | 3 | Planned | [SPEC-005](../005-nested-guidance-pattern/spec.md) approved and implementation authorized on 2026-09-13. Template, five inert examples, infrastructure adoption, and offline checks merged in [PR #11](https://github.com/danielbardsley/gptclaw/pull/11) on 2026-09-13. PR CI run #56 passed; fresh-task remote acceptance remains pending. [Acceptance evidence](../005-nested-guidance-pattern/acceptance.md). |
| AGT-004 | Specification skill | 2 | Candidate | Reusable workflow creates consistent spec, technical design, task, and acceptance documents. |
| AGT-005 | Project bootstrap skill | 2 | Candidate | Agent can safely create a project from an approved template and verify the result. |
| AGT-006 | Runtime-operation skill | 3 | Candidate | Agent uses typed project lifecycle commands rather than improvised process management. |
| AGT-007 | Release and production-promotion skill | 5 | Candidate | Releases follow consistent versioning, evidence, approval, rollback, and deployment steps. |
| AGT-008 | Session handover generator | 3 | Candidate | Produce a concise, non-secret project state summary for a future remote session. |
| AGT-009 | Architecture decision records | 3 | Candidate | Preserve cross-cutting decisions and supersession history outside individual specs. |
| AGT-010 | Context validation | 3 | Candidate | Detect stale specs, missing tasks, conflicting instructions, and undocumented deviations before implementation. |

## 5. Project creation and repository lifecycle

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| PRJ-001 | Versioned project manifest | 2 | Candidate | `.gptclaw/project.yaml` becomes the validated contract for runtime, health, routing, data, and quality commands. |
| PRJ-002 | `gptclawctl` CLI | 2 | Candidate | Provide idempotent `new`, `validate`, `start`, `stop`, `status`, `logs`, `test`, `expose`, and `archive` operations. |
| PRJ-003 | Template catalogue | 2 | Candidate | Versioned templates cover web, API, Python, Expo, static site, CLI, and multi-package products. |
| PRJ-004 | New GitHub repository automation | 3 | Candidate | Create repositories, protections, environments, secrets references, and initial pull requests with narrow credentials. |
| PRJ-005 | Repository credential broker | 3 | Candidate | Prefer a scoped GitHub App; otherwise issue and rotate one deploy key per repository. |
| PRJ-006 | Branch and worktree policy | 2 | Candidate | Parallel agents use isolated worktrees, predictable branch names, per-project locks, and clean handoff. |
| PRJ-007 | Project discovery | 3 | Candidate | Dashboard safely discovers valid manifests without executing repository content. |
| PRJ-008 | Project archive and restore | 4 | Candidate | Stop services, retain or export data by policy, archive metadata, and make later restoration predictable. |
| PRJ-009 | Example and seed projects | 3 | Candidate | Golden-path sample applications continuously prove every supported template and routing mode. |
| PRJ-010 | Repository ownership transfer | 5 | Optional | Re-key and move a project without leaking credentials or breaking history. |

## 6. Controlled software installation

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| SYS-001 | Rootless container toolchain | 2 | Candidate | Install and configure Podman, subordinate IDs, networking, storage, Quadlet, and user-service persistence. |
| SYS-002 | Pinned language toolchains | 2 | Candidate | Projects declare and automatically obtain supported Node, pnpm, Python, uv, and other approved versions. |
| SYS-003 | Project dependency policy | 2 | Candidate | Agents may install dependencies inside their project boundary and must record lockfile changes. |
| SYS-004 | Host tool profile | 2 | Candidate | Common host packages are declared in GptClaw code and deployed through the infrastructure pipeline. |
| SYS-005 | Privileged capability broker | 4 | Candidate | Exceptional system changes use a narrow allowlist, owner approval, audit log, and mandatory reconciliation. |
| SYS-006 | Dependency cache management | 3 | Candidate | Share safe package/build caches with quotas while preventing cross-project credential or artifact leakage. |
| SYS-007 | Software bill of materials | 4 | Candidate | Produce SBOMs for images and releases and retain them with build provenance. |

## 7. Parallel project runtime

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| RUN-001 | Rootless project containers | 3 | Candidate | Each project runs in its own non-root network, containers, volumes, and namespace. |
| RUN-002 | User systemd/Quadlet lifecycle | 3 | Candidate | Services survive disconnects, restart predictably, and expose status through standard tooling. |
| RUN-003 | Port registry | 3 | Candidate | Allocate collision-free loopback ports and preserve stable assignments across restarts. |
| RUN-004 | Resource limits | 3 | Candidate | Apply per-project CPU, memory, process, storage, and log limits with sensible defaults. |
| RUN-005 | Health contract | 3 | Candidate | Every long-running service has startup, readiness, and ongoing health checks. |
| RUN-006 | Multi-service projects | 3 | Candidate | Run web, API, database, cache, and worker components as one declared project group. |
| RUN-007 | Background jobs and schedulers | 4 | Candidate | Declare recurring or asynchronous workers without unmanaged terminal processes. |
| RUN-008 | Pause, resume, and idle shutdown | 4 | Candidate | Reclaim memory and CPU from inactive projects while preserving data and URLs. |
| RUN-009 | Build queue | 4 | Candidate | Bound concurrent CPU-heavy builds and surface queue state to agents and the dashboard. |
| RUN-010 | Runtime garbage collection | 4 | Candidate | Safely remove orphaned containers, images, caches, ports, and abandoned worktrees. |
| RUN-011 | Development database lifecycle | 3 | Candidate | Create isolated PostgreSQL databases, users, backups, migrations, and safe reset operations per project. |
| RUN-012 | Synthetic seed-data lifecycle | 4 | Candidate | Load and reset approved non-sensitive datasets consistently. |

## 8. Framework templates

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| TPL-001 | Next.js full-stack template | 3 | Candidate | TypeScript, App Router, Tailwind, health route, tests, container, base-path support, and CI. |
| TPL-002 | TypeScript API template | 4 | Candidate | Fastify service with schema validation, OpenAPI, health checks, tests, container, and migrations. |
| TPL-003 | Python API/AI template | 4 | Candidate | FastAPI, Pydantic, uv, Ruff, pytest, health checks, container, and typed configuration. |
| TPL-004 | Expo universal application template | 4 | Candidate | Expo Router, TypeScript, web export, device development, EAS profiles, tests, and environment separation. |
| TPL-005 | Static site template | 4 | Candidate | Minimal static output with accessibility, link, performance, and private-preview checks. |
| TPL-006 | CLI/automation template | 5 | Optional | Typed CLI, structured output, tests, packaging, and scheduled execution hooks. |
| TPL-007 | Multi-package product template | 5 | Optional | pnpm workspace with shared contracts and UI packages when one release lifecycle justifies a monorepo. |
| TPL-008 | Shared UI foundation | 4 | Candidate | Accessible components, tokens, themes, forms, error states, and responsive layout conventions. |
| TPL-009 | Authentication starter | 5 | Candidate | Pluggable authentication with secure session defaults and local test identities. |
| TPL-010 | AI-enabled application starter | 5 | Candidate | Server-side OpenAI integration, structured outputs, eval hooks, tracing, limits, and secret-safe configuration. |

## 9. Private networking and previews

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| NET-101 | Private loopback ingress | 3 | Candidate | Route stable project paths to healthy loopback services without opening EC2 inbound ports. |
| NET-102 | Tailscale Serve manager | 3 | Candidate | Publish the dashboard and private project routes to the tailnet with declarative, recoverable configuration. |
| NET-103 | Base-path compatibility | 3 | Candidate | Templates work beneath `/projects/<slug>/`, including assets, API calls, redirects, and WebSockets. |
| NET-104 | Dedicated private service ports | 4 | Candidate | Support applications that cannot operate under a path while keeping access tailnet-only. |
| NET-105 | Funnel exposure manager | 4 | Candidate | Owner-confirmed, time-limited, health-gated public exposure with automatic shutdown and audit. |
| NET-106 | Public exposure authentication | 5 | Candidate | Add application-level identity or share tokens when a Funnel preview is not intentionally anonymous. |
| NET-107 | Exposure policy scanner | 4 | Candidate | Block dashboard, admin, database, log, metric, secret, and non-HTTP endpoints from Funnel. |
| NET-108 | Preview URL registry | 3 | Candidate | Dashboard and task results return stable private URLs and active public URLs with expiry. |
| NET-109 | Tailnet access groups | 4 | Candidate | Express developer/viewer access separately from host administration and Funnel capability. |

## 10. Platform dashboard

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| DSH-001 | Project inventory | 3 | Candidate | List all managed projects with type, repository, owner, runtime, and documentation state. |
| DSH-002 | Live service status | 3 | Candidate | Show health, uptime, restarts, components, and last status change. |
| DSH-003 | Private/open links | 3 | Candidate | Open project UI, API docs, repository, logs, and active preview URLs. |
| DSH-004 | Git status | 3 | Candidate | Show branch, dirty state, ahead/behind, last commit, pull request, and active worktrees. |
| DSH-005 | Resource telemetry | 3 | Candidate | Display host and per-project CPU, memory, disk, network, and process consumption. |
| DSH-006 | Log viewer | 4 | Candidate | Stream and search redacted recent logs with project/component filters. |
| DSH-007 | Build and test status | 4 | Candidate | Show last local checks, GitHub checks, image build, and deployment result. |
| DSH-008 | Backup state | 2 | Candidate | Show snapshot freshness, retention, restore-test status, and recovery warnings. |
| DSH-009 | Constrained controls | 4 | Candidate | Start, stop, restart, rebuild, pause, resume, and open a remote task through typed operations. |
| DSH-010 | Funnel controls | 4 | Candidate | Request, confirm, time-box, extend, and revoke public exposure with a persistent warning. |
| DSH-011 | Activity and audit timeline | 4 | Candidate | Correlate agent tasks, lifecycle changes, deployments, exposure, alerts, and operator approvals. |
| DSH-012 | Mobile-friendly dashboard | 4 | Candidate | Make status, approvals, logs, and safe controls usable from a phone over Tailscale. |
| DSH-013 | Search and filtering | 4 | Candidate | Find projects by status, stack, owner, tag, repository, health, or exposure. |
| DSH-014 | Read-only degraded mode | 3 | Candidate | Preserve useful diagnosis when the lifecycle manager or a project is unhealthy. |

## 11. Mobile and Expo workflow

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| MOB-001 | Expo project creation | 4 | Candidate | Generate the approved Expo Router template with consistent native/web structure. |
| MOB-002 | Physical-device development | 4 | Candidate | Connect a device to Metro over the tailnet or an explicitly approved Expo transport. |
| MOB-003 | Expo Go workflow | 4 | Candidate | Provide the quickest compatible feedback loop for applications without unsupported native modules. |
| MOB-004 | Development builds | 4 | Candidate | Create signed EAS development builds when native modules or production parity require them. |
| MOB-005 | Environment profiles | 4 | Candidate | Separate local, development, preview, and production configuration and credentials. |
| MOB-006 | EAS Build and Submit | 5 | Candidate | Produce reviewable iOS/Android artifacts and owner-approved store submissions. |
| MOB-007 | EAS Update policy | 5 | Candidate | Define channels, runtime compatibility, rollout, rollback, and owner approval for updates. |
| MOB-008 | Universal web preview | 4 | Candidate | Export or serve the Expo web target through the same private preview model when appropriate. |
| MOB-009 | Device and release dashboard state | 5 | Candidate | Show active Metro sessions, build jobs, QR links, channels, and release versions. |

## 12. Secrets, data, and security

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| SEC-001 | Project secret registry | 3 | Candidate | Store secrets outside Git and materialize only the values authorized for one project/process. |
| SEC-002 | Secret rotation workflow | 4 | Candidate | Rotate, restart dependants, verify health, and audit without displaying values. |
| SEC-003 | Runtime permission profiles | 3 | Candidate | Express allowed filesystem, network, process, and tool capabilities per project. |
| SEC-004 | Dependency and image scanning | 4 | Candidate | Scan lockfiles, containers, SBOMs, and infrastructure in CI with actionable severity policy. |
| SEC-005 | Repository secret scanning | 2 | Candidate | Expand current pattern checks with pre-commit and CI controls across every generated project. |
| SEC-006 | Audit log | 3 | Candidate | Record actor, request, approval, operation, target, result, and correlation ID without secrets. |
| SEC-007 | Destructive-action controls | 3 | Candidate | Require typed targets, backups where applicable, previews, confirmations, and recoverable defaults. |
| SEC-008 | Production credential isolation | 5 | Candidate | Make production roles usable only by protected GitHub/HCP workflows, never remote project processes. |
| SEC-009 | Tailnet policy as code | 4 | Candidate | Review SSH, Serve, Funnel, device, and project access policy through a controlled source workflow. |
| SEC-010 | Security review workflow | 5 | Candidate | Add threat modeling and targeted review before public exposure or production launch. |

## 13. Quality and developer experience

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| QLT-001 | Standard quality commands | 2 | Candidate | Every project exposes `format`, `lint`, `typecheck`, `test`, `build`, and `verify` through its manifest. |
| QLT-002 | Pull-request workflow template | 3 | Candidate | Generated repositories get pinned actions, minimal permissions, caches, tests, scans, and artifacts. |
| QLT-003 | Dependency automation | 3 | Candidate | Dependabot or an approved equivalent opens bounded, tested update pull requests. |
| QLT-004 | Preview smoke tests | 3 | Candidate | Verify the private URL, assets, health endpoint, and important journeys after each service update. |
| QLT-005 | Accessibility baseline | 4 | Candidate | Generated web/mobile projects include keyboard, semantics, contrast, and automated accessibility checks. |
| QLT-006 | Performance budgets | 4 | Candidate | Detect unacceptable bundle, response-time, memory, and startup regressions. |
| QLT-007 | Database migration gates | 4 | Candidate | Test forward migration, backup prerequisites, destructive detection, and rollback/restore strategy. |
| QLT-008 | Contract and API documentation | 4 | Candidate | Generate and validate OpenAPI or equivalent contracts where services cross boundaries. |
| QLT-009 | Golden-template tests | 3 | Candidate | Continuously generate, build, run, route, and destroy sample projects from every supported template. |
| QLT-010 | Release notes and changelog | 5 | Optional | Generate reviewed human-facing release summaries from accepted changes. |

## 14. Observability and operations

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| OBS-001 | Structured logging contract | 3 | Candidate | Consistent time, severity, project, component, request, and correlation fields with redaction. |
| OBS-002 | Host and project metrics | 3 | Candidate | Collect enough CPU, memory, disk, network, process, and health data for diagnosis and capacity planning. |
| OBS-003 | Alert routing | 4 | Candidate | Notify on failed health, low disk, stale backup, repeated restarts, and failed deployment. |
| OBS-004 | Trace correlation | 5 | Optional | Add OpenTelemetry-compatible traces where distributed behavior justifies them. |
| OBS-005 | Retention and pruning | 3 | Candidate | Bound journald, CloudWatch, build, image, cache, artifact, and audit growth. |
| OBS-006 | Service-level history | 4 | Candidate | Preserve recent availability and deployment markers for each project. |
| OPS-001 | Cost dashboard | 4 | Candidate | Show current and forecast development/production cost with budget thresholds. |
| OPS-002 | Host schedule | 5 | Optional | Stop the EC2 host during defined idle windows only after reliable remote wake-up exists. |
| OPS-003 | Capacity recommendations | 5 | Optional | Recommend host resizing or project limits from observed demand. |
| OPS-004 | Platform upgrade workflow | 4 | Candidate | Upgrade Ubuntu, Codex, Tailscale, Podman, templates, and schema through reviewed staged changes. |

## 15. Slack and remote collaboration

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| COL-001 | Slack notification adapter | 5 | Candidate | Post task completion, approval requests, failures, health alerts, and exposure expiry notices. |
| COL-002 | Slack command adapter | 5 | Candidate | Authenticated users submit typed project operations without receiving shell access. |
| COL-003 | Slack identity mapping | 5 | Candidate | Map Slack identity to an approved GptClaw role and project scope. |
| COL-004 | Approval workflow | 5 | Candidate | High-impact Slack requests require an explicit owner approval tied to the exact operation. |
| COL-005 | Conversation-to-task bridge | 5 | Candidate | Turn an approved Slack request into a traceable Codex task with repository/project context. |
| COL-006 | Progress summaries | 5 | Candidate | Provide concise, rate-limited updates and links back to the authoritative task and diff. |
| COL-007 | Slack security boundary | 5 | Candidate | Prevent arbitrary prompts, secrets, public channels, replay, and spoofed interactive actions from becoming host commands. |
| COL-008 | Official integration evaluation | 5 | Candidate | Re-evaluate the current Codex Slack integration before building a custom gateway. |

## 16. Production promotion

| ID | Feature | Priority | Status | Intended outcome |
|---|---|---:|---|---|
| PRD-001 | Production architecture template | 6 | Candidate | Choose managed AWS targets, data, networking, scaling, observability, and recovery from product requirements. |
| PRD-002 | Per-project HCP workspace | 6 | Candidate | Give each production environment isolated state, variables, OIDC roles, approvals, and drift visibility. |
| PRD-003 | Artifact build and registry | 5 | Candidate | Build immutable images/assets once, scan and attest them, then promote the same artifact. |
| PRD-004 | Environment promotion | 6 | Candidate | Move accepted revisions through preview/staging/production with explicit approval and provenance. |
| PRD-005 | Domain and TLS management | 6 | Candidate | Manage DNS, certificates, redirects, and ownership verification through Terraform. |
| PRD-006 | Production secrets | 6 | Candidate | Provision and rotate production secrets without exposing them to development or GitHub logs. |
| PRD-007 | Database deployment | 6 | Candidate | Provision managed PostgreSQL, networking, migrations, backups, monitoring, and recovery controls. |
| PRD-008 | Rollback and roll-forward | 6 | Candidate | Restore a prior artifact or complete a corrective release without ambiguous state. |
| PRD-009 | Production smoke tests | 6 | Candidate | Verify health, critical journeys, observability, and rollback readiness after deployment. |
| PRD-010 | Production incident mode | 6 | Deferred | Provide time-bounded, audited diagnosis without granting the development agent standing production administration. |

## 17. Suggested specification sequence

This is the recommended order for selecting future work:

1. **Protect the persistent volume:** RES-001, RES-002, and DSH-008's data
   source. This closes the only material handover warning from SPEC-001.
2. **Create the consistent agent/project contract:** AGT-001, AGT-002,
   AGT-004, PRJ-001, QLT-001.
3. **Install the safe runtime foundation:** SYS-001, SYS-002, SYS-003,
   SYS-004, RUN-001 through RUN-005.
4. **Automate project creation:** PRJ-002 through PRJ-006 and the first
   golden-path template, normally TPL-001.
5. **Run and route several private projects:** RUN-006, RUN-008, RUN-010,
   NET-101 through NET-104, and NET-108.
6. **Build the read-only dashboard:** DSH-001 through DSH-005, DSH-008, and
   DSH-014.
7. **Add data, logs, secrets, and safe controls:** RUN-011, SEC-001 through
   SEC-007, OBS-001 through OBS-003, DSH-006, DSH-009, and DSH-011.
8. **Add Expo/mobile development:** TPL-004 and MOB-001 through MOB-005.
9. **Add temporary public sharing:** NET-105 through NET-107 and DSH-010.
10. **Add Slack:** COL-001 through COL-008 after the typed control API and audit
    boundary are proven.
11. **Add production promotion:** PRD-001 through PRD-009 per product, never as
    a blanket grant to the development host.

The owner may reorder features, but each new specification should state which
catalogue IDs it covers and why its dependencies are ready.

## 18. Selection checklist

Before asking for a new specification, decide:

- Which feature IDs are in scope.
- What user-visible outcome matters first.
- Which existing project or platform component owns the capability.
- Whether it changes the host, tailnet, GitHub, HCP Terraform, AWS, Expo, or
  production trust boundary.
- Whether it stores data or secrets.
- Whether it creates a public URL.
- Whether it needs a rollback, backup, migration, or destructive-action plan.
- What evidence will prove completion.

The resulting specification may narrow or reject a catalogue idea. The
architecture and catalogue should then be updated so future sessions inherit
the accepted decision.
