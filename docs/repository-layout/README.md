# GptClaw directory guide

GptClaw provides a private remote development environment: it provisions the AWS
host, supplies tools for creating and managing projects, guides agent work, and
provides a private dashboard. Applications created with those tools live in
separate project directories under `/srv/forge/projects`.

This guide explains the repository's contents and their purpose. A directory's
presence does not establish that its capability is deployed or accepted; consult
[initiative acceptance records](../README.md) for that evidence.

## Top-level directories

| Directory | Contents and purpose |
|---|---|
| [`.agents/`](../../.agents/) | Workflows for coding agents. `skills/` contains instructions for specification writing, project bootstrap, context review, runtime operations, release promotion, and handovers. Supporting `assets/` provide document templates; `references/` provide checklists and operating contracts. |
| [`.github/`](../../.github/) | Automation run by GitHub. `workflows/` contains infrastructure deployment and validation workflows, plus checks for private application tooling and the dashboard. `dependabot.yml` configures dependency updates. Infrastructure deployment follows committed code → GitHub Actions → HCP Terraform → AWS. |
| [`config/`](../../config/) | Reviewed policies, profiles, and catalogue data consumed by platform tools. These define supported templates, toolchains, dependency policies, databases, mobile tooling, browser checks, repository credential settings, and the canonical host agent policy. See the configuration table below. |
| [`docs/`](../) | Specifications, technical designs, task lists, and acceptance evidence grouped by numbered initiative. `platform/` contains architecture, feature direction, and sequencing; `decisions/` records durable architecture choices. These documents connect requirements to implementation and verification. |
| [`examples/`](../../examples/) | Small synthetic examples and verification fixtures. `project-manifest/` demonstrates a project declaration. `rootless-toolchain/` supplies a container and service fixture for testing host container capabilities. |
| [`infra/`](../../infra/) | Infrastructure as code. `dev-host/` defines the AWS development host, networking, identities, persistent storage, backups, logging, and bootstrap configuration. `tailscale-federation/` is a separate Terraform stack for the account-level identity issuer used in automatic private-network enrollment. |
| [`platform/`](../../platform/) | Source for GptClaw's own platform interface. `dashboard/` contains the Next.js dashboard: pages, components, API routes, collector access code, and tests for project inventory, service status, and project links. Its installed runtime lives separately under `/srv/forge/platform`. |
| [`requirements/`](../../requirements/) | Pinned Python dependencies for repository tooling. `project-manifest.txt` records exact versions and hashes so the validation environment can be reproduced without installing packages globally. |
| [`runbooks/`](../../runbooks/) | Procedures for operating the system: connection, deployment prerequisites, backup inspection, host recovery, policy and tool updates, private apps, dependencies, toolchains, databases, credentials, and other operations. |
| [`schemas/`](../../schemas/) | Machine-readable validation rules. Versioned JSON Schemas describe valid project manifests, dependency policies, template catalogues, and toolchain profiles. Validators use these to reject unsupported or malformed declarations. |
| [`scripts/`](../../scripts/) | Executable platform and repository tooling. This includes `gptclawctl`, project bootstrap and manifest validation, app lifecycle and private routing, dependencies, toolchains, templates, repositories, credentials, databases, mobile projects, worktrees, and dashboard collection. `tests/` contains automated checks and synthetic fixtures; `lib/` contains shared host-policy code. |
| [`templates/`](../../templates/) | Reusable starting material for new projects: agent guidance, planning documents, architecture decision records, container toolchain definitions, and versioned application starters. See the template table below. |
| `.venv-manifest/` | Generated local Python environment for manifest validation and repository tests. Contains the environment and installed dependencies; it is ignored by Git and may be absent in a fresh checkout. |
| `.git/` | Git's internal repository data: commit history, branches, tags, staging index, and remote configuration. Managed through Git commands. |

## Configuration groups

| Subdirectory | Use |
|---|---|
| [`config/codex/`](../../config/codex/) | Canonical reviewed host `AGENTS.md` policy source. Editing the source does not install the policy; installation follows the [host-policy runbook](../../runbooks/manage-host-agents.md). |
| [`config/templates/`](../../config/templates/) | Versioned catalogues telling project-creation tooling which application template releases are available. |
| [`config/toolchains/`](../../config/toolchains/) | Versioned profiles describing supported language toolchains. |
| [`config/project-dependencies/`](../../config/project-dependencies/) | Policies consumed by dependency-management commands. |
| [`config/repository-credentials/`](../../config/repository-credentials/) | GitHub App configuration metadata used by repository credential tooling. |
| [`config/databases/`](../../config/databases/) | Profiles for supported development database tooling. |
| [`config/mobile/`](../../config/mobile/) | Configuration for mobile project tooling. |
| [`config/browser-checks/`](../../config/browser-checks/) | Profiles for browser-based verification tooling. |

## Infrastructure support directories

Within [`infra/dev-host/`](../../infra/dev-host/):

- `templates/` contains cloud-init and shell templates rendered into host bootstrap configuration.
- `lib/` contains Python helpers for rootless tooling, host tools, and Tailscale federation.
- `tests/` contains Terraform tests for security, deployment policy, storage backups, host policy, and bootstrap behavior.

[`infra/tailscale-federation/tests/`](../../infra/tailscale-federation/tests/)
checks the separate account-level federation stack.

## Template groups

| Subdirectory | Use |
|---|---|
| [`templates/agents/`](../../templates/agents/) | Repository guidance templates and adaptation instructions. `nested/` supplies guidance for individual areas, with examples for backend, infrastructure, migrations, mobile, and UI work. |
| [`templates/projects/planning/`](../../templates/projects/planning/) | A planning-ready project skeleton containing initial guidance, README, documentation structure, feature catalogue, and Git ignore rules. |
| [`templates/decisions/`](../../templates/decisions/) | An architecture decision record template and guidance for recording decisions. |
| [`templates/apps/node-toolchain/`](../../templates/apps/node-toolchain/) | Container build material for the Node toolchain, including pnpm installation. |
| [`templates/apps/python-toolchain/`](../../templates/apps/python-toolchain/) | Container build material for the Python toolchain. |
| [`templates/apps/releases/`](../../templates/apps/releases/) | Versioned application starter source. Each release preserves its source, dependencies, guidance, and checks so project creation can select a specific starting point. |

Application starter families under `templates/apps/releases/` include:

- **`nextjs/`** — a TypeScript web application.
- **`fastapi/`** — a Python API application.
- **`notes/`** — a multi-service example combining a web frontend and API.
- **`notes-postgres/`** — a notes application with PostgreSQL support and database migrations.
- **`expo-react-native/`** — a mobile application starter.

Within these starters, `app/` or `src/` holds application code; `api/` and `web/`
separate services in the notes starters; `tests/` and `checks/` verify behavior
and quality; `docs/` records architecture and standards; and `migrations/`
contains database schema changes where applicable.

## How the directories fit together

A typical change starts in `docs/`, which defines the requirements and design.
`config/` and `schemas/` define supported declarations. `scripts/`, `templates/`,
`platform/`, or `infra/` implement the capability. `.github/` validates or deploys
it, and `runbooks/` explains its operation. `.agents/` guides agent work through
that process. Tests and synthetic examples provide verification, while initiative
acceptance records document the results.

The root [README](../../README.md) is the project entry point, and root
[AGENTS.md](../../AGENTS.md) supplies repository working guidance. The
[documentation index](../README.md) links to individual initiatives and their
current acceptance records.
