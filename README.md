# GptClaw

GptClaw is a private-access remote development platform, built around a
persistent AWS development host and ChatGPT/Codex remote project access. This
repository owns the infrastructure, reviewed agent guidance, project planning
and validation tools, and operator runbooks.

Infrastructure changes follow committed code → GitHub Actions → HCP Terraform →
AWS. The development host has no public inbound access; SSH uses Tailscale and
recovery uses AWS Systems Manager. Project storage is encrypted and retained
across compute replacement.

## Current state

As of October 15, 2026, GptClaw runs private web applications, Python and
TypeScript APIs, web/API groups, managed development PostgreSQL and Android-first
Expo workflows, with a read-only projects dashboard. Delivered scope and remaining acceptance are distinguished below.

| Capability | Current state and evidence |
|---|---|
| Remote development foundation | **Delivered.** Protected encrypted project storage, private SSH, SSM recovery and infrastructure workload identity. [SPEC-001 acceptance](docs/001-bootstrap-remote-development-host/acceptance.md). |
| Project-volume snapshots | **Delivered initial scope.** Daily DLM snapshots with seven-snapshot retention. Retention-expiry evidence, restore testing and freshness monitoring remain outstanding or separately scoped. [SPEC-002 acceptance](docs/002-automated-ebs-snapshots/acceptance.md). |
| Agent guidance and workflows | **Deployed, with initiative-specific acceptance remaining.** Host/repository/area guidance, planning/bootstrap/runtime/release skills, handovers and decision records. [Initiatives 003–012](docs/README.md). |
| Rootless runtime and host profile | **Deployed; remaining host acceptance pending.** Rootless Podman, user systemd/Quadlet and the declared 26-component tool profile. Logout/reboot/replacement and recovery/owner checks remain as recorded. Tool-profile source exceptions expire November 1, 2026. [SPEC-014](docs/014-rootless-container-toolchain/acceptance.md) · [SPEC-015](docs/015-host-tool-profile/acceptance.md). |
| Automatic replacement-host enrollment | **Deployed; final acceptance pending.** Tailscale workload-identity enrollment and retained-storage evidence are recorded; remaining owner gates are documented. [SPEC-016](docs/016-tailscale-workload-identity/acceptance.md). |
| Private project lifecycle | **Initial web workflow delivered; subsequently extended.** Installed provider 1.14.0 validates manifest schemas 1–9: web, standalone FastAPI/Fastify, web/API/PostgreSQL groups, mobile source/Metro and explicit mobile backend binding. Source-only mobile schema 5 does not start a runtime. Shared private ingress, health, logs, quality commands and owned lifecycle operations are available. [Web](runbooks/manage-private-apps.md) · [API](runbooks/manage-python-apis.md) · [Groups](runbooks/manage-multi-service-projects.md). The initial RUN-006 web/API slice is merged and accepted; its closeout preserves the separate database scope and hydration follow-up. |
| Dependencies, toolchains and templates | **Initial slices delivered, extended for APIs, groups and Expo.** Reviewed dependency policies, pinned Node/pnpm and Python/uv profiles, immutable versioned template entries and explicit adoption/update workflows. [Dependencies](runbooks/manage-project-dependencies.md) · [Toolchains](runbooks/manage-project-toolchains.md) · [Templates](runbooks/manage-project-templates.md). |
| Mobile development | **Creation, managed private Metro and compatible Android Expo Go foundations delivered.** The Python/PostgreSQL Fieldnotes integration has an approved working preview; detailed native CRUD/recovery/accessibility and final integration acceptance remain pending. [Expo](runbooks/manage-expo-projects.md) · [Metro](runbooks/manage-metro.md) · [Go](runbooks/manage-expo-go.md) · [Backend evidence](docs/036-mobile-python-backend/acceptance.md). |
| GitHub repository automation and credentials | **Delivered scoped slices.** Reviewed repository creation/adoption and credential broker with explicit repository bindings. This grants no production or unrelated credential access. [Repositories](runbooks/manage-project-repositories.md) · [Credentials](runbooks/manage-repository-credentials.md). |
| Development databases | **Delivered initial development slice.** Private PostgreSQL, persistent data outside source checkouts, migrations, native backup/restore and explicitly confirmed destructive operations. Local backups do not replace volume recovery or production database design. [SPEC-026 evidence](docs/026-development-databases/acceptance.md) · [Operations](runbooks/manage-development-databases.md). |
| Private projects dashboard | **Inventory, live status and links delivered and accepted.** Web/API/DB component details and available private app/API-doc/repository links; bounded in-memory observations, with no durable status history or mutation API. [SPEC-027](docs/027-dashboard-project-inventory/acceptance.md) · [SPEC-028](docs/028-dashboard-live-service-status/acceptance.md) · [SPEC-029](docs/029-dashboard-project-links/acceptance.md). The visual refresh is deployed and merged in [PR #71](https://github.com/danielbardsley/gptclaw/pull/71); owner appearance feedback is positive, while the separately requested actual-browser zoom check remains unrecorded. |

Active projects change as application and acceptance work proceeds. Use the
private dashboard for current inventory rather than treating example project
names as a complete list. The dashboard itself runs in a separate rootless
container at the private `/dashboard/` route. Retained synthetic acceptance APIs
are development fixtures, not production deployments.

Planning bootstrap remains separate from runnable application creation. Public
preview management, general runtime-secret management, signed mobile build/release
flows, dashboard lifecycle controls and product production pipelines remain future
work. Native integration acceptance is tracked independently from basic Go preview. Release/promotion skills require an existing reviewed product pipeline.

Use the [documentation index](docs/README.md) for specifications, designs, task
lists, and acceptance records. The [platform architecture](docs/platform/architecture.md)
and [feature catalogue](docs/platform/features.md) describe direction and future
scope. Historical initiative sections retain observations from earlier revisions;
use current acceptance summaries for deployed status and remaining evidence.
Catalogue entries alone do not
authorize implementation.

## Repository layout

```text
.agents/skills/            Repository-local agent workflows and supporting resources
.github/                   Protected infrastructure workflows and dependency automation
config/                    Host policy, dependency/toolchain/template/database catalogues
docs/                      Initiative plans, acceptance evidence, and platform direction
examples/                  Synthetic manifest and rootless-container acceptance fixtures
infra/dev-host/            Development host, storage, backups, and bootstrap tooling
infra/tailscale-federation/Separate account-level workload-identity issuer stack
requirements/              Hash-pinned manifest validation dependencies
runbooks/                  Setup, connection, maintenance, and recovery procedures
platform/dashboard/        Private Next.js dashboard frontend
schemas/                   Versioned manifest and catalogue schemas
scripts/                   Bootstrap, validation, verification, and offline tests
templates/                 App starters, container toolchain, planning and guidance templates
```

For the purpose of each directory and its main subdirectories, see the
[directory guide](docs/repository-layout/README.md).

## Working with GptClaw

- **Connect to the host:** follow [the remote project connection runbook](runbooks/connect-chatgpt.md).
- **Prepare another project's guidance:** use [the repository template and adaptation guide](templates/agents/README.md) and [nested guidance pattern](templates/agents/nested/README.md).
- **Create a local planning starter:** follow [the project bootstrap workflow](.agents/skills/gptclaw-project-bootstrap/SKILL.md), which uses `scripts/bootstrap-project.py` and copies the complete planning skill
  and [engineering standards](templates/projects/engineering/README.md). Application
  creation receives the same guidance; stack selection must map standards to checks.
- **Create and run private apps:** follow [the private application runbook](runbooks/manage-private-apps.md), using the source CLI or installed stable launcher.
- **Validate a project declaration:** follow [the manifest setup and usage reference](docs/project-manifest.md); [the example](examples/project-manifest/web.yaml) is inert.
- **Plan and review work:** start with [AGENTS.md](AGENTS.md), the applicable initiative, and [architecture decisions](docs/decisions/README.md).

## Operations and deployment

| Operation | Runbook |
|---|---|
| Establish GitHub/HCP/AWS deployment prerequisites | [Bootstrap HCP and AWS](runbooks/bootstrap-hcp-aws.md) |
| Inspect backups and outstanding retention evidence | [Inspect backups](runbooks/inspect-backups.md) |
| Replace or recover the development host | [Recover the host](runbooks/recover-dev-host.md) |
| Install or update the reviewed host policy | [Manage host guidance](runbooks/manage-host-agents.md) |
| Deploy and verify the declared tool profile | [Manage host tools](runbooks/manage-host-tools.md) |
| Deploy and accept the rootless toolchain | [Manage rootless tooling](runbooks/manage-rootless-toolchain.md) |
| Manage project dependencies | [Manage project dependencies](runbooks/manage-project-dependencies.md) |
| Create, start, stop and inspect private apps | [Manage private apps](runbooks/manage-private-apps.md) |
| Manage standalone APIs and multi-service groups | [Python APIs](runbooks/manage-python-apis.md) · [TypeScript APIs](runbooks/manage-typescript-apis.md) · [Groups](runbooks/manage-multi-service-projects.md) |
| Author mobile applications and bind private backends | [Expo](runbooks/manage-expo-projects.md) · [Metro](runbooks/manage-metro.md) · [Mobile backends](runbooks/manage-mobile-backends.md) |
| Operate development PostgreSQL | [Development databases](runbooks/manage-development-databases.md) |
| Prepare, activate or roll back the private dashboard | [Dashboard](runbooks/manage-dashboard.md) |
| Configure automatic Tailscale enrollment | [Manage workload identity federation](runbooks/manage-tailscale-federation.md) |

Merging a PR does not deploy infrastructure. Plans and applies use protected
manual GitHub Actions workflows with HCP remote execution:

- [Development host workflow](.github/workflows/terraform-dev-host.yml), workspace `gptclaw-dev-host`.
- [Account federation workflow](.github/workflows/terraform-tailscale-federation.yml), workspace `gptclaw-tailscale-federation`.

For any future replacement, verify the account issuer and exact-role tailnet
trust described in the federation runbook. Replacement also requires a suitable
recovery point, a reviewed window, and post-deployment verification of private
access and preserved project storage.
Project runtime operations use the reviewed unprivileged CLI; dashboard releases use
the owned release manager. These are distinct from AWS infrastructure deployment.
Operator-only directory allocation and Tailscale administration retain their
reviewed SSM path. Deployment and final acceptance remain separate from local
and PR checks.

## Local validation

For policies, templates, scripts, workflows, or infrastructure changes, run
`./scripts/check-repository.sh` from the repository root. It includes offline
checks for agent workflows, host policy/bootstrap, project manifests, host tools,
rootless containers, Tailscale federation, project providers and dashboard contracts.
Dashboard frontend checks and private rollout are documented in its runbook;
repository checks alone do not prove browser acceptance. First prepare and activate the
isolated Python 3.12 environment:

```sh
python3 scripts/setup-project-manifest.py --venv .venv-manifest
source .venv-manifest/bin/activate
./scripts/check-repository.sh
```

Setup downloads hash-pinned dependencies; validation/tests then run offline.
Reuse the prepared environment; setup refuses existing destinations. Do not
install host packages to make checks pass.

For documentation-only edits, review relative links and run:

```sh
git diff --check
git diff --cached --check
```

For Terraform changes, use the version declared in
[the development version file](infra/dev-host/.terraform-version) and run in each
affected Terraform root (`infra/dev-host` or `infra/tailscale-federation`):

```sh
terraform fmt -check -recursive
terraform init -backend=false -input=false -lockfile=readonly
terraform validate
terraform test
```

Initialization may fetch providers. Terraform tests use mocked AWS resources;
the development-host suite also renders cloud-init locally. These checks do not
prove deployed behavior. Local `terraform apply` and direct AWS infrastructure
mutation are not supported.

Never commit Terraform state, saved plans, local variable files, access tokens,
private keys, Codex authentication data, or environment dumps. Preserve private
host access, persistent-volume protection, and development/production isolation.

For exact per-project Node/pnpm selection, verified image acquisition and legacy
adoption, see [the toolchain runbook](runbooks/manage-project-toolchains.md).
