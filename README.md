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

As of October 10, 2026, the repository has progressed beyond the initial host
bootstrap. The statuses below distinguish accepted capabilities from merged
code that still needs deployment or acceptance.

| Capability | Current state and evidence |
|---|---|
| Remote development foundation | **Delivered.** EC2 host, persistent project volume, Tailscale-only SSH, SSM recovery, repository-scoped Git access, remote project connection, and HCP AWS workload identity. [SPEC-001 acceptance](docs/001-bootstrap-remote-development-host/acceptance.md). |
| Automated project-volume backups | **Delivered.** Daily DLM snapshots with seven-snapshot retention; a naturally scheduled snapshot and a subsequent no-change plan were verified. Retention-expiry follow-up remains unrecorded in the acceptance document; restore testing and freshness monitoring are not delivered. [SPEC-002 acceptance](docs/002-automated-ebs-snapshots/acceptance.md). |
| Agent guidance and workflows | **Deployed, with acceptance remaining.** Reviewed host policy, repository and nested guidance templates, specification and project-bootstrap skills, runtime-operation and release-promotion skills, handovers, decision records, and context validation. Fresh-session, client, or live-workflow checks remain outstanding by initiative. [Initiatives 003–012](docs/README.md). |
| Project manifest v1 | **Delivered.** A versioned declaration for one private HTTP service, JSON Schema, offline validator, and synthetic example. Validation does not create or run an application. [Reference](docs/project-manifest.md) · [SPEC-013 acceptance](docs/013-versioned-project-manifest/acceptance.md). |
| Rootless container toolchain | **Deployed; remaining host acceptance pending.** Rootless packages/configuration and matching receipts are installed. October 9 container build/run, network, file ownership, crash restart and cleanup checks passed; independent logout/reboot and synthetic-source replacement checks remain pending. [PR #26](https://github.com/danielbardsley/gptclaw/pull/26) · [SPEC-014 evidence](docs/014-rootless-container-toolchain/acceptance.md). |
| Declared host tool profile | **Deployed; final acceptance pending.** Successful receipts cover all 26 components and match the reviewed profile/deployment revision. Protected deployment is correlated; recovery/rollback reconciliation and owner acceptance remain pending. Temporary upstream-source exceptions expire November 1, 2026 (America/New_York). [SPEC-015 evidence](docs/015-host-tool-profile/acceptance.md). |
| Private application workflow | **Deployed; final acceptance pending.** Initial CLI, pinned Next.js template, independent rootless services and shared private routing merged in PR #40. Both desktop apps/counters confirmed; source-update/first-app cleanup acceptance remains. [SPEC-018 evidence](docs/018-first-private-application/acceptance.md). |
| Automatic replacement-host Tailscale enrollment | **Deployed; final acceptance pending.** Account issuer/trust and matching host receipts are recorded; the node is tagged online, retained storage checks passed, and Daniel confirmed independent SSM access. Recovered October 8 verification records manual-key-free enrollment and protected-run provenance; final owner acceptance remains pending. [PR #28](https://github.com/danielbardsley/gptclaw/pull/28) · [SPEC-016 evidence](docs/016-tailscale-workload-identity/acceptance.md). |

The first private-app workflow is merged in [PR #40](https://github.com/danielbardsley/gptclaw/pull/40)
and running on EC2. Its narrow CLI creates a pinned Next.js/TypeScript app and
manages independent rootless containers, loopback ports, health and private URLs.
Daniel confirmed both Hello World and Hello Second pages/counters from his desktop.
One shared Tailscale Serve prefix handles all app routes; subsequent app starts
need no individual Serve commands. See [the app runbook](runbooks/manage-private-apps.md).
Desktop source-update and first-app stop/source-retention acceptance remain pending
in [SPEC-018](docs/018-first-private-application/acceptance.md).

The planning bootstrap remains a separate local planning-ready starter. Runtime
and promotion skills use reviewed interfaces; production promotion requires an
existing product pipeline. A dashboard, public-preview manager, databases, secrets
management and product production pipelines are not yet delivered.

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
config/codex/              Canonical reviewed host-policy source
docs/                      Initiative plans, acceptance evidence, and platform direction
examples/                  Synthetic manifest and rootless-container acceptance fixtures
infra/dev-host/            Development host, storage, backups, and bootstrap tooling
infra/tailscale-federation/Separate account-level workload-identity issuer stack
requirements/              Hash-pinned manifest validation dependencies
runbooks/                  Setup, connection, maintenance, and recovery procedures
schemas/                   Versioned project manifest schema
scripts/                   Bootstrap, validation, verification, and offline tests
templates/                 App starters, container toolchain, planning and guidance templates
```

## Working with GptClaw

- **Connect to the host:** follow [the remote project connection runbook](runbooks/connect-chatgpt.md).
- **Prepare another project's guidance:** use [the repository template and adaptation guide](templates/agents/README.md) and [nested guidance pattern](templates/agents/nested/README.md).
- **Create a local planning starter:** follow [the project bootstrap workflow](.agents/skills/gptclaw-project-bootstrap/SKILL.md), which uses `scripts/bootstrap-project.py`.
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
| Create, start, stop and inspect private apps | [Manage private apps](runbooks/manage-private-apps.md) |
| Configure automatic Tailscale enrollment | [Manage workload identity federation](runbooks/manage-tailscale-federation.md) |

Merging a PR does not deploy infrastructure. Plans and applies use protected
manual GitHub Actions workflows with HCP remote execution:

- [Development host workflow](.github/workflows/terraform-dev-host.yml), workspace `gptclaw-dev-host`.
- [Account federation workflow](.github/workflows/terraform-tailscale-federation.yml), workspace `gptclaw-tailscale-federation`.

For any future replacement, verify the account issuer and exact-role tailnet
trust described in the federation runbook. Replacement also requires a suitable
recovery point, a reviewed window, and post-deployment verification of private
access and preserved project storage.
Deployment and final acceptance remain separate from local and PR checks.

## Local validation

For policies, templates, scripts, workflows, or infrastructure changes, run
`./scripts/check-repository.sh` from the repository root. It includes offline
checks for agent workflows, host policy/bootstrap, project manifests, host tools,
rootless containers, and Tailscale federation. First prepare and activate the
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
