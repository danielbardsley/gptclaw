# GptClaw

GptClaw is a secure remote development platform built around a persistent AWS
development host and ChatGPT's SSH project connection. Infrastructure changes
are reviewed in GitHub, executed remotely by HCP Terraform, and never applied
from a developer workstation.

The first implementation slice is documented in
[`docs/001-bootstrap-remote-development-host`](./docs/001-bootstrap-remote-development-host/).

The intended platform shape and candidate feature backlog are documented in
the [platform architecture](./docs/platform/architecture.md) and
[feature catalogue](./docs/platform/features.md). Catalogue entries are not
implementation specifications; each selected feature is specified separately.

## Repository layout

```text
.github/        GitHub Actions and dependency automation
docs/           Specifications, designs, and implementation task lists
infra/dev-host/ Terraform for the first remote development host
runbooks/       Operator setup, connection, and recovery procedures
scripts/        Non-secret verification utilities
```

## Local validation

Use the Terraform version declared in `infra/dev-host/.terraform-version`.

```sh
cd infra/dev-host
terraform fmt -check -recursive
terraform init -backend=false -input=false
terraform validate
terraform test
```

Local validation is supported. Local `terraform apply` is not. Plans and applies
must be initiated by `.github/workflows/terraform-dev-host.yml`; provider
operations execute in the HCP Terraform workspace `gptclaw-dev-host`.

Do not commit Terraform state, saved plans, variable files, access tokens,
private keys, Codex authentication data, or captured environment dumps.
