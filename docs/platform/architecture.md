# GptClaw Platform Architecture

- **Status:** Current architecture and desired future state
- **Last updated:** 2026-10-15
- **Delivery evidence:** [README current state](../../README.md#current-state) and [initiative records](../README.md)
- **Feature catalogue:** [Platform features](./features.md)

## 1. Purpose

This document describes the intended GptClaw platform at a level that is stable
enough to guide future specifications. It is not itself a specification and it
does not authorize implementation. Each material capability must be selected
from the feature catalogue and turned into its own specification, technical
design, task list, and acceptance record before it is implemented.

GptClaw is a private, agent-operated development environment. ChatGPT connects
to an always-on AWS development host over SSH and can create, build, run, test,
and evolve multiple projects. Projects use consistent repository guidance,
templates, runtime isolation, health reporting, and deployment conventions.
Development services remain private to the Tailscale network unless the owner
explicitly requests a temporary public share through Tailscale Funnel.

## 2. Outcomes

The target platform should let the owner:

1. Describe a product or feature in plain language.
2. Turn that idea into reviewed specification, design, and task documents.
3. Create a repository from an approved template with consistent agent
   instructions and engineering defaults.
4. Ask Codex to implement and test changes on the remote development host.
5. Run several isolated projects concurrently without port or dependency
   conflicts.
6. Open every development application privately over Tailscale.
7. Temporarily expose one approved application through Funnel when requested.
8. See project, service, Git, health, resource, URL, and exposure status in one
   dashboard.
9. Build mobile applications with Expo and test them on physical devices.
10. Promote reviewed applications to production through project-specific
    GitHub Actions and Terraform, without turning the development host into a
    production server.
11. Add Slack as a later control surface without weakening authentication,
    approval, or audit boundaries.

## 3. Architectural principles

### 3.1 Non-negotiable controls

- Every AWS infrastructure change follows committed code -> GitHub Actions ->
  HCP Terraform -> AWS.
- Direct AWS CLI and console access may be used for read-only diagnosis, but
  never to create, update, or delete AWS infrastructure.
- The EC2 security group has no inbound rules. Administrative access uses
  Tailscale SSH transport or AWS Systems Manager.
- Development services bind to loopback or an isolated container network, not
  the public interface.
- Tailscale Serve is the default publishing mechanism and remains tailnet-only.
- Funnel remains disabled. A future exposure manager must make publication
  explicit, visibly public, auditable and automatically expiring.
- The `forge` account remains unprivileged. Agents do not receive unrestricted
  `sudo`, production AWS credentials, or access to unrelated repositories.
- Secrets never enter source control, prompts, dashboard payloads, build logs,
  Terraform state when a write-only alternative exists, or generated project
  documentation.
- Development and production are separate environments, identities, state,
  data, and deployment pipelines.

### 3.2 Operating preferences

- Prefer a small number of well-supported defaults over a broad menu of stacks.
- Prefer declarative manifests and idempotent commands over undocumented host
  state.
- Prefer rootless containers for project services and user-scoped package
  managers for development tools.
- Prefer a dedicated repository per independently deployable product. Use a
  monorepo only when multiple packages share a release lifecycle.
- Prefer reversible actions, visible diffs, health checks, resource limits,
  and automatic cleanup.
- Keep the dashboard useful when control actions are unavailable; observation
  must not depend on broad mutation permissions.

## 4. Current implemented architecture

The foundation remains the private Ubuntu EC2 host, protected encrypted EBS volume
at `/srv/forge`, unprivileged `forge` identity, Tailscale-only OpenSSH, independent
SSM recovery and GitHub Actions/HCP Terraform infrastructure path. Daily DLM
snapshots are deployed; restore drills and freshness monitoring are separate work.
Host/tool-profile and replacement-enrollment acceptance gaps remain recorded in
the [current-state summary](../../README.md#current-state).

The initial single-web workflow has grown into installed provider 1.14.0,
validating manifests 1–9, with pinned Next.js, FastAPI, Fastify and Expo templates,
dependency/toolchain policies, repository automation, scoped credential bindings,
multi-service groups and managed development PostgreSQL. Android-first project
creation, private Metro and compatible Expo Go foundations are delivered. The
Python/PostgreSQL native backend integration has an approved working preview;
its detailed device/recovery/accessibility and final integration acceptance remain
separate gates in [SPEC-036](../036-mobile-python-backend/acceptance.md). The dashboard inventory/status/link slices are
merged and accepted. Its visual refinement is also merged and privately deployed;
the actual-browser zoom acceptance check remains unrecorded. Historical initiative
records can retain earlier pending gates; do not infer acceptance from code alone.

## 5. Current logical architecture and storage

```text
Project owner -> remote Codex/ChatGPT -> SSH as forge
                                    |
                          AGENTS.md + skills + selected spec
                                    |
                    reviewed gptclawctl provider and Git/PR workflow
                                    |
/srv/forge/projects/<slug>           | source + .gptclaw/project.yaml
/srv/forge/projects/.gptclaw-runtime/v1/
  immutable providers, owned receipts, allocated ports, credentials, DB data
                                    |
                rootless Podman + user systemd/Quadlet
                   web | API | private PostgreSQL
                                    |
                  loopback ingress :18079 -> Tailscale Serve /projects/

read-only Python collector as forge -> Unix socket -> rootless Next.js dashboard
/srv/forge/platform/releases/<digest>                 loopback :18200
/srv/forge/platform/run/collector.sock                Serve /dashboard/

GitHub Actions -> HCP Terraform -> AWS infrastructure
Future product production environments remain separate from this host.
```

Project containers are individually managed services, not a requirement to use
Podman pods. Group startup/readiness orders database, API and web as applicable;
database ports are not published on the host. Application loopback allocations
use the reviewed 18080–18179 range. Runtime state and database data stay outside
Git checkouts. Stopping a service retains its source and persistent data.

The dashboard frontend mounts only immutable application assets and the collector
socket directory. It receives no project source, credential store or Podman socket.
The collector uses bounded manifest discovery and owned provider observations;
it does not execute repository code to discover inventory. These controls reduce
accidental exposure within a shared forge identity; they do not isolate malicious
code running under that same identity.

Future additions include explicit public-preview management, richer observability,
signed mobile build/release workflows, constrained control actions and optional
Slack integration.
They must extend reviewed interfaces rather than turn the dashboard into a shell.

## 6. Control and data planes

### 6.1 Control plane

The control plane describes and coordinates work but does not directly serve
application traffic. It comprises:

- ChatGPT remote projects and Codex tasks.
- Repository specifications, designs, tasks, decisions, and acceptance records.
- Layered `AGENTS.md` instructions and repository skills.
- The installed, versioned `gptclawctl` provider and manifest schemas.
- The dashboard and its local status collector.
- GitHub pull requests, checks, Actions, environments, and approvals.
- HCP Terraform workspaces and phase-specific AWS identities.
- A later Slack adapter that submits constrained operations to the same control
  interface rather than exposing a shell.

### 6.2 Development data plane

The development data plane runs project code on the EC2 host:

- One rootless runtime boundary per project.
- Supported web/API services and development PostgreSQL containers; cache and
  worker profiles remain future extensions.
- Loopback-only host port publication.
- Health checks, user-journal logs, and resource limits.
- Tailscale Serve routes for authenticated tailnet access.
- Temporary public exposure remains a future, separately authorized capability.

### 6.3 Production data plane

Production does not run on the development host. Each product receives a
separate production design. Expected AWS targets include:

- Static web: S3 and CloudFront, or another explicitly selected managed host.
- Web/API containers: ECR plus ECS/Fargate behind an ALB.
- Relational data: RDS or Aurora PostgreSQL.
- Queues and events: SQS, EventBridge, and purpose-specific managed services.
- Mobile: EAS Build/Submit/Update and the required application backends.

These are defaults for later evaluation, not pre-approved implementation
choices. Every production environment uses its own HCP workspace, IAM roles,
secrets, domain configuration, budgets, and approval gates.

## 7. Project contract

Managed projects declare `.gptclaw/project.yaml`. The bundled schemas and provider,
not illustrative architecture YAML, define the executable contract:

| Schema | Supported shape | Contract source |
|---|---|---|
| 1 | Single private web service | [Schema](../../schemas/project/v1.schema.json) · [Initial reference](../project-manifest.md) |
| 2 | Standalone Python FastAPI service | [Schema](../../schemas/project/v2.schema.json) · [API runbook](../../runbooks/manage-python-apis.md) |
| 3 | One project containing web and API services | [Schema](../../schemas/project/v3.schema.json) · [Group runbook](../../runbooks/manage-multi-service-projects.md) |
| 4 | Web/API group with managed development PostgreSQL | [Schema](../../schemas/project/v4.schema.json) · [Database runbook](../../runbooks/manage-development-databases.md) |
| 5 | Expo application source and quality jobs; no service runtime | [Schema](../../schemas/project/v5.schema.json) · [Expo runbook](../../runbooks/manage-expo-projects.md) |
| 6 | Explicit private Metro / compatible Expo Go opt-in | [Schema](../../schemas/project/v6.schema.json) · [Metro runbook](../../runbooks/manage-metro.md) |
| 7 | Standalone stateless TypeScript/Fastify API | [Schema](../../schemas/project/v7.schema.json) · [API runbook](../../runbooks/manage-typescript-apis.md) |
| 8 | Explicit Python API/PostgreSQL-only backend group | [Schema](../../schemas/project/v8.schema.json) · [Backend runbook](../../runbooks/manage-mobile-backends.md) |
| 9 | Native application with explicit private backend binding | [Schema](../../schemas/project/v9.schema.json) · [Backend runbook](../../runbooks/manage-mobile-backends.md) |

Validation is separate from execution and does not authorize arbitrary commands.
Template, dependency, toolchain and database registries pin approved capabilities;
unsupported shapes are rejected rather than inferred. Manifests contain no secrets.
Allocated ports, ownership receipts, credential bindings and observations belong
in runtime-owned state outside source. New schema/adaptor support requires its own
specification, compatibility tests, reviewed rollout and acceptance evidence.

## 8. Repository and documentation conventions

### 8.1 Repository model

- `gptclaw` remains the platform control repository: host infrastructure,
  platform services, templates, schema, shared agent policy, and runbooks.
- New products receive their own GitHub repository by default.
- Repository automation and the GitHub App credential broker use explicit
  repository bindings and constrained runtime handoff. App installation breadth
  does not authorize unrelated credential use; follow the credential runbook.
- Agents work on branches or Codex worktrees. Reviewable changes flow through
  pull requests before they reach a protected default branch.

### 8.2 Planning documents

Every material feature uses the existing folder convention:

```text
docs/NNN-kebab-case-name/
  spec.md
  technical-design.md
  tasks.md
  acceptance.md       # added when implementation is accepted
```

Feature ideas remain in the catalogue until selected. A feature is not ready
for implementation merely because it appears in that catalogue.

### 8.3 Decision records

Cross-cutting decisions that outlive one feature should be captured as concise
architecture decision records under `docs/decisions/`. A specification may
propose a decision, but the record preserves why the platform default changed.

## 9. Agent configuration model

Codex loads project guidance from `AGENTS.md` files, with instructions closer
to the working directory taking precedence. GptClaw uses that hierarchy
deliberately:

1. **Host policy:** `~/.codex/AGENTS.md`, installed from a reviewed platform
   source, defines universal security and workflow rules.
2. **Repository policy:** `<repo>/AGENTS.md` defines stack, commands, quality
   gates, folder conventions, and product-specific boundaries.
3. **Area policy:** nested `AGENTS.md` files define focused rules for areas such
   as mobile, infrastructure, database migrations, or UI.
4. **Temporary override:** `AGENTS.override.md` is permitted only for an
   explicit, short-lived experiment and must not silently become permanent
   policy.
5. **Skills:** repeatable procedures live in repository-scoped
   `.agents/skills/<skill>/SKILL.md` folders and are versioned with the project.

The host policy should require agents to:

- Read the active spec, design, and tasks before implementation.
- Keep AWS mutations on the GitHub/HCP Terraform path.
- Protect secrets and generated state.
- Prefer project containers or user-scoped tools over privileged installation.
- Ask before adding production dependencies, exposing a Funnel, changing data,
  or performing destructive operations.
- Run stack-specific checks and report exact evidence.
- Preserve user changes, use feature branches/worktrees, and report Git status without discarding unrelated work.
- Update documentation and acceptance evidence as part of completion.

Templates should supply a short repository `AGENTS.md`; detailed procedures
belong in skills or referenced documentation so the instruction chain remains
focused.

## 10. Framework and tooling defaults

The table combines implemented families with desired defaults. Current catalogue
entries support Next.js, FastAPI, stateless Fastify, Expo and approved
web/API/PostgreSQL or API/PostgreSQL shapes. Full native integration acceptance
remains separate from template availability. Tailwind, Vitest, Redis and SQLite
support is not implied by this table. The dashboard
uses repository-local CSS and the Node test runner.

Versions are pinned when a project is created and updated through reviewed
dependency automation. This document names families, not permanent versions.

| Project need | Default | Notes |
|---|---|---|
| Full-stack web application | Next.js App Router, React, TypeScript | Use server components and route handlers where they simplify the product; self-host behind the platform ingress. |
| Web styling and components | Tailwind CSS plus an accessible, repository-owned component layer | Establish design tokens; do not make a remote component service a runtime dependency. |
| TypeScript package manager | pnpm | Pin the package manager and Node LTS version in the repository. |
| Web unit/component tests | Vitest and Testing Library | Keep tests fast and colocated with behavior. |
| Browser acceptance tests | Playwright | Require focused smoke tests for the private preview route. |
| Standalone TypeScript API | Fastify | Prefer Next.js route handlers when the API and web UI share one lifecycle. |
| Python API or AI/data service | FastAPI, Pydantic, uv, Ruff, pytest | Preferred application-backend stack; other stacks require their own selected scope. |
| Mobile or universal application | Expo, Expo Router, React Native, TypeScript | Start with Expo Go when suitable; use development builds for native modules. |
| Relational database | PostgreSQL, supported major pinned per project | Use one isolated database/role per project; SQLite is acceptable for genuinely local single-process tools. |
| Cache or ephemeral coordination | Redis-compatible service only when justified | Do not add a cache by default. |
| Project containers | Rootless Podman | No Docker-socket or root-equivalent access for the agent. |
| Long-running services | User systemd units generated through Podman Quadlet | Enable deliberate restart, health, logging, and boot behavior. |
| Private HTTP ingress | Loopback reverse proxy plus Tailscale Serve | Project processes never listen publicly. |
| Platform dashboard | Next.js and TypeScript | Read-only inventory first; constrained actions later. |
| Manifest validation | YAML plus published JSON Schema | CI and `gptclawctl` validate before acting. |

Templates may deviate when a specification gives a reason. Framework choice is
an architectural default, not a substitute for product requirements.

## 11. Multi-project runtime

Projects live under `/srv/forge/projects/<slug>`. Runtime data lives outside the
Git checkout, under a platform-owned location on the persistent volume.

The reviewed provider allocates loopback ports, generates owned user services,
applies finite resource limits, checks readiness and serializes lifecycle changes.
Its interfaces include start, stop, restart, status, observe, logs, test, dependency,
toolchain, template, repository and database operations. Use the applicable
runbook rather than inventing commands from this overview. Scoped credential
handoff is separate from arbitrary environment-file forwarding.

General pause/resume/remove commands, orphan detection, disk reclamation and idle
suspension remain future work. Recent project retirement used reviewed stop
operations followed by source archival outside inventory discovery, retaining data;
it did not introduce a general deletion API. Future destructive operations need
explicit scope, data protection and ownership checks.

## 12. Private and public routing

### 12.1 Private by default

Every application binds to `127.0.0.1` or its rootless container network. A
local ingress layer maps stable project routes to those services. Tailscale
Serve terminates HTTPS and exposes the ingress only to authorized tailnet
members.

The preferred URL pattern is:

```text
https://<forge-magicdns-name>/projects/<project-slug>/
```

Current templates support the declared private base path. Standalone API docs
use `/projects/<slug>/docs`; group API docs use `/projects/<slug>/api/docs`.
General private HTTPS-port fallback for arbitrary frameworks remains future
design. Reviewed Metro sessions use explicit owned private transport/port profiles,
with operator-managed Serve routes; see the [Metro runbook](../../runbooks/manage-metro.md).
Forge cannot administer Tailscale. Shared and Metro-specific handlers retain the
reviewed operator path; no generic port exposure is implied.

### 12.2 Funnel only on request

This section defines desired future behavior; no exposure manager or automatic
expiry service is delivered. Funnel is a public publication action, not a
development default. The exposure
manager must require:

- The project manifest to permit Funnel.
- An explicit owner request and confirmation naming the project.
- A health check and a warning that the URL is internet-accessible.
- A supported Funnel port separate from the private Serve listener.
- An expiry time, with automatic disablement even if the initiating task ends.
- An audit record and a prominent dashboard indicator.
- Optional application authentication when the content is not intentionally
  public.

The dashboard, databases, admin interfaces, logs, metrics, and arbitrary TCP
services must never be exposed through Funnel.

## 13. Dashboard and local control service

The private, read-only dashboard delivers manifest inventory, supported component
status/health/resources and available app/API-doc/repository links. Missing or
stale observations remain explicit, and unavailable destinations explain missing
prerequisites. README/docs presence is metadata, not an assessment of quality.

The Python collector runs as a forge user service. The Next.js frontend reads its
Unix socket and exposes only health/snapshot reads. Collection is bounded in size,
concurrency and time; timeouts preserve clearly labeled last-known state. Status
observations and observed changes are bounded in-memory data, reset on collector
restart. There is no durable service history, uptime ledger or event timeline.

The owned dashboard manager prepares immutable releases and performs activation,
status, stop and rollback without managing project runtime data. See the
[dashboard runbook](../../runbooks/manage-dashboard.md) for exact flags, resource
limits, socket ownership and operator-only Serve setup.

Git telemetry, build/test summaries, log viewing, public-preview registry, host
resource graphs, backup freshness, search/filter/rescan and lifecycle buttons remain
future work. Later actions must use a typed, narrow interface with ownership,
authorization and audit checks; no API may accept arbitrary shell text.

## 14. Software installation boundary

The platform supports three installation classes:

1. **Project dependencies:** installed inside a project container or through a
   user-scoped package manager; Codex may manage these under repository policy.
2. **Approved host toolchain:** declared in GptClaw infrastructure/bootstrap
   code and deployed through the normal GitHub/HCP pipeline.
3. **Exceptional system package:** requested through a future constrained
   capability broker with an allowlist, owner approval, logging, and a required
   follow-up change to the declared host profile.

Unrestricted `sudo`, mounting the container engine socket with root-equivalent
access, and ad hoc host configuration are not platform features.

## 15. Secrets, data, and identity

Current development PostgreSQL credentials are restricted local role files outside
checkouts, handed only to selected components through the reviewed database
profile. Repository credentials use explicitly scoped broker bindings. The
provider does not grant general forwarding of `.env` or authentication files.
Dashboard payloads exclude credentials; secrets never belong in manifests or logs.

An external runtime-secret manager and broader application-secret injection are
desired future capabilities, not delivered integrations. Each extension must define
identity, materialization, rotation, redaction and recovery before use.

Development database data lives under the runtime-owned project data tree, separate
from application source. Versioned migrations and confirmed backup/reset/restore/
rotation/recovery operations follow the database runbook. Local native backups
share the project volume and are not independent disaster recovery. Use synthetic
data unless another source and its handling are explicitly approved. Production
identities, databases, data and state remain separate.

## 16. Observability, backup, and cost

Supported services have health probes and bounded runtime resources; owned service
logs are available through the lifecycle interface and user journal. The dashboard
shows current component observations, not host-wide monitoring or durable history.
CloudWatch foundation logging and daily seven-retention DLM snapshots are deployed.
Retention-expiry evidence remains unrecorded; restore drills, backup freshness
monitoring and alert delivery are not delivered by RES-001.

Desired extensions include host CPU/memory/disk/load visibility, storage and cost
reporting, backup alerts, ChatGPT/email notifications and later Slack delivery.
Budgets should cover development and separately designed production resources.
Automatic idle shutdown and host scheduling require reviewed wake-up/recovery
contracts before implementation.

## 17. Lifecycle from idea to production

```text
feature catalogue
  -> selected feature
  -> spec
  -> technical design
  -> tasks
  -> branch/worktree implementation
  -> tests and pull request
  -> acceptance record
  -> private development service
  -> optional time-limited Funnel share
  -> production specification
  -> GitHub Actions + HCP Terraform deployment
```

The sequence describes the desired end-to-end workflow; Funnel and production
stages require future product-specific implementation. Local tests, CI, merge,
private rollout and owner acceptance are distinct gates, with sanitized evidence
recorded for each.

An agent may help draft every artifact, but the owner selects scope, approves
public exposure, reviews infrastructure plans, and authorizes production
promotion.

## 18. Handover guidance

Start with applicable host, repository and area `AGENTS.md` guidance, then the
[documentation index](../README.md), selected specification/design/tasks and its
acceptance record. Consult operational runbooks for runtime or host work. Use this
architecture and the [feature catalogue](./features.md) for direction, not as
execution authority.

Verify actual Git/runtime state and preserve unrelated work. Check pending gates
rather than treating installation, passing CI or merge as proof of acceptance.
Future features should add compatible reviewed contracts and meaningful tests,
keep development access private and retain separate infrastructure/production
approval paths. A catalogue entry alone never authorizes implementation.

## 19. Reference basis

- [OpenAI: Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [OpenAI: Customization](https://learn.chatgpt.com/docs/customization/overview)
- [OpenAI: Remote connections](https://learn.chatgpt.com/docs/remote-connections)
- [Next.js: Installation defaults](https://nextjs.org/docs/app/getting-started/installation)
- [Next.js: Self-hosting](https://nextjs.org/docs/app/guides/self-hosting)
- [Expo: Expo Router](https://docs.expo.dev/router/introduction/)
- [Expo: Publish a web app](https://docs.expo.dev/deploy/web/)
- [Podman: Rootless Quadlet units](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)
- [Tailscale: Serve](https://tailscale.com/docs/reference/tailscale-cli/serve)
- [Tailscale: Funnel](https://tailscale.com/docs/features/tailscale-funnel)
- [AWS: EBS snapshot lifecycle automation](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-lifecycle.html)
- [AWS Backup: Restore testing](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html)
