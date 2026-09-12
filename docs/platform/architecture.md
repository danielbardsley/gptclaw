# GptClaw Platform Architecture

- **Status:** Directional architecture and session handover
- **Last updated:** 2026-09-06
- **Implemented baseline:** [SPEC-001](../001-bootstrap-remote-development-host/spec.md)
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
- Funnel is disabled by default, explicit per exposure, visibly public,
  auditable, and automatically expires.
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

## 4. Implemented foundation

SPEC-001 provides the current platform floor:

- An Ubuntu 24.04 EC2 host created only by GitHub Actions and HCP Terraform.
- A protected, encrypted EBS project volume mounted at `/srv/forge`.
- A constrained `forge` user with Tailscale-only OpenSSH access.
- AWS Systems Manager as the independent recovery path.
- Codex installed and authenticated for `forge`.
- A write-enabled, repository-specific GitHub deploy key for GptClaw.
- A ChatGPT SSH project connection to `/srv/forge/projects/gptclaw`.
- CloudWatch bootstrap and authentication logging.

The accepted baseline is recorded in
[ACCEPTANCE-001](../001-bootstrap-remote-development-host/acceptance.md).

## 5. Target logical architecture

```text
Owner
  |
  +-- ChatGPT desktop/mobile -------------------------------+
  |     remote tasks, approvals, diffs                      |
  +-- Future Slack adapter                                  |
  |     authenticated commands, notifications               |
  |                                                         v
  +--------------------------------------------------- Tailscale tailnet
                                                            |
                                                    SSH to forge-dev
                                                            |
┌──────────────────────────────── EC2 development host ─────┴───────────────┐
│ Codex app server / CLI as forge                                           │
│       |                                                                   │
│       +-- layered AGENTS.md + repository skills                           │
│       +-- gptclawctl project lifecycle CLI                                │
│       +-- Git worktrees and repository-specific credentials               │
│                                                                           │
│ /srv/forge/projects/<project>          /srv/forge/platform                │
│   .gptclaw/project.yaml                  registry and generated state      │
│   AGENTS.md                              dashboard/control application     │
│   docs/NNN-feature/...                   templates and skills              │
│   application source                                                       │
│          |                                                                │
│          v                                                                │
│ rootless Podman + user systemd/Quadlet                                    │
│   project-a containers  127.0.0.1:41xx                                    │
│   project-b containers  127.0.0.1:42xx                                    │
│   project-c containers  127.0.0.1:43xx                                    │
│          |                                                                │
│          +--> private loopback ingress --> Tailscale Serve --> tailnet     │
│          +--> explicit share ingress --> Tailscale Funnel --> internet     │
│                                                                           │
│ dashboard: inventory, health, Git, resources, URLs, logs, exposure state   │
└───────────────────────────────────────────────────────────────────────────┘

GitHub repositories
  +-- pull requests, checks, releases, container images
  +-- GitHub Actions
          |
          +-- HCP Terraform workspaces --> development AWS infrastructure
          +-- HCP Terraform workspaces --> isolated production environments
```

## 6. Control and data planes

### 6.1 Control plane

The control plane describes and coordinates work but does not directly serve
application traffic. It comprises:

- ChatGPT remote projects and Codex tasks.
- Repository specifications, designs, tasks, decisions, and acceptance records.
- Layered `AGENTS.md` instructions and repository skills.
- The proposed `gptclawctl` command and project manifest schema.
- The dashboard and its local status collector.
- GitHub pull requests, checks, Actions, environments, and approvals.
- HCP Terraform workspaces and phase-specific AWS identities.
- A later Slack adapter that submits constrained operations to the same control
  interface rather than exposing a shell.

### 6.2 Development data plane

The development data plane runs project code on the EC2 host:

- One rootless runtime boundary per project.
- Project-specific application, database, cache, and worker containers.
- Loopback-only host port publication.
- Health checks, user-journal logs, and resource limits.
- Tailscale Serve routes for authenticated tailnet access.
- Explicit Funnel routes for temporary public access.

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

Every managed project should contain a versioned `.gptclaw/project.yaml`. This
manifest is the contract between the repository, lifecycle tooling, dashboard,
runtime, and ingress layer. A future specification will define its exact schema.

Illustrative shape:

```yaml
schema_version: 1
project:
  id: example-app
  name: Example App
  kind: web
repository:
  default_branch: main
runtime:
  profile: nextjs
  start: pnpm dev
  health_path: /api/health
  internal_port: 3000
  resources:
    memory_mb: 1024
    cpu_shares: 512
exposure:
  private: true
  base_path: /projects/example-app
  funnel:
    allowed: false
data:
  postgres: false
quality:
  test: pnpm test
  lint: pnpm lint
  build: pnpm build
```

The manifest must not contain credentials. It describes desired behavior;
runtime identifiers, allocated ports, health history, and process state belong
in generated platform state.

## 8. Repository and documentation conventions

### 8.1 Repository model

- `gptclaw` remains the platform control repository: host infrastructure,
  platform services, templates, schema, shared agent policy, and runbooks.
- New products receive their own GitHub repository by default.
- Each repository uses a dedicated host credential or a future narrowly scoped
  GitHub App installation. Credentials are never shared across unrelated
  projects.
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
to the working directory taking precedence. GptClaw will use that hierarchy
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
- Preserve user changes, use feature branches/worktrees, and leave clean status.
- Update documentation and acceptance evidence as part of completion.

Templates should supply a short repository `AGENTS.md`; detailed procedures
belong in skills or referenced documentation so the instruction chain remains
focused.

## 10. Framework and tooling defaults

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
| Python API or AI/data service | FastAPI, Pydantic, uv, Ruff, pytest | Use only when Python materially improves the workload. |
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

The future lifecycle manager should:

- Allocate a collision-free loopback port range per project.
- Create a rootless container network, volumes, and user services per project.
- Apply default CPU, memory, process, and log limits.
- Build from a pinned container definition or run a declared development
  command inside a controlled development container.
- Require a health check before marking a project available.
- Maintain start, stop, restart, rebuild, pause, resume, and remove operations.
- Serialize destructive operations per project while allowing unrelated
  projects and Codex worktrees to run concurrently.
- Detect stale worktrees, orphaned containers, abandoned ports, and excessive
  disk use.
- Never infer a command from dashboard input; execute only manifest-defined,
  schema-validated operations.

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

Templates must support a configurable development base path. Projects that
cannot safely operate beneath a path receive a dedicated private HTTPS port
recorded in the manifest and dashboard.

### 12.2 Funnel only on request

Funnel is a public publication action, not a development default. The exposure
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

The dashboard is the human-readable control plane for all projects. Its first
release should be read-only and available only through Tailscale Serve.

It should combine:

- Manifest metadata and repository location.
- Git branch, dirty state, ahead/behind status, and last commit.
- Runtime state, health, uptime, restart count, and resource consumption.
- Private URL and any active Funnel URL with expiry.
- Build/test status and recent deployment revision.
- Recent structured logs with secret redaction.
- Storage consumption and backup freshness.

Later control actions call a narrow local API or `gptclawctl`. The API runs as
`forge`, uses a Unix-domain socket where practical, accepts typed operations,
and never accepts arbitrary shell text. High-impact actions require explicit
confirmation and produce an audit event.

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

- Project runtime secrets are stored in an external secret manager and
  materialized only at process start.
- Each project receives the smallest repository and cloud permissions it needs.
- Dashboard responses show whether a secret is configured, never its value.
- Local `.env` files are ignored, mode-restricted, and treated as temporary
  development material rather than the system of record.
- Database migrations are versioned, reversible where practical, and backed up
  before destructive execution.
- Seed data is synthetic unless a specification explicitly approves another
  source and its handling controls.
- Production identities are unavailable to development containers and agents
  by default.

## 16. Observability, backup, and cost

- Every service defines a health check and writes structured logs to stdout or
  stderr.
- User-service logs remain queryable through journald; selected platform logs
  may be shipped to CloudWatch with retention controls.
- The dashboard reports host CPU, memory, disk, load, container use, and failed
  health checks.
- Alerts initially target ChatGPT notifications or email; Slack becomes an
  additional destination later.
- The protected project EBS volume receives an automated snapshot policy
  created by Terraform, with retention and a documented restore test. RES-001
  permits silent DLM failures; backup monitoring and notifications are excluded.
- Budgets and cost visibility cover EC2, EBS, snapshots, CloudWatch, data
  transfer, HCP Terraform, Expo/EAS, and production resources.
- Idle projects can be stopped automatically; the development host may gain a
  deliberate schedule only after remote wake-up and recovery are designed.

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

An agent may help draft every artifact, but the owner selects scope, approves
public exposure, reviews infrastructure plans, and authorizes production
promotion.

## 18. Handover guidance

When starting a new ChatGPT session on `forge-dev`, provide or point the agent
to these files in order:

1. This architecture document.
2. [The feature catalogue](./features.md).
3. The selected feature's future `spec.md`, `technical-design.md`, and
   `tasks.md`.
4. The repository's `AGENTS.md` once the agent-configuration feature is
   implemented.
5. [ACCEPTANCE-001](../001-bootstrap-remote-development-host/acceptance.md) and
   the applicable runbooks when work touches the host.

The agent should not implement a catalogue item until a specification exists
and the owner has asked for that specification to be implemented.

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
